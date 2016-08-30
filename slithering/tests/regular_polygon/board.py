from slithering.tests.base.board import BaseAllBoardTests
from slithering.tests.base.parts import BaseTestBoardCells


class BaseTestRegularPolygonBoardCells(BaseTestBoardCells):
    @property
    def minimum_cell_side_count(self):
        return self.board_class.cell_sides_count

    @property
    def maximum_cell_side_count(self):
        return self.board_class.cell_sides_count


class BaseAllRegularPolygonBoardTests(
        BaseTestRegularPolygonBoardCells,
        BaseAllBoardTests):
    pass
