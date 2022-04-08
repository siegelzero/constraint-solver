![Unit Tests](https://github.com/siegelzero/satisfier/workflows/Unit%20Tests/badge.svg)


# Satisfier
Finds solutions for finite domain Constraint Satisfaction Problems.

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