from os.path import join
import sys
import numpy as np
import cupy as cp


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi_gpu(u_gpu, interior_mask_gpu, max_iter, atol=1e-4):
    u_gpu = cp.copy(u_gpu)

    for i in range(max_iter):
        u_new = 0.25 * (
            u_gpu[1:-1, :-2] +
            u_gpu[1:-1, 2:]  +
            u_gpu[:-2, 1:-1] +
            u_gpu[2:,  1:-1]
        )

        u_new_interior = u_new[interior_mask_gpu]

        delta = cp.abs(
            u_gpu[1:-1, 1:-1][interior_mask_gpu] - u_new_interior
        ).max()

        u_gpu[1:-1, 1:-1][interior_mask_gpu] = u_new_interior

        if delta.item() < atol:
            break

    return u_gpu


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

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    MAX_ITER = 20_000
    ABS_TOL  = 1e-4

    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))

    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u_gpu             = cp.asarray(u0)
        interior_mask_gpu = cp.asarray(interior_mask)
        u_gpu = jacobi_gpu(u_gpu, interior_mask_gpu, MAX_ITER, ABS_TOL)
        stats = summary_stats_gpu(u_gpu, interior_mask_gpu)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))