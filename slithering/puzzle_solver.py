import itertools
from collections import namedtuple


class PuzzleSolver(object):
    puzzle_restriction_classes = []
    cell_restriction_classes = []
    side_restriction_classes = []
    corner_restriction_classes = []

    @classmethod
    def register_puzzle_restriction_class(cls, restriction_class):
        cls.puzzle_restriction_classes.append(restriction_class)
        return restriction_class

    @classmethod
    def register_cell_restriction_class(cls, restriction_class):
        cls.cell_restriction_classes.append(restriction_class)
        return restriction_class

    @classmethod
    def register_side_restriction_class(cls, restriction_class):
        cls.side_restriction_classes.append(restriction_class)
        return restriction_class

    @classmethod
    def register_corner_restriction_class(cls, restriction_class):
        cls.corner_restriction_classes.append(restriction_class)
        return restriction_class

    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.restrictions = self.find_new_restrictions()
        self.all_restrictions = set(self.restrictions)

    def find_new_restrictions(self):
        restrictions = set()

        restrictions.update(self.find_new_puzzle_restrictions())
        restrictions.update(self.find_new_cell_restrictions())
        restrictions.update(self.find_new_side_restrictions())
        restrictions.update(self.find_new_corner_restrictions())

        return restrictions

    def find_new_puzzle_restrictions(self):
        return self.create_suitable_puzzle_restrictions(
            self.puzzle_restriction_classes)

    def find_new_cell_restrictions(self):
        return self.create_suitable_puzzle_item_restrictions(
            self.puzzle.cells, self.cell_restriction_classes)

    def find_new_side_restrictions(self):
        return self.create_suitable_puzzle_item_restrictions(
            self.puzzle.sides, self.side_restriction_classes)

    def find_new_corner_restrictions(self):
        return self.create_suitable_puzzle_item_restrictions(
            self.puzzle.corners, self.corner_restriction_classes)

    def create_suitable_puzzle_restrictions(self, restriction_classes):
        return {
            restriction_class(self.puzzle)
            for restriction_class in restriction_classes
            if restriction_class.is_suitable(self.puzzle)
        }

    def create_suitable_puzzle_item_restrictions(
            self, items, restriction_classes):
        return {
            restriction_class(self.puzzle, item)
            for item in items
            for restriction_class in restriction_classes
            if restriction_class.is_suitable(self.puzzle, item)
        }

    def apply(self):
        changed = False
        new_restrictions = set()

        for restriction in self.restrictions:
            restriction_changed, restriction_new_restrictions = \
                restriction.apply()
            changed |= restriction_changed
            new_restrictions |= restriction_new_restrictions

        new_restrictions |= self.find_new_restrictions()

        # Only add restrictions that we never encountered before
        new_restrictions -= self.all_restrictions
        self.all_restrictions |= new_restrictions

        changed |= bool(new_restrictions)

        unfinished_restrictions = {
            restriction
            for restriction in self.restrictions
            if not restriction.finished
        }
        self.restrictions = unfinished_restrictions | new_restrictions

        return changed

    def solve(self):
        print 'Unsolved:', self.puzzle.solved, \
            len(self.puzzle.cells), 'cells', \
            len(self.puzzle.sides), 'sides', \
            len(self.puzzle.corners), 'corners'
        print 'Solved:', self.puzzle.solved, \
            len(self.puzzle.cells.solved), 'cells', \
            len(self.puzzle.sides.solved), 'sides', \
            len(self.puzzle.corners.solved), 'corners'
        while self.apply():
            print 'Solved:', self.puzzle.solved, \
                len(self.puzzle.cells.solved), 'cells', \
                len(self.puzzle.sides.solved), 'sides', \
                len(self.puzzle.corners.solved), 'corners'
            if self.puzzle.solved:
                break


