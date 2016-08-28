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
            print 'Finishing with %s constraints' % len(self.constraints)

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

        # Keep a map of the update version of each constraint: we will use this
        # to reduce the constraint even further
        current_constraints = {
            constraint: constraint
            for constraint in self.constraints
        }

        for constraint_1, constraint_2 in constraint_pairs:
            current_constraint_1 = current_constraints[constraint_1]
            current_constraint_2 = current_constraints[constraint_2]

            # We remove cases from the changed constraint, using the original
            # constraint, as we want to use as many as possible to trim it down
            # TODO: Maybe it's not necessary
            new_constraint_1 = self.remove_incompatible_cases_from_constraint(
                current_constraint_1, constraint_2)
            new_constraint_2 = self.remove_incompatible_cases_from_constraint(
                current_constraint_2, constraint_1)

            assert new_constraint_1, \
                "Constraint %s with %s was impossible" \
                % (str(constraint_1), str(constraint_2))
            assert new_constraint_2, \
                "Constraint %s with %s was impossible" \
                % (str(constraint_2), str(constraint_1))

            current_constraints[constraint_1] = new_constraint_1
            current_constraints[constraint_2] = new_constraint_2

        changed_constraints = {
            constraint: current_constraint
            for constraint, current_constraint
            in current_constraints.iteritems()
            if constraint != current_constraint
        }
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
            for simplified_constraint in self.simplify_constraint(constraint)
        )

        if simplified_constraints != self.constraints:
            if self.debug:
                print 'Simplified %s constraints' \
                      % len(simplified_constraints - self.constraints)
            changed = True
            self.constraints.difference_update(self.constraints)
            self.constraints.update(simplified_constraints)

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
        constraints_by_side = self.get_constraints_by_side()

        constraint_pairs = frozenset(
            pair
            for constraints in constraints_by_side.itervalues()
            for pair in itertools.combinations(sorted(constraints), 2)
        )

        return constraint_pairs

    def get_constraints_by_side(self):
        constraints_by_side = {}
        for constraint in self.constraints:
            for side in constraint.sides:
                constraints_by_side.setdefault(side, set()).add(constraint)

        return constraints_by_side

    def remove_incompatible_cases_from_constraint(
            self, constraint_1, constraint_2):
        return self.make_constraint(source=constraint_1.source, constraint=(
            case_1
            for case_1 in constraint_1
            if any(
                self.are_cases_compatible(case_1, case_2)
                for case_2 in constraint_2
            )
        ))

    def are_cases_compatible(self, case_1, case_2):
        sides = case_1.sides & case_2.sides
        if not sides:
            return True

        sides_case_1 = self.filter_case_sides(case_1, sides)
        sides_case_2 = self.filter_case_sides(case_2, sides)

        return sides_case_1 == sides_case_2

    def filter_case_sides(self, case, sides):
        if case.sides == sides:
            return case

        return self.make_case(source=case.source, case=(
            (side, is_closed)
            for (side, is_closed) in case
            if side in sides
        ))

    def filter_constraint_sides(self, constraint, sides):
        if constraint.sides == sides:
            return constraint

        return self.make_constraint(source=constraint.source, constraint=(
            self.filter_case_sides(case, sides)
            for case in constraint
        ))

    def exclude_case_sides(self, case, sides):
        if not sides:
            return case

        return self.make_case(source=case.source, case=(
            (side, is_closed)
            for (side, is_closed) in case
            if side not in sides
        ))

    def exclude_constraint_sides(self, constraint, sides):
        if not sides:
            return constraint

        return self.make_constraint(source=constraint.source, constraint=(
            self.exclude_case_sides(case, sides)
            for case in constraint
        ))

    def simplify_constraint(self, constraint):
        if len(constraint) == 1:
            return [constraint]

        common_sides = constraint.common_facts_sides
        if not common_sides:
            return [constraint]
        if common_sides == constraint.sides:
            return [constraint]

        simplified_constraint = \
            self.exclude_constraint_sides(constraint, common_sides)
        resolved_constraint = \
            self.filter_constraint_sides(constraint, common_sides)

        simplified_constraints = \
            filter(None, [simplified_constraint, resolved_constraint])

        assert simplified_constraints, \
            "Simplifying constraint %s ended up in incompatibility" \
            % str(constraint)

        return simplified_constraints
