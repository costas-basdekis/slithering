class PuzzleSolver(object):
    puzzle_sub_solver_classes = []
    cell_sub_solver_classes = []
    side_sub_solver_classes = []
    corner_sub_solver_classes = []

    @classmethod
    def register_puzzle_sub_solver_class(cls, sub_solver_class):
        cls.puzzle_sub_solver_classes.append(sub_solver_class)
        return sub_solver_class

    @classmethod
    def register_cell_sub_solver_class(cls, sub_solver_class):
        cls.cell_sub_solver_classes.append(sub_solver_class)
        return sub_solver_class

    @classmethod
    def register_side_sub_solver_class(cls, sub_solver_class):
        cls.side_sub_solver_classes.append(sub_solver_class)
        return sub_solver_class

    @classmethod
    def register_corner_sub_solver_class(cls, sub_solver_class):
        cls.corner_sub_solver_classes.append(sub_solver_class)
        return sub_solver_class

    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.sub_solvers = self.create_sub_solvers()
        self.all_sub_solvers = frozenset(self.sub_solvers)

    def create_sub_solvers(self):
        sub_solvers = frozenset()

        sub_solvers |= self.create_puzzle_sub_solvers()
        sub_solvers |= self.create_cell_sub_solvers()
        sub_solvers |= self.create_side_sub_solvers()
        sub_solvers |= self.create_corner_sub_solvers()

        return sub_solvers

    def create_puzzle_sub_solvers(self):
        return self.create_suitable_puzzle_sub_solvers(
            self.puzzle_sub_solver_classes)

    def create_cell_sub_solvers(self):
        return self.create_suitable_puzzle_item_sub_solvers(
            self.puzzle.cells, self.cell_sub_solver_classes)

    def create_side_sub_solvers(self):
        return self.create_suitable_puzzle_item_sub_solvers(
            self.puzzle.sides, self.side_sub_solver_classes)

    def create_corner_sub_solvers(self):
        return self.create_suitable_puzzle_item_sub_solvers(
            self.puzzle.corners, self.corner_sub_solver_classes)

    def create_suitable_puzzle_sub_solvers(self, sub_solver_classes):
        return frozenset(
            sub_solver_class(self, self.puzzle)
            for sub_solver_class in sub_solver_classes
        )

    def create_suitable_puzzle_item_sub_solvers(
            self, items, sub_solver_classes):
        return frozenset(
            sub_solver_class(self, self.puzzle, item)
            for item in items
            for sub_solver_class in sub_solver_classes
        )

    def apply(self):
        changed = False

        for sub_solver in self.sub_solvers:
            if sub_solver.is_suitable():
                changed |= sub_solver.apply()

        self.sub_solvers = frozenset(
            sub_solver
            for sub_solver in self.sub_solvers
            if not sub_solver.finished
        )

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