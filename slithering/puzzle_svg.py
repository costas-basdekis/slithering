import math

import svgwrite
import svgwrite.shapes
import svgwrite.text


class PuzzleSVG(object):
    INTERNAL_CELL_FILL_COLOUR = '#77DD77'
    EXTERNAL_CELL_FILL_COLOUR = '#779ECB'

    def __init__(self, puzzle, side_width, corner_width, filename=None):
        self.puzzle = puzzle
        self.side_width = side_width
        self.corner_width = corner_width

        if filename is None:
            filename = '/tmp/%s.svg' % type(self.puzzle).__name__
        self.filename = filename

        self.svg = self.create_svg()

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
        return [
            self.create_cell_fill(cell),
            self.add_cell_hint_text(cell),
        ]

    def create_cell_fill(self, cell):
        kwargs = self.get_cell_fill_kwargs(cell)
        points = self.get_cell_fill_points(cell)

        return svgwrite.shapes.Polygon(points, **kwargs)

    def get_cell_fill_kwargs(self, cell):
        if cell.is_internal:
            kwargs = self.get_internal_cell_fill_kwargs(cell)
        else:
            kwargs = self.get_external_cell_fill_kwargs(cell)

        return kwargs

    def get_base_cell_fill_kwargs(self, cell):
        kwargs = {
            'stroke': svgwrite.rgb(100, 100, 100, '%'),
        }

        return kwargs

    def get_internal_cell_fill_kwargs(self, cell):
        kwargs = self.get_base_cell_fill_kwargs(cell)

        kwargs['fill'] = self.INTERNAL_CELL_FILL_COLOUR

        return kwargs

    def get_external_cell_fill_kwargs(self, cell):
        kwargs = self.get_base_cell_fill_kwargs(cell)

        kwargs['fill'] = self.EXTERNAL_CELL_FILL_COLOUR

        return kwargs

    def get_cell_fill_points(self, cell):
        raise NotImplementedError()

    def add_cell_hint_text(self, cell):
        kwargs = self.get_cell_hint_text_kwargs(cell)
        point = self.get_cell_hint_text_center(cell)
        hint_text = self.get_cell_hint_text(cell)

        return svgwrite.text.Text(hint_text, point, **kwargs)

    def get_cell_hint_text_kwargs(self, cell):
        kwargs = {
            'text-anchor': 'middle',
            'style': "dominant-baseline: central;",
            'stroke-width': '2',
        }

        return kwargs

    def get_cell_hint_text_center(self, cell):
        cell_x, cell_y = cell.key
        point = self.get_cell_center_point(cell_x, cell_y)

        return point

    def get_cell_center_point(self, cell_x, cell_y):
        raise NotImplementedError()

    def get_cell_hint_text(self, cell):
        hint_text = unicode(len(cell.closed_sides))

        return hint_text

    def create_side(self, side):
        return [
            self.create_side_line(side),
        ]

    def create_side_line(self, side):
        kwargs = self.get_side_kwargs(side)
        point_1, point_2 = self.get_side_points(side)

        return svgwrite.shapes.Line(point_1, point_2, **kwargs)

    def get_side_kwargs(self, side):
        if side.is_closed:
            return self.get_closed_side_kwargs(side)
        else:
            return self.get_open_side_kwargs(side)

        return kwargs

    def get_base_side_kwargs(self, side):
        kwargs = {
            'stroke': svgwrite.rgb(0, 0, 0, '%'),
        }

        return kwargs

    def get_closed_side_kwargs(self, side):
        kwargs = self.get_base_side_kwargs(side)

        kwargs['stroke-width'] = '2'

        return kwargs

    def get_open_side_kwargs(self, side):
        kwargs = self.get_base_side_kwargs(side)

        kwargs['stroke-width'] = '1px'
        kwargs['stroke-dasharray'] = '0 2 0'

        return kwargs

    def get_side_points(self, side):
        raise NotImplementedError()

    def create_corner(self, corner):
        return [
            self.create_corner_dot(corner),
        ]

    def create_corner_dot(self, corner):
        kwargs = self.get_corner_dot_kwargs(corner)
        x, y = self.get_corner_point(corner)

        return svgwrite.shapes.Circle((x, y), self.corner_width, **kwargs)

    def get_corner_point(self, corner):
        return NotImplementedError()

    def get_corner_dot_kwargs(self, corner):
        if corner.is_active:
            return self.get_active_corner_dot_kwargs(corner)
        else:
            return self.get_inactive_corner_dot_kwargs(corner)

    def get_base_corner_dot_kwargs(self, corner):
        kwargs = {
            'stroke': svgwrite.rgb(0, 0, 0, '%'),
            'fill': "#000000"
        }

        return kwargs

    def get_active_corner_dot_kwargs(self, corner):
        kwargs = self.get_base_corner_dot_kwargs(corner)

        return kwargs

    def get_inactive_corner_dot_kwargs(self, corner):
        kwargs = self.get_base_corner_dot_kwargs(corner)

        return kwargs


class RegularPolygonPuzzleSVG(PuzzleSVG):
    @property
    def corner_index_offset(self):
        return self.puzzle.cell_sides_count / 2 + 0.5

    def get_cell_center_point(self, cell_x, cell_y):
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
            self.get_cell_center_point(cell_x, cell_y)

        corner_angle = 2. * math.pi / self.puzzle.cell_sides_count
        angle = corner_angle * (self.corner_index_offset + corner_index)

        x_offset = math.cos(angle)
        x = x_center + x_offset * self.side_width

        y_offset = math.sin(angle)
        y = y_center + y_offset * self.side_width

        return x, y

    def get_cell_fill_points(self, cell):
        cell_x, cell_y = cell.key
        points = [
            self.get_corner_point_by_key(cell_x, cell_y, corner_index)
            for corner_index in xrange(self.puzzle.cell_sides_count)
        ]

        return points

    def get_side_points(self, side):
        corner1, corner2 = side.corners
        (x1, y1, corner_index_1), (x2, y2, corner_index_2) = \
            corner1.key, corner2.key
        point_1 = self.get_corner_point_by_key(x1, y1, corner_index_1)
        point_2 = self.get_corner_point_by_key(x2, y2, corner_index_2)

        return point_1, point_2