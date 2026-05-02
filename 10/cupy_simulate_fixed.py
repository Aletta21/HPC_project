from os.path import join
import sys
import time
import numpy as np
import cupy as cp


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


# Raw CUDA kernel — one full Jacobi step per launch
jacobi_kernel = cp.RawKernel(r'''
extern "C" __global__
void jacobi_step(
    const double* u_old,
    double* u_new,
    const bool* interior_mask,
    int rows,
    int cols
) {
    int j = blockIdx.x * blockDim.x + threadIdx.x;
    int i = blockIdx.y * blockDim.y + threadIdx.y;

    if (i >= rows || j >= cols) return;

    int idx = i * cols + j;

    // interior_mask is (rows-2) x (cols-2), u is rows x cols
    // interior points: i in [1, rows-2], j in [1, cols-2]
    if (i >= 1 && i < rows-1 && j >= 1 && j < cols-1) {
        int mask_idx = (i-1) * (cols-2) + (j-1);
        if (interior_mask[mask_idx]) {
            u_new[idx] = 0.25 * (
                u_old[i * cols + (j-1)] +
                u_old[i * cols + (j+1)] +
                u_old[(i-1) * cols + j] +
                u_old[(i+1) * cols + j]
            );
        } else {
            u_new[idx] = u_old[idx];
        }
    } else {
        u_new[idx] = u_old[idx];
    }
}
''', 'jacobi_step')


def jacobi_gpu(u_gpu, interior_mask_gpu, max_iter, atol=1e-4):
    rows, cols = u_gpu.shape
    u_old = cp.array(u_gpu, dtype=cp.float64)
    u_new = cp.empty_like(u_old)

    # interior_mask needs to be contiguous bool
    mask = cp.ascontiguousarray(interior_mask_gpu, dtype=cp.bool_)

    threads = (16, 16)
    blocks = (
        (cols + threads[0] - 1) // threads[0],
        (rows + threads[1] - 1) // threads[1]
    )

    for i in range(max_iter):
        jacobi_kernel(blocks, threads, (u_old, u_new, mask,
                                        np.int32(rows), np.int32(cols)))
        # Check convergence every 100 iterations
        if i % 100 == 0:
            interior = u_new[1:-1, 1:-1][interior_mask_gpu]
            interior_old = u_old[1:-1, 1:-1][interior_mask_gpu]
            delta = cp.abs(interior - interior_old).max()
            if delta.item() < atol:
                break
        u_old, u_new = u_new, u_old

    return u_old


def summary_stats_gpu(u_gpu, interior_mask_gpu):
    u_interior = u_gpu[1:-1, 1:-1][interior_mask_gpu]
    mean_temp    = float(u_interior.mean())
    std_temp     = float(u_interior.std())
    pct_above_18 = float(cp.sum(u_interior > 18) / u_interior.size * 100)
    pct_below_15 = float(cp.sum(u_interior < 15) / u_interior.size * 100)
    return {
        'mean_temp':    mean_temp,
        'std_temp':     std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    building_ids = building_ids[:N]

    MAX_ITER = 20_000
    ABS_TOL  = 1e-4

    t0 = time.perf_counter()
    results = []
    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u_gpu             = cp.asarray(u0)
        interior_mask_gpu = cp.asarray(interior_mask)
        u_gpu = jacobi_gpu(u_gpu, interior_mask_gpu, MAX_ITER, ABS_TOL)
        stats = summary_stats_gpu(u_gpu, interior_mask_gpu)
        results.append((bid, stats))
    t1 = time.perf_counter()

    print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid, stats in results:
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, {stats['pct_above_18']}, {stats['pct_below_15']}")

    print(f"\nElapsed time: {t1 - t0:.6f} s")
