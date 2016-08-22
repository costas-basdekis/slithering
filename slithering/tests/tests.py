from __future__ import absolute_import

import unittest

from slithering import square_puzzle, hexagonal_puzzle
from slithering.tests import base_tests


class TestSquareBoard(base_tests.BaseAllRegularPolygonBoardTests):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_cells_in_row_are_neighbours(self):
        cells_that_are_not_neighbours_in_row = {
            cell
            for y in xrange(self.puzzle.height)
            for cell, next_cell in (
                (self.puzzle.cells_by_key[(x, y)],
                 self.puzzle.cells_by_key[(x + 1, y)])
                for x in xrange(self.puzzle.width - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_row)

    def test_cells_in_column_are_neighbours(self):
        cells_that_are_not_neighbours_in_column = {
            cell
            for x in xrange(self.puzzle.width)
            for cell, next_cell in (
                (self.puzzle.cells_by_key[(x, y)],
                 self.puzzle.cells_by_key[(x, y + 1)])
                for y in xrange(self.puzzle.height - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_column)


class TestSquarePuzzle(base_tests.BaseAllPuzzleTests):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        self.puzzle.print_all_possible_hints()
        self.puzzle.print_cells_membership()


class BadTestSquarePuzzle1(base_tests.BaseTestPuzzleCreation):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {
        'width': 20,
        'height': 20,
        'seed': 1943095418764571628,
    }


class BadTestSquarePuzzle2(base_tests.BaseTestPuzzleCreation):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {
        'width': 20,
        'height': 20,
        'seed': 7379886256663183349,
    }


class TestHexagonalBoard(base_tests.BaseAllRegularPolygonBoardTests):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_cells_in_row_are_neighbours(self):
        cells_that_are_not_neighbours_in_row = {
            cell
            for y in xrange(self.puzzle.height)
            for cell, next_cell in (
                (self.puzzle.cells_by_key[(x, y)],
                 self.puzzle.cells_by_key[(x + 1, y)])
                for x in xrange(self.puzzle.width - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_row)

    def test_cells_in_column_right_are_neighbours(self):
        cells_that_are_not_neighbours_in_column = {
            cell
            for x in xrange(self.puzzle.width)
            for cell, next_cell in (
                (self.puzzle.cells_by_key[(x, y)],
                 self.puzzle.cells_by_key[(x, y + 1)])
                for y in xrange(self.puzzle.height - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_column)

    def test_cells_in_column_left_are_neighbours(self):
        cells_that_are_not_neighbours_in_column = {
            cell
            for x in xrange(1, self.puzzle.width)
            for cell, next_cell in (
                (self.puzzle.cells_by_key[(x, y)],
                 self.puzzle.cells_by_key[(x - (1 if (y % 2 == 0) else 0), y + 1)])
                for y in xrange(self.puzzle.height - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_column)


class BadTestHexagonalBoard1(base_tests.BaseTestPuzzleCreation):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {
        'width': 20,
        'height': 20,
        'seed': 6527052551791180456,
    }


class TestHexagonalPuzzle(base_tests.BaseAllPuzzleTests):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        self.puzzle.print_all_possible_hints()
        self.puzzle.print_cells_membership()


if __name__ == '__main__':
    unittest.main()
