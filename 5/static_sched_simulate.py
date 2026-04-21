from os.path import join
import sys
import numpy as np
from multiprocessing import Pool, cpu_count
import time
import matplotlib.pyplot as plt


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u


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


def process_building(args):
    bid, load_dir, max_iter, atol = args
    u0, interior_mask = load_data(load_dir, bid)
    u = jacobi(u0, interior_mask, max_iter, atol)
    stats = summary_stats(u, interior_mask)
    return bid, stats


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # All remaining args are worker counts
    worker_counts = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [cpu_count()]

    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    args = [(bid, LOAD_DIR, MAX_ITER, ABS_TOL) for bid in building_ids]

    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    elapsed_times = []

    for num_workers in worker_counts:
        t0 = time.perf_counter()

        with Pool(processes=num_workers) as pool:
            chunksize = max(1, N // num_workers)
            results = pool.map(process_building, args, chunksize=chunksize)

        t1 = time.perf_counter()
        elapsed = t1 - t0
        elapsed_times.append(elapsed)
        print(f"\nWorkers={num_workers}, Elapsed time: {elapsed:.6f} s")

    # Print CSV results from the last run
    print('\nbuilding_id, ' + ', '.join(stat_keys))
    for bid, stats in results:
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

    # Speedup plot
    baseline = elapsed_times[0]
    speedup = [baseline / t for t in elapsed_times]
    ideal = [w / worker_counts[0] for w in worker_counts]

    plt.figure(figsize=(7, 4))
    plt.plot(worker_counts, speedup, 'o-', color='#378ADD', linewidth=2, markersize=6, label='Measured speed-up')
    plt.plot(worker_counts, ideal, '--', color='#888780', linewidth=1.5, label='Ideal (linear)')
    plt.xlabel('Workers')
    plt.ylabel('Speed-up')
    plt.title('Parallel speed-up vs. number of workers')
    plt.xticks(worker_counts)
    plt.legend()
    plt.tight_layout()
    plt.savefig('speedup.png', dpi=150)
    print("Speedup plot saved to speedup.png")