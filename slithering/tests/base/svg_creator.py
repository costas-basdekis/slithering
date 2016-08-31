import os

from slithering.tests.base.base import BaseSVGCreatorTestCase, SolverBase


class BaseTestSVGCreator(SolverBase, BaseSVGCreatorTestCase):
    def test_can_create_svg(self):
        svg = self.puzzle.create_svg(**self.svg_creator_kwargs)
        print svg.filename

    def test_can_create_unsolved_svg(self):
        svg = self.puzzle.create_unsolved_svg(**self.svg_creator_kwargs)
        print svg.filename

    def test_can_create_solved_svg(self):
        solver = self.create_solver(self.puzzle)
        try:
            solver.solve()
        finally:
            svg_creator_kwargs = dict(self.svg_creator_kwargs)
            filename = os.path.join(
                self.puzzle.unsolved_svg_generator_class.base_directory,
                '%s_solved.svg' % type(self.puzzle).__name__,
            )
            svg_creator_kwargs.setdefault('filename', filename)
            svg = self.puzzle.create_unsolved_svg(**svg_creator_kwargs)
            print svg.filename


class AllSVGCreatorTests(
        BaseTestSVGCreator):
    pass
