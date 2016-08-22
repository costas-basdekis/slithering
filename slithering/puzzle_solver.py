class PuzzleSolver(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.restrictions = self.create_initial_restrictions()

    def create_initial_restrictions(self):
        return {
            ZeroHintRestriction(cell)
            for cell in self.puzzle.cells
            if cell.hint_is_given and (cell.hint == 0)
        }

    def apply(self):
        changed = False
        new_restrictions = set()
        for restriction in self.restrictions:
            restriction_changed, restriction_new_restrictions = \
                restriction.apply()
            if restriction_changed:
                changed = True
                new_restrictions |= restriction_new_restrictions

        self.restrictions = {
            restriction
            for restriction in self.restrictions
            if not restriction.finished
        } | new_restrictions

        return changed

    def solve(self):
        while self.apply():
            continue


class Restriction(object):
    """A restriction that can make changes, or create new hints"""
    def __init__(self):
        self.finished = False

    def __hash__(self):
        raise NotImplementedError()

    def apply(self):
        """
        Apply the restriction further, if possible.
        It should return if it managed to make any changes, or create any new
        hints, and the any new hints it could create.
        It should change `self.finished` to `True`, if it can make no furhter
        changes.
        """
        raise NotImplementedError()


class ZeroHintRestriction(Restriction):
    """Cell hint = 0"""
    def __init__(self, cell):
        super(ZeroHintRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

    def apply(self):
        changed = False
        new_restrictions = set()

        for side in self.cell.sides:
            assert not side.solved or not side.solved_is_closed
            if (side.solved, side.solved_is_closed) != (True, False):
                changed = True
                side.solved, side.solved_is_closed = True, False

        self.finished = True

        return changed, new_restrictions
