import puzzle


class HexagonalPuzzle(puzzle.Puzzle):
    def __init__(self, width, height):
        self.width, self.height = width, height
        super(HexagonalPuzzle, self).__init__()

    def create_cells(self):
        cells = {
            (x, y): puzzle.Cell((x, y))
            for x in xrange(self.width)
            for y in xrange(self.height)
        }

        corners = self._create_corners()

        self._create_sides(corners)

        for x in xrange(self.width):
            for y in xrange(self.height):
                cell = cells[(x, y)]
                for corner_index in xrange(6):
                    cell.add_sides(*[
                        side
                        for side in corners[(x, y, corner_index)].sides
                    ])

        return set(cells.itervalues())

    def _create_corners(self):
        def same(x, y):
            return x, y

        def left_of(x, y):
            return x - 1, y

        def right_of(x, y):
            return x + 1, y

        def top_left_of(x, y):
            if x % 2 == 0:
                return x - 1, y - 1
            else:
                return x, y - 1

        def top_right_of(x, y):
            x, y = top_left_of(x, y)
            return right_of(x, y)

        def bottom_left_of(x, y):
            if x % 2 == 0:
                return x - 1, y + 1
            else:
                return x, y + 1

        def bottom_right_of(x, y):
            x, y = bottom_left_of(x, y)
            return right_of(x, y)

        def make_groups(equivalences):
            groups = {
                tuple(sorted([
                    move(x, y) + (moved_corner,)
                    for move, moved_corner
                    in equivalences
                ]))
                for x in xrange(self.width)
                for y in xrange(self.height)
            }
            return {
                item: group
                for group in groups
                for item in group
            }

        corners_groups = {}
        corners_groups.update(make_groups([
            (same, 0),
            (left_of, 4),
            (bottom_left_of, 2),
        ]))
        corners_groups.update(make_groups([
            (same, 1),
            (left_of, 3),
            (top_left_of, 5),
        ]))
        corners_groups.update(make_groups([
            (same, 2),
            (top_left_of, 4),
            (top_right_of, 0),
        ]))
        corners_groups.update(make_groups([
            (same, 3),
            (top_right_of, 5),
            (right_of, 1),
        ]))
        corners_groups.update(make_groups([
            (same, 4),
            (right_of, 0),
            (bottom_right_of, 2),
        ]))
        corners_groups.update(make_groups([
            (same, 5),
            (bottom_right_of, 1),
            (bottom_left_of, 3),
        ]))

        unique_groups = set(corners_groups.itervalues())

        unique_corners = {
            group: puzzle.Corner()
            for group in unique_groups
        }

        corners = {
            (x, y, corner): unique_corners[corners_groups[(x, y, corner)]]
            for x in xrange(self.width)
            for y in xrange(self.height)
            for corner in xrange(6)
        }

        return corners

    def _create_sides(self, corners):
        corner_indexes = range(6)
        corner_index_pairs = zip(
            corner_indexes, corner_indexes[1:] + corner_indexes[:1])
        for x in xrange(self.width):
            for y in xrange(self.height):
                for corner, next_corner in corner_index_pairs:
                    side = puzzle.Side()
                    side.add_corners(
                        corners[(x, y, corner)], corners[x, y, next_corner])

        sides = {
            side
            for corner in corners.itervalues()
            for side in corner.sides
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
        for row in self.rows:
            print ' '.join(
                str(len(cell.closed_sides) or' ')
                for cell in row
            )

    def print_cells_membership(self):
        for row in self.rows:
            print ' '.join(
                'I' if cell.is_internal else ' '
                for cell in row
            )
