import itertools

from slithering.puzzle_solver.constraint_solver import ConstraintSolver
from slithering.puzzle_solver.constraints import WithPuzzleConstraints
from slithering.puzzle_solver.sub_solvers import PuzzleSubSolver, \
    CellSubSolver, CornerSubSolver
from slithering.puzzle_solver.solver import PuzzleSolver


@PuzzleSolver.register_cell_sub_solver_class
class CellHintSubSolver(WithPuzzleConstraints, CellSubSolver):
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if not cell.hint_is_given:
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

        constraint = self.make_constraint(source=u'From hint', constraint=(
            self.make_case(source=u'Hint possibility', case=(
                (side, side in combination)
                for side in sides
            ))
            for combination in combinations
        ))

        return constraint


@PuzzleSolver.register_cell_sub_solver_class
class CellSolvedEdgeSideSubSolver(CellSubSolver):
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if cell.solved:
            return False

        if not cell.is_on_edge:
            return False

        solved_on_edge_sides = cell.sides.solved & cell.sides.on_edge
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
    """An edge side of cell is solved"""
    @classmethod
    def is_suitable(cls, puzzle, cell):
        if cell.solved:
            return False

        solved_sides_with_solved_cell = {
            side
            for side in cell.sides.solved
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

        if is_internal:
            self.cell.solved_is_internal = True
            changed = True
        elif is_external:
            self.cell.solved_is_internal = False
            changed = True

        return changed


@PuzzleSolver.register_corner_sub_solver_class
class CornerConstraints(WithPuzzleConstraints, CornerSubSolver):
    @classmethod
    def is_suitable(cls, puzzle, corner):
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
        constraint = self.make_constraint(source=u'From corner', constraint=(
            self.make_case(
                source=u'Corner solves to unused',
                case=(
                    (side, False) for side in self.corner.sides
                ),
            ),
        ) + tuple(
            self.make_case(
                source=u'Corner uses sides %s' % str(side_pair),
                case=(
                    (side, side in side_pair) for side in self.corner.sides
                ),
            )
            for side_pair in itertools.combinations(self.corner.sides, 2)
        ))

        return constraint


@PuzzleSolver.register_puzzle_sub_solver_class
class PuzzleConstraints(WithPuzzleConstraints, PuzzleSubSolver):
    @classmethod
    def is_suitable(cls, puzzle):
        return True

    def __init__(self, puzzle):
        super(PuzzleConstraints, self).__init__(puzzle)
        self.constraint_solver = \
            ConstraintSolver(self.puzzle, debug=True)

    def apply(self):
        changed = self.constraint_solver.apply()

        self.finished = not self.constraints

        return changed
