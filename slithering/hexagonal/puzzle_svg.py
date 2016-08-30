import math

from slithering.base import puzzle_svg
from slithering.hexagonal.puzzle import HexagonalPuzzle


@HexagonalPuzzle.register_svg_generator_class
class HexagonalPuzzleSVG(puzzle_svg.RegularPolygonPuzzleSVG):
    pass


@HexagonalPuzzleSVG.register_PointMapper
class HexagonalPointMapperSVG(puzzle_svg.RegularPolygonPointMapper):
    def get_cell_center_point_by_position(self, cell_x, cell_y):
        size_angle = 2 * math.pi * 1 / 6

        cell_width = 2 * math.sin(size_angle)
        odd_line_x_offset = (0.5 if (cell_y % 2) else 0)
        x_center = (1 + cell_x + odd_line_x_offset) * cell_width
        x = x_center * self.side_width

        cell_height = 3 * math.cos(size_angle)
        y_center = (1 + cell_y) * cell_height
        y = y_center * self.side_width

        return (x, y)


@HexagonalPuzzle.register_unsolved_svg_generator_class
class UnslovedHexagonalPuzzleSVG(puzzle_svg.UnsolvedRegularPolygonPuzzleSVG, HexagonalPuzzleSVG):
    pass