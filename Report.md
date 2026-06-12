# Workshop in AI - 2nd assignment part 2

----------------

# Minimax TSP — Genetic and Memetic Algorithms

**Student:** karam mahameed
**ID:** 213029143
**Student:** moamen haj yosef
**ID:** 212489942
# Minimax TSP — Genetic / Memetic Algorithm

**Student:** karam mahameed
**ID:** 213029143

---

## Problem

The goal of this project is to solve a variation of the Traveling Salesman Problem called **Minimax TSP**.

Instead of finding one Hamiltonian cycle, the task is to find **two** Hamiltonian cycles:

```text
T1 and T2
```

over the same set of cities.

The objective is:

```text
minimize max(c(T1), c(T2))
```

where:

```text
c(T1) = cost of the first route
c(T2) = cost of the second route
```

The solution also has an **edge-disjointness constraint**

The main fitness value used by the algorithm is:

```text
fitness = max(c(T1), c(T2)) + penalty_per_overlap * overlaps
```

For reporting and comparison, the following values are also saved:

```text
Minimax score = max(c(T1), c(T2))
Total cost    = c(T1) + c(T2)
Balance       = |c(T1) - c(T2)|
```

Lower values are better.


---

## Requirements

The project was implemented in Python.
Python 3.9+ 
numpy - matplotlib bash pip install numpy matplotlib TSPLIB instance files

## Quick Start

### Run one instance with all three configurations

```
py main.py --tsp "tsps/burma14.tsp" --method all
```

### Run one specific configuration

```
py main.py --tsp "tsps/burma14.tsp" --method regular_ga
py main.py --tsp "tsps/burma14.tsp" --method partial_memetic
py main.py --tsp "tsps/burma14.tsp" --method full_memetic
```

### Run all required instances from folder

```
py main.py --folder "tsps" --method all
```

### Run with different seeds

```
py main.py --tsp "tsps/burma14.tsp" --method all --seeds 1 7 42
```

or for all files:

```
py main.py --folder "tsps" --method all --seeds 1 7 42
```

---

## Command-Line Reference

```text
--tsp PATH        path to one .tsp or .csv input file
--folder PATH     path to folder containing TSP files
--method METHOD   regular_ga / partial_memetic / full_memetic / all
--seeds N ...     one or more random seeds
--output DIR      output folder, default is results
```

Examples:

```
py\ main.py --tsp "tsps/att48.tsp" --method full_memetic --seeds x
```

```
py main.py --folder "tsps" --method all --seeds x
```

---

## Supported TSPLIB Instances

| Instance  |  n | Edge Weight Type | Status |
| --------- | -: | ---------------- | ------ |
| burma14   | 14 | GEO              | tested |
| gr17      | 17 | EXPLICIT         | tested |
| gr24      | 24 | EXPLICIT         | tested |
| fri26     | 26 | EXPLICIT         | tested |
| bayg29    | 29 | EXPLICIT         | tested |
| dantzig42 | 42 | EXPLICIT         | tested |
| att48     | 48 | ATT              | tested |
| eil51     | 51 | EUC_2D           | tested |
| berlin52  | 52 | EUC_2D           | tested |
| eil76     | 76 | EUC_2D           | tested |


## Three Variants

All three variants share the same GA backbone:

```text
initial population
tournament selection
ordered crossover
mutation
repair
elitism
fitness evaluation
early stopping
```

They differ in how local search is applied.

|  Method key     | Local Search Schedule                                             |
|--------------- | ----------------------------------------------------------------- |
| `regular_ga`    | No local search                                                |
| `partial_memetic` | Local search sometimes: every 5 generations with probability 0.25 |
| `full_memetic`  | Local search on every new child                                  |

---


The program also saves 3 plots per instance and seed:

| Plot file                                          | Meaning                                      |
| -------------------------------------------------- | -------------------------------------------- |
| `<instance>_seed<seed>_convergence_comparison.png` | Best minimax score over generations          |
| `<instance>_seed<seed>_diversity.png`              | Population diversity over generations        |
| `<instance>_seed<seed>_valid_count.png`            | Number of legal individuals over generations |


## Discussion: Minimax, Total Cost, and Balance

The main objective is:

```text
Minimax score = max(c(T1), c(T2))
```

This is the most important metric because the problem is defined as a minimax problem.

`Total cost` is also useful because it shows whether the two routes are short overall:

```text
Total cost = c(T1) + c(T2)
```

`Balance` shows how close the two route costs are:

```text
Balance = |c(T1) - c(T2)|
```

The experiments show that full memetic usually gives the best minimax and total cost. However, it does not always give the best balance. Sometimes partial memetic gives better balance, but with a worse minimax score.

This means that balance alone is not enough. A solution can be balanced but still bad if both routes are long.

Therefore, the priority is:

```text
1. Legal solution
2. Minimax score
3. Total cost
4. Balance
5. Runtime
```

---

## Final Conclusions

In this project, we implemented a Genetic Algorithm and two Memetic Algorithm variants for the Minimax TSP problem.

All final solutions were legal:

```text
Legal = True
Overlaps = 0
```

This means that the edge-disjointness constraint was handled correctly.

The regular GA was the fastest method, but usually gave weaker minimax scores.

The partial memetic method improved many results with moderate runtime increase.

The full memetic method achieved the best minimax score on every tested instance, but required the longest runtime.

The main conclusion is that local search is very useful for Minimax TSP. It improves the longer route and reduces the minimax score. However, the cost is higher runtime, especially in the full memetic configuration.

Overall:

```text
regular_ga       = fastest
partial_memetic  = balanced tradeoff
full_memetic     = best solution quality
```

--- 

## Project Structure

```text
Minmax_TSP/
├── main.py              ← command-line entry point
├── parser_utils.py      ← reads TSPLIB/CSV files and builds distance matrix
├── ga_engine.py         ← GA engine, configurations, selection, crossover, mutation, repair
├── local_search.py      ← 2-opt local search for memetic versions
├── output_utils.py      ← saves txt results, csv results, and plots
├── tsps/                ← input TSP files
│   ├── burma14.tsp
│   ├── gr17.tsp
│   ├── gr24.tsp
│   ├── fri26.tsp
│   ├── bayg29.tsp
│   ├── dantzig42.tsp
│   ├── att48.tsp
│   ├── eil51.tsp
│   ├── berlin52.tsp
│   └── eil76.tsp
└── results/
    ├── results.csv
    ├── best_routes_<instance>_<method>_seed<seed>.txt
    └── plots/
        ├── <instance>_seed<seed>_convergence_comparison.png
        ├── <instance>_seed<seed>_diversity.png
        └── <instance>_seed<seed>_valid_count.png
```

