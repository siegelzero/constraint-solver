from collections import defaultdict

from typing import Any, Dict, Iterator, Set, Tuple

from satisfier.system import ConstraintSystem, Constraint, Variable


# Type aliases
Domain = Dict[Variable, Set[Any]]
Assignment = Dict[Variable, Any]


def solutions(system: ConstraintSystem) -> Iterator[Assignment]:
    """Yields all solutions to the given constraint system.

    Implements backtracking with domain reduction to find all solutions to the
    constraint system.

    Example:
    >>> C = ConstraintSystem()
    >>> x = C.variable_set
    >>> C.add_constraints([
    ...     x[0] < x[1],
    ...     x[0]**2 + x[1]**2 == x[2]**2
    ... ])
    ...
    >>> for variable in C.variables:
    ...     C.set_domain(variable, range(1, 20))
    ...
    >>> for solution in all_solutions(C):
    ...     print(solution)
    ...
    [3, 4, 5]
    [6, 8, 10]
    [5, 12, 13]
    [9, 12, 15]
    [8, 15, 17]
    """
    def compatible_values(constraint: Constraint, variable: Variable, domain: Domain) -> Set[Any]:
        """Returns all values of the variable in its domain that satisfy the constraint.
        i.e. returns the reduced domain of the variable by excluding any values that violate the constraint.
        """
        assert variable.value is None
        compatible = set()
        for value in domain[variable]:
            variable.value = value
            if constraint.is_satisfied():
                compatible.add(value)
        variable.value = None
        return compatible

    def accessible_constraints(unsatisfied: Set[Constraint]) -> Dict[Variable, Set[Constraint]]:
        """Finds all constraints that have only one unassigned variable.
        Returns a mapping from the variable to the set of constraints that have that variable.
        """
        constraint_map: Dict[Variable, Set[Constraint]] = defaultdict(set)
        for constraint in unsatisfied:
            unassigned = constraint.unassigned_variables()
            if len(unassigned) == 1:
                variable = unassigned[0]
                constraint_map[variable].add(constraint)
        return constraint_map

    def reduce_domain(unsatisfied: Set[Constraint],
                      domain: Domain) -> Tuple[bool, Domain, Dict[Variable, Set[Constraint]]]:
        """Reduces the domain of each variable in the constraint system by
        excluding values that violate the constraints.
        """
        reduced = domain.copy()
        prune = False

        # Find all constraints that have only one unassigned variable
        # If none are one variable away, no reductions are performed
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


def search(system: ConstraintSystem) -> Assignment:
    """Search for a solution to the given constraint system."""
    return next(solutions(system))
