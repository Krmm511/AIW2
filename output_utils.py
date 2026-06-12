"""
by karam mahameed - 213029143
local_search.py
Saving experiment outputs.
Creates results.csv and best_routes_instance_method.txt files.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv
import os

"""
    Convert route from 0-based indexing to 1-based indexing.
    Inside the code, cities are stored from 0 to n-1.
    But in the TSP files, cities start from 1.
    So before printing the route, we add 1 to every city.
    """
def route_to_one_based(route):
    return [city + 1 for city in route]

"""
    Save the best solution into a text file and also print it to the CMD.
    The saved output includes:
    - instance name
    - algorithm method
    - route 1 and route 2
    - cost of each route
    - minimax score
    - total cost
    - balance between the two routes
    - legality check
    - runtime and other metrics
    """
def save_best_route(output_dir, instance, method, best, metrics):
    os.makedirs(output_dir, exist_ok=True)
    # Create the output folder if it does not already exist.
    seed = metrics["seed"]
    path = os.path.join(output_dir, f"best_routes_{instance}_{method}_seed{seed}.txt")
    output_text = ""
    output_text += f"Instance: {instance}\n"
    output_text += f"Method: {method}\n\n"

    output_text += "Route 1:\n"
    output_text += " ".join(map(str, route_to_one_based(best.route1))) + "\n\n"

    output_text += "Route 2:\n"
    output_text += " ".join(map(str, route_to_one_based(best.route2))) + "\n\n"

    output_text += f"Route 1 cost: {best.cost1}\n"
    output_text += f"Route 2 cost: {best.cost2}\n"
    output_text += f"Best score max(c(T1), c(T2)): {best.score}\n"
    output_text += f"Total cost c(T1)+c(T2): {best.total}\n"
    output_text += f"Balance |c(T1)-c(T2)|: {best.balance}\n"
    output_text += f"Legal solution: {best.legal}\n"
    output_text += f"Overlapping edges: {best.overlaps}\n\n"

    output_text += f"Runtime: {metrics['runtime']:.4f}\n"
    output_text += f"Generations to convergence: {metrics['generations_to_convergence']}\n"
    output_text += f"Legal solution rate: {metrics['legal_solution_rate']:.4f}\n"
    output_text += f"Diversity: {metrics['diversity']:.4f}\n"
    output_text += f"Seed: {metrics['seed']}\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print()
    print(output_text)


def append_result_csv(output_dir, row):
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, "results.csv")
    exists = os.path.exists(path)

    fields = [
        "instance",
        "method",
        "cities",
        "route1_cost",
        "route2_cost",
        "best_score",
        "total_cost",
        "balance",
        "is_legal",
        "overlapping_edges",
        "runtime",
        "generations_to_convergence",
        "legal_solution_rate",
        "diversity",
        "seed"
    ]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)

        if not exists:
            writer.writeheader()

        writer.writerow(row)
def save_instance_graphs(output_dir, instance, histories, aspirational_target=None):
    """
    Save 3 graphs for one TSP instance.
    The graphs:
    1. convergence comparison
    2. diversity over generations
    3. valid solution count over generations
    """

    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    labels = {
        "regular_ga": "A: Regular GA",
        "partial_memetic": "B: Partial LS",
        "full_memetic": "C: Full Memetic"
    }

    # ----------------------------------------------------
    # Graph 1: convergence comparison
    # ----------------------------------------------------
    plt.figure(figsize=(10, 6))

    for method, history in histories.items():
        generations = [row["generation"] for row in history]
        best_scores = [row["best_score"] for row in history]

        plt.plot(generations, best_scores, label=labels.get(method, method), linewidth=2)

    if aspirational_target is not None:
        plt.axhline(
            y=aspirational_target,
            linestyle=":",
            linewidth=2,
            label=f"Aspirational ({aspirational_target})"
        )

    plt.title(f"{instance} — Convergence Comparison A vs B vs C")
    plt.xlabel("Generation")
    plt.ylabel("Best max(c(T1), c(T2))")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(plots_dir, f"{instance}_convergence_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()

    # ----------------------------------------------------
    # Graph 2: population diversity
    # ----------------------------------------------------
    plt.figure(figsize=(10, 6))

    for method, history in histories.items():
        generations = [row["generation"] for row in history]
        diversity = [row["diversity"] for row in history]

        plt.plot(generations, diversity, label=labels.get(method, method), linewidth=2)

    plt.title(f"{instance} — Population Diversity over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Diversity")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(plots_dir, f"{instance}_diversity.png")
    plt.savefig(path, dpi=150)
    plt.close()

    # ----------------------------------------------------
    # Graph 3: valid solutions count
    # ----------------------------------------------------
    plt.figure(figsize=(10, 6))

    for method, history in histories.items():
        generations = [row["generation"] for row in history]
        valid_counts = [row["valid_count"] for row in history]

        plt.plot(generations, valid_counts, label=labels.get(method, method), linewidth=2)

    plt.title(f"{instance} — Valid Solutions over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Valid individuals count")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(plots_dir, f"{instance}_valid_count.png")
    plt.savefig(path, dpi=150)
    plt.close()