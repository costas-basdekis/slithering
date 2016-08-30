from slithering.tests.base.base import BaseBoardTestCase
from slithering.tests.base.parts import BaseAllBoardPartsTests


class BaseTestBoardCreation(BaseBoardTestCase):
    def test_can_create_a_board(self):
        self.assertTrue(self.board)


class BaseAllBoardTests(
        BaseTestBoardCreation,
        BaseAllBoardPartsTests):
    pass
