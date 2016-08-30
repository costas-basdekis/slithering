import itertools

from slithering.solver.constraints import Constraint, Case


class ConstraintSolver(object):
    def __init__(self, puzzle, debug=False):
        self.puzzle = puzzle
        self.debug = debug

    @property
    def constraints(self):
        return self.puzzle.constraints

    def apply(self):
        changed = False

        if self.debug:
            print '*' * 80
            print 'Starting with %s constraints' % len(self.constraints)

        solved_sides_constraint = self.add_solved_sides_constraint()
        changed |= self.apply_resolved_constraints(solved_sides_constraint)
        self.remove_resolved_constraints()

        if self.debug:
            print 'Finishing with %s constraints, changed: %s' \
                  % (len(self.constraints), changed)

        return changed

    def add_solved_sides_constraint(self):
        constraint = Constraint((
            Case((
                (side, side.is_closed)
                for side in self.puzzle.sides.solved
            ), source=u'Solved sides'),
        ), source=u'Solved sides')
        self.constraints.add(constraint)
        return constraint

    def apply_resolved_constraints(self, *ignoring):
        changed = False
        resolved_constraints = self.get_resolved_constraints()
        resolved_constraints -= frozenset(ignoring)
        if self.debug:
            print 'Applying %s resolved constraints' % len(resolved_constraints)
        for constraint in resolved_constraints:
            changed |= self.apply_resolved_constraint(constraint)

        return changed

    def remove_resolved_constraints(self):
        resolved_constraints = self.get_resolved_constraints()
        if self.debug:
            print 'Removing %s resolved constraints' % len(resolved_constraints)
        self.constraints.difference_update(resolved_constraints)

    def apply_resolved_constraint(self, constraint):
        changed = False
        for case in constraint:
            for side, is_closed in case:
                if not side.solved:
                    changed = True
                side.solved_is_closed = is_closed

        return changed

    def get_resolved_constraints(self):
        resolved_constraints = frozenset(
            constraint
            for constraint in self.constraints
            if len(constraint) == 1
        )
        return resolved_constraints

    def get_constraints_pairs(self):
        constraints_by_side = self.constraints.by_side

        constraint_pairs = frozenset(
            pair
            for constraints in constraints_by_side.itervalues()
            for pair in itertools.combinations(sorted(constraints), 2)
        )

        return constraint_pairs
