import sys
import random

from slithering import puzzle_svg


class KeyedSet(object):
    @property
    def by_key(self):
        return {
            item.key: item
            for item in self
        }

    def __getitem__(self, key):
        return self.by_key[key]


class Cell(object):
    def __init__(self, key):
        self.key = key
        self.sides = MutableSides()
        self.is_internal = False

        self._solved = False

        self.hint_is_given = True

    def __unicode__(self):
        return u'Cell %s %s' % \
            (self.key, 'internal' if self.is_internal else 'external')

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

    def freeze(self):
        self.sides = self.sides.frozen()

    @property
    def solved(self):
        return self._solved

    @property
    def solved_is_internal(self):
        assert self.solved, "Hasn't solved %s yet" % self
        return self.is_internal

    @solved_is_internal.setter
    def solved_is_internal(self, value):
        assert value == self.is_internal, \
            "Solved wrong value for %s: should be %s" % (self, self.is_internal)
        self._solved = True

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_cells(self) for side in new_sides]

    @property
    def neighbours(self):
        return self.sides.cells - {self}

    @property
    def hint(self):
        return len(self.sides.closed)

    @property
    def corners(self):
        return self.sides.corners

    @property
    def ordered_corners(self):
        ordered_sides = self.sides.ordered
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
        return self.corners.cells - {self}

    @classmethod
    def group_cells_by_internal_adjacent_cells_ratio(cls, cells):
        cells_and_ratios = [
            (cell, cell.adjacent_cells.internal_ratio)
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

    def get_connected_cells_in(self, cells):
        cells = set(cells) | {self}
        if len(cells) <= 1:
            return cells

        connected = {self}
        connected_stack = [self]

        while connected_stack:
            cell = connected_stack.pop()
            new_cells = (cell.neighbours & cells) - connected
            connected_stack.extend(new_cells)
            connected.update(new_cells)

        return connected

    @property
    def is_on_edge(self):
        return any(self.sides.on_edge)


class CellsBase(KeyedSet):
    def frozen(self):
        return Cells(self)

    def freeze(self):
        for cell in self:
            cell.freeze()
        return self

    def set(self, is_internal):
        for cell in self:
            cell.is_internal = is_internal

        return self

    @property
    def internal(self):
        return Cells((
            cell
            for cell in self
            if cell.is_internal
        ))

    @property
    def external(self):
        return self - self.internal

    @property
    def internal_ratio(self):
        return 1. * len(self.internal) / len(self)

    @property
    def border(self):
        neighbours = Cells((
            neighbour
            for cell in self.internal
            for neighbour in cell.neighbours
        ))
        return neighbours - self.internal

    @property
    def non_splitting(self):
        return Cells((
            cell
            for cell in self
            if cell.adjacent_cells.internal.are_connected()
        ))

    def are_connected(self):
        a_cell = set(self).pop()
        connected_cells = a_cell.get_connected_cells_in(self)

        return connected_cells == self

    @property
    def on_edge(self):
        return Cells((
            cell
            for cell in self
            if cell.is_on_edge
        ))

    def solve(self, is_internal):
        for cell in self:
            cell.solved_is_internal = is_internal

        return self

    @property
    def solved(self):
        return Cells((
            cell
            for cell in self
            if cell.solved
        ))

    @property
    def unsolved(self):
        return self - self.solved

    @property
    def sides(self):
        return Sides((
            side
            for cell in self
            for side in cell.sides
        ))

    @property
    def corners(self):
        return self.sides.corners


class MutableCells(CellsBase, set):
    pass


class Cells(CellsBase, frozenset):
    pass


class Side(object):
    def __init__(self):
        self.cells = MutableCells()
        self.corners = MutableCorners()

        self._solved = False

    def __unicode__(self):
        return u'Side %s - %s' % tuple(self.corners)

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

    def freeze(self):
        self.cells = self.cells.frozen()
        self.corners = self.corners.frozen()

    @property
    def key(self):
        return tuple(corner.key for corner in self.corners)

    @property
    def solved(self):
        return self._solved

    @property
    def solved_is_closed(self):
        assert self.solved, "Hasn't solved %s yet" % self
        return self.is_closed

    @solved_is_closed.setter
    def solved_is_closed(self, value):
        assert value == self.is_closed, \
            "Solved wrong value for %s: should be %s" % (self, self.is_closed)
        self._solved = True

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
        return self.corners.sides - {self}

    @property
    def closed_neighbours_recursive(self):
        connected_sides = {self}
        connected_sides_stack = [self]

        while connected_sides_stack:
            side = connected_sides_stack.pop()
            new_sides = side.neighbours.closed - connected_sides
            connected_sides_stack.extend(new_sides)
            connected_sides |= new_sides

        return connected_sides

    @property
    def is_closed(self):
        if len(self.cells) == 1:
            cell, = self.cells
            return cell.is_internal
        cell_1, cell_2 = self.cells
        return cell_1.is_internal != cell_2.is_internal

    @property
    def is_on_edge(self):
        return len(self.cells) == 1


class SidesBase(KeyedSet):
    def frozen(self):
        return Sides(self)

    def freeze(self):
        for side in self:
            side.freeze()

        return self

    @property
    def closed(self):
        return Sides((
            side
            for side in self
            if side.is_closed
        ))

    @property
    def open(self):
        return self - self.closed

    @property
    def on_edge(self):
        return Sides((
            side
            for side in self
            if side.is_on_edge
        ))

    @property
    def ordered(self):
        remaining = Sides(self)
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

    def solve(self, is_closed):
        for side in self:
            side.solved_is_closed = is_closed

        return self

    @property
    def solved(self):
        return Sides((
            side
            for side in self
            if side.solved
        ))

    @property
    def unsolved(self):
        return self - self.solved

    @property
    def cells(self):
        return Cells((
            cell
            for side in self
            for cell in side.cells
        ))

    @property
    def corners(self):
        return Corners((
            corner
            for side in self
            for corner in side.corners
        ))


class MutableSides(SidesBase, set):
    pass


class Sides(SidesBase, frozenset):
    pass


class Corner(object):
    def __init__(self, key):
        self.key = key
        self.sides = MutableSides()

        self._solved = False

    def __unicode__(self):
        return u'Corner %s' % (self.key,)

    def __repr__(self):
        return u'<%s>' % self

    def __lt__(self, other):
        return self.key.__lt__(other.key)

    def freeze(self):
        self.sides = self.sides.frozen()

    @property
    def solved(self):
        return self._solved

    @property
    def solved_is_used(self):
        assert self.solved, "Haven't solved %s yet" % self
        return self.is_used

    @solved_is_used.setter
    def solved_is_used(self, value):
        assert value == self.is_used, \
            "Solved wrong value for %s: should be %s" % (self, self.is_used)
        self._solved = True

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_corners(self) for side in new_sides]

    @property
    def is_used(self):
        return bool(self.sides.closed)

    @property
    def neighbours(self):
        return self.sides.corners - {self}


