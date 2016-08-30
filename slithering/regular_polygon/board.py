from slithering.base import puzzle_svg
from slithering.base.board import Board


class RegularPolygonBoard(Board):
    cell_sides_count = None
    svg_generator_class = puzzle_svg.RegularPolygonPuzzleSVG
