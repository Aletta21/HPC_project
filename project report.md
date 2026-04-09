1. Familiarize yourself with the data. Load and visualize the input data for a few floorplans using a separate Python script, Jupyter notebook, or your preferred tool.
	- ![[Pasted image 20260407124828.png]]

2. Familiarize yourself with the provided script. Run and time the reference implementation for a small subset of floorplans (e.g., 10–20). How long do you estimate it would take to process all the floorplans? Perform the timing as a batch job so you get reliable results.
	- i ran the reference implementation for a small subset of floorplans (20 floorplans), and those were the results: 
		```
		real	7m31.585s
		user	7m29.889s
		sys	0m0.267s

		```
		The real time for 20 floorplans in seconds is 7 * 60 + 31.585 = 451.585 sec, so for a building 
		We know that the dataset consists of 4571 floorplans, so per floorplan it is 451,585/20≈22,579 sec per floorplan. 
		We know that we have 4571 floorplans, so 22,579×4571≈103208sec, which is equal to 103208/3600≈28,66 hours needed to process all the floorplans with the reference python script.


3. Visualize the simulation results for a few floorplans.
![[Pasted image 20260407135631.png]]


4. Profile the reference `jacobi` function using `kernprof`. Explain the different parts of the function and how much time each part takes.

	this is the output of the profile with kernprof:
```
n-62-30-8(s253129) $ python -m line_profiler profile_simulate.py.lprof
Timer unit: 1e-06 s

Total time: 48.8142 s
File: profile_simulate.py
Function: jacobi at line 13

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    13                                           @profile
    14                                           def jacobi(u, interior_mask,    max_iter, atol=1e-6):
    15         5       2674.0    534.8      0.0      u = np.copy(u)
    16     28423      21180.7      0.7      0.0      for i in range(max_iter):
    17     28423   27065966.4    952.3     55.4          u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
    18     28423    5555940.3    195.5     11.4          u_new_interior = u_new[interior_mask]
    19     28423   10324776.6    363.3     21.2          delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
    20     28423    5816578.9    204.6     11.9          u[1:-1, 1:-1][interior_mask] = u_new_interior
    21     28423      27113.6      1.0      0.1          if delta < atol:
    22         5          4.2      0.8      0.0              break
    23         5          5.2      1.0      0.0      return u
```

- **Copying the input grid:**  
    `u = np.copy(u)`
    - Time: **2674.0 μs** ≈ **0.0027 s**
    - Percentage: **0.0%**
    **What it does:** This creates a copy of the input array so the original grid is not modified.
    ### **Interpretation:**
    This step takes essentially no time compared to the full runtime, so it is **not a bottleneck**.
---
- **Iteration loop control:**  
    `for i in range(max_iter):`
    - Hits: **28,423**
    - Time: **21180.7 μs** ≈ **0.0212 s**
    - Percentage: **0.0%**
    
    ### **What it does:**
    This controls the repeated Jacobi iterations until convergence or until the maximum number of iterations is reached.

    ### **Interpretation:**
    
    The loop structure itself is very cheap. The important point is that the function executed **28,423 iterations in total across 5 buildings**, so on average about:
    
    284235≈5685\frac{28423}{5} \approx 5685528423​≈5685
    
    iterations per building.
    
    So the cost is **not** from the Python `for` loop itself, but from the work performed inside each iteration.
    

---

- **Computing the new grid values from neighbors:**  
    `u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])`
    
    - Time: **27.0659664 s**
    - Percentage: **55.4%**
    
    ### **What it does:**
    This is the core **Jacobi stencil update**. For each grid point, it computes the average of the four neighboring values: left, right, up, and down.
    
    This corresponds directly to the numerical update rule of the Jacobi method used in the assignment.
    
    ### **Interpretation:**
    This is the **largest cost in the function** and the main bottleneck.
    
    Why it is expensive:
    - it performs large array operations over almost the whole grid
    - it creates temporary arrays
    - it reads several large slices from memory
    - it repeats this work at every iteration
    
    This step alone takes **55.4% of the total runtime**, so more than half of the execution time is spent computing the new candidate values.
---
- **Extracting only the interior points:**  
    `u_new_interior = u_new[interior_mask]`
    - Time: **5.5559403 s**
    - Percentage: **11.4%**
    
    **What it does:**  
    The full `u_new` array contains values for the whole inner grid, but only the points inside rooms should actually be updated. This line uses the boolean mask `interior_mask` to extract only those interior values. That matches the project requirement that only interior grid points are updated, while walls and outside points remain fixed.
    
    ### **Interpretation:**
    This is also a significant cost.
    Why:
    - boolean masking is not free
    - NumPy must scan the mask
    - it gathers selected values into a new array
    
    So this line contributes about **11.4% of the total runtime**.
