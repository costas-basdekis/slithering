from slithering.base.puzzle import RegularPolygonPuzzle
from slithering.hexagonal import svg_creator


class HexagonalPuzzle(RegularPolygonPuzzle):
    unsolved_svg_generator_class = svg_creator.UnsolvedHexagonalSVGCreator
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
        for index, row in enumerate(self.rows):
            print ' ' * (index % 2) + ' '.join(
                str(len(cell.sides.closed) or ' ')
                for cell in row
            )

    def print_cells_membership(self):
        for index, row in enumerate(self.rows):
            print ' ' * (index % 2) + ' '.join(
                'I' if cell.is_internal else ' '
                for cell in row
            )