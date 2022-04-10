![Unit Tests](https://github.com/siegelzero/satisfier/workflows/Unit%20Tests/badge.svg)


# Satisfier
Satisfier is a package for finding solutions to Constraint Satisfaction Problems (CSPs), supporting variables over finite domains with a rich and flexible set of constraints and combination methods.
The package includes enumerative methods that explore the entire search space of a problem, as well as a variety of heuristic methods to search for solutions to larger problem instances.

Satisfier can be used for a variety of mathematical tasks.
* Enumerating solutions to equations or systems of equations
* Searching for solutions to CSPs, or proving that no solutions exist
* Constructing combinatorial structures
* Graph coloring
* Many more!

### Installation

```bash
pip install satisfier
```

### Example Usage

Below is a system that has a small Pythagorean triple as a solution.

```python
from satisfier.system import ConstraintSystem
from satisfier.enumerative import search

C = ConstraintSystem()
x = C.variable_set

C.add_constraints([
    x[0] < x[1],
    x[0]**2 + x[1]**2 == x[2]**2
])

for variable in C.variables:
    C.set_domain(variable, range(1, 6))

search(C)
```

Satisfier can be used to enumerate combinatorial structures.
A *derangement* is a permutation that has no fixed points.
We can enumerate the `44` derangements of the `5` symbols `0, 1, 2, 3, 4` as follows, using the `all_different` constraint to ensure that all variable values are distinct.
```python
from satisfier.system import ConstraintSystem
from satisfier.enumerative import solutions

C = ConstraintSystem()
position = C.variable_set

n = 5
for i in range(n):
    C.set_domain(position[i], range(n))

for i in range(n):
    C.add_constraint(position[i] != i)

C.all_different(C.variables)

assert sum(1 for _ in solutions(C)) == 44
```
