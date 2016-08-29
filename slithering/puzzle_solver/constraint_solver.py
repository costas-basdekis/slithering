import itertools

from slithering.puzzle_solver.constraints import Constraint, Case, Fact


class ConstraintSolver(object):
    def __init__(self, puzzle, debug=False):
        self.puzzle = puzzle
        self.debug = debug

    @property
    def constraints(self):
        return self.puzzle.constraints

    def make_constraint(self, constraint, source=None):
        return Constraint(constraint, source=source)

    def make_case(self, case, source=None):
        return Case(case, source=source)

    def make_fact(self, fact, source=None):
        return Fact(*fact, source=source)

    def apply(self):
        changed = False

        if self.debug:
            print '*' * 80
            print 'Starting with %s constraints' % len(self.constraints)

        self.add_solved_sides_constraint()
        changed |= self.remove_incompatible_cases()
        changed |= self.simplify_constraints()
        changed |= self.apply_resolved_constraints()
        self.remove_resolved_constraints()

        if self.debug:
            print 'Finishing with %s constraints, changed: %s' \
                  % (len(self.constraints), changed)

        return changed

    def add_solved_sides_constraint(self):
        self.constraints.add(self.make_constraint(
            source=u'Solved sides',
            constraint=(
                self.make_case(source=u'Solved sides', case=(
                    (side, side.is_closed)
                    for side in self.puzzle.sides.solved
                )),
            )),
        )

    def remove_incompatible_cases(self):
        constraint_pairs = self.get_constraints_pairs()

        changed_constraints = {}

        for constraint_1, constraint_2 in constraint_pairs:
            current_constraint_1 = \
                changed_constraints.get(constraint_1, constraint_1)
            current_constraint_2 = \
                changed_constraints.get(constraint_2, constraint_2)

            # We remove cases from the changed constraint, using the original
            # constraint, as we want to use as many as possible to trim it down
            # TODO: Maybe it's not necessary
            new_constraint_1 = \
                current_constraint_1.being_compatible_with(constraint_2)
            new_constraint_2 = \
                current_constraint_2.being_compatible_with(constraint_1)

            assert new_constraint_1, \
                "Constraint %s with %s was impossible" \
                % (str(constraint_1), str(constraint_2))
            assert new_constraint_2, \
                "Constraint %s with %s was impossible" \
                % (str(constraint_2), str(constraint_1))

            if new_constraint_1 != constraint_1:
                changed_constraints[constraint_1] = new_constraint_1
            if new_constraint_2 != constraint_2:
                changed_constraints[constraint_2] = new_constraint_2

        changed = bool(changed_constraints)

        if self.debug:
            print 'Updating %s constraints' % len(changed_constraints)

        self.constraints.difference_update(changed_constraints.iterkeys())
        self.constraints.update(changed_constraints.itervalues())

        return changed

    def simplify_constraints(self):
        changed = False

        simplified_constraints = frozenset(
            simplified_constraint
            for constraint in self.constraints
            for simplified_constraint in constraint.simplified()
        )

        removed_constraints = self.constraints - simplified_constraints
        added_constraints = simplified_constraints - self.constraints

        if removed_constraints or added_constraints:
            if self.debug:
                print 'Simplified constraints: removing %s, adding %s' \
                      % (len(removed_constraints), len(added_constraints))
            changed = True
            self.constraints.difference_update(removed_constraints)
            self.constraints.update(added_constraints)

        return changed

    def apply_resolved_constraints(self):
        changed = False
        resolved_constraints = self.get_resolved_constraints()
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
