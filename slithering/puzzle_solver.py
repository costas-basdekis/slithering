class PuzzleSolver(object):
    cell_restriction_classes = []
    side_restriction_classes = []
    corner_restriction_classes = []

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

        restrictions.update(self.find_new_cell_restrictions())
        restrictions.update(self.find_new_side_restrictions())
        restrictions.update(self.find_new_corner_restrictions())

        return restrictions

    def find_new_cell_restrictions(self):
        return self.create_suitable_puzzle_restrictions(
            self.puzzle.cells, self.cell_restriction_classes)

    def find_new_side_restrictions(self):
        return self.create_suitable_puzzle_restrictions(
            self.puzzle.sides, self.side_restriction_classes)

    def find_new_corner_restrictions(self):
        return self.create_suitable_puzzle_restrictions(
            self.puzzle.corners, self.corner_restriction_classes)

    def create_suitable_puzzle_restrictions(self, items, restriction_classes):
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


class PuzzleRestriction(Restriction):
    def __init__(self, puzzle):
        super(PuzzleRestriction, self).__init__()
        self.puzzle = puzzle


class CellRestriction(PuzzleRestriction):
    def __init__(self, puzzle, cell):
        super(CellRestriction, self).__init__(puzzle)
        self.cell = cell

    def __hash__(self):
        return hash((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, puzzle, cell):
        return super(CellRestriction, cls).is_suitable(puzzle=puzzle, cell=cell)


class CornerRestriction(PuzzleRestriction):
    def __init__(self, puzzle, corner):
        super(CornerRestriction, self).__init__(puzzle)
        self.corner = corner

    def __hash__(self):
        return hash((type(self), self.corner.key))

    @classmethod
    def is_suitable(cls, puzzle, corner):
        return super(CornerRestriction, cls)\
            .is_suitable(puzzle=puzzle, corner=corner)


@PuzzleSolver.register_cell_restriction_class
class ZeroHintRestriction(CellRestriction):
    """Cell hint = 0"""

    @classmethod
    def is_suitable(cls, puzzle, cell):
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
class CellSolvedEdgeSideRestriction(CellRestriction):
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
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
class CellSolvedSideRestriction(CellRestriction):
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
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


@PuzzleSolver.register_corner_restriction_class
class CornerSingleUnsolvedSide(CornerRestriction):
    @classmethod
    def is_suitable(cls, puzzle, corner):
        if len(corner.unsolved_sides) != 1:
            return False

        return True

    def apply(self):
        changed = False
        new_restrictions = set()
        self.finished = True

        if not self.corner.unsolved_sides:
            return changed, new_restrictions

        unsolved_side, = self.corner.unsolved_sides

        closed_solved_sides = \
            self.corner.closed_sides & self.corner.solved_sides
        if len(closed_solved_sides) > 1:
            return changed, new_restrictions

        changed = True

        if closed_solved_sides:
            unsolved_side.solved_is_closed = True
        else:
            unsolved_side.solved_is_closed = False

        return changed, new_restrictions
