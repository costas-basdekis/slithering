import unittest

import square_puzzle
import hexagonal_puzzle


class BaseTestPuzzle(object):
    puzzle_class = None
    puzzle_kwargs = {}

    def create_puzzle(self):
        return self.puzzle_class(**self.puzzle_kwargs)

    def test_can_create_a_puzzle(self):
        puzzle = self.create_puzzle()

        print 'Cell count:', len(puzzle.cells)
        print 'Internal cell count:', len(puzzle.internal_cells)
        print 'Closed sides count:', len(puzzle.closed_sides)
        cell = list(puzzle.cells)[0]
        print 'Cell sides count:', len(cell.sides)
        print 'Cell closed sides count:', len(cell.closed_sides)
        side = list(cell.sides)[0]
        print 'Cell is part of one of it\'s sides:', cell in side.cells,
        print 'Side cells count:', len(side.cells)
        print 'Side corners count:', len(side.corners)
        corner = list(side.corners)[0]
        print 'Side is part of it\'s corner:', side in corner.sides,
        print 'Corner sides count:', len(corner.sides)


class TestSquarePuzzle(BaseTestPuzzle, unittest.TestCase):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        puzzle = self.create_puzzle()

        puzzle.print_all_possible_hints()
        puzzle.print_cells_membership()


class TestHexagonalPuzzle(BaseTestPuzzle, unittest.TestCase):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}


if __name__ == '__main__':
    unittest.main()
