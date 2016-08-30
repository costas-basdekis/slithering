from slithering.base import puzzle_svg


class Board(object):
    svg_generator_class = puzzle_svg.PuzzleSVG

    def __init__(self):
        self._frozen = False

        self.cells = self.create_cells()
        self.freeze()

    def create_cells(self):
        raise NotImplementedError()

    def freeze(self):
        self.cells = self.cells.frozen()
        self.cells.freeze()
        self.cells.sides.freeze()
        self.cells.corners.freeze()
        self._frozen = True

    @property
    def sides(self):
        return self.cells.sides

    @property
    def corners(self):
        return self.cells.corners

    @property
    def solved(self):
        return not self.sides.unsolved

    @classmethod
    def register_svg_generator_class(cls, svg_generator_class):
        cls.svg_generator_class = svg_generator_class
        return svg_generator_class

    def create_svg(self, *args, **kwargs):
        return self.svg_generator_class(self, *args, **kwargs).svg
