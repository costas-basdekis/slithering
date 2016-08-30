from slithering.tests.base import base
from slithering.hexagonal.board import HexagonalBoard
from slithering.hexagonal.puzzle import HexagonalPuzzle


class HexagonalBase(object):
    board_class = HexagonalBoard
    board_kwargs = dict(base.PuzzleSVGBase.board_kwargs, **{
        'width': 20,
        'height': 20,
    })

    puzzle_class = HexagonalPuzzle
    puzzle_kwargs = dict(base.PuzzleSVGBase.puzzle_kwargs, **{
        'seed': 1177294445585927408,
    })
