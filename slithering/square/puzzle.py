from slithering.base.puzzle import RegularPolygonPuzzle


class SquarePuzzle(RegularPolygonPuzzle):
    @property
    def width(self):
        return self.board.width

    @property
    def height(self):
        return self.board.height

    def row(self, y):
        return self.board.row(y)

    @property
    def rows(self):
        return self.board.rows

    def get_random_starting_cell_for_puzzle(self):
        return self.cells[(self.width / 2, self.height / 2)]

    def print_all_possible_hints(self):
        for row in self.rows:
            print ' '.join(
                str(len(cell.sides.closed) or' ')
                for cell in row
            )

    def print_cells_membership(self):
        for row in self.rows:
            print ' '.join(
                'I' if cell.is_internal else ' '
                for cell in row
            )