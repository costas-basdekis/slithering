import sys
import random

from slithering import puzzle_svg


class Cell(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()
        self.is_internal = False

        self.solved = False
        self.solved_is_internal = None

        self.hint_is_given = True

    def __unicode__(self):
        return u'Cell %s %s' % \
            (self.key, 'internal' if self.is_internal else 'external')

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

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
    def ordered_sides(self):
        remaining = set(self.sides)
        ordered = []
        side = remaining.pop()
        ordered.append(side)
        while remaining:
            head = ordered[-1]
            remaining_sides = head.neighbours & remaining
            if not remaining_sides:
                ordered.reverse()
                head = ordered[-1]
                remaining_sides = head.neighbours & remaining
            side = remaining_sides.pop()
            remaining.remove(side)
            ordered.append(side)

        return ordered

    @property
    def hint(self):
        return len(self.closed_sides)

    @property
    def corners(self):
        return {
            corner
            for side in self.sides
            for corner in side.corners
        }

    @property
    def ordered_corners(self):
        ordered_sides = self.ordered_sides
        next_ordered_sides = ordered_sides[1:] + ordered_sides[:1]

        return [
            corner
            for corner, in (
                side.corners & next_side.corners
                for side, next_side in zip(ordered_sides, next_ordered_sides)
            )
        ]

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
        remaining = set(self.adjacent_cells)
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

    @classmethod
    def group_cells_by_internal_adjacent_cells_ratio(self, cells):
        cells_and_ratios = [
            (cell, cell.internal_adjacent_cells_ratio)
            for cell in cells
        ]

        ratios = set(ratio for _, ratio in cells_and_ratios)
        by_ratio = {
            ratio: {
                cell
                for cell, cell_ratio in cells_and_ratios
                if cell_ratio == ratio
            }
            for ratio in ratios
        }

        return by_ratio

    @property
    def is_on_edge(self):
        return any(side.is_on_edge for side in self.sides)


class Side(object):
    def __init__(self):
        self.cells = set()
        self.corners = set()

        self.solved = False
        self.solved_is_closed = None

    def __unicode__(self):
        return u'Side %s - %s' % tuple(self.corners)

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

    @property
    def key(self):
        return tuple(corner.key for corner in self.corners)

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
            for corner in self.corners
            for side in corner.sides
            if side != self
        }

    @property
    def closed_neighbours(self):
        return {
            side
            for side in self.neighbours
            if side.is_closed
        }

    @property
    def closed_neighbours_recursive(self):
        connected_sides = {self}
        connected_sides_stack = [self]

        while connected_sides_stack:
            side = connected_sides_stack.pop()
            new_sides = side.closed_neighbours - connected_sides
            connected_sides_stack.extend(new_sides)
            connected_sides |= new_sides

        return connected_sides

    @property
    def is_closed(self):
        unique_memberships = set(cell.is_internal for cell in self.cells)
        if len(self.cells) == 1:
            return unique_memberships == {True}
        return unique_memberships == {True, False}

    @property
    def is_on_edge(self):
        return len(self.cells) == 1


class Corner(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()

        self.solved = False
        self.solved_is_active = None

    def __unicode__(self):
        return u'Corner %s' % (self.key,)

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_corners(self) for side in new_sides]

    @property
    def is_active(self):
        return bool(self.sides)

    @property
    def neighbours(self):
        return {
            corner
            for side in self.sides
            for corner in side.corners
            if corner != self
        }


class Puzzle(object):
    target_internal_cells_percentage = 0.5
    svg_generator_class = puzzle_svg.PuzzleSVG
    unsolved_svg_generator_class = puzzle_svg.UnsolvedPuzzleSVG

    def __init__(self, seed=None):
        if seed is None:
            seed = self.get_random_seed()
        self.seed = seed
        self.random = random.Random(self.seed)

        self.cells = self.create_cells()
        self.cells_by_key = {
            cell.key: cell
            for cell in self.cells
        }

    def get_random_seed(self):
        return random.randint(0, sys.maxint)

    def create_cells(self):
        raise NotImplementedError()

    def clear_puzzle(self):
        for cell in self.cells:
            cell.is_internal = False

    def create_puzzle_from_key_sequence(self, key_sequence):
        cells_sequence = self.get_cells_from_keys(key_sequence)
        self.create_random_puzzle_from_cells_sequence(cells_sequence)

        return self

    def get_cells_from_keys(self, keys):
        return [
            self.cells_by_key[key]
            for key in keys
        ]

    def create_random_puzzle(self):
        cells_sequence = self.create_random_puzzle_cells_sequence()
        self.create_random_puzzle_from_cells_sequence(cells_sequence)

        return self

    def create_random_puzzle_from_cells_sequence(self, cells_sequence):
        cells = []

        for cell in cells_sequence:
            cell.is_internal = True
            cells.append(cell)

        return cells

    def create_random_puzzle_cells_sequence(self):
        target_internal_cells_count = \
            len(self.cells) * self.target_internal_cells_percentage

        yield self.get_random_starting_cell_for_puzzle()
        while len(self.internal_cells) < target_internal_cells_count:
            yield self.get_random_cell_for_puzzle()

    def get_random_cell_for_puzzle(self):
        cells_by_ratio = self.non_splitting_border_cells_by_ratio
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
        return self.random.choice(sorted(self.external_cells))

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
    def non_splitting_border_cells(self):
        return {
            cell
            for cell in self.border_cells
            if cell.are_internal_adjacent_cells_together
        }

    @property
    def non_splitting_border_cells_by_ratio(self):
        return Cell.group_cells_by_internal_adjacent_cells_ratio(
            self.non_splitting_border_cells)

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

    @classmethod
    def register_unsolved_svg_generator_class(cls, unsolved_svg_generator_class):
        cls.unsolved_svg_generator_class = unsolved_svg_generator_class
        return unsolved_svg_generator_class

    def create_svg(self, *args, **kwargs):
        return self.svg_generator_class(self, *args, **kwargs).svg

    def create_unsolved_svg(self, *args, **kwargs):
        return self.unsolved_svg_generator_class(self, *args, **kwargs).svg


class RegularPolygonPuzzle(Puzzle):
    cell_sides_count = None
    svg_generator_class = puzzle_svg.RegularPolygonPuzzleSVG
    unsolved_svg_generator_class = puzzle_svg.UnsolvedRegularPolygonPuzzleSVG
