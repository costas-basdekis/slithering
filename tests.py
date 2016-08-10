import unittest

import square_puzzle


class TestSquarePuzzle(unittest.TestCase):
    def test_can_create_a_puzzle(self):
        puzzle = square_puzzle.SquarePuzzle(20, 20)
        print len(puzzle.cells), len(puzzle.internal_cells), len(puzzle.closed_sides)
        cell = list(puzzle.cells)[0]
        print len(cell.sides), len(cell.closed_sides)
        side = list(cell.sides)[0]
        print cell in side.cells, len(side.cells)
        print len(side.corners)
        corner = list(side.corners)[0]
        print side in corner.sides, len(corner.sides)
        puzzle.print_all_possible_hints()
        puzzle.print_cells_membership()
