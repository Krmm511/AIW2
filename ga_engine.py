"""
by karam mahameed - 213029143
ga_engine.py
Implements the baseline Genetic Algorithm, including population generation,
Tournament Selection, and Order Crossover.
"""
import random
import time
from dataclasses import dataclass

from local_search import improve_solution

#Represents one solution candidate.
@dataclass
class Individual:
    route1: list
    route2: list

    cost1: float = 0.0
    cost2: float = 0.0
    score: float = 0.0
    total: float = 0.0
    balance: float = 0.0
    overlaps: int = 0
    legal: bool = False
    fitness: float = 0.0

    def clone(self):
        return Individual(
            route1=self.route1[:],
            route2=self.route2[:],
            cost1=self.cost1,
            cost2=self.cost2,
            score=self.score,
            total=self.total,
            balance=self.balance,
            overlaps=self.overlaps,
            legal=self.legal,
            fitness=self.fitness
        )

#Holds all parameters of one GA configuration.
@dataclass
class GAConfig:
    name: str
    population_size: int = 120
    generations: int = 250
    tournament_size: int = 4
    crossover_rate: float = 0.9
    mutation_rate: float = 0.25
    elite_size: int = 4

    local_search_mode: str = "none"
    local_search_rate: float = 0.0
    local_search_every: int = 1
    local_search_max_moves: int = 60

    repair_attempts: int = 300
    convergence_patience: int = 45
    penalty_per_overlap: float = 1000000.0

 # Regular GA: no local search.
# Partial memetic: local search is applied sometimes
# Full memetic: local search is applied to every new child.
CONFIGS = {
    "regular_ga": GAConfig(
        name="regular_ga",
        local_search_mode="none",
        local_search_rate=0.0,
        local_search_every=999999,
        local_search_max_moves=0
    ),

    "partial_memetic": GAConfig(
        name="partial_memetic",
        local_search_mode="partial",
        local_search_rate=0.25,
        local_search_every=5,
        local_search_max_moves=40
    ),

    "full_memetic": GAConfig(
        name="full_memetic",
        local_search_mode="full",
        local_search_rate=1.0,
        local_search_every=1,
        local_search_max_moves=80
    )
}


def tour_length(route, dist):
    total = 0

    for i in range(len(route)):
        a = route[i]
        b = route[(i + 1) % len(route)]
        total += dist[a][b]

    return total


def edge_set(route):
    edges = set()

    for i in range(len(route)):
        a = route[i]
        b = route[(i + 1) % len(route)]

        if a > b:
            a, b = b, a

        edges.add((a, b))

    return edges


def count_overlaps(route1, route2):
    return len(edge_set(route1).intersection(edge_set(route2)))


def evaluate(ind, dist, config):
    ind.cost1 = tour_length(ind.route1, dist)
    ind.cost2 = tour_length(ind.route2, dist)

    ind.score = max(ind.cost1, ind.cost2)
    ind.total = ind.cost1 + ind.cost2
    ind.balance = abs(ind.cost1 - ind.cost2)

    ind.overlaps = count_overlaps(ind.route1, ind.route2)
    ind.legal = ind.overlaps == 0

    ind.fitness = ind.score + config.penalty_per_overlap * ind.overlaps

    return ind


def better(a, b):
    if a.legal != b.legal:
        return a.legal

    if a.fitness != b.fitness:
        return a.fitness < b.fitness

    if a.score != b.score:
        return a.score < b.score

    if a.total != b.total:
        return a.total < b.total

    return a.balance < b.balance


def random_route(n):
    route = list(range(n))
    random.shuffle(route)
    return route


def nearest_neighbor_route(dist, start):
    n = len(dist)
    unused = set(range(n))

    route = [start]
    unused.remove(start)

    current = start

    while unused:
        nxt = min(unused, key=lambda x: dist[current][x])
        route.append(nxt)
        unused.remove(nxt)
        current = nxt

    return route


def ordered_crossover(parent1, parent2):
    n = len(parent1)
    a, b = sorted(random.sample(range(n), 2))

    child = [-1] * n
    child[a:b + 1] = parent1[a:b + 1]

    used = set(child[a:b + 1])
    pos = (b + 1) % n

    for x in parent2[b + 1:] + parent2[:b + 1]:
        if x not in used:
            child[pos] = x
            used.add(x)
            pos = (pos + 1) % n

    return child


def swap_mutation(route):
    i, j = random.sample(range(len(route)), 2)
    route[i], route[j] = route[j], route[i]


def inversion_mutation(route):
    i, j = sorted(random.sample(range(len(route)), 2))
    route[i:j + 1] = reversed(route[i:j + 1])


def displacement_mutation(route):
    n = len(route)
    i, j = sorted(random.sample(range(n), 2))

    segment = route[i:j + 1]
    rest = route[:i] + route[j + 1:]

    k = random.randint(0, len(rest))
    route[:] = rest[:k] + segment + rest[k:]


def mutate_route(route):
    choice = random.random()

    if choice < 0.45:
        swap_mutation(route)

    elif choice < 0.85:
        inversion_mutation(route)

    else:
        displacement_mutation(route)


