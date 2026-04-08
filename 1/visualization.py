import numpy as np
import matplotlib.pyplot as plt
from os.path import join

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()

N = 4

fig, axes = plt.subplots(2, N, figsize=(4*N, 8))

for i, bid in enumerate(building_ids[:N]):
    domain = np.load(join(LOAD_DIR, f"{bid}_domain.npy"))
    interior = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))

    im = axes[0, i].imshow(domain, cmap='plasma', vmin=0, vmax=25)
    axes[0, i].set_title(f'ID: {bid}')

    axes[1, i].imshow(interior, cmap='gray', vmin=0, vmax=1)
    axes[1, i].set_title(f'ID: {bid}')

# Colorbar only on the right of the top row
fig.colorbar(im, ax=axes[0, -1], label='Temperature')

plt.tight_layout()
plt.savefig('floorplans_visualization.png', dpi=150)
plt.show()