import itertools

from slithering.solver.constraints import WithPuzzleConstraints, \
    Constraint, Case
from slithering.solver.sub_solvers import PuzzleSubSolver, \
    CellSubSolver, CornerSubSolver
from slithering.solver.solver import PuzzleSolver


@PuzzleSolver.register_cell_sub_solver_class
class CellHintSubSolver(WithPuzzleConstraints, CellSubSolver):
    def is_suitable(self):
        if not self.cell.hint_is_given:
            return False

        return True

    def apply(self):
        self.finished = True
        changed = False

        constraints = self.constraints

        constraint = self.constraint()
        if constraint not in constraints:
            changed = True
            constraints.add(constraint)

        return changed

    def constraint(self):
        sides = self.cell.sides
        combinations = itertools.combinations(sides, self.cell.hint)

        constraint = Constraint((
            Case((
                (side, side in combination)
                for side in sides
            ), source=u'Hint possibility')
            for combination in combinations
        ), source=u'From hint')

        return constraint


@PuzzleSolver.register_cell_sub_solver_class
class CellSolvedEdgeSideSubSolver(CellSubSolver):
    """An edge side of cell is solved"""
    def is_suitable(self):
        if self.cell.solved:
            return False

        if not self.cell.is_on_edge:
            return False

        solved_on_edge_sides = self.cell.sides.solved & self.cell.sides.on_edge
        if not any(solved_on_edge_sides):
            return False

        return True

    def apply(self):
        changed = False
        self.finished = True

        if self.cell.solved:
            return changed

        changed = True

        is_internal = any(
            side.is_on_edge and side.solved and side.solved_is_closed
            for side in self.cell.sides
        )
        is_external = any(
            side.is_on_edge and side.solved and not side.solved_is_closed
            for side in self.cell.sides
        )

        assert not (is_internal and is_external), \
            u"Invalid state: a cell should be both internal and external, " \
            u"based on sides"

        self.cell.solved_is_internal = is_internal

        return changed


@PuzzleSolver.register_cell_sub_solver_class
class CellSolvedSideSubSolver(CellSubSolver):
    """An non-edge side of cell is solved"""
    def is_suitable(self):
        if self.cell.solved:
            return False

        solved_sides_with_solved_cell = {
            side
            for side in self.cell.sides.solved
            if any(side.cells.solved)
        }
        if not any(solved_sides_with_solved_cell):
            return False

        return True

    def apply(self):
        changed = False
        self.finished = True

        if self.cell.solved:
            return changed

        solved_sides_with_solved_cell = {
            side
            for side in self.cell.sides.solved
            if any(side.cells.solved)
        }
        is_internal = False
        is_external = False
        for side in solved_sides_with_solved_cell:
            other_cell, = side.cells.solved - {self.cell}
            if side.is_closed == other_cell.is_internal:
                is_external = True
            else:
                is_internal = True

        assert is_internal != is_external, \
            u"Invalid state: a cell must be either internal and external, " \
            u"based on sides"

        self.cell.solved_is_internal = is_internal

        changed = True

        return changed


@PuzzleSolver.register_corner_sub_solver_class
class CornerConstraints(WithPuzzleConstraints, CornerSubSolver):
    def is_suitable(self):
        return True

    def apply(self):
        self.finished = True
        changed = False

        constraint = self.constraint()
        if constraint not in self.constraints:
            changed = True
            self.constraints.add(constraint)

        return changed

    def constraint(self):
        constraint = Constraint((
            Case((
                (side, False) for side in self.corner.sides
            ), source=u'Corner solves to unused'),
        ) + tuple(
            Case((
                (side, side in side_pair) for side in self.corner.sides
            ), source=u'Corner uses sides %s' % str(side_pair))
            for side_pair in itertools.combinations(self.corner.sides, 2)
        ), source=u'From corner')

        return constraint


@PuzzleSolver.register_puzzle_sub_solver_class
class PuzzleConstraints(WithPuzzleConstraints, PuzzleSubSolver):
    def is_suitable(self):
        return True

    def apply(self):
        changed = self.constraint_solver.apply()

        self.finished = not self.constraints

        return changed
