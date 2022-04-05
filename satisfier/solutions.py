import random

from collections import defaultdict
from typing import Any, Dict, Iterator, List, Set, Tuple

from satisfier.system import ConstraintSystem, Constraint, Variable


# Type aliases
Domain = Dict[Variable, Set[Any]]
Assignment = Dict[Variable, Any]


def enumerate(system: ConstraintSystem) -> Iterator[Assignment]:
    def compatible_values(constraint: Constraint, variable: Variable, domain: Domain) -> Set[Any]:
        assert variable.value is None
        compatible = set()
        for value in domain[variable]:
            variable.value = value
            if constraint.is_satisfied():
                compatible.add(value)
        variable.value = None
        return compatible

    def accessible_constraints(unsatisfied: Set[Constraint]) -> Dict[Variable, Set[Constraint]]:
        constraint_map: Dict[Variable, Set[Constraint]] = defaultdict(set)
        for constraint in unsatisfied:
            unassigned = constraint.unassigned_variables()
            if len(unassigned) == 1:
                variable = unassigned[0]
                constraint_map[variable].add(constraint)
        return constraint_map

    def reduce_domain(unsatisfied: Set[Constraint],
                      domain: Domain) -> Tuple[bool, Domain, Dict[Variable, Set[Constraint]]]:
        reduced = domain.copy()
        prune = False
        constraint_map = accessible_constraints(unsatisfied)
        for (variable, constraints) in constraint_map.items():
            for constraint in constraints:
                compatible = compatible_values(constraint, variable, reduced)
                if not compatible:
                    prune = True
                    break
                else:
                    reduced[variable] = compatible
            if prune:
                break
        return prune, reduced, constraint_map

    def backtrack(fixed: Set[Variable],
                  unfixed: Set[Variable],
                  unsatisfied: Set[Constraint],
                  domain: Domain) -> Iterator[Dict[Variable, Any]]:
        if not unsatisfied:
            yield system.variable_set.values_dict()
        else:
            prune, reduced_domain, constraint_map = reduce_domain(unsatisfied, domain)
            if prune:
                return

            variable = max(unfixed, key=lambda v: len(constraint_map[v]))
            constraints_to_check = constraint_map[variable]

            for value in sorted(reduced_domain[variable]):
                variable.value = value
                yield from backtrack(
                    fixed | {variable},
                    unfixed - {variable},
                    unsatisfied - constraints_to_check,
                    reduced_domain,
                )
            variable.value = None

    system.variable_set.reset()
    return backtrack(
        fixed=set(),
        unfixed=set(system.variables),
        unsatisfied=set(system.constraints),
        domain=system.domain
    )


def tabu(system: ConstraintSystem, max_iterations=1000, penalty_func='error'):
    alpha = 0.6
    # Initialize with random assignment
    for variable in system.variables:
        variable.value = random.choice(sorted(system.domain[variable]))

    # Build a map of variables to the constraints that each belongs to
    constraints: Dict[Variable, List[Constraint]] = defaultdict(list)

    bad_variables: Set[Variable] = set()

    # Cost of our random assignment
    cost = 0
    for constraint in system.constraints:
        for variable in constraint.variables:
            constraints[variable].append(constraint)

        if constraint.is_satisfied():
            continue

        cost += constraint.penalty(method=penalty_func)
        bad_variables |= constraint.variables

    tabu: Dict[Tuple[Variable, Any], Any] = defaultdict(int)

    best_cost = cost
    best_assignment = system.variable_set.values_dict()

    print(f"Initial cost: {cost}")
    iteration = 0

    def best_neighbor(cost):
        best_neighbor_cost = 10**100
        best_neighbors = []

        for variable in bad_variables:
            original = variable.value
            old = sum(
                constraint.penalty(method=penalty_func)
                for constraint in constraints[variable] if constraint.is_violated()
            )

            if old == 0:
                continue

            for value in system.domain[variable]:
                if value == original:
                    continue

                variable.value = value

                new = sum(
                    constraint.penalty(method=penalty_func)
                    for constraint in constraints[variable] if constraint.is_violated()
                )

                ncost = cost + new - old

                if tabu[variable, value] > iteration:
                    if ncost >= best_cost:
                        continue
                    print(f'aspiration! {variable}: {value} -> {ncost} {best_cost}')

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
            alpha *= 0.8
            continue

        variable.value = new_value

        tabu[variable, old_value] = iteration + alpha*cost + (iteration % 11)

        bad_variables.clear()
        for constraint in system.constraints:
            if constraint.is_violated():
                bad_variables |= constraint.variables

        if cost < best_cost:
            print(f"found {cost} on iteration {iteration - 1}/{max_iterations}")
            best_cost = cost
            best_assignment = system.variable_set.values_dict()

    return best_cost, best_assignment
