import unittest

import square_puzzle
import hexagonal_puzzle


class BaseTestPuzzle(object):
    puzzle_class = None
    puzzle_kwargs = {}

    def setUp(self):
        self.puzzle = self.create_puzzle()

    def create_puzzle(self):
        return self.puzzle_class(**self.puzzle_kwargs)

    def test_can_create_a_puzzle(self):
        self.assertTrue(self.puzzle)


class BaseTestPuzzleCells(BaseTestPuzzle):
    def test_there_are_cells(self):
        self.assertTrue(self.puzzle.cells)

    def test_there_are_internal_cells(self):
        self.assertTrue(self.puzzle.internal_cells)

    def test_there_are_closed_sides(self):
        self.assertTrue(self.puzzle.closed_sides)

    def test_every_cell_has_sides(self):
        cells_without_sides = {
            cell
            for cell in self.puzzle.cells
            if not cell.sides
        }
        self.assertFalse(cells_without_sides)

    def test_every_cell_has_at_least_three_sides(self):
        cells_with_too_few_sides = {
            cell
            for cell in self.puzzle.cells
            if len(cell.sides) < 3
        }
        self.assertFalse(cells_with_too_few_sides)

    def test_some_cells_have_closed_sides(self):
        cells_with_closed_sides = {
            cell
            for cell in self.puzzle.cells
            if cell.closed_sides
        }
        self.assertTrue(cells_with_closed_sides)

    def test_all_cells_are_part_of_all_their_sides(self):
        cells_that_are_not_part_of_some_of_their_sides = {
            cell
            for cell in self.puzzle.cells
            if any(
                cell not in side.cells
                for side in cell.sides
            )
        }
        self.assertFalse(cells_that_are_not_part_of_some_of_their_sides)


class BaseTestPuzzleCellsNeighbours(BaseTestPuzzleCells):
    def test_all_cells_have_neighbours(self):
        cells_without_neighbours = {
            cell
            for cell in self.puzzle.cells
            if not cell.neighbours
        }
        self.assertFalse(cells_without_neighbours)

    def test_all_cells_neighbours_share_a_side(self):
        cells_with_neighbours_that_dont_share_a_side = {
            cell
            for cell in self.puzzle.cells
            if any(
                not cell.sides & neighbour.sides
                for neighbour in cell.neighbours
            )
        }
        self.assertFalse(cells_with_neighbours_that_dont_share_a_side)

    def test_all_cells_neighbours_are_at_most_as_many_as_sides(self):
        cells_with_more_neighbours_than_sides = {
            cell
            for cell in self.puzzle.cells
            if len(set(cell.neighbours)) > len(set(cell.sides))
        }
        self.assertFalse(cells_with_more_neighbours_than_sides)

    def test_all_cells_have_adjacent_cells(self):
        cells_without_adjacent_cells = {
            cell
            for cell in self.puzzle.cells
            if not cell.adjacent_cells
        }
        self.assertFalse(cells_without_adjacent_cells)

    def test_all_cells_share_a_corner_with_all_adjacent_cells(self):
        cells_with_adjacent_cells_that_dont_share_a_corner = {
            cell
            for cell in self.puzzle.cells
            if any(
                not cell.corners & adjacent_cell.corners
                for adjacent_cell in cell.adjacent_cells
            )
        }
        self.assertFalse(cells_with_adjacent_cells_that_dont_share_a_corner)

    def test_all_cells_can_order_adjacent_cells(self):
        for cell in self.puzzle.cells:
            self.assertTrue(cell.ordered_adjacent_cells)

    def test_all_cells_ordered_adjacent_cells_are_all_adjacent_cells(self):
        for cell in self.puzzle.cells:
            self.assertEquals(set(cell.ordered_adjacent_cells),
                              set(cell.adjacent_cells))

    def test_all_cells_adjacent_cells_share_a_corner_with_cell(self):
        cells_with_adjacent_cells_that_dont_share_a_corner_with_cell = {
            cell
            for cell in self.puzzle.cells
            if any(
                not cell.corners & adjacent_cell.corners
                for adjacent_cell in cell.adjacent_cells
            )
        }
        self.assertFalse(
            cells_with_adjacent_cells_that_dont_share_a_corner_with_cell)

    def test_all_cells_ordered_adjacent_cells_share_a_side_in_order(self):
        cells_with_adjacent_cells_that_dont_share_a_side_in_order = {
            cell
            for cell, ordered_adjacent_cells in (
                (cell, cell.ordered_adjacent_cells)
                for cell in self.puzzle.cells
            )
            if any(
                not adjacent_cell.sides & next_adjacent_cell.sides
                for adjacent_cell, next_adjacent_cell
                # The last one might not be continuous with the first
                in zip(ordered_adjacent_cells, ordered_adjacent_cells[1:])
            )
        }
        self.assertFalse(
            cells_with_adjacent_cells_that_dont_share_a_side_in_order)

    def test_all_cells_ordered_adjacent_cells_are_neighbours_in_order(self):
        cells_with_adjacent_cells_that_are_not_neighbours_in_order = {
            cell
            for cell, ordered_adjacent_cells in (
                (cell, cell.ordered_adjacent_cells)
                for cell in self.puzzle.cells
            )
            if any(
                adjacent_cell not in next_adjacent_cell.neighbours
                for adjacent_cell, next_adjacent_cell
                # The last one might not be continuous with the first
                in zip(ordered_adjacent_cells, ordered_adjacent_cells[1:])
            )
        }
        self.assertFalse(
            cells_with_adjacent_cells_that_are_not_neighbours_in_order)


