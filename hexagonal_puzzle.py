import math

import puzzle


class HexagonalPuzzle(puzzle.RegularPolygonPuzzle):
    cell_sides_count = 6

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


@HexagonalPuzzle.register_svg_generator_class
class HexagonalPuzzleSVG(puzzle.RegularPolygonPuzzleSVG):
    def get_cell_center_point(self, cell_x, cell_y):
        size_angle = 2 * math.pi * 1 / 6

        cell_width = 2 * math.sin(size_angle)
        odd_line_x_offset = (0.5 if (cell_y % 2) else 0)
        x_center = (1 + cell_x + odd_line_x_offset) * cell_width
        x = x_center * self.side_width

        cell_height = 3 * math.cos(size_angle)
        y_center = (1 + cell_y) * cell_height
        y = y_center * self.side_width

        return (x, y)
