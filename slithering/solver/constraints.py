from collections import namedtuple

from slithering.solver.sub_solvers import PuzzleSubSolver


class WithPuzzleConstraints(PuzzleSubSolver):
    @property
    def constraint_solver(self):
        if not hasattr(self.solver, 'constraint_solver'):
            from slithering.solver.constraint_solver import ConstraintSolver
            self.solver.constraint_solver = \
                ConstraintSolver(self.puzzle, debug=True)

        return self.solver.constraint_solver

    @property
    def constraints(self):
        return self.constraint_solver.constraints


class Constraints(set):
    def __init__(self):
        super(Constraints, self).__init__()
        self.by_side = {}

    def _update(self, values):
        return (
            self._add(value)
            for value in values
        )

    def _add(self, value):
        others = self.sharing_sides_with(value)
        if others:
            value = value.being_compatible_with(*others)
            self._reduce_existing(others, value)
        map(self._add_to_sides, value.simplified())

        return value

    def _add_to_sides(self, value):
        for side in value.sides:
            self.by_side.setdefault(side, set()).add(value)

    def sharing_sides_with(self, constraint):
        others = frozenset(
            other
            for side in constraint.sides
            if side in self.by_side
            for other in self.by_side[side]
        )
        return others

    def _reduce_existing(self, others, value):
        compatible_others = frozenset(
            simplified
            for other in others
            for simplified in other.being_compatible_with(value).simplified()
        )
        removed_others = others - compatible_others
        new_others = compatible_others - others
        if removed_others:
            self.difference_update(removed_others)
        if new_others:
            self.update(new_others)

    def _difference_update(self, values):
        for value in values:
            self._remove(value)

    def _remove(self, value):
        for side in value.sides:
            self.by_side[side].discard(value)

    def add(self, value):
        value = self._add(value)
        super(Constraints, self).add(value)

    def update(self, values):
        values = self._update(values)
        super(Constraints, self).update(values)

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
        self.sides = frozenset(
            side
            for case in self
            for side in case.sides
        )
        self.common_facts = reduce(frozenset.__and__, map(frozenset, self))
        self.common_facts_sides = \
            frozenset(side for side, _ in self.common_facts)

    def __str__(self):
        return u'Constraint(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )

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
                case
                for case in self
                if all(
                    case.is_compatible_with_constraint(other)
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
        self.sides_dict = {
            side: is_closed
            for side, is_closed in self
        }
        self.sides = frozenset(self.sides_dict)

    def __str__(self):
        return u'Case(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
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

    def is_compatible_with(self, other):
        sides = self.sides & other.sides
        if not sides:
            return True

        return all(
            self.sides_dict[side] == other.sides_dict[side]
            for side in sides
        )

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
