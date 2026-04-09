from os.path import join
import sys
import time
import numpy as np
from numba import njit


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2), dtype=np.float64)
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


@njit
def jacobi_numba(u, interior_mask, max_iter, atol=1e-6):
    u_old = u.copy()
    u_new = u.copy()

    for it in range(max_iter):
        delta = 0.0

        for i in range(1, u_old.shape[0] - 1):
            ii = i - 1
            for j in range(1, u_old.shape[1] - 1):
                jj = j - 1

                if interior_mask[ii, jj]:
                    new_val = 0.25 * (
                        u_old[i, j - 1] +
                        u_old[i, j + 1] +
                        u_old[i - 1, j] +
                        u_old[i + 1, j]
                    )

                    diff = abs(new_val - u_old[i, j])
                    if diff > delta:
                        delta = diff

                    u_new[i, j] = new_val
                else:
                    u_new[i, j] = u_old[i, j]

        if delta < atol:
            return u_new

        tmp = u_old
        u_old = u_new
        u_new = tmp

    return u_old


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
    ABS_TOL = 1e-4

    # warm-up compile
    u0, mask0 = load_data(LOAD_DIR, building_ids[0])
    _ = jacobi_numba(u0, mask0, 1, ABS_TOL)

    t0 = time.perf_counter()

    results = []
    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi_numba(u0, interior_mask, MAX_ITER, ABS_TOL)
        stats = summary_stats(u, interior_mask)
        results.append((bid, stats))

    t1 = time.perf_counter()

    print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid, stats in results:
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, {stats['pct_above_18']}, {stats['pct_below_15']}")

    print(f"\nElapsed time: {t1 - t0:.6f} s")