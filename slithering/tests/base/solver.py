from slithering.tests.base.base import BaseSolverTestCase


class BaseTestPuzzleSolver(BaseSolverTestCase):
    def test_can_solve_puzzle(self):
        self.assertTrue(self.puzzle.solved)
