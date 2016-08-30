from slithering.tests import regular_polygon as _regular_polygon
from slithering.tests.square import base as _square_base


class TestSquareBoard(
        _square_base.SquareBase,
        _regular_polygon.BaseAllRegularPolygonBoardTests):
    def test_cells_in_row_are_neighbours(self):
        cells_that_are_not_neighbours_in_row = {
            cell
            for y in xrange(self.board.height)
            for cell, next_cell in (
                (self.board.cells[(x, y)],
                 self.board.cells[(x + 1, y)])
                for x in xrange(self.board.width - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_row)

    def test_cells_in_column_are_neighbours(self):
        cells_that_are_not_neighbours_in_column = {
            cell
            for x in xrange(self.board.width)
            for cell, next_cell in (
                (self.board.cells[(x, y)],
                 self.board.cells[(x, y + 1)])
                for y in xrange(self.board.height - 1)
            )
            if cell not in next_cell.neighbours
        }
        self.assertFalse(cells_that_are_not_neighbours_in_column)
