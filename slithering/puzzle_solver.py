class PuzzleSolver(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.restrictions = self.create_initial_restrictions()
        self.all_restrictions = set(self.restrictions)

    def create_initial_restrictions(self):
        return {
            ZeroHintRestriction(cell)
            for cell in self.puzzle.cells
            if cell.hint_is_given and (cell.hint == 0)
        }

    def find_new_restrictions(self):
        restrictions = set()
        for cell in self.puzzle.cells:
            if cell.is_on_edge and not cell.solved:
                if any(side.is_on_edge and side.solved for side in cell.sides):
                    restrictions.add(CellSolvedEdgeSideRestriction(cell))
            if not cell.solved:
                if any(side.solved and any(cell.solved for cell in side.cells) for side in cell.sides):
                    restrictions.add(CellSolvedSideRestriction(cell))

        return restrictions

    def apply(self):
        changed = False
        new_restrictions = set()
        for restriction in self.restrictions:
            restriction_changed, restriction_new_restrictions = \
                restriction.apply()
            if restriction_changed:
                changed = True
                new_restrictions |= restriction_new_restrictions

        new_restrictions |= self.find_new_restrictions()

        # Only add restrictions that we never encountered before
        new_restrictions -= self.all_restrictions
        self.all_restrictions |= new_restrictions

        unfinished_restrictions = {
            restriction
            for restriction in self.restrictions
            if not restriction.finished
        }
        self.restrictions = unfinished_restrictions | new_restrictions

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
        It should change `self.finished` to `True`, if it can make no further
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


class CellSolvedEdgeSideRestriction(Restriction):
    """An edge side of cell is solved"""
    def __init__(self, cell):
        super(CellSolvedEdgeSideRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

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

        self.cell.solved = True
        self.cell.solved_is_internal = is_internal

        return changed, new_restrictions


class CellSolvedSideRestriction(Restriction):
    """An edge side of cell is solved"""
    def __init__(self, cell):
        super(CellSolvedSideRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

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

        self.cell.solved = True
        self.cell.solved_is_internal = is_internal

        return changed, new_restrictions
