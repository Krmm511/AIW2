"""
by karam mahameed - 213029143
local_search.py
Implements local search heuristics. Specifically contains the targeted
2-opt algorithm that only improves the longer/worse path (Operator 'b').
"""
import parser_utils

import random

#Calculate the total length of one Hamiltonian route.
def tour_length(route, dist):
    total = 0

    for i in range(len(route)):
        a = route[i]
        b = route[(i + 1) % len(route)]
        total += dist[a][b]

    return total

#Convert a route into a set of undirected edges.
def edge_set(route):
    edges = set()

    for i in range(len(route)):
        a = route[i]
        b = route[(i + 1) % len(route)]

        if a > b:
            a, b = b, a

        edges.add((a, b))

    return edges

#Count how many edges are shared between route1 and route2.
def count_overlaps(route1, route2):
    return len(edge_set(route1).intersection(edge_set(route2)))

#Calculate all important values of a solution.
def evaluate_values(route1, route2, dist):
    cost1 = tour_length(route1, dist)
    cost2 = tour_length(route2, dist)
    score = max(cost1, cost2)
    total = cost1 + cost2
    balance = abs(cost1 - cost2)
    overlaps = count_overlaps(route1, route2)

    return cost1, cost2, score, total, balance, overlaps

'''
 Decide if a candidate solution is better than the current best solution.

    Priority order:
    1. fewer overlapping edges
    2. smaller minimax score
    3. smaller total cost
    4. better balance between the two routes
'''
def is_better(candidate_values, best_values):
    candidate_cost1, candidate_cost2, candidate_score, candidate_total, candidate_balance, candidate_overlaps = candidate_values
    best_cost1, best_cost2, best_score, best_total, best_balance, best_overlaps = best_values

    if candidate_overlaps != best_overlaps:
        return candidate_overlaps < best_overlaps

    if candidate_score != best_score:
        return candidate_score < best_score

    if candidate_total != best_total:
        return candidate_total < best_total

    return candidate_balance < best_balance

# Apply 2-opt on one selected route.
def two_opt_on_route(route1, route2, dist, route_id, max_moves):
    best_route1 = route1[:]
    best_route2 = route2[:]
    best_values = evaluate_values(best_route1, best_route2, dist)

    n = len(route1)
    moves = 0
    improved = True

    while improved and moves < max_moves:
        improved = False

        pairs = []
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                pairs.append((i, j))

        random.shuffle(pairs)

        for i, j in pairs:
            if moves >= max_moves:
                break

            candidate_route1 = best_route1[:]
            candidate_route2 = best_route2[:]

            if route_id == 1:
                candidate_route1[i:j + 1] = reversed(candidate_route1[i:j + 1])
            else:
                candidate_route2[i:j + 1] = reversed(candidate_route2[i:j + 1])

            candidate_values = evaluate_values(candidate_route1, candidate_route2, dist)
            moves += 1

            if candidate_values[5] == 0 and is_better(candidate_values, best_values):
                best_route1 = candidate_route1
                best_route2 = candidate_route2
                best_values = candidate_values
                improved = True
                break

    return best_route1, best_route2

# Improve a full solution using local search.
def improve_solution(route1, route2, dist, max_moves):
    cost1, cost2, score, total, balance, overlaps = evaluate_values(route1, route2, dist)

    if cost1 >= cost2:
        first = 1
        second = 2
    else:
        first = 2
        second = 1

    improved_route1, improved_route2 = two_opt_on_route(route1, route2, dist, first, max_moves)
    improved_route1, improved_route2 = two_opt_on_route(improved_route1, improved_route2, dist, second, max_moves)

    return improved_route1, improved_route2