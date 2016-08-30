from slithering.tests.base.base import BasePuzzleTestCase


class BaseTestPuzzle(BasePuzzleTestCase):
    puzzle_svg_kwargs = {}


class BaseTestPuzzleCreation(BaseTestPuzzle):
    def test_all_closed_sides_are_connected(self):
        closed_sides = self.puzzle.sides.closed
        a_side = closed_sides.peek()
        connected_sides = a_side.closed_neighbours_recursive
        unconnected_sides = closed_sides - connected_sides
        self.assertFalse(unconnected_sides)

    def test_all_internal_cells_are_connected(self):
        internal_cells = self.puzzle.cells.internal
        an_internal_cell = internal_cells.peek()
        connected_internal_cells = \
            an_internal_cell.get_connected_cells_in(internal_cells)
        unconnected_internal_cells = internal_cells - connected_internal_cells
        self.assertFalse(unconnected_internal_cells)


class BaseTestPuzzleCells(BaseTestPuzzle):
    def test_there_are_closed_sides(self):
        self.assertTrue(self.puzzle.sides.closed)

    def test_some_cells_have_closed_sides(self):
        cells_with_closed_sides = {
            cell
            for cell in self.puzzle.cells
            if cell.sides.closed
        }
        self.assertTrue(cells_with_closed_sides)

    def test_there_are_internal_cells(self):
        self.assertTrue(self.puzzle.cells.internal)


class BaseAllPuzzleTests(
        BaseTestPuzzleCells,
        BaseTestPuzzleCreation,
        BaseTestPuzzle):
    pass


class BaseTestBadKeySequencePuzzleCreation(BaseTestPuzzleCreation):
    key_sequence = None

    def setUp(self):
        super(BaseTestBadKeySequencePuzzleCreation, self).setUp()
        self.puzzle = self.create_puzzle(self.board)
        self.puzzle.create_puzzle_from_key_sequence(self.key_sequence)

    def test_all_closed_sides_are_connected(self):
        with self.assertRaises(AssertionError):
            super(BaseTestBadKeySequencePuzzleCreation, self)\
                .test_all_closed_sides_are_connected()

    def test_key_sequence_is_not_permissible(self):
        puzzle = self.create_puzzle(self.board)
        with self.assertRaises(AssertionError):
            for key in self.key_sequence:
                cell = puzzle.cells[key]
                self.assertIn(cell, puzzle.get_permissible_puzzle_cells())
                puzzle.add_internal_cell(cell)
