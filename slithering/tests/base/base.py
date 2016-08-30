from unittest import TestCase

from slithering import solver


class BoardBase(object):
    board_class = None
    board_kwargs = {}

    def create_board(self):
        return self.board_class(**self.board_kwargs)


class PuzzleBase(BoardBase):
    puzzle_class = None
    puzzle_kwargs = {}

    def create_puzzle(self, board):
        return self.puzzle_class(board=board, **self.puzzle_kwargs)


class SolverBase(PuzzleBase):
    solver_class = solver.PuzzleSolver

    def create_solver(self, puzzle):
        return self.solver_class(puzzle)


class PuzzleSVGBase(PuzzleBase):
    puzzle_svg_kwargs = {}


class BaseBoardTestCase(BoardBase, TestCase):
    def setUp(self):
        super(BaseBoardTestCase, self).setUp()
        self.board = self.create_board()


class BasePuzzleTestCase(PuzzleBase, BaseBoardTestCase):
    def setUp(self):
        super(BasePuzzleTestCase, self).setUp()
        self.puzzle = self.create_puzzle(self.board)
        print 'Seed: #%s, %s' % (self.puzzle.seed, type(self.puzzle).__name__)
        self.puzzle.create_random_puzzle()


class BaseSolverTestCase(SolverBase, BasePuzzleTestCase):
    def setUp(self):
        super(BaseSolverTestCase, self).setUp()
        self.solver = self.create_solver(self.puzzle)
        self.solver.solve()


class BasePuzzleSVGTestCase(PuzzleSVGBase, BasePuzzleTestCase):
    pass
