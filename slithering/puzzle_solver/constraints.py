from collections import namedtuple

from slithering.puzzle_solver.sub_solvers import PuzzleSubSolver
from slithering.utils import cached_property


class WithPuzzleConstraints(PuzzleSubSolver):
    @property
    def constraints(self):
        if not hasattr(self.puzzle, 'constraints'):
            self.puzzle.constraints = Constraints()

        return self.puzzle.constraints

    def make_constraint(self, constraint, source=None):
        return Constraint(constraint, source=source)

    def make_case(self, case, source=None):
        return Case(case, source=source)

    def make_fact(self, fact, source=None):
        return Fact(*fact, source=source)


class Constraints(set):
    def __init__(self):
        super(Constraints, self).__init__()
        self.by_side = {}

    def _update(self, values):
        for value in values:
            self._add(value)

    def _add(self, value):
        for side in value.sides:
            self.by_side.setdefault(side, set()).add(value)

    def _difference_update(self, values):
        for value in values:
            self._remove(value)

    def _remove(self, value):
        for side in value.sides:
            self.by_side[side].discard(value)

    def add(self, value):
        super(Constraints, self).add(value)
        self._add(value)

    def update(self, values):
        values = tuple(values)
        super(Constraints, self).update(values)
        self._update(values)

    def remove(self, value):
        super(Constraints, self).remove(value)
        self._remove(value)

    def difference_update(self, values):
        values = tuple(values)
        super(Constraints, self).difference_update(values)
        self._difference_update(values)


class Constraint(frozenset):
    def __init__(self, constraint, source=None):
        if source is None:
            if isinstance(constraint, Constraint):
                source = constraint.source
        self.source = source
        super(Constraint, self).__init__(constraint)

    def __str__(self):
        return u'Constraint(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )

    @cached_property
    def sides(self):
        return frozenset(
            side
            for case in self
            for side in case.sides
        )

    @cached_property
    def common_facts(self):
        return reduce(frozenset.__and__, map(frozenset, self))

    @cached_property
    def common_facts_sides(self):
        return frozenset(side for side, _ in self.common_facts)

    def simplified(self):
        if len(self) == 1:
            return [self]

        common_sides = self.common_facts_sides
        if not common_sides:
            return [self]
        if common_sides == self.sides:
            return [self]

        simplified_constraint = \
            self.excluding_sides(common_sides)
        resolved_constraint = \
            self.filtering_sides(common_sides)

        simplified_constraints = \
            filter(None, [simplified_constraint, resolved_constraint])

        assert simplified_constraints, \
            "Simplifying constraint %s ended up in incompatibility" \
            % str(self)

        return simplified_constraints

    def being_compatible_with(self, *others):
        return Constraint(
            (
                case_1
                for case_1 in self
                if all(
                    case_1.is_compatible_with_constraint(other)
                    for other in others
                )
            ),
            source=self.source,
        )

    def excluding_sides(self, sides):
        if not sides:
            return self

        return Constraint((
            case.excluding_sides(sides)
            for case in self
        ), source=self.source)

    def filtering_sides(self, sides):
        if self.sides == sides:
            return self

        return Constraint((
            case.filtering_sides(sides)
            for case in self
        ), source=self.source)


class Case(frozenset):
    def __init__(self, case, source=None):
        if source is None:
            if isinstance(case, Case):
                source = case.source
        self.source = source
        super(Case, self).__init__(case)

    def __str__(self):
        return u'Case(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )

    @cached_property
    def sides(self):
        return frozenset(
            side
            for side, _ in self
        )

    def excluding_sides(self, sides):
        if not sides:
            return self

        return Case((
            (side, is_closed)
            for (side, is_closed) in self
            if side not in sides
        ), source=self.source)

    def filtering_sides(self, sides):
        if self.sides == sides:
            return self

        return Case((
            (side, is_closed)
            for (side, is_closed) in self
            if side in sides
        ), source=self.source)

    def sides_dict(self, sides):
        return {
            side: is_closed
            for side, is_closed in self
            if side in sides
        }

    def is_compatible_with(self, other):
        sides = self.sides & other.sides
        if not sides:
            return True

        if sides == self.sides == other.sides:
            self_sides = self.sides
            other_sides = other.sides
        else:
            self_sides = self.sides_dict(sides)
            other_sides = other.sides_dict(sides)

        return self_sides == other_sides

    def is_compatible_with_constraint(self, constraint):
        return any(
            self.is_compatible_with(case)
            for case in constraint
        )


class Fact(namedtuple('Fact', ['side', 'is_closed'])):
    def __init__(self, *values, **kwargs):
        kwargs.setdefault('source', None)
        self.source, = kwargs.values()
        super(Fact, self).__init__(*values)