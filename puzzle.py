import math
import random

import svgwrite
import svgwrite.shapes
import svgwrite.text


class Cell(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()
        self.is_internal = False

    def __unicode__(self):
        return u'Cell %s %s' % \
            (self.key, 'internal' if self.is_internal else 'external')

    def __repr__(self):
        return u'<%s>' % self

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_cells(self) for side in new_sides]

    @property
    def neighbours(self):
        return {
            cell
            for side in self.sides
            for cell in side.cells
            if cell != self
        }

    @property
    def closed_sides(self):
        return {
            side
            for side in self.sides
            if side.is_closed
        }

    @property
    def corners(self):
        return {
            corner
            for side in self.sides
            for corner in side.corners
        }

    @property
    def adjacent_cells(self):
        return {
            cell
            for corner in self.corners
            for side in corner.sides
            for cell in side.cells
            if cell != self
        }

    @property
    def ordered_adjacent_cells(self):
        remaining = self.adjacent_cells
        ordered = []
        cell = remaining.pop()
        ordered.append(cell)
        while remaining:
            head = ordered[-1]
            remaining_neighbours = head.neighbours & remaining
            if not remaining_neighbours:
                ordered.reverse()
                head = ordered[-1]
                remaining_neighbours = head.neighbours & remaining
            cell = remaining_neighbours.pop()
            remaining.remove(cell)
            ordered.append(cell)

        return ordered

    @property
    def are_internal_adjacent_cells_together(self):
        ordered_adjacent_cells = self.ordered_adjacent_cells
        if len(ordered_adjacent_cells) <= 3:
            return True

        previous_ordered_adjacent_cells = \
            ordered_adjacent_cells[-1:] + ordered_adjacent_cells[:-1]
        external_to_internal_count = len([
            cell
            for cell, previous
            in zip(ordered_adjacent_cells, previous_ordered_adjacent_cells)
            if cell.is_internal and not previous.is_internal
        ])

        return external_to_internal_count <= 1

    @property
    def adjacent_cell_count(self):
        return len(self.adjacent_cells)

    @property
    def internal_adjacent_cells(self):
        return {
            cell
            for cell in self.adjacent_cells
            if cell.is_internal
        }

    @property
    def internal_adjacent_cells_count(self):
        return len(self.internal_adjacent_cells)

    @property
    def internal_adjacent_cells_ratio(self):
        return 1. * self.internal_adjacent_cells_count / self.adjacent_cell_count


class Side(object):
    def __init__(self):
        self.cells = set()
        self.corners = set()

    def add_cells(self, *cells):
        new_cells = set(cells) - self.cells
        self.cells.update(new_cells)
        [cell.add_sides(self) for cell in new_cells]

    def add_corners(self, *corners):
        new_corners = set(corners) - self.corners
        self.corners.update(new_corners)
        [corner.add_sides(self) for corner in new_corners]

    @property
    def neighbours(self):
        return {
            side
            for cell in self.cells
            for side in cell.sides
            if side != self
        }

    @property
    def is_closed(self):
        unique_memberships = set(cell.is_internal for cell in self.cells)
        if len(self.cells) == 1:
            return unique_memberships == {True}
        return unique_memberships == {True, False}


class Corner(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_corners(self) for side in new_sides]


class Puzzle(object):
    target_internal_cells_percentage = 0.5
    svg_generator_class = None

    def __init__(self):
        self.cells = self.create_cells()
        self.cells_by_key = {
            cell.key: cell
            for cell in self.cells
        }

    def create_cells(self):
        raise NotImplementedError()

    def create_random_puzzle(self):
        target_internal_cells_count = \
            len(self.cells) * self.target_internal_cells_percentage
        # cell = random.choice(tuple(self.external_cells))
        cell = self.cells_by_key[(self.width / 2, self.height / 2)]
        cell.is_internal = True
        while len(self.internal_cells) < target_internal_cells_count:
            cell = random.choice(tuple(self.border_cells))

            if not cell.are_internal_adjacent_cells_together:
                continue
            if random.random() < cell.internal_adjacent_cells_ratio:
                continue

            cell.is_internal = True

    @property
    def internal_cells(self):
        return {
            cell
            for cell in self.cells
            if cell.is_internal
        }

    @property
    def external_cells(self):
        return self.cells - self.internal_cells

    @property
    def border_cells(self):
        neighbours = {
            neighbour
            for cell in self.internal_cells
            for neighbour in cell.neighbours
        }
        return neighbours - self.internal_cells

    @property
    def sides(self):
        return {
            side
            for cell in self.cells
            for side in cell.sides
        }

    @property
    def closed_sides(self):
        return {
            side
            for side in self.sides
            if side.is_closed
        }

    @property
    def corners(self):
        return {
            corner
            for side in self.sides
            for corner in side.corners
        }

    @classmethod
    def register_svg_generator_class(cls, svg_generator_class):
        cls.svg_generator_class = svg_generator_class
        return svg_generator_class

    def create_svg(self, *args, **kwargs):
        return self.svg_generator_class(self, *args, **kwargs).svg


class RegularPolygonPuzzle(Puzzle):
    cell_sides_count = None


@Puzzle.register_svg_generator_class
class PuzzleSVG(object):
    def __init__(self, puzzle, side_width, filename=None):
        self.puzzle = puzzle
        self.side_width = side_width

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
        kwargs = {
            'stroke': svgwrite.rgb(100, 100, 100, '%'),
        }
        if cell.is_internal:
            kwargs['fill'] = '#77DD77'
        else:
            kwargs['fill'] = '#779ECB'

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
        kwargs = {
            'stroke': svgwrite.rgb(0, 0, 0, '%'),
            'stroke-width': '2',
        }
        if not side.is_closed:
            kwargs['stroke-dasharray'] = '0 2 0'
            kwargs['stroke-width'] = '1px'

        return kwargs

    def get_side_points(self, side):
        raise NotImplementedError()


@RegularPolygonPuzzle.register_svg_generator_class
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

    def get_corner_point(self, cell_x, cell_y, corner_index):
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
            self.get_corner_point(cell_x, cell_y, corner_index)
            for corner_index in xrange(self.puzzle.cell_sides_count)
        ]

        return points

    def get_side_points(self, side):
        corner1, corner2 = side.corners
        (x1, y1, corner_index_1), (x2, y2, corner_index_2) = \
            corner1.key, corner2.key
        point_1 = self.get_corner_point(x1, y1, corner_index_1)
        point_2 = self.get_corner_point(x2, y2, corner_index_2)

        return point_1, point_2
