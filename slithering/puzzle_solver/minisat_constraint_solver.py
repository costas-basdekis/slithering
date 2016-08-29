from satispy import Variable, Cnf
from satispy.solver import Minisat


class MinisatConstraintSolver(object):
    def __init__(self, puzzle, debug=False):
        self.puzzle = puzzle
        self.debug = debug
        self.variables = {
            side: Variable(side)
            for side in self.puzzle.sides
        }

    @property
    def constraints(self):
        return self.puzzle.constraints

    def apply(self):
        if self.debug:
            print '*' * 80
            print 'Starting with %s constraints' % len(self.constraints)

        cnf = self.get_initial_cnf()
        solved_variables = self.solve_variables(cnf)
        solved_sides = self.get_solved_sides(solved_variables)
        changed = self.apply_solved_sides(solved_sides)

        return changed

    def get_initial_cnf(self):
        constraints_cnf = self.constraints_to_sat(self.constraints)
        solved_cnf = reduce(self.and_vars, (
            self.variables[side] if side.is_closed else -self.variables[side]
            for side in self.puzzle.sides
            if side.solved
        ), Cnf())
        cnf = constraints_cnf & solved_cnf

        return cnf

    def solve_variables(self, cnf):
        if self.debug:
            print 'Solving for %s constraints' % len(self.constraints)

        solution = self.solve(cnf)
        assert solution.success, "Constraints ended up incompatible"
        solved_variables = frozenset(solution.varmap.iteritems())
        while solution.success and solved_variables:
            if self.debug:
                print 'Gathering solved variables: %s so far' \
                      % len(solved_variables)
            solved_variables &= frozenset(solution.varmap.iteritems())
            cnf = cnf & -(self.from_varmap(solution.varmap))

            solution = self.solve(cnf)

        return solved_variables

    def get_solved_sides(self, solved_variables):
        solved_sides = frozenset(
            (variable.side, is_closed)
            for variable, is_closed in solved_variables
        )
        return solved_sides

    def apply_solved_sides(self, solved_sides):
        if self.debug:
            print 'Apply %s solved sides' % len(solved_sides)

        changed = False
        for side, is_closed in solved_sides:
            changed |= not side.solved
            side.solved_is_closed = is_closed
        return changed

    def solve(self, cnf):
        solver = Minisat()
        solution = solver.solve(cnf)
        if solution.error:
            raise Exception("minisat could not solve CNF")

        return solution

    def from_varmap(self, varmap):
        return reduce(self.and_vars, (
            var if truth else -var
            for var, truth in varmap.iteritems()
        ))

    @staticmethod
    def or_vars(lhs, rhs):
        return lhs | rhs

    @staticmethod
    def and_vars(lhs, rhs):
        return lhs & rhs

    def constraints_to_sat(self, constraints):
        return reduce(self.and_vars, map(self.constraint_to_sat, constraints))

    def constraint_to_sat(self, constraint):
        return reduce(self.or_vars, map(self.case_to_sat, constraint))

    def case_to_sat(self, case):
        return reduce(self.and_vars, map(self.fact_to_sat, case))

    def fact_to_sat(self, (side, is_closed)):
        variable = self.variables[side]
        if is_closed:
            return variable
        else:
            return -variable
