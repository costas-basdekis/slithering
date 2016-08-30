from slithering.tests.base import base as _base
from slithering.square.board import SquareBoard
from slithering.square.puzzle import SquarePuzzle


class SquareBase(object):
    board_class = SquareBoard
    board_kwargs = dict(_base.PuzzleSVGBase.board_kwargs, **{
        'width': 20,
        'height': 20,
    })

    puzzle_class = SquarePuzzle
    puzzle_kwargs = {
        'seed': 3125568123140421500,
    }
