from os.path import join
import sys
import time
import numpy as np
from numba import cuda


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2), dtype=np.float64)
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


@cuda.jit
def jacobi_single_iter(u_old, u_new, interior_mask):
    i, j = cuda.grid(2)

    # valid interior of padded 514x514 array is 1..512
    if 1 <= i < u_old.shape[0] - 1 and 1 <= j < u_old.shape[1] - 1:
        # map padded array indices to 512x512 mask indices
        mi = i - 1
        mj = j - 1

        if interior_mask[mi, mj]:
            u_new[i, j] = 0.25 * (
                u_old[i, j - 1] +
                u_old[i, j + 1] +
                u_old[i - 1, j] +
                u_old[i + 1, j]
            )
        else:
            u_new[i, j] = u_old[i, j]


def jacobi_cuda(u, interior_mask, max_iter):
    # copy input to device
    d_u_old = cuda.to_device(u)
    d_u_new = cuda.to_device(u.copy())
    d_mask = cuda.to_device(interior_mask)

    threadsperblock = (16, 16)
    blockspergrid_x = (u.shape[0] + threadsperblock[0] - 1) // threadsperblock[0]
    blockspergrid_y = (u.shape[1] + threadsperblock[1] - 1) // threadsperblock[1]
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    for _ in range(max_iter):
        jacobi_single_iter[blockspergrid, threadsperblock](d_u_old, d_u_new, d_mask)
        d_u_old, d_u_new = d_u_new, d_u_old

    return d_u_old.copy_to_host()


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
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

    # warm-up compilation
    u0, mask0 = load_data(LOAD_DIR, building_ids[0])
    _ = jacobi_cuda(u0, mask0, 1)

    t0 = time.perf_counter()

    results = []
    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi_cuda(u0, interior_mask, MAX_ITER)
        stats = summary_stats(u, interior_mask)
        results.append((bid, stats))

    cuda.synchronize()
    t1 = time.perf_counter()

    print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid, stats in results:
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, {stats['pct_above_18']}, {stats['pct_below_15']}")

    print(f"\nElapsed time: {t1 - t0:.6f} s")