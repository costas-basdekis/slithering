import math

import svgwrite
import svgwrite.shapes
import svgwrite.text

import puzzle


class HexagonalPuzzle(puzzle.Puzzle):
    def __init__(self, width, height):
        self.width, self.height = width, height
        super(HexagonalPuzzle, self).__init__()

    def create_cells(self):
        corners_by_key = self._create_corners()
        sides_by_key = self._create_sides(corners_by_key)
        cells = self._create_cells(sides_by_key)

        return cells

    def _create_cells(self, sides_by_key):
        cells = {
            (x, y): puzzle.Cell((x, y))
            for x in xrange(self.width)
            for y in xrange(self.height)
        }

        for x in xrange(self.width):
            for y in xrange(self.height):
                cell = cells[(x, y)]
                for corner_index in xrange(6):
                    cell.add_sides(*[
                        sides_by_key[(x, y, side_index)]
                        for side_index in xrange(6)
                        ])
                    assert len(cell.sides) == 6, len(cell.sides)

        return set(cells.itervalues())

    def _create_corners(self):
        positions_by_key = {}
        for x in xrange(self.width):
            for y in xrange(self.height):
                positions_by_key[(x, y, 0)] = ((y % 2) + 2 * x, y)
                positions_by_key[(x, y, 1)] = ((y % 2) + 2 * x + 1, y)
                positions_by_key[(x, y, 2)] = ((y % 2) + 2 * x + 2, y)
                positions_by_key[(x, y, 3)] = ((y % 2) + 2 * x + 2, y + 1)
                positions_by_key[(x, y, 4)] = ((y % 2) + 2 * x + 1, y + 1)
                positions_by_key[(x, y, 5)] = ((y % 2) + 2 * x, y + 1)

        a_key_py_position = {
            position: a_key
            for a_key, position in positions_by_key.iteritems()
        }

        corners_by_position = {
            position: puzzle.Corner(a_key)
            for position, a_key in a_key_py_position.iteritems()
        }

        corners_by_key = {
            key: corners_by_position[position]
            for key, position in positions_by_key.iteritems()
        }

        return corners_by_key

    def _create_sides(self, corners_by_key):
        corner_indexes = range(6)
        next_corner_indexes = corner_indexes[1:] + corner_indexes[:1]
        corner_index_pairs = zip(corner_indexes, next_corner_indexes)

        all_corner_pairs = {
            tuple(sorted([
                corners_by_key[(x, y, corner_index)],
                corners_by_key[(x, y, next_corner_index)],
            ]))
            for x in xrange(self.width)
            for y in xrange(self.height)
            for corner_index, next_corner_index in corner_index_pairs
        }
        sides_by_corner_pairs = {}
        for corner_pair in all_corner_pairs:
            side = puzzle.Side()
            side.add_corners(*corner_pair)
            sides_by_corner_pairs[corner_pair] = side

        sides = {
            (x, y, corner_index): sides_by_corner_pairs[tuple(sorted([
                corners_by_key[(x, y, corner_index)],
                corners_by_key[(x, y, next_corner_index)],
            ]))]
            for x in xrange(self.width)
            for y in xrange(self.height)
            for corner_index, next_corner_index in corner_index_pairs
        }

        return sides

    def row(self, y):
        return [
            self.cells_by_key[(x, y)]
            for x in xrange(self.height)
        ]

    @property
    def rows(self):
        return map(self.row, xrange(self.height))

    def print_all_possible_hints(self):
        for index, row in enumerate(self.rows):
            print ' ' * (index % 2) + ' '.join(
                str(len(cell.closed_sides) or ' ')
                for cell in row
            )

    def print_cells_membership(self):
        for index, row in enumerate(self.rows):
            print ' ' * (index % 2) + ' '.join(
                'I' if cell.is_internal else ' '
                for cell in row
            )

    def _get_svg_center_point(self, side_width, cell_x, cell_y, with_odd_line_x_offset=True):
        cell_width = math.sin(math.pi * 1 / 3)

        if with_odd_line_x_offset:
            odd_line_x_offset = (0.5 if (cell_y % 2) else 0)
        else:
            odd_line_x_offset = (0.5 if (cell_y % 2) else 0)
        x_center = (1 + cell_x + odd_line_x_offset) * 2 * cell_width
        x = x_center * side_width

        cell_height = math.cos(math.pi * 1 / 3)
        y_center = (1 + cell_y) * 3 * cell_height
        y = y_center * side_width

        return (x, y)

    def _get_svg_corner_point(self, side_width, cell_x, cell_y, corner_index, with_odd_line_x_offset=True):
        x_center, y_center = \
            self._get_svg_center_point(side_width, cell_x, cell_y, with_odd_line_x_offset=with_odd_line_x_offset)

        x_offset = math.cos(math.pi * (3.5 + corner_index) / 3)
        x = x_center + x_offset * side_width

        y_offset = math.sin(math.pi * (3.5 + corner_index) / 3)
        y = y_center + y_offset * side_width

        return (x, y)

    def create_svg(self, side_width, filename='/tmp/HexagonalPuzzle.svg'):
        drawing = svgwrite.Drawing(filename)

        for cell in self.cells:
            kwargs = {
                'stroke': svgwrite.rgb(100, 100, 100, '%'),
            }
            if cell.is_internal:
                kwargs['fill'] = '#77DD77'
            else:
                kwargs['fill'] = '#779ECB'

            cell_x, cell_y = cell.key
            points = [
                self._get_svg_corner_point(side_width, cell_x, cell_y, corner_index)
                for corner_index in xrange(6)
            ]
            drawing.add(svgwrite.shapes.Polygon(
                points,
                **kwargs))

            kwargs = {
                'text-anchor': 'middle',
                'style': "dominant-baseline: central;",
                'stroke-width': '2',
            }
            drawing.add(svgwrite.text.Text(
                unicode(len(cell.closed_sides)),
                self._get_svg_center_point(side_width, cell_x, cell_y),
                **kwargs))

        for side in self.sides:
            kwargs = {
                'stroke': svgwrite.rgb(0, 0, 0, '%'),
                'stroke-width': '2',
            }
            if not side.is_closed:
                kwargs['stroke-dasharray'] = '0 2 0'
                kwargs['stroke-width'] = '1px'

            corner1, corner2 = side.corners
            (x1, y1, corner_index_1), (x2, y2, corner_index_2) = \
                corner1.key, corner2.key
            drawing.add(svgwrite.shapes.Line(
                self._get_svg_corner_point(side_width, x1, y1, corner_index_1,
                                           with_odd_line_x_offset=False),
                self._get_svg_corner_point(side_width, x2, y2, corner_index_2,
                                           with_odd_line_x_offset=False),
                **kwargs))

        drawing.save()
