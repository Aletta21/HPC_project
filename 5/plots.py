import matplotlib.pyplot as plt

workers = [1, 2, 4, 8, 16]
speedup = [1.00, 2.09, 6.80, 9.44, 14.84]
ideal = workers

plt.figure(figsize=(7, 4))
plt.plot(workers, speedup, 'o-', color='#378ADD', linewidth=2, markersize=6, label='Measured speed-up')
plt.plot(workers, ideal, '--', color='#888780', linewidth=1.5, label='Ideal (linear)')
plt.xlabel('Workers')
plt.ylabel('Speed-up')
plt.title('Parallel speed-up vs. number of workers')
plt.xticks(workers)
plt.legend()
plt.tight_layout()
plt.savefig('speedup.png', dpi=150)
plt.show()