import math

import svgwrite
import svgwrite.shapes
import svgwrite.text

from slithering import registrable
from slithering import strategy_creator


@registrable.registrable
class PuzzleSVG(object):
    base_directory = '/tmp/'

    PointMapper = registrable.Registrable

    CellSVG = registrable.Registrable
    SideSVG = registrable.Registrable
    CornerSVG = registrable.Registrable

    def __init__(self, puzzle, side_width=25, corner_width=2, filename=None):
        self.puzzle = puzzle
        self.side_width = side_width
        self.corner_width = corner_width

        if filename is None:
            filename = self.get_default_filename()
        self.filename = filename

        self.point_mapper = self.PointMapper(self, self.puzzle)

        self.svg = self.create_svg()

    def get_default_filename(self):
        return '%s%s.svg' % (self.base_directory, type(self.puzzle).__name__)

    def create_svg(self):
        drawing = svgwrite.Drawing(self.filename)

        for cell in self.puzzle.cells:
            map(drawing.add, self.create_cell(cell))

        for side in self.puzzle.sides:
            map(drawing.add, self.create_side(side))

        for corner in self.puzzle.corners:
            map(drawing.add, self.create_corner(corner))

        drawing.save()

        return drawing

    def create_cell(self, cell):
        return self.CellSVG.create(item=cell, puzzle_svg=self)

    def create_side(self, side):
        return self.SideSVG.create(item=side, puzzle_svg=self)

    def create_corner(self, corner):
        return self.CornerSVG.create(item=corner, puzzle_svg=self)

    def get_cell_center_point(self, cell):
        return self.point_mapper.get_cell_center_point(cell)

    def get_corner_point(self, corner):
        return self.point_mapper.get_corner_point(corner)


@PuzzleSVG.register_PointMapper
class PointMapper(object):
    def __init__(self, puzzle_svg, puzzle):
        self.puzzle_svg = puzzle_svg
        self.puzzle = puzzle

    def get_cell_center_point(self, cell):
        raise NotImplementedError()

    def get_corner_point(self, corner):
        raise NotImplementedError()

    @property
    def side_width(self):
        return self.puzzle_svg.side_width

    @property
    def corner_width(self):
        return self.puzzle_svg.corner_width


class PuzzleItemCreator(strategy_creator.StrategyCreator):
    @property
    def item_name(self):
        raise NotImplementedError("%s must define 'item_name'" % type(self))

    @property
    def creators(self):
        raise NotImplementedError("%s must define 'creators'" % type(self))

    def __init__(self, puzzle_svg, item):
        self.puzzle_svg = puzzle_svg
        self.item = item

    @property
    def item(self):
        return getattr(self, self.item_name)

    @item.setter
    def item(self, value):
        setattr(self, self.item_name, value)

    def create_item(self):
        return sum([
            creatable.create(puzzle_svg=self.puzzle_svg, item=self.item)
            for creatable in self.creators
        ], [])

    @property
    def side_width(self):
        return self.puzzle_svg.side_width

    @property
    def corner_width(self):
        return self.puzzle_svg.corner_width

    def get_corner_point(self, corner):
        return self.puzzle_svg.get_corner_point(corner)

    def get_corner_points(self, corners):
        return map(self.get_corner_point, corners)

    def get_cell_center_point(self, cell):
        return self.puzzle_svg.get_cell_center_point(cell)


@PuzzleSVG.register_CellSVG
@registrable.registrable
class CellSVG(PuzzleItemCreator):
    item_name = 'cell'

    CellFillSVG = registrable.Registrable
    CellHintTextSVG = registrable.Registrable

    @property
    def creators(self):
        return [
            self.CellFillSVG,
            self.CellHintTextSVG,
        ]


