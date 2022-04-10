![Unit Tests](https://github.com/siegelzero/satisfier/workflows/Unit%20Tests/badge.svg)


# Satisfier
Satisfier is a package for finding solutions to Constraint Satisfaction Problems (CSPs), supporting variables over finite domains, with a flexible set of constraints.
The packages includes enumerative methods that explore the entire search space of a problem, as well as a variety of heuristic methods to search for solutions to larger problem instances.

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

Below is a system that has some small Pythagorean triples as solutions.

```python
from satisfier import system
C = system.ConstraintSystem()
x = C.variable_set

C.add_constraints([
    x[0] < x[1],
    x[0]**2 + x[1]**2 == x[2]**2
])

for variable in C.variables:
    C.set_domain(variable, range(1, 20))

for solution in all_solutions(C):
    print(solution)
```
