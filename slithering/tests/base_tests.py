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


class BaseTestBoardCellsSides(BaseTestBoardCells):
    def test_all_cells_have_sides(self):
        cells_without_sides = {
            cell
            for cell in self.puzzle.cells
            if not cell.sides
        }
        self.assertFalse(cells_without_sides)

    def test_all_cells_sides_share_a_corner(self):
        cells_with_sides_that_dont_share_a_corner = {
            cell
            for cell in self.puzzle.cells
            if any(
                not cell.corners & side.corners
                for side in cell.sides
            )
        }
        self.assertFalse(cells_with_sides_that_dont_share_a_corner)

    def test_all_cells_sides_are_as_many_as_corners(self):
        cells_with_different_count_sides_than_corners = {
            cell
            for cell in self.puzzle.cells
            if len(set(cell.sides)) != len(set(cell.corners))
        }
        self.assertFalse(cells_with_different_count_sides_than_corners)

    def test_all_cells_can_order_sides(self):
        cells_that_cannot_order_sides = {
            cell
            for cell in self.puzzle.cells
            if not cell.ordered_sides
        }
        self.assertFalse(cells_that_cannot_order_sides)

    def test_all_cells_ordered_sides_are_all_sides(self):
        cells_with_different_ordered_sides_than_sides = {
            cell
            for cell in self.puzzle.cells
            if set(cell.ordered_sides) != set(cell.sides)
        }
        self.assertFalse(cells_with_different_ordered_sides_than_sides)

    def test_all_cells_ordered_sides_share_a_side_in_order(self):
        cells_with_sides_that_dont_share_a_side_in_order = {
            cell
            for cell, ordered_sides in (
                (cell, cell.ordered_sides)
                for cell in self.puzzle.cells
            )
            if any(
                not side.corners & next_side.corners
                for side, next_side
                in zip(ordered_sides, ordered_sides[1:] + ordered_sides[:1])
            )
        }
        self.assertFalse(
            cells_with_sides_that_dont_share_a_side_in_order)

    def test_all_cells_ordered_sides_are_neighbours_in_order(self):
        cells_with_sides_that_are_not_neighbours_in_order = {
            cell
            for cell, ordered_sides in (
                (cell, cell.ordered_sides)
                for cell in self.puzzle.cells
            )
            if any(
                side not in next_side.neighbours
                for side, next_side
                in zip(ordered_sides, ordered_sides[1:] + ordered_sides[:1])
            )
        }
        self.assertFalse(
            cells_with_sides_that_are_not_neighbours_in_order)


class BaseTestBoardCellsCorners(BaseTestBoardCells):
    def test_all_cells_have_corners(self):
        cells_without_corners = {
            cell
            for cell in self.puzzle.cells
            if not cell.corners
        }
        self.assertFalse(cells_without_corners)

    def test_all_cells_corners_share_a_side(self):
        cells_with_corners_that_dont_share_a_side = {
            cell
            for cell in self.puzzle.cells
            if any(
                not cell.sides & corner.sides
                for corner in cell.corners
            )
        }
        self.assertFalse(cells_with_corners_that_dont_share_a_side)

    def test_all_cells_corners_are_as_many_as_sides(self):
        cells_with_different_count_corners_than_sides = {
            cell
            for cell in self.puzzle.cells
            if len(set(cell.corners)) != len(set(cell.sides))
        }
        self.assertFalse(cells_with_different_count_corners_than_sides)

    def test_all_cells_can_order_corners(self):
        cells_that_cannot_order_corners = {
            cell
            for cell in self.puzzle.cells
            if not cell.ordered_corners
        }
        self.assertFalse(cells_that_cannot_order_corners)

    def test_all_cells_ordered_corners_are_all_corners(self):
        cells_with_different_ordered_corners_than_corners = {
            cell
            for cell in self.puzzle.cells
            if set(cell.ordered_corners) != set(cell.corners)
        }
        self.assertFalse(cells_with_different_ordered_corners_than_corners)

    def test_all_cells_ordered_corners_share_a_side_in_order(self):
        cells_with_corners_that_dont_share_a_side_in_order = {
            cell
            for cell, ordered_corners in (
                (cell, cell.ordered_corners)
                for cell in self.puzzle.cells
            )
            if any(
                not corner.sides & next_corner.sides
                for corner, next_corner
                in zip(ordered_corners, ordered_corners[1:] + ordered_corners[:1])
            )
        }
        self.assertFalse(
            cells_with_corners_that_dont_share_a_side_in_order)

    def test_all_cells_ordered_corners_are_neighbours_in_order(self):
        cells_with_corners_that_are_not_neighbours_in_order = {
            cell
            for cell, ordered_corners in (
                (cell, cell.ordered_corners)
                for cell in self.puzzle.cells
            )
            if any(
                corner not in next_corner.neighbours
                for corner, next_corner
                in zip(ordered_corners, ordered_corners[1:] + ordered_corners[:1])
            )
        }
        self.assertFalse(
            cells_with_corners_that_are_not_neighbours_in_order)


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
        BaseTestBoardCellsSides,
        BaseTestBoardCellsCorners,
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
    puzzle_svg_kwargs = {}

    def setUp(self):
        self.puzzle = self.create_puzzle()
        print 'Seed: #%s' % self.puzzle.seed
        self.puzzle.create_random_puzzle()


class BaseTestPuzzleCreation(BaseTestPuzzle):
    def create_puzzle(self):
        return self.puzzle_class(**self.puzzle_kwargs)

    def test_all_closed_sides_are_connected(self):
        closed_sides = self.puzzle.closed_sides
        a_side = sorted(closed_sides).pop()
        connected_sides = a_side.closed_neighbours_recursive
        unconnected_sides = closed_sides - connected_sides
        self.assertFalse(unconnected_sides)

    def test_all_internal_cells_are_connected(self):
        internal_cells = self.puzzle.internal_cells
        an_internal_cell = set(internal_cells).pop()
        connected_internal_cells = \
            an_internal_cell.get_connected_cells_in(internal_cells)
        unconnected_internal_cells = internal_cells - connected_internal_cells
        self.assertFalse(unconnected_internal_cells)


class BaseTestPuzzleSVG(BaseTestPuzzle):
    def test_can_create_svg(self):
        svg = self.puzzle.create_svg(**self.puzzle_svg_kwargs)
        print svg.filename

    def test_can_create_unsolved_svg(self):
        svg = self.puzzle.create_unsolved_svg(**self.puzzle_svg_kwargs)
        print svg.filename


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
        BaseTestPuzzleSVG,
        BaseTestPuzzleCreation,
        BaseTestPuzzle):
    pass


class BaseTestBadKeySequencePuzzleCreation(BaseTestPuzzleCreation):
    key_sequence = None

    def setUp(self):
        self.puzzle = self.create_puzzle()
        self.puzzle.create_puzzle_from_key_sequence(self.key_sequence)

    def test_all_closed_sides_are_connected(self):
        with self.assertRaises(AssertionError):
            super(BaseTestBadKeySequencePuzzleCreation, self)\
                .test_all_closed_sides_are_connected()

    def test_key_sequence_is_not_permissible(self):
        puzzle = self.create_puzzle()
        with self.assertRaises(AssertionError):
            for key in self.key_sequence:
                cell = puzzle.cells_by_key[key]
                self.assertIn(cell, puzzle.get_permissible_puzzle_cells())
                puzzle.add_internal_cell(cell)
