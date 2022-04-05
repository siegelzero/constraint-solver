from __future__ import annotations

import itertools
import numbers
import operator

from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Set


class Variable:
    def __init__(self, label: str):
        self.label = label
        self.value = None

    def __hash__(self):
        return hash(self.label)

    def __repr__(self):
        return f"{self.label}"

    def __neg__(self):
        return operator.__neg__(Expression.to_expression(self))

    def __add__(self, other):
        if isinstance(other, numbers.Number) and other == 0:
            return Expression.to_expression(self)
        else:
            return operator.__add__(Expression.to_expression(self), Expression.to_expression(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, numbers.Number) and other == 0:
            return Expression.to_expression(self)
        else:
            return operator.__sub__(Expression.to_expression(self), Expression.to_expression(other))

    def __mul__(self, other):
        if isinstance(other, numbers.Number) and other == 1:
            return
        else:
            return operator.__mul__(Expression.to_expression(self), Expression.to_expression(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, other):
        if isinstance(other, numbers.Number) and other == 1:
            return Expression.to_expression(self)
        else:
            return operator.__pow__(Expression.to_expression(self), Expression.to_expression(other))

    def __eq__(self, other):
        return operator.__eq__(Expression.to_expression(self), Expression.to_expression(other))

    def __ne__(self, other):
        return operator.__ne__(Expression.to_expression(self), Expression.to_expression(other))

    def __le__(self, other):
        return operator.__le__(Expression.to_expression(self), Expression.to_expression(other))

    def __lt__(self, other):
        return operator.__lt__(Expression.to_expression(self), Expression.to_expression(other))

    def __ge__(self, other):
        return operator.__ge__(Expression.to_expression(self), Expression.to_expression(other))

    def __gt__(self, other):
        return operator.__gt__(Expression.to_expression(self), Expression.to_expression(other))


class Expression:
    def __init__(self,
                 label: str,
                 variables: FrozenSet[Variable],
                 value: Callable):
        self.label = label
        self.value = value
        self.variables = variables

    @classmethod
    def to_expression(cls, thing) -> Expression:
        if isinstance(thing, Expression):
            return thing
        elif isinstance(thing, Variable):
            return Expression(
                label=thing.label,
                variables=frozenset([thing]),
                value=lambda: thing.value,
            )
        else:
            return Expression(
                label=str(thing),
                variables=frozenset(),
                value=lambda: thing
            )

    def __repr__(self):
        return f"{self.label}"

    def __neg__(self):
        return Expression(
            label=f"-({self.label})",
            variables=self.variables,
            value=lambda: -self.value()
        )

    def __add__(self, other):
        if isinstance(other, Expression):
            return Expression(
                label=f"{self.label} + {other.label}",
                variables=self.variables | other.variables,
                value=lambda: self.value() + other.value()
            )
        else:
            return self.__add__(Expression.to_expression(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Expression):
            return Expression(
                label=f"{self.label} - ({other.label})",
                variables=self.variables | other.variables,
                value=lambda: self.value() - other.value()
            )
        else:
            return self.__add__(Expression.to_expression(other))

    def __mul__(self, other):
        if isinstance(other, Expression):
            return Expression(
                label=f"({self.label})*({other.label})",
                variables=self.variables | other.variables,
                value=lambda: self.value() * other.value()
            )
        else:
            return self.__mul__(Expression.to_expression(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, other):
        if isinstance(other, Expression):
            return Expression(
                label=f"({self.label})**({other.label})",
                variables=self.variables | other.variables,
                value=lambda: self.value() ** other.value()
            )
        else:
            return self.__pow__(Expression.to_expression(other))

    def __eq__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__eq__, f"{self.label} == {other.label}")
        else:
            return self.__eq__(Expression.to_expression(other))

    def __ne__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__ne__, f"{self.label} != {other.label}")
        else:
            return self.__ne__(Expression.to_expression(other))

    def __ge__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__ge__, f"{self.label} >= {other.label}")
        else:
            return self.__ge__(Expression.to_expression(other))

    def __le__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__le__, f"{self.label} <= {other.label}")
        else:
            return self.__le__(Expression.to_expression(other))

    def __gt__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__gt__, f"{self.label} > {other.label}")
        else:
            return self.__gt__(Expression.to_expression(other))

    def __lt__(self, other):
        if isinstance(other, Expression):
            return Constraint(self, other, operator.__lt__, f"{self.label} < {other.label}")
        else:
            return self.__lt__(Expression.to_expression(other))


