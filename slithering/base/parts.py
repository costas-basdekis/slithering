class KeyedSet(object):
    _frozen = False

    @property
    def by_key(self):
        return {
            item.key: item
            for item in self
        }

    def __getitem__(self, key):
        return self.by_key[key]

    def from_keys(self, keys):
        by_key = self.by_key
        from_keys = (
            by_key[key]
            for key in keys
        )

        if type(from_keys) != type(keys):
            from_keys = type(keys)(from_keys)

        return from_keys


class SetBase(KeyedSet):
    def peek(self):
        return next(iter(self))


class Cell(object):
    def __init__(self, key):
        self._frozen = False

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
        self._frozen = True

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


class CellsBase(SetBase):
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
    def grouped_by_internal_adjacent_cells_ratio(self):
        cells_and_ratios = [
            (cell, cell.adjacent_cells.internal_ratio)
            for cell in self
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
    def border(self):
        neighbours = Cells((
            neighbour
            for cell in self
            for neighbour in cell.neighbours
        ))
        return neighbours - self

    @property
    def non_splitting(self):
        return Cells((
            cell
            for cell in self
            if cell.adjacent_cells.internal.are_connected
        ))

    @property
    def are_connected(self):
        a_cell = self.peek()
        connected_cells = a_cell.get_connected_cells_in(self)

        return connected_cells == self

    @property
    def on_edge(self):
        return Cells((
            cell
            for cell in self
            if cell.is_on_edge
        ))

    @property
    def not_on_edge(self):
        return self - self.on_edge

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
    _frozen = True


class Side(object):
    def __init__(self):
        self._frozen = False
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
        self._frozen = True

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


class SidesBase(SetBase):
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
    def not_on_edge(self):
        return self - self.on_edge

    @property
    def ordered(self):
        remaining = MutableSides(self)
        ordered = []
        side = remaining.pop()
        ordered.append(side)
        while remaining:
            head = ordered[-1]
            remaining_sides = MutableSides(head.neighbours & remaining)
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
    _frozen = True


class Corner(object):
    def __init__(self, key):
        self._frozen = False
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
        self._frozen = True

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


class CornersBase(SetBase):
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
    _frozen = True