class BaseTestPuzzleSides(BaseTestPuzzle):
    def test_there_are_sides(self):
        self.assertTrue(self.puzzle.sides)

    def test_all_sides_have_cells(self):
        sides_without_cells = {
            side
            for side in self.puzzle.sides
            if not side.cells
        }
        self.assertFalse(sides_without_cells)

    def test_all_sides_one_or_two_cells(self):
        sides_with_not_one_or_two_cells = {
            side
            for side in self.puzzle.sides
            if len(side.cells) not in [1, 2]
        }
        self.assertFalse(sides_with_not_one_or_two_cells)

    def test_all_sides_are_part_of_all_their_cells(self):
        sides_that_are_not_part_of_some_of_their_cells = {
            side
            for side in self.puzzle.sides
            if any(
                side not in cell.sides
                for cell in side.cells
            )
        }
        self.assertFalse(sides_that_are_not_part_of_some_of_their_cells)

    def test_all_sides_have_corners(self):
        sides_without_corners = {
            side
            for side in self.puzzle.sides
            if not side.corners
        }
        self.assertFalse(sides_without_corners)

    def test_all_sides_are_parts_of_their_corners(self):
        sides_that_are_not_part_of_some_of_their_corners = {
            side
            for side in self.puzzle.sides
            if any(
                side not in corner.sides
                for corner in side.corners
            )
        }
        self.assertFalse(sides_that_are_not_part_of_some_of_their_corners)

    def test_there_are_corners(self):
        self.assertTrue(self.puzzle.corners)

    def test_all_corners_have_sides(self):
        corners_without_sides = {
            corner
            for corner in self.puzzle.corners
            if not corner.sides
        }
        self.assertFalse(corners_without_sides)

    def test_all_corners_have_at_least_two_sides(self):
        corners_with_too_few_sides = {
            corner
            for corner in self.puzzle.corners
            if len(corner.sides) < 2
        }
        self.assertFalse(corners_with_too_few_sides)


class BaseAllPuzzleTests(
        BaseTestPuzzleCellsNeighbours,
        BaseTestPuzzleCells,
        BaseTestPuzzleSides,
        BaseTestPuzzle):
    pass


class TestSquarePuzzle(BaseAllPuzzleTests, unittest.TestCase):
    puzzle_class = square_puzzle.SquarePuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}

    def test_debug_info(self):
        puzzle = self.create_puzzle()

        puzzle.print_all_possible_hints()
        puzzle.print_cells_membership()


class TestHexagonalPuzzle(BaseAllPuzzleTests, unittest.TestCase):
    puzzle_class = hexagonal_puzzle.HexagonalPuzzle
    puzzle_kwargs = {'width': 20, 'height': 20}


if __name__ == '__main__':
    unittest.main()
