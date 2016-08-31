import random
import sys

from slithering.base import svg_creator


class Puzzle(object):
    target_internal_cells_percentage = 0.5
    unsolved_svg_generator_class = svg_creator.UnsolvedSVGCreator

    def __init__(self, board, seed=None):
        self._frozen = False

        self.board = board

        if seed is None:
            seed = self.get_random_seed()
        self.seed = seed
        self.random = random.Random(self.seed)

    @property
    def cells(self):
        return self.board.cells

    @property
    def sides(self):
        return self.board.sides

    @property
    def corners(self):
        return self.board.corners

    @property
    def solved(self):
        return not self.sides.unsolved

    def get_random_seed(self):
        return random.randint(0, sys.maxint)

    def clear_puzzle(self):
        self.cells.set(False)

    def create_puzzle_from_key_sequence(self, key_sequence):
        cells_sequence = self.cells.from_keys(key_sequence)
        self.create_random_puzzle_from_cells_sequence(cells_sequence)

        return self

    def create_random_puzzle(self):
        cells_sequence = self.create_random_puzzle_cells_sequence()
        self.create_random_puzzle_from_cells_sequence(cells_sequence)

        return self

    def create_random_puzzle_from_cells_sequence(self, cells_sequence):
        cells = []

        for cell in cells_sequence:
            self.add_internal_cell(cell)
            cells.append(cell)

        return cells

    def add_internal_cell(self, cell):
        cell.is_internal = True

    def get_permissible_puzzle_cells(self):
        internal = self.cells.internal
        if not internal:
            return self.cells

        return internal.border.non_splitting

    def create_random_puzzle_cells_sequence(self):
        target_internal_cells_count = \
            len(self.cells) * self.target_internal_cells_percentage

        yield self.get_random_starting_cell_for_puzzle()
        while len(self.cells.internal) < target_internal_cells_count:
            yield self.get_random_cell_for_puzzle()

    def get_random_cell_for_puzzle(self):
        permissible_cells = self.get_permissible_puzzle_cells()
        cells_by_ratio = \
            permissible_cells.grouped_by_internal_adjacent_cells_ratio
        ratios = sorted(set(cells_by_ratio))
        minimum_ratio = self.random.random()

        passing_ratios = [
            ratio
            for ratio in ratios
            if ratio >= minimum_ratio
        ]

        if not passing_ratios:
            ratio = ratios[0]
        else:
            ratio = passing_ratios[0]

        ratio_cells = cells_by_ratio[ratio]
        cell = self.random.choice(sorted(ratio_cells))

        return cell

    def get_random_starting_cell_for_puzzle(self):
        return self.get_random_cell()

    def get_random_cell(self):
        permissible_cells = self.get_permissible_puzzle_cells()
        return self.random.choice(sorted(permissible_cells))

    @classmethod
    def register_unsolved_svg_generator_class(
            cls, unsolved_svg_generator_class):
        cls.unsolved_svg_generator_class = unsolved_svg_generator_class
        return unsolved_svg_generator_class

    def create_svg(self, *args, **kwargs):
        return self.board.create_svg(*args, **kwargs)

    def create_unsolved_svg(self, *args, **kwargs):
        return self.unsolved_svg_generator_class(self, *args, **kwargs).svg


class RegularPolygonPuzzle(Puzzle):
    unsolved_svg_generator_class = svg_creator.UnsolvedRegularPolygonSVGCreator

    @property
    def cell_sides_count(self):
        return self.board.cell_sides_count
