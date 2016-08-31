from slithering.base import svg_creator
from slithering.base.board import Board


class RegularPolygonBoard(Board):
    cell_sides_count = None
    svg_generator_class = svg_creator.RegularPolygonSVGCreator
