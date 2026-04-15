from os.path import join
import sys
import numpy as np
import cupy as cp


def load_data(load_dir, bid):
    """Load floor plan data from disk using NumPy (CPU).
    Data lives on disk, so we always load with NumPy first.
    """
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi_gpu(u_gpu, interior_mask_gpu, max_iter, atol=1e-4):
    """Jacobi solver running entirely on the GPU using CuPy.

    The logic is identical to the reference NumPy version,
    but every operation runs on the GPU. No CPU<->GPU transfers
    happen inside this function.

    Args:
        u_gpu:            CuPy array (514x514) — already on GPU
        interior_mask_gpu: CuPy bool array (512x512) — already on GPU
        max_iter:         maximum number of Jacobi iterations
        atol:             convergence tolerance

    Returns:
        u_gpu: CuPy array with the converged temperature field
    """
    u_gpu = cp.copy(u_gpu)

    for i in range(max_iter):
        # Compute average of left, right, up, down neighbors
        # Identical slicing to the NumPy reference — CuPy supports it natively
        u_new = 0.25 * (
            u_gpu[1:-1, :-2] +   # left neighbor
            u_gpu[1:-1, 2:]  +   # right neighbor
            u_gpu[:-2, 1:-1] +   # upper neighbor
            u_gpu[2:,  1:-1]     # lower neighbor
        )

        # Extract only the interior values (using the mask)
        u_new_interior = u_new[interior_mask_gpu]

        # Check convergence — max change across all interior points
        delta = cp.abs(
            u_gpu[1:-1, 1:-1][interior_mask_gpu] - u_new_interior
        ).max()

        # Update only the interior points (walls stay fixed)
        u_gpu[1:-1, 1:-1][interior_mask_gpu] = u_new_interior

        # .item() transfers a single scalar GPU->CPU for the comparison
        if delta.item() < atol:
            break

    return u_gpu


def summary_stats_gpu(u_gpu, interior_mask_gpu):
    """Compute summary statistics entirely on the GPU.

    We keep everything on the GPU until we have 4 scalar results.
    This avoids a large GPU->CPU transfer of the full 514x514 array.

    Args:
        u_gpu:             CuPy array (514x514) with temperature field
        interior_mask_gpu: CuPy bool array (512x512)

    Returns:
        dict with mean_temp, std_temp, pct_above_18, pct_below_15
        (all Python floats — small CPU scalars)
    """
    # Extract interior temperatures — still on GPU
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

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    MAX_ITER = 20_000
    ABS_TOL  = 1e-4

    # Print CSV header
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))

    for bid in building_ids:
        # 1. Load from disk (CPU/NumPy — unavoidable)
        u0, interior_mask = load_data(LOAD_DIR, bid)

        # 2. Transfer to GPU — one transfer per building
        u_gpu            = cp.asarray(u0)
        interior_mask_gpu = cp.asarray(interior_mask)

        # 3. Run Jacobi entirely on GPU
        u_gpu = jacobi_gpu(u_gpu, interior_mask_gpu, MAX_ITER, ABS_TOL)

        # 4. Compute stats on GPU — only scalars come back to CPU
        stats = summary_stats_gpu(u_gpu, interior_mask_gpu)

        # 5. Print results
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))