@CellSVG.register_CellFillSVG
@registrable.registrable
class CellFillSVG(PuzzleItemCreator):
    item_name = 'cell'

    CELL_FILL_COLOUR = None

    InternalCellFillSVG = registrable.Registrable
    ExternalCellFillSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        if item.is_internal:
            return cls.InternalCellFillSVG
        else:
            return cls.ExternalCellFillSVG

    def create_item(self):
        kwargs = self.get_kwargs()
        points = self.get_cell_fill_points()

        return [
            svgwrite.shapes.Polygon(points, **kwargs),
        ]

    def get_kwargs(self):
        kwargs = {
            'stroke': svgwrite.rgb(100, 100, 100, '%'),
            'fill': self.CELL_FILL_COLOUR,
        }

        return kwargs

    def get_cell_fill_points(self):
        return self.get_corner_points(self.cell.ordered_corners)


@CellFillSVG.register_InternalCellFillSVG
class InternalCellFillSVG(CellFillSVG):
    CELL_FILL_COLOUR = '#77DD77'


@CellFillSVG.register_ExternalCellFillSVG
class ExternalCellFillSVG(CellFillSVG):
    CELL_FILL_COLOUR = '#779ECB'


@CellSVG.register_CellHintTextSVG
@registrable.registrable
class CellHintTextSVG(PuzzleItemCreator):
    item_name = 'cell'

    GivenCellHintTextSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        return cls.GivenCellHintTextSVG


@CellHintTextSVG.register_GivenCellHintTextSVG
class GivenCellHintTextSVG(CellHintTextSVG):
    def create_item(self):
        kwargs = self.get_kwargs()
        point = self.get_text_center()
        hint_text = self.get_text()

        return [
            svgwrite.text.Text(hint_text, point, **kwargs),
        ]

    def get_kwargs(self):
        kwargs = {
            'text-anchor': 'middle',
            'style': "dominant-baseline: central;",
            'stroke-width': '2',
        }

        return kwargs

    def get_text_center(self):
        point = self.get_cell_center_point(self.cell)

        return point

    def get_text(self):
        hint_text = unicode(self.cell.hint)

        return hint_text


@PuzzleSVG.register_SideSVG
@registrable.registrable
class SideSVG(PuzzleItemCreator):
    item_name = 'side'

    SideLineSVG = registrable.Registrable

    @property
    def creators(self):
        return [
            self.SideLineSVG,
        ]


@SideSVG.register_SideLineSVG
@registrable.registrable
class SideLineSVG(PuzzleItemCreator):
    item_name = 'side'

    ClosedSideLineSVG = registrable.Registrable
    OpenSideLineSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        if item.is_closed:
            return cls.ClosedSideLineSVG
        else:
            return cls.OpenSideLineSVG

    def create_item(self):
        kwargs = self.get_kwargs()
        point_1, point_2 = self.get_side_points()

        return [
            svgwrite.shapes.Line(point_1, point_2, **kwargs),
        ]

    def get_kwargs(self):
        kwargs = {
            'stroke': svgwrite.rgb(0, 0, 0, '%'),
        }

        return kwargs

    def get_side_points(self):
        return self.get_corner_points(self.side.corners)


@SideLineSVG.register_ClosedSideLineSVG
class ClosedSideLineSVG(SideLineSVG):
    def get_kwargs(self):
        kwargs = super(ClosedSideLineSVG, self).get_kwargs()

        kwargs['stroke-width'] = '2'

        return kwargs


@SideLineSVG.register_OpenSideLineSVG
class OpenSideLineSVG(SideLineSVG):
    def get_kwargs(self):
        kwargs = super(OpenSideLineSVG, self).get_kwargs()

        kwargs['stroke-width'] = '1px'
        kwargs['stroke-dasharray'] = '1 5'

        return kwargs


@PuzzleSVG.register_CornerSVG
@registrable.registrable
class CornerSVG(PuzzleItemCreator):
    item_name = 'corner'

    CornerDotSVG = registrable.Registrable

    @property
    def creators(self):
        return [
            self.CornerDotSVG,
        ]


@CornerSVG.register_CornerDotSVG
class CornerDotSVG(PuzzleItemCreator):
    item_name = 'corner'

    def create_item(self):
        kwargs = self.get_kwargs()
        x, y = self.get_corner_point(self.item)

        return [
            svgwrite.shapes.Circle(
                (x, y), self.puzzle_svg.corner_width, **kwargs),
        ]

    def get_kwargs(self):
        kwargs = {
            'stroke': svgwrite.rgb(0, 0, 0, '%'),
            'fill': "#000000"
        }

        return kwargs


