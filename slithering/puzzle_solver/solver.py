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