class Restriction(object):
    """A restriction that can make changes, or create new hints"""
    def __init__(self):
        self.finished = False

    def __hash__(self):
        return hash(tuple(self.hash_key()))

    def hash_key(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.hash_key() == other.hash_key()

    @classmethod
    def is_suitable(cls, *args, **kwargs):
        """Check whether the restriction can be created from the arguments"""
        raise NotImplementedError()

    def apply(self):
        """
        Apply the restriction further, if possible.
        It should return if it managed to make any changes, or create any new
        hints, and the any new hints it could create.
        It should change `self.finished` to `True`, if it can make no further
        changes.
        """
        raise NotImplementedError()


class PuzzleRestriction(Restriction):
    def __init__(self, puzzle):
        super(PuzzleRestriction, self).__init__()
        self.puzzle = puzzle

    def hash_key(self):
        return tuple((type(self), self.puzzle))

    @classmethod
    def is_suitable(cls, puzzle):
        raise NotImplementedError()


class CellRestriction(PuzzleRestriction):
    def __init__(self, puzzle, cell):
        super(CellRestriction, self).__init__(puzzle)
        self.cell = cell

    def hash_key(self):
        return tuple((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, puzzle, cell):
        raise NotImplementedError()


class CornerRestriction(PuzzleRestriction):
    def __init__(self, puzzle, corner):
        super(CornerRestriction, self).__init__(puzzle)
        self.corner = corner

    def hash_key(self):
        return tuple((type(self), self.corner.key))

    @classmethod
    def is_suitable(cls, puzzle, corner):
        return super(CornerRestriction, cls)\
            .is_suitable(puzzle=puzzle, corner=corner)


class WithPuzzleConstraints(PuzzleRestriction):
    @property
    def constraints(self):
        if not hasattr(self.puzzle, 'constraints'):
            self.puzzle.constraints = set()

        return self.puzzle.constraints

    def make_constraint(self, constraint, source=None):
        cases = map(self.make_case, constraint)
        return Constraint(cases, source=source)

    def make_case(self, case, source=None):
        facts = map(self.make_fact, case)
        return Case(facts, source=source)

    def make_fact(self, fact, source=None):
        return Fact(*fact, source=source)


class Constraint(tuple):
    def __new__(cls, value, source=None):
        value = tuple(value)
        cases = map(Case, value)
        normalised = tuple(sorted(set(cases)))
        return super(Constraint, cls).__new__(cls, normalised)

    def __init__(self, value, source=None):
        if source is None:
            if isinstance(value, Constraint):
                source = value.source
        self.source = source
        super(Constraint, self).__init__(value)

    def __str__(self):
        return u'Constraint(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )


class Case(tuple):
    def __new__(cls, value, source=None):
        facts = [Fact(*fact) for fact in value]
        normalised = tuple(sorted(set(facts)))
        return super(Case, cls).__new__(cls, normalised)

    def __init__(self, value, source=None):
        if source is None:
            if isinstance(value, Case):
                source = value.source
        self.source = source
        super(Case, self).__init__(value)

    def __str__(self):
        return u'Case(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )


class Fact(namedtuple('Fact', ['side', 'is_closed'])):
    def __new__(cls, *values, **kwargs):
        return super(Fact, cls).__new__(cls, *values)

    def __init__(self, *values, **kwargs):
        kwargs.setdefault('source', None)
        self.source, = kwargs.values()
        super(Fact, self).__init__(*values)


@PuzzleSolver.register_cell_restriction_class
class CellHintRestriction(WithPuzzleConstraints, CellRestriction):
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if not cell.hint_is_given:
            return False

        return True

    def apply(self):
        self.finished = True
        changed = False
        new_restrictions = set()

        constraints = self.constraints

        constraint = self.constraint()
        if constraint not in constraints:
            changed = True
            constraints.add(constraint)

        return changed, new_restrictions

    def constraint(self):
        sides = sorted(self.cell.sides)
        combinations = itertools.combinations(sides, self.cell.hint)

        constraint = self.make_constraint(source=u'From hint', constraint=(
            self.make_case(source=u'Hint possibility', case=(
                (side, side in combination)
                for side in sides
            ))
            for combination in combinations
        ))

        return constraint


@PuzzleSolver.register_cell_restriction_class
class CellSolvedEdgeSideRestriction(CellRestriction):
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if cell.solved:
            return False

        if not cell.is_on_edge:
            return False

        solved_on_edge_sides = cell.sides.solved & cell.sides.on_edge
        if not any(solved_on_edge_sides):
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()
        self.finished = True

        if self.cell.solved:
            return changed, new_restrictions

        changed = True

        is_internal = any(
            side.is_on_edge and side.solved and side.solved_is_closed
            for side in self.cell.sides
        )
        is_external = any(
            side.is_on_edge and side.solved and not side.solved_is_closed
            for side in self.cell.sides
        )

        assert not (is_internal and is_external), \
            u"Invalid state: a cell should be both internal and external, " \
            u"based on sides"

        self.cell.solved_is_internal = is_internal

        return changed, new_restrictions


@PuzzleSolver.register_cell_restriction_class
class CellSolvedSideRestriction(CellRestriction):
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if cell.solved:
            return False

        solved_sides_with_solved_cell = {
            side
            for side in cell.sides.solved
            if any(side.cells.solved)
        }
        if not any(solved_sides_with_solved_cell):
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()
        self.finished = True

        if self.cell.solved:
            return changed, new_restrictions

        is_internal = any(
            side.is_on_edge and side.solved and side.solved_is_closed
            for side in self.cell.sides
        )
        is_external = any(
            side.is_on_edge and side.solved and not side.solved_is_closed
            for side in self.cell.sides
        )

        assert not (is_internal and is_external), \
            u"Invalid state: a cell should be both internal and external, " \
            u"based on sides"

        if is_internal:
            self.cell.solved_is_internal = True
            changed = True
        elif is_external:
            self.cell.solved_is_internal = False
            changed = True

        return changed, new_restrictions


# TODO: Remove, since it's superseded by CornerConstraints
@PuzzleSolver.register_corner_restriction_class
class CornerSingleUnsolvedSide(CornerRestriction):
    @classmethod
    def is_suitable(cls, puzzle, corner):
        if len(corner.sides.unsolved) != 1:
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()
        self.finished = True

        if not self.corner.sides.unsolved:
            return changed, new_restrictions

        unsolved_side, = self.corner.sides.unsolved

        closed_solved_sides = \
            self.corner.sides.closed & self.corner.sides.solved
        if len(closed_solved_sides) > 1:
            return changed, new_restrictions

        changed = True

        if closed_solved_sides:
            unsolved_side.solved_is_closed = True
        else:
            unsolved_side.solved_is_closed = False

        return changed, new_restrictions


# TODO: Remove, since it's superseded by CornerConstraints
@PuzzleSolver.register_corner_restriction_class
class CornerTwoSolvedSides(CornerRestriction):
    @classmethod
    def is_suitable(cls, puzzle, corner):
        if len(corner.sides.solved.closed) != 2:
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()
        self.finished = True

        for side in self.corner.sides.unsolved:
            changed = True
            side.solved_is_closed = False

        return changed, new_restrictions


# TODO: Remove, since it's superseded by CornerConstraints
@PuzzleSolver.register_corner_restriction_class
class CornerTwoUnsolvedSides(WithPuzzleConstraints, CornerRestriction):
    @classmethod
    def is_suitable(cls, puzzle, corner):
        if corner.sides.solved.closed:
            return False

        if len(corner.sides.unsolved) != 2:
            return False

        return True

    def apply(self):
        self.finished = True
        changed = False
        new_restrictions = set()

        constraints = self.constraints

        constraint = self.constraint()
        if constraint not in constraints:
            changed = True
            constraints.add(constraint)

        return changed, new_restrictions

    def constraint(self):
        unsolved_sides = sorted(self.corner.sides.unsolved)
        constraint = self.make_constraint(
            source=u'From corner two unsolved sides',
            constraint=(
                self.make_case(source=u'Corner solves to used', case=(
                    (side, True) for side in unsolved_sides
                )),
                self.make_case(source=u'Corner solves to unused', case=(
                    (side, False) for side in unsolved_sides
                )),
            ),
        )

        return constraint


# @PuzzleSolver.register_corner_restriction_class
class CornerConstraints(WithPuzzleConstraints, CornerRestriction):
    @classmethod
    def is_suitable(cls, puzzle, corner):
        return True

    def apply(self):
        self.finished = True
        changed = False
        new_restrictions = set()

        constraints = self.constraints
        constraint = self.constraint()
        if constraint not in constraints:
            changed = True
            constraints.add(constraint)

        return changed, new_restrictions

    def constraint(self):
        constraint = self.make_constraint(source=u'From corner', constraint=(
            self.make_case(
                source=u'Corner solves to unused',
                case=(
                    (side, False) for side in self.corner.sides
                ),
            ),
        ) + tuple(
            self.make_case(
                source=u'Corner uses sides %s' % str(side_pair),
                case=(
                    (side, side in side_pair) for side in self.corner.sides
                ),
            )
            for side_pair in itertools.combinations(self.corner.sides, 2)
        ))

        return constraint


@PuzzleSolver.register_puzzle_restriction_class
class PuzzleConstraints(WithPuzzleConstraints, PuzzleRestriction):
    @classmethod
    def is_suitable(cls, puzzle):
        return True

    def apply(self):
        changed = False
        new_restrictions = set()

        print '*' * 80
        print 'Starting with %s constraints' % len(self.constraints)

        self.add_solved_sides_constraint()
        changed |= self.remove_incompatible_cases()
        changed |= self.simplify_constraints()
        changed |= self.apply_resolved_constraints()
        self.remove_resolved_constraints()

        print 'Finishing with %s constraints' % len(self.constraints)

        self.finished = not self.constraints

        return changed, new_restrictions

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

        print 'Updating %s constraints' % len(changed_constraints)

        self.constraints.difference_update(set(changed_constraints.iterkeys()))
        self.constraints.update(set(changed_constraints.itervalues()))

        return changed

    def simplify_constraints(self):
        changed = False

        simplified_constraints = {
            simplified_constraint
            for constraint in self.constraints
            for simplified_constraint in self.simplify_constraint(constraint)
        }

        if simplified_constraints != self.constraints:
            print 'Simplified %s constraints' \
                  % len(simplified_constraints - self.constraints)
            changed = True
            self.constraints.difference_update(self.constraints)
            self.constraints.update(simplified_constraints)

        return changed

    def apply_resolved_constraints(self):
        changed = False
        resolved_constraints = self.get_resolved_constraints()
        print 'Applying %s resolved constraints' % len(resolved_constraints)
        for constraint in resolved_constraints:
            changed |= self.apply_resolved_constraint(constraint)

        return changed

    def remove_resolved_constraints(self):
        resolved_constraints = self.get_resolved_constraints()
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
        resolved_constraints = {
            constraint
            for constraint in self.constraints
            if len(constraint) == 1
            }
        return resolved_constraints

    def get_constraints_pairs(self):
        constraints_and_all_sides = [
            (constraint, self.get_sides_of_constraint(constraint))
            for constraint in self.constraints
        ]
        constraints_and_sides = [
            (constraint, side)
            for constraint, sides in constraints_and_all_sides
            for side in sides
        ]
        sides = {
            side
            for _, side in constraints_and_sides
        }
        constraints_by_side = {
            side: sorted({
                 constraint
                 for constraint, constraint_side
                 in constraints_and_sides
                 if constraint_side == side
             })
            for side in sides
        }
        constraint_pairs = {
            pair
            for constraints in constraints_by_side.itervalues()
            for pair in itertools.combinations(constraints, 2)
        }

        return constraint_pairs

    def get_sides_of_constraint(self, constraint):
        return {
            side
            for case in constraint
            for side in self.get_sides_of_case(case)
        }

    def get_sides_of_case(self, case):
        return {
            side
            for side, _ in case
        }

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
        sides = self.get_sides_of_case(case_1) & self.get_sides_of_case(case_2)
        if not sides:
            return True

        sides_case_1 = self.filter_case_sides(case_1, sides)
        sides_case_2 = self.filter_case_sides(case_2, sides)

        return sides_case_1 == sides_case_2

    def filter_case_sides(self, case, sides):
        return self.make_case(source=case.source, case=(
            fact
            for fact in case
            if fact.side in sides
        ))

    def filter_constraint_sides(self, constraint, sides):
        return self.make_constraint(source=constraint.source, constraint=(
            self.filter_case_sides(case, sides)
            for case in constraint
        ))

    def exclude_case_sides(self, case, sides):
        return self.make_case(source=case.source, case=(
            fact
            for fact in case
            if fact.side not in sides
        ))

    def exclude_constraint_sides(self, constraint, sides):
        return self.make_constraint(source=constraint.source, constraint=(
            self.exclude_case_sides(case, sides)
            for case in constraint
        ))

    def simplify_constraint(self, constraint):
        if len(constraint) == 1:
            return [constraint]

        common_sides_and_states = reduce(set.__and__, map(set, constraint))
        common_sides = self.get_sides_of_case(common_sides_and_states)

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
