from slithering.tests.base.base import BasePuzzleSVGTestCase, SolverBase


class BaseTestPuzzleSVG(SolverBase, BasePuzzleSVGTestCase):
    def test_can_create_svg(self):
        svg = self.puzzle.create_svg(**self.puzzle_svg_kwargs)
        print svg.filename

    def test_can_create_unsolved_svg(self):
        svg = self.puzzle.create_unsolved_svg(**self.puzzle_svg_kwargs)
        print svg.filename

    def test_can_create_solved_svg(self):
        solver = self.create_solver(self.puzzle)
        try:
            solver.solve()
        finally:
            puzzle_svg_kwargs = dict(self.puzzle_svg_kwargs)
            filename = '%s%s_solved.svg' % (
                self.puzzle.unsolved_svg_generator_class.base_directory,
                type(self.puzzle).__name__,
            )
            puzzle_svg_kwargs.setdefault('filename', filename)
            svg = self.puzzle.create_unsolved_svg(**puzzle_svg_kwargs)
            print svg.filename


class AllPuzzleSVGTests(
        BaseTestPuzzleSVG):
    pass
