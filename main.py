"""
main.py
Main running file.
Runs Minimax TSP with one of the required methods
regular_ga, partial_memetic, full_memetic, or all three.
"""
import argparse
import os

from parser_utils import load_problem, make_distance_matrix
from ga_engine import CONFIGS, run_ga, evaluate
from output_utils import save_best_route, append_result_csv, save_instance_graphs


REQUIRED_INSTANCES = {
    "burma14",
    "gr17",
    "gr24",
    "fri26",
    "bayg29",
    "dantzig42",
    "att48",
    "eil51",
    "berlin52",
    "eil76"
}
ASPIRATIONAL_TARGETS = {
    "burma14": 5317,
    "gr17": 3336,
    "gr24": 2036,
    "fri26": 1500,
    "bayg29": 2576,
    "dantzig42": 1119,
    "att48": 17005,
    "eil51": 682,
    "berlin52": 12068,
    "eil76": 861
}

# Run the algorithm on one TSP file.
def run_one_file(tsp_path, method, seeds, output_dir):
    """
    Run one TSP file.

    This version supports multiple seeds.
    For every seed, it runs the selected method or all three methods.
    """

    instance, coords, edge_weight_type, explicit_matrix = load_problem(tsp_path)
    dist = make_distance_matrix(coords, edge_weight_type, explicit_matrix)

    if method == "all":
        methods = ["regular_ga", "partial_memetic", "full_memetic"]
    else:
        methods = [method]

    for seed in seeds:
        histories = {}

        for method_name in methods:
            config = CONFIGS[method_name]

            best, metrics = run_ga(dist, config, seed)
            evaluate(best, dist, config)

            save_best_route(output_dir, instance, method_name, best, metrics)

            histories[method_name] = metrics["history"]

            row = {
                "instance": instance,
                "method": method_name,
                "cities": len(dist),
                "route1_cost": best.cost1,
                "route2_cost": best.cost2,
                "best_score": best.score,
                "total_cost": best.total,
                "balance": best.balance,
                "is_legal": best.legal,
                "overlapping_edges": best.overlaps,
                "runtime": round(metrics["runtime"], 4),
                "generations_to_convergence": metrics["generations_to_convergence"],
                "legal_solution_rate": round(metrics["legal_solution_rate"], 4),
                "diversity": round(metrics["diversity"], 4),
                "seed": seed
            }

            append_result_csv(output_dir, row)

            print(
                f"{instance:12s} | {method_name:16s} | "
                f"seed={seed:4d} | "
                f"score={best.score:10.2f} | "
                f"c1={best.cost1:10.2f} | "
                f"c2={best.cost2:10.2f} | "
                f"legal={best.legal} | "
                f"overlaps={best.overlaps} | "
                f"time={metrics['runtime']:.2f}s"
            )

        target = ASPIRATIONAL_TARGETS.get(instance.lower())

        save_instance_graphs(
            output_dir=output_dir,
            instance=f"{instance}_seed{seed}",
            histories=histories,
            aspirational_target=target
        )

# Collect all required TSP files from a folder.
def collect_tsp_files(folder):
    files = []

    for filename in os.listdir(folder):
        lower_name = filename.lower()

        if not lower_name.endswith((".tsp", ".csv")):
            continue

        base = os.path.splitext(lower_name)[0]

        if base in REQUIRED_INSTANCES:
            files.append(os.path.join(folder, filename))

    files.sort()
    return files

# Run the experiment on all required TSP files inside a folder.
def run_folder(folder, method, seeds, output_dir):
    """
    Run all required TSP files inside a folder.

    Supports multiple seeds.
    """

    tsp_files = collect_tsp_files(folder)

    if not tsp_files:
        raise FileNotFoundError("No required TSP files found in folder")

    for tsp_path in tsp_files:
        run_one_file(tsp_path, method, seeds, output_dir)
'''
 Program entry point.

    This function reads command line arguments and decides whether to run:
    1. one TSP file
    2. a folder of TSP files
'''
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--tsp", type=str, default=None)
    parser.add_argument("--folder", type=str, default=None)

    parser.add_argument(
        "--method",
        type=str,
        default="all",
        choices=["regular_ga", "partial_memetic", "full_memetic", "all"]
    )

    parser.add_argument("--seeds", type=int, nargs="+", default=[1])
    parser.add_argument("--output", type=str, default="results")

    args = parser.parse_args()
    # The user must give either one file or one folder.
    if args.tsp is None and args.folder is None:
        raise ValueError("Use --tsp file.tsp or --folder TSPLIB")
    # Run one file if --tsp was given.
    if args.tsp is not None:
        run_one_file(args.tsp, args.method, args.seeds, args.output)

    else:
        run_folder(args.folder, args.method, args.seeds, args.output)

if __name__ == "__main__":
    main()