---
- **Computing the convergence criterion:**  
    `delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()`
    - Time: **10.3247766 s**
    - Percentage: **21.2%**
    
    ### **What it does:**
    
    This line measures the maximum absolute change between the old and new interior values. That maximum difference is stored in `delta`, and it is used to decide whether the solution has converged.
    
    ### **Interpretation:**
    
    This is the **second most expensive part** of the function.
    
    Why it is expensive:
    
    - it slices the grid
    - applies the mask
    - subtracts arrays
    - computes absolute values
    - finds the maximum
    
    So even though it is written as a single line, it actually performs several array operations and creates temporary arrays.
    
    This makes the convergence check quite costly: **21.2% of the total runtime**.
    

---

- **Writing updated values back into the grid:**  
    `u[1:-1, 1:-1][interior_mask] = u_new_interior`
    
    - Time: **5.8165789 s**
    - Percentage: **11.9%**
    
    ### **What it does:**
    
    This writes the newly computed interior values back into the solution grid.
    
    ### **Interpretation:**
    
    This step is also expensive because masked assignment involves scattered memory writes rather than a simple contiguous write.
    
    It takes about **11.9%** of the total runtime, so updating the interior values is another non-trivial cost.
    

---

- **Convergence check:**  
    `if delta < atol:`  
    `break`
    
    - `if delta < atol:`
        - Time: **27113.6 μs** ≈ **0.0271 s**
        - Percentage: **0.1%**
    - `break`
        - Time: **4.2 μs**
        - Percentage: **0.0%**
    
    **What it does:**  
    It checks whether the maximum update size is below the tolerance `atol`. If yes, the iterations stop early.
    
    ### **Interpretation:**
    
    The check itself is extremely cheap.
    
    The expensive part is **computing `delta`**, not testing it.
    

---

- **Returning the result:**  
    `return u`
    
    - Time: **5.2 μs**
    - Percentage: **0.0%**
    
    **What it does:**  
    Returns the final converged temperature grid.
    
    ### **Interpretation:**
    
    Negligible cost.




5. Make a new Python program where you parallelize the computations over the floorplans. Use static scheduling such that each worker is assigned the same amount of floorplans to process.
	You should use no more than 100 floorplans for your timing experiments. Again, use a batch job to ensure consistent results.
	a) Measure the speed-up as more workers are added. Plot your speed-ups.
		Speed-up(p)=T(1)/ T(PP​​: 

This is the speed-up measurements for 90 floors, and multiple workers.

| Workers | Real-Time(s) | Speed-up |
| ------- | ------------ | -------- |
| 1       | 2761.126     | 1.00     |
| 2       | 1321.550     | 2.09     |
| 4       | 406.213      | 6.80     |
| 8       | 292.468      | 9.44     |
| 16      | 186.068      | 14.84    |
![[Pasted image 20260408232356.png]]

	b) Estimate your parallel fraction according to Amdahl's law. How much (roughly) is paral-
	lelized?


Amdahl's law says: S(p)= 1/(1−f)+f/p​  , where f is the parallel fraction and p is the number of workers. 
Rearrange to solve for f:
	f = ((1/s) - 1 ) / ((1/p) -1)

|p|S|f|
|---|---|---|
|2|2.09|(1/2.09 - 1) / (1/2 - 1) = 0.9569|
|4|6.80|(1/6.80 - 1) / (1/4 - 1) = 0.9510|
|8|9.44|(1/9.44 - 1) / (1/8 - 1) = 0.9208|
|16|14.84|(1/14.84 - 1) / (1/16 - 1) = 0.9386|

Mean f is around 0.942, so roughly 94% is parallelized and around 6% is serial.


	c) What is your theoretical maximum speed-up according to Amdahl's law? How much of that did you achieve? How many cores did that take?

With f = 0.942  , the theoritical maximum speed-up is:
Smax​=1/1−f​ = 1−0.9421​≈17.24

the best achieved speed-up is 14.84 at 16 workers(16 cores)

	d) How long would you estimate it would take to process all floorplans using your fastest
	parallel solution?

From the project description we know that there are 4571 buildings total. 
We know that we need 186.068 seconds for 90 buildings and 16 workers. So:

T = (186.068 / 90) / 4571 ≈ 9.448 seconds ≈ 2.6 hours