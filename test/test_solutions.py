from satisfier import all_solutions, ConstraintSystem


def test_pythagorean_triple():
    C = ConstraintSystem()
    x = C.variable_set

    C.add_constraints([
        x[0] < x[1],
        x[0]**2 + x[1]**2 == x[2]**2
    ])

    for variable in C.variables:
        C.set_domain(variable, range(1, 6))

    sols = list(all_solutions(C))
    assert len(sols) == 1

    solution = sols[0]
    assert solution[0]**2 + solution[1]**2 == solution[2]**2


def test_arithmetic():
    C = ConstraintSystem()
    x = C.variable_set

    C.add_constraints([
        x['x']**3 + x['y']**3 + x['z']**3 + x['u']**3 == 100,
        x['x'] < x['u'],
        x['x'] + x['y'] == x['z']
    ])

    for variable in C.variables:
        C.set_domain(variable, range(10))

    sols = list(all_solutions(C))
    assert len(sols) == 3


def test_magic_square():
    """Enumerates the 8 3x3 magic squares."""
    C = ConstraintSystem()
    x = C.variable_set
    n = 3
    target = n * (n**2 + 1) // 2

    # Rows
    C.add_constraint(x[0] + x[1] + x[2] == target)
    C.add_constraint(x[3] + x[4] + x[5] == target)
    C.add_constraint(x[6] + x[7] + x[8] == target)

    # Columns
    C.add_constraint(x[0] + x[3] + x[6] == target)
    C.add_constraint(x[1] + x[4] + x[7] == target)
    C.add_constraint(x[2] + x[5] + x[8] == target)

    # Diagonals
    C.add_constraint(x[0] + x[4] + x[8] == target)
    C.add_constraint(x[2] + x[4] + x[6] == target)

    # All different
    C.all_different(C.variables)

    for variable in C.variables:
        C.set_domain(variable, range(1, n**2 + 1))

    sols = list(all_solutions(C))
    assert len(sols) == 8


def test_nqueens():
    """Enumerates the 92 solutions to the 8-queens problem."""
    C = ConstraintSystem()
    x = C.variable_set

    n = 8

    for i in range(n):
        for j in range(i + 1, n):
            C.add_constraint(x[i] != x[j])
            C.add_constraint(x[i] - x[j] != i - j)
            C.add_constraint(x[i] - x[j] != j - i)

    for i in range(n):
        C.set_domain(x[i], range(n))

    sols = list(all_solutions(C))

    assert len(sols) == 92


def test_latin_square():
    """Enumerates the 576 4x4 latin squares"""
    C = ConstraintSystem()
    x = C.variable_set
    n = 4

    for i in range(n*n):
        C.set_domain(x[i], range(n))

    for i in range(n):
        C.all_different(x[j] for j in range(i*n, (i + 1)*n))
        C.all_different(x[j] for j in range(i, n*n, n))

    sols = list(all_solutions(C))
    assert len(sols) == 576
