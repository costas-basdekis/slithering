import slithering.base
from slithering.regular_polygon.board import RegularPolygonBoard


class SquareBoard(RegularPolygonBoard):
    cell_sides_count = 4

    def __init__(self, width, height, **kwargs):
        self.width, self.height = width, height
        super(SquareBoard, self).__init__(**kwargs)

    def create_cells(self):
        cells = {
            (x, y): slithering.base.parts.Cell((x, y))
            for x in xrange(self.width)
            for y in xrange(self.height)
        }
        corners = {
            (x, y): slithering.base.parts.Corner((x, y, 0))
            for x in xrange(self.width + 1)
            for y in xrange(self.height + 1)
        }

        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"
        sides = {}
        sides.update({
            (x, y, HORIZONTAL): slithering.base.parts.Side()
            for x in xrange(self.width)
            for y in xrange(self.height + 1)
        })
        sides.update({
            (x, y, VERTICAL): slithering.base.parts.Side()
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

        return slithering.base.parts.Cells(cells.itervalues())

    def row(self, y):
        return [
            self.cells[(x, y)]
            for x in xrange(self.height)
        ]

    @property
    def rows(self):
        return map(self.row, xrange(self.height))