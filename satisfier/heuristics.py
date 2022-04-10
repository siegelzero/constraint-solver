import random

from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

from satisfier.system import ConstraintSystem, Constraint, Variable


# Type aliases
Domain = Dict[Variable, Set[Any]]
Assignment = Dict[Variable, Any]


def greedy(system: ConstraintSystem, penalty_func='error'):
    # Initialize with random assignment
    for variable in system.variables:
        variable.value = random.choice(sorted(system.domain[variable]))

    cost = sum(
        constraint.penalty(method=penalty_func)
        for constraint in system.constraints if not constraint.is_satisfied()
    )

    best_cost = cost
    print("initial cost:", cost)

    for variable in system.variables:
        cost_map = defaultdict(list)

        for value in system.domain[variable]:
            variable.value = value
            cost = sum(
                constraint.penalty(method=penalty_func)
                for constraint in system.constraints if not constraint.is_satisfied()
            )
            print(f"{variable} = {value} cost: {cost}")
            cost_map[cost].append(value)

        print(cost_map)
        best_cost = min(cost_map)
        print("best_cost", best_cost)
        variable.value = random.choice(cost_map[best_cost])

    best_assignment = system.variable_set.values_dict()
    return best_cost, best_assignment


def tabu(system: ConstraintSystem,
         max_iterations=1000,
         penalty_func='error',
         alpha=0.6):
    # Initialize with random assignment
    for variable in system.variables:
        variable.value = random.choice(sorted(system.domain[variable]))

    # map of variables to the constraints that each belongs to
    constraints: Dict[Variable, List[Constraint]] = defaultdict(list)

    bad_variables: Dict[Variable, int] = defaultdict(int)

    # Cost of our random assignment
    cost = 0
    for constraint in system.constraints:
        for variable in constraint.variables:
            constraints[variable].append(constraint)

        if constraint.is_satisfied():
            continue

        penalty = constraint.penalty(method=penalty_func)
        cost += penalty
        for v in constraint.variables:
            bad_variables[v] += penalty

    tabu: Dict[Tuple[Variable, Any], Any] = defaultdict(int)

    best_cost = cost
    best_assignment = system.variable_set.values_dict()

    print(f"initial cost: {cost}")
    iteration = 0

    def best_neighbor(cost):
        best_neighbor_cost = 10**100
        best_neighbors = []

        for variable, old in bad_variables.items():
            original = variable.value

            for value in system.domain[variable]:
                if value == original:
                    continue

                variable.value = value
                ncost = cost - old + sum(
                    constraint.penalty(method=penalty_func)
                    for constraint in constraints[variable] if not constraint.is_satisfied()
                )

                if tabu[variable, value] > iteration:
                    if ncost >= best_cost:
                        continue
                    print(f'aspiration! {variable}: {original} -> {value} {best_cost}')

                if ncost < best_neighbor_cost:
                    best_neighbor_cost = ncost
                    best_neighbors = [(variable, value, original)]

                elif ncost == best_neighbor_cost:
                    best_neighbors.append((variable, value, original))

            variable.value = original

        variable, new_value, old_value = random.choice(best_neighbors)

        return variable, new_value, old_value, best_neighbor_cost

    while iteration <= max_iterations and best_cost > 0:
        iteration += 1
        try:
            (variable, new_value, old_value, cost) = best_neighbor(cost)
        except IndexError:
            alpha *= (1 - best_cost/max_iterations)
            continue

        variable.value = new_value

        tabu[variable, old_value] = iteration + alpha*cost + (iteration % 11)

        bad_variables.clear()
        for constraint in system.constraints:
            if constraint.is_satisfied():
                continue

            penalty = constraint.penalty(method=penalty_func)
            for v in constraint.variables:
                bad_variables[v] += penalty

        if cost < best_cost:
            print(f"found {cost} on iteration {iteration - 1}/{max_iterations}")
            best_cost = cost
            best_assignment = system.variable_set.values_dict()

    return best_cost, best_assignment
