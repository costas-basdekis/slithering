import unittest

import hexagonal_puzzle
import square_puzzle
import base_tests


class TestSquareBoard(base_tests.BaseAllBoardTests):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}
    minimum_cell_side_count = 4
    maximum_cell_side_count = 4


class TestSquarePuzzle(base_tests.BaseAllPuzzleTests):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        self.puzzle.print_all_possible_hints()
        self.puzzle.print_cells_membership()


class TestHexagonalBoard(base_tests.BaseAllBoardTests):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}
    minimum_cell_side_count = 6
    maximum_cell_side_count = 6


class TestHexagonalPuzzle(base_tests.BaseAllPuzzleTests):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        self.puzzle.print_all_possible_hints()
        self.puzzle.print_cells_membership()


if __name__ == '__main__':
    unittest.main()