class RegularPolygonPuzzleSVG(PuzzleSVG):
    pass


@RegularPolygonPuzzleSVG.register_PointMapper
class RegularPolygonPointMapper(PointMapper):
    @property
    def corner_index_offset(self):
        return self.puzzle.cell_sides_count / 2 + 0.5

    def get_cell_center_point(self, cell):
        cell_x, cell_y = cell.key
        return self.get_cell_center_point_by_position(cell_x, cell_y)

    def get_cell_center_point_by_position(self, cell_x, cell_y):
        size_angle = 2 * math.pi * 1 / (self.puzzle.cell_sides_count * 2)

        cell_width = 2 * math.sin(size_angle)
        x_center = (1 + cell_x) * cell_width
        x = x_center * self.side_width

        cell_height = 2 * math.cos(size_angle)
        y_center = (1 + cell_y) * cell_height
        y = y_center * self.side_width

        return (x, y)

    def get_corner_point(self, corner):
        x, y, corner_index = corner.key

        return self.get_corner_point_by_key(x, y, corner_index)

    def get_corner_point_by_key(self, cell_x, cell_y, corner_index):
        x_center, y_center = \
            self.get_cell_center_point_by_position(cell_x, cell_y)

        corner_angle = 2. * math.pi / self.puzzle.cell_sides_count
        angle = corner_angle * (self.corner_index_offset + corner_index)

        x_offset = math.cos(angle)
        x = x_center + x_offset * self.side_width

        y_offset = math.sin(angle)
        y = y_center + y_offset * self.side_width

        return x, y


class UnsolvedPuzzleSVG(PuzzleSVG):
    def get_default_filename(self):
        return '%s%s_unsolved.svg' \
               % (self.base_directory, type(self.puzzle).__name__)


@UnsolvedPuzzleSVG.register_CellSVG
@registrable.registrable
class UnsolvedCellSVG(CellSVG):
    pass


@UnsolvedCellSVG.register_CellFillSVG
@registrable.registrable
class UnsolvedCellFillSVG(UnsolvedCellSVG, CellFillSVG):
    EmptyCellFillSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        if item.solved:
            return super(UnsolvedCellFillSVG, cls).for_item(item)

        return cls.EmptyCellFillSVG


@UnsolvedCellFillSVG.register_EmptyCellFillSVG
class EmptyCellFillSVG(UnsolvedCellFillSVG):
    CELL_FILL_COLOUR = '#FFFFFF'


@UnsolvedCellSVG.register_CellHintTextSVG
@registrable.registrable
class UnsolvedCellHintTextSVG(CellHintTextSVG):
    WithheldCellHintTextSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        if item.hint_is_given:
            return super(UnsolvedCellHintTextSVG, cls).for_item(item)

        return cls.WithheldCellHintTextSVG


@UnsolvedCellHintTextSVG.register_WithheldCellHintTextSVG
class WithheldCellHintTextSVG(CellHintTextSVG):
    def create_item(self):
        return []


class UnsolvedRegularPolygonPuzzleSVG(UnsolvedPuzzleSVG, RegularPolygonPuzzleSVG):
    # PointMapper = RegularPolygonPointMapper
    pass


@UnsolvedPuzzleSVG.register_SideSVG
@registrable.registrable
class UnsolvedSideSVG(SideSVG):
    UnsolvedSideLineSVG = registrable.Registrable

    @classmethod
    def for_item(cls, item):
        if item.solved:
            return super(UnsolvedSideSVG, cls).for_item(item)

        return cls.UnsolvedSideLineSVG


@UnsolvedSideSVG.register_UnsolvedSideLineSVG
class UnsolvedSideLineSVG(SideLineSVG):
    def get_kwargs(self):
        kwargs = super(UnsolvedSideLineSVG, self).get_kwargs()

        kwargs['stroke-width'] = '1px'
        kwargs['stroke-dasharray'] = '0 2 0'

        return kwargs
