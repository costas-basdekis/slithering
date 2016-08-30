class SubSolver(object):
    """A sub-solver that can make changes, or create new sub-solvers"""
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
        """Check whether the sub-solver can be created from the arguments"""
        raise NotImplementedError()

    def apply(self):
        """
        Apply the sub-solver further, if possible.
        It should return if it managed to make any changes, or create any new
        hints, and the any new hints it could create.
        It should change `self.finished` to `True`, if it can make no further
        changes.
        """
        raise NotImplementedError()


class PuzzleSubSolver(SubSolver):
    def __init__(self, puzzle):
        super(PuzzleSubSolver, self).__init__()
        self.puzzle = puzzle

    def hash_key(self):
        return tuple((type(self), self.puzzle))

    @classmethod
    def is_suitable(cls, puzzle):
        raise NotImplementedError()


class CellSubSolver(PuzzleSubSolver):
    def __init__(self, puzzle, cell):
        super(CellSubSolver, self).__init__(puzzle)
        self.cell = cell

    def hash_key(self):
        return tuple((type(self), self.cell.key))

    @classmethod
    def is_suitable(cls, puzzle, cell):
        raise NotImplementedError()


class CornerSubSolver(PuzzleSubSolver):
    def __init__(self, puzzle, corner):
        super(CornerSubSolver, self).__init__(puzzle)
        self.corner = corner

    def hash_key(self):
        return tuple((type(self), self.corner.key))

    @classmethod
    def is_suitable(cls, puzzle, corner):
        return super(CornerSubSolver, cls)\
            .is_suitable(puzzle=puzzle, corner=corner)