def repair(ind, dist, config):
    best_route2 = ind.route2[:]
    best_overlaps = count_overlaps(ind.route1, best_route2)
    best_cost = tour_length(best_route2, dist)
    if best_overlaps == 0:
        return
    current = best_route2[:]
    for _ in range(config.repair_attempts):
        candidate = current[:]
        if random.random() < 0.7:
            swap_mutation(candidate)
        else:
            inversion_mutation(candidate)
        candidate_overlaps = count_overlaps(ind.route1, candidate)
        candidate_cost = tour_length(candidate, dist)
        if candidate_overlaps < best_overlaps:
            current = candidate
            best_route2 = candidate
            best_overlaps = candidate_overlaps
            best_cost = candidate_cost
        elif candidate_overlaps == best_overlaps and candidate_cost < best_cost:
            current = candidate
            best_route2 = candidate
            best_cost = candidate_cost
        if best_overlaps == 0:
            break
    ind.route2 = best_route2


def create_initial_population(dist, config):
    n = len(dist)
    population = []

    for i in range(config.population_size):
        if i < min(n, config.population_size // 5):
            route1 = nearest_neighbor_route(dist, i % n)
            route2 = random_route(n)
        else:
            route1 = random_route(n)
            route2 = random_route(n)

        ind = Individual(route1, route2)

        repair(ind, dist, config)
        evaluate(ind, dist, config)

        population.append(ind)

    return population


def tournament_selection(population, config):
    group = random.sample(population, config.tournament_size)
    best = group[0]

    for ind in group[1:]:
        if better(ind, best):
            best = ind

    return best


def make_child(parent1, parent2, config):
    if random.random() < config.crossover_rate:
        route1 = ordered_crossover(parent1.route1, parent2.route1)
        route2 = ordered_crossover(parent1.route2, parent2.route2)
    else:
        route1 = parent1.route1[:]
        route2 = parent1.route2[:]

    if random.random() < config.mutation_rate:
        mutate_route(route1)

    if random.random() < config.mutation_rate:
        mutate_route(route2)

    return Individual(route1, route2)


def should_apply_local_search(config, generation):
    if config.local_search_mode == "full":
        return True

    if config.local_search_mode == "partial":
        if generation % config.local_search_every == 0:
            return random.random() < config.local_search_rate

    return False


def legal_solution_rate(population):
    if not population:
        return 0.0

    legal_count = sum(1 for ind in population if ind.legal)
    return legal_count / len(population)


def edge_similarity(ind1, ind2):
    edges1 = edge_set(ind1.route1).union(edge_set(ind1.route2))
    edges2 = edge_set(ind2.route1).union(edge_set(ind2.route2))

    if not edges1 and not edges2:
        return 1.0

    return len(edges1.intersection(edges2)) / len(edges1.union(edges2))


def population_diversity(population, samples=80):
    if len(population) < 2:
        return 0.0

    similarities = []

    for _ in range(samples):
        a, b = random.sample(population, 2)
        similarities.append(edge_similarity(a, b))

    average_similarity = sum(similarities) / len(similarities)
    return 1.0 - average_similarity

def history_row(generation, population, best):
    """
    Create one history row for plots.
    """

    scores = [ind.score for ind in population]
    valid_count = sum(1 for ind in population if ind.legal)

    return {
        "generation": generation,
        "best_score": best.score,
        "avg_score": sum(scores) / len(scores),
        "worst_score": max(scores),
        "diversity": population_diversity(population),
        "valid_count": valid_count
    }
def run_ga(dist, config, seed=1):
    """
    Run the full GA / memetic algorithm.
    """
    random.seed(seed)
    start_time = time.time()
    population = create_initial_population(dist, config)
    best = min(population, key=lambda x: x.fitness).clone()
    last_best_fitness = best.fitness
    no_improve = 0
    convergence_generation = config.generations
    # This list stores data for the graphs.
    history = []
    # Save generation 0 before evolution starts.
    history.append(history_row(0, population, best))
    for generation in range(1, config.generations + 1):
        population.sort(key=lambda x: x.fitness)
        # Keep elite individuals unchanged.
        next_population = []
        for ind in population[:config.elite_size]:
            next_population.append(ind.clone())
        # Create children until the new population is full.
        while len(next_population) < config.population_size:
            parent1 = tournament_selection(population, config)
            parent2 = tournament_selection(population, config)
            child = make_child(parent1, parent2, config)
            repair(child, dist, config)
            # Apply local search according to the selected method.
            if should_apply_local_search(config, generation):
                child.route1, child.route2 = improve_solution(
                    child.route1,
                    child.route2,
                    dist,
                    config.local_search_max_moves
                )
            evaluate(child, dist, config)
            next_population.append(child)
        population = next_population
        current = min(population, key=lambda x: x.fitness)
        if better(current, best):
            best = current.clone()
        # Save history for this generation.
        history.append(history_row(generation, population, best))
        # Track improvement for convergence.
        if best.fitness < last_best_fitness:
            last_best_fitness = best.fitness
            no_improve = 0
        else:
            no_improve += 1
        # Early stop if there is no improvement for many generations.
        if no_improve >= config.convergence_patience:
            convergence_generation = generation
            break
    runtime = time.time() - start_time
    metrics = {
        "runtime": runtime,
        "generations_to_convergence": convergence_generation,
        "legal_solution_rate": legal_solution_rate(population),
        "diversity": population_diversity(population),
        "seed": seed,
        "history": history
    }
    return best, metrics