class CornersBase(KeyedSet):
    def frozen(self):
        return Corners(self)

    def freeze(self):
        for corner in self:
            corner.freeze()

        return self

    def solve(self, is_used):
        for corner in self:
            corner.solved_is_used = is_used

        return self

    @property
    def solved(self):
        return Corners((
            corner
            for corner in self
            if corner.solved
        ))

    @property
    def unsolved(self):
        return self - self.solved

    @property
    def cells(self):
        return self.sides.cells

    @property
    def sides(self):
        return Sides((
            side
            for corner in self
            for side in corner.sides
        ))


class MutableCorners(CornersBase, set):
    pass


class Corners(CornersBase, frozenset):
    pass


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
        self.freeze()

    def get_random_seed(self):
        return random.randint(0, sys.maxint)

    def create_cells(self):
        raise NotImplementedError()

    def freeze(self):
        self.cells = self.cells.frozen()
        self.cells.freeze()
        self.cells.sides.freeze()
        self.cells.corners.freeze()

    def clear_puzzle(self):
        self.cells.set(False)

    def create_puzzle_from_key_sequence(self, key_sequence):
        cells_sequence = self.get_cells_from_keys(key_sequence)
        self.create_random_puzzle_from_cells_sequence(cells_sequence)

        return self

    def get_cells_from_keys(self, keys):
        return [
            self.cells[key]
            for key in keys
        ]

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
        if not self.cells.internal:
            return self.cells

        return self.cells.border.non_splitting

    def create_random_puzzle_cells_sequence(self):
        target_internal_cells_count = \
            len(self.cells) * self.target_internal_cells_percentage

        yield self.get_random_starting_cell_for_puzzle()
        while len(self.cells.internal) < target_internal_cells_count:
            yield self.get_random_cell_for_puzzle()

    def get_random_cell_for_puzzle(self):
        permissible_cells = self.get_permissible_puzzle_cells()
        cells_by_ratio = \
            Cell.group_cells_by_internal_adjacent_cells_ratio(permissible_cells)
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

    @property
    def sides(self):
        return self.cells.sides

    @property
    def corners(self):
        return self.cells.corners

    @property
    def solved(self):
        return not self.sides.unsolved

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
