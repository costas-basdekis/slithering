from slithering import puzzle


class SquarePuzzle(puzzle.RegularPolygonPuzzle):
    cell_sides_count = 4

    def __init__(self, width, height):
        self.width, self.height = width, height
        super(SquarePuzzle, self).__init__()

    def create_cells(self):
        cells = {
            (x, y): puzzle.Cell((x, y))
            for x in xrange(self.width)
            for y in xrange(self.height)
        }
        corners = {
            (x, y): puzzle.Corner((x, y, 0))
            for x in xrange(self.width + 1)
            for y in xrange(self.height + 1)
        }

        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"
        sides = {}
        sides.update({
            (x, y, HORIZONTAL): puzzle.Side()
            for x in xrange(self.width)
            for y in xrange(self.height + 1)
        })
        sides.update({
            (x, y, VERTICAL): puzzle.Side()
            for x in xrange(self.width + 1)
            for y in xrange(self.height)
        })

        for (x, y), cell in cells.iteritems():
            cell.add_sides(
                sides[(x, y, HORIZONTAL)],
                sides[(x, y, VERTICAL)],
                sides[(x, y + 1, HORIZONTAL)],
                sides[(x + 1, y, VERTICAL)],
            )

        for (x, y, orientation), side in sides.iteritems():
            if orientation == HORIZONTAL:
                side.add_corners(
                    corners[(x, y)],
                    corners[(x + 1, y)],
                )
            else:
                side.add_corners(
                    corners[(x, y)],
                    corners[(x, y + 1)],
                )

        return set(cells.itervalues())

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
