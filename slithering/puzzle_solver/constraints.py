from collections import namedtuple

from slithering.puzzle_solver.restrictions import PuzzleRestriction


class WithPuzzleConstraints(PuzzleRestriction):
    @property
    def constraints(self):
        if not hasattr(self.puzzle, 'constraints'):
            self.puzzle.constraints = set()

        return self.puzzle.constraints

    def make_constraint(self, constraint, source=None):
        return Constraint(constraint, source=source)

    def make_case(self, case, source=None):
        return Case(case, source=source)

    def make_fact(self, fact, source=None):
        return Fact(*fact, source=source)


class Constraint(frozenset):
    def __init__(self, constraint, source=None):
        if source is None:
            if isinstance(constraint, Constraint):
                source = constraint.source
        self.source = source
        super(Constraint, self).__init__(constraint)
        self.sides = self.calculate_sides()
        self.common_facts = self.calculate_common_facts()
        self.common_facts_sides = self.calculate_common_facts_sides()

    def __str__(self):
        return u'Constraint(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )

    def calculate_sides(self):
        return frozenset(
            side
            for case in self
            for side in case
        )

    def calculate_common_facts(self):
        return reduce(frozenset.__and__, map(frozenset, self))

    def calculate_common_facts_sides(self):
        return frozenset(side for side, _ in self.calculate_common_facts())


class Case(frozenset):
    def __init__(self, case, source=None):
        if source is None:
            if isinstance(case, Case):
                source = case.source
        self.source = source
        super(Case, self).__init__(case)
        self.sides = self.calculate_sides()

    def __str__(self):
        return u'Case(%s\n%s\n)' % (
            u'source=%s' % self.source if self.source else '',
            u'\n'.join(
                u'    %s' % line
                for line in u'\n'.join(map(str, self)).split('\n')
            )
        )

    def calculate_sides(self):
        return frozenset(
            side
            for side, _ in self
        )


class Fact(namedtuple('Fact', ['side', 'is_closed'])):
    def __init__(self, *values, **kwargs):
        kwargs.setdefault('source', None)
        self.source, = kwargs.values()
        super(Fact, self).__init__(*values)