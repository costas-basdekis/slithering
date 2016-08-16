import random


class Cell(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()
        self.is_internal = False

    def __unicode__(self):
        return u'Cell %s %s' % \
            (self.key, 'internal' if self.is_internal else 'external')

    def __repr__(self):
        return u'<%s>' % self

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
    def corners(self):
        return {
            corner
            for side in self.sides
            for corner in side.corners
        }

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
        remaining = self.adjacent_cells
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


class Side(object):
    def __init__(self):
        self.cells = set()
        self.corners = set()

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
            for cell in self.cells
            for side in cell.sides
            if side != self
        }

    @property
    def is_closed(self):
        unique_memberships = set(cell.is_internal for cell in self.cells)
        if len(self.cells) == 1:
            return unique_memberships == {True}
        return unique_memberships == {True, False}


class Corner(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()

    def add_sides(self, *sides):
        new_sides = set(sides) - self.sides
        self.sides.update(new_sides)
        [side.add_corners(self) for side in new_sides]


class Puzzle(object):
    target_internal_cells_percentage = 0.5

    def __init__(self):
        self.cells = self.create_cells()
        self.cells_by_key = {
            cell.key: cell
            for cell in self.cells
        }

    def create_cells(self):
        raise NotImplementedError()

    def create_random_puzzle(self):
        target_internal_cells_count = \
            len(self.cells) * self.target_internal_cells_percentage
        # cell = random.choice(tuple(self.external_cells))
        cell = self.cells_by_key[(self.width / 2, self.height / 2)]
        cell.is_internal = True
        while len(self.internal_cells) < target_internal_cells_count:
            cell = random.choice(tuple(self.border_cells))

            if not cell.are_internal_adjacent_cells_together:
                continue
            if random.random() < cell.internal_adjacent_cells_ratio:
                continue

            cell.is_internal = True

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
