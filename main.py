#-*-coding:utf8;-*-
#qpy:2
#qpy:console

import random


class Cell(object):
    def __init__(self, key):
        self.key = key
        self.sides = set()
        self.is_internal = False
        
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
    def neighbours(self):
        return {
            cell
            for side in self.sides
            for cell in side.cells
            if cell != self
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
    def __init__(self):
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
        self.create_random_puzzle()
        
    def create_cells(self):
        raise NotImplementedError()
        
    def create_random_puzzle(self):
        target_internal_cells_count = len(self.cells) * self.target_internal_cells_percentage
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
        

class SquarePuzzle(Puzzle):
    def __init__(self, width, height):
        self.width, self.height = width, height
        super(SquarePuzzle, self).__init__()
        	
    def create_cells(self):
        cells = {
            (x, y): Cell((x, y))
            for x in xrange(self.width)
            for y in xrange(self.height)
        }
        corners = {
            (x, y): Corner()
            for x in xrange(self.width + 1)
            for y in xrange(self.height + 1)
        }
        
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"
        sides = {}
        sides.update({
            (x, y, HORIZONTAL): Side()
            for x in xrange(self.width)
            for y in xrange(self.height + 1)
        })
        sides.update({
            (x, y, VERTICAL): Side()
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
 

def test():
    puzzle = SquarePuzzle(20, 20)
    print len(puzzle.cells), len(puzzle.internal_cells), len(puzzle.closed_sides)
    cell = list(puzzle.cells)[0]
    print len(cell.sides), len(cell.closed_sides)
    side = list(cell.sides)[0]
    print cell in side.cells, len(side.cells)
    print len(side.corners)
    corner = list(side.corners)[0]
    print side in corner.sides, len(corner.sides)
    puzzle.print_all_possible_hints()
    puzzle.print_cells_membership()
    
    
if __name__ == '__main__':
    test()
    