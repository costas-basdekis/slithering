class PuzzleSolver(object):
    cell_restrictions_classes = []

    @classmethod
    def register_cell_restriction_class(cls, restriction_class):
        cls.cell_restrictions_classes.append(restriction_class)
        return restriction_class

    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.restrictions = self.find_new_restrictions()
        self.all_restrictions = set(self.restrictions)

    def find_new_restrictions(self):
        restrictions = set()
        for cell in self.puzzle.cells:
            for restriction_class in self.cell_restrictions_classes:
                if restriction_class.is_suitable(cell):
                    restrictions.add(restriction_class(cell))

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


@PuzzleSolver.register_cell_restriction_class
class ZeroHintRestriction(Restriction):
    """Cell hint = 0"""
    def __init__(self, cell):
        super(ZeroHintRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, cell):
        if not cell.hint_is_given:
            return False
        if cell.hint != 0:
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()

        for side in self.cell.sides:
            if not side.solved:
                changed = True
                side.solved_is_closed = False

        self.finished = True

        return changed, new_restrictions


@PuzzleSolver.register_cell_restriction_class
class CellSolvedEdgeSideRestriction(Restriction):
    """An edge side of cell is solved"""
    def __init__(self, cell):
        super(CellSolvedEdgeSideRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, cell):
        if cell.solved:
            return False

        if not cell.is_on_edge:
            return False

        solved_on_edge_sides = cell.solved_sides & cell.on_edge_sides
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
class CellSolvedSideRestriction(Restriction):
    """An edge side of cell is solved"""
    def __init__(self, cell):
        super(CellSolvedSideRestriction, self).__init__()
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, cell):
        if cell.solved:
            return False

        solved_sides_with_solved_cell = {
            side
            for side in cell.solved_sides
            if any(side.solved_cells)
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
