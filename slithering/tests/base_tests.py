import unittest


class BaseTestBoard(unittest.TestCase):
    puzzle_class = None
    puzzle_kwargs = {}

    def setUp(self):
        self.puzzle = self.create_puzzle()

    def create_puzzle(self):
        return self.puzzle_class(**self.puzzle_kwargs)

    def test_can_create_a_puzzle(self):
        self.assertTrue(self.puzzle)


class BaseTestBoardCells(BaseTestBoard):
    minimum_cell_side_count = None
    maximum_cell_side_count = None

    def test_there_are_cells(self):
        self.assertTrue(self.puzzle.cells)

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

    def test_every_cell_has_as_many_sides_as_expected(self):
        cells_with_unexpected_number_of_sides = {
            cell
            for cell in self.puzzle.cells
            if not (
                self.minimum_cell_side_count
                <= len(cell.sides)
                <= self.maximum_cell_side_count
            )
        }
        self.assertFalse(cells_with_unexpected_number_of_sides)

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

    def test_some_cells_are_on_edge(self):
        some_cells_are_on_edge = any(
            cell.is_on_edge
            for cell in self.puzzle.cells
        )

        self.assertTrue(some_cells_are_on_edge)


class BaseTestBoardCellsNeighbours(BaseTestBoardCells):
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


class BaseTestBoardSides(BaseTestBoard):
    def test_there_are_sides(self):
        self.assertTrue(self.puzzle.sides)

    def test_all_sides_have_cells(self):
        sides_without_cells = {
            side
            for side in self.puzzle.sides
            if not side.cells
        }
        self.assertFalse(sides_without_cells)

    def test_all_sides_have_one_or_two_cells(self):
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

    def test_some_sides_are_on_edge(self):
        some_sides_are_on_edge = any(
            side.is_on_edge
            for side in self.puzzle.sides
        )

        self.assertTrue(some_sides_are_on_edge)


class BaseTestBoardSidesNeighbours(BaseTestBoardSides):
    def test_all_sides_have_neighbours(self):
        sides_without_neighbours = {
            side
            for side in self.puzzle.sides
            if not side.neighbours
        }
        self.assertFalse(sides_without_neighbours)

    def test_all_sides_neighbours_share_a_corner(self):
        sides_with_neighbours_that_dont_share_a_corner = {
            side
            for side in self.puzzle.sides
            if any(
                not side.corners & neighbour.corners
                for neighbour in side.neighbours
            )
        }
        self.assertFalse(sides_with_neighbours_that_dont_share_a_corner)


class BaseTestBoardCorners(BaseTestBoard):
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


class BaseAllBoardTests(
        BaseTestBoardCellsNeighbours,
        BaseTestBoardCells,
        BaseTestBoardSidesNeighbours,
        BaseTestBoardSides,
        BaseTestBoardCorners,
        BaseTestBoard):
    pass


class BaseTestRegularPolygonBoardCells(BaseTestBoardCells):
    @property
    def minimum_cell_side_count(self):
        return self.puzzle_class.cell_sides_count

    @property
    def maximum_cell_side_count(self):
        return self.puzzle_class.cell_sides_count


class BaseAllRegularPolygonBoardTests(
        BaseTestRegularPolygonBoardCells,
        BaseAllBoardTests):
    pass


class BaseTestPuzzle(unittest.TestCase):
    puzzle_class = None
    puzzle_kwargs = {}

    def setUp(self):
        self.puzzle = self.create_puzzle()
        self.puzzle.create_random_puzzle()

    def create_puzzle(self):
        return self.puzzle_class(**self.puzzle_kwargs)


class BaseTestPuzzleCells(BaseTestPuzzle):
    def test_there_are_closed_sides(self):
        self.assertTrue(self.puzzle.closed_sides)

    def test_some_cells_have_closed_sides(self):
        cells_with_closed_sides = {
            cell
            for cell in self.puzzle.cells
            if cell.closed_sides
        }
        self.assertTrue(cells_with_closed_sides)

    def test_there_are_internal_cells(self):
        self.assertTrue(self.puzzle.internal_cells)


class BaseAllPuzzleTests(
        BaseTestPuzzleCells,
        BaseTestPuzzle):
    pass