class Constraint:
    def __init__(self,
                 left: Expression,
                 right: Expression,
                 relation: Callable,
                 label: str):
        self.left = left
        self.right = right
        self.relation = relation
        self.label = label
        self.variables: FrozenSet[Variable] = left.variables | right.variables

    def __repr__(self):
        return f"{self.label}"

    def __boolean_penalty(self) -> int:
        """Returns 1 if the penalty is violated and 0 otherwise"""
        return int(self.is_violated())

    def __variable_penalty(self) -> int:
        """Returns the number of variables in the constraint"""
        return len(self.variables)

    def __error_penalty(self) -> int:
        """Returns the error penalty of the constraint"""
        if self.relation == operator.__eq__:
            return abs(self.right.value() - self.left.value())
        else:
            return len(self.variables)

    def __weird_penalty(self) -> int:
        """Returns the error penalty of the constraint"""
        if self.relation == operator.__eq__:
            return 2**len(self.variables)
        else:
            return 3**len(self.variables)

    def penalty(self, method='error') -> int:
        if method == 'error':
            return self.__error_penalty()
        elif method == 'variable':
            return self.__variable_penalty()
        elif method == 'weird':
            return self.__weird_penalty()
        else:
            return self.__boolean_penalty()

    def is_satisfied(self) -> bool:
        return self.relation(self.left.value(), self.right.value())

    def is_violated(self) -> bool:
        return not self.is_satisfied()

    def unassigned_variables(self) -> List[Variable]:
        return [v for v in self.variables if v.value is None]


class VariableSet:
    def __init__(self, label: str):
        self.label: str = label
        self.variables: Set[Variable] = set()
        self._map: Dict[Any, Variable] = dict()

    def __repr__(self):
        variables = ', '.join([f"{e}" for e in sorted(self.variables)])
        return f"VariableSet with variables {variables}"

    def __getitem__(self, key):
        if key not in self._map:
            variable = Variable(f"{self.label}_{key}")
            self.variables.add(variable)
            self._map[key] = variable
        return self._map[key]

    def __setitem__(self, key, value):
        if key not in self._map:
            self._map[key] = Variable(f"{self.label}_{key}")

        variable = self._map[key]
        variable.value = value

    def values_dict(self) -> Dict[Any, Any]:
        return {k: v.value for (k, v) in self._map.items()}

    def reset(self):
        for variable in self.variables:
            variable.value = None


class ConstraintSystem:
    def __init__(self):
        self.constraints: Set[Constraint] = set()
        self.variables: Set[Variable] = set()
        self.variable_set: VariableSet = VariableSet(label='x')
        self.domain: Dict[Variable, Set[Any]] = {}

    def __repr__(self):
        cons = "\n".join([str(con) for con in self.constraints])
        return f"""Constraint Satisfaction Problem with constraints:\n{cons}"""

    def add_constraint(self, constraint: Constraint):
        self.variables.update(constraint.variables)
        self.constraints.add(constraint)

    def add_constraints(self, constraints: Iterable[Constraint]):
        for constraint in constraints:
            self.add_constraint(constraint)

    def set_domain(self, variable: Variable, values: Iterable[Any]):
        self.domain[variable] = set(values)

    def all_different(self, variables: Iterable[Variable]):
        for (v1, v2) in itertools.combinations(variables, 2):
            self.add_constraint(v1 != v2)
