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