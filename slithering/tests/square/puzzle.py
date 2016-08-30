from slithering.tests import base as _base
from slithering.tests.square import base as _square_base


class TestSquarePuzzle(_square_base.SquareBase, _base.BaseAllPuzzleTests):
    def test_debug_info(self):
        self.puzzle.print_all_possible_hints()
        self.puzzle.print_cells_membership()


class BadTestSquarePuzzle1943095418764571628(
        _square_base.SquareBase, _base.BaseTestPuzzleCreation):
    puzzle_kwargs = dict(_square_base.SquareBase.puzzle_kwargs, **{
        'seed': 1943095418764571628,
    })


class BadTestKeySequenceSquarePuzzle1943095418764571628(
        _base.BaseTestBadKeySequencePuzzleCreation,
        BadTestSquarePuzzle1943095418764571628):
    key_sequence = [
        (10, 10),
        (10, 11),
        (10, 12),
        (10, 13),
        (9, 11),
        (9, 12),
        (10, 9),
        (10, 14),
        (9, 13),
        (10, 15),
        (10, 8),
        (11, 15),
        (8, 13),
        (12, 15),
        (13, 15),
        (11, 9),
        (11, 14),
        (12, 9),
        (14, 15),
        (13, 9),
        (12, 14),
        (14, 9),
        (10, 7),
        (8, 11),
        (13, 14),
        (9, 14),
        (10, 6),
        (7, 11),
        (9, 10),
        (13, 13),
        (15, 15),
        (11, 7),
        (14, 13),
        (10, 5),
        (12, 13),
        (15, 9),
        (6, 11),
        (8, 10),
        (15, 13),
        (7, 13),
        (11, 13),
        (8, 9),
        (11, 10),
        (11, 8),
        (16, 9),
        (14, 14),
        (12, 10),
        (9, 5),
        (5, 11),
        (16, 15),
        (16, 13),
        (13, 8),
        (9, 6),
        (8, 14),
        (17, 15),
        (8, 12),
        (8, 8),
        (4, 11),
        (14, 8),
        (13, 10),
        (18, 15),
        (14, 10),
        (8, 5),
        (7, 10),
        (7, 12),
        (19, 15),
        (3, 11),
        (12, 8),
        (14, 7),
        (11, 12),
        (9, 9),
        (15, 14),
        (17, 9),
        (15, 12),
        (12, 7),
        (16, 14),
        (9, 8),
        (14, 6),
        (5, 12),
        (19, 16),
        (18, 9),
        (5, 13),
        (13, 7),
        (19, 17),
        (19, 9),
        (6, 12),
        (5, 14),
        (7, 5),
        (9, 15),
        (19, 18),
        (4, 12),
        (14, 5),
        (2, 11),
        (2, 10),
        (1, 10),
        (3, 12),
        (6, 5),
        (5, 5),
        (13, 6),
        (14, 4),
        (19, 19),
        (0, 10),
        (10, 4),
        (5, 15),
        (11, 11),
        (10, 3),
        (12, 11),
        (7, 8),
        (16, 10),
        (14, 12),
        (4, 5),
        (13, 16),
        (14, 3),
        (13, 17),
        (9, 4),
        (6, 8),
        (4, 15),
        (11, 6),
        (17, 8),
        (17, 7),
        (18, 17),
        (12, 6),
        (3, 15),
        (17, 17),
        (18, 16),
        (7, 9),
        (17, 6),
        (16, 17),
        (4, 13),
        (1, 9),
        (1, 8),
        (4, 16),
        (1, 7),
        (12, 12),
        (5, 8),
        (8, 4),
        (9, 7),
        (17, 16),
        (4, 14),
        (4, 10),
        (0, 11),
        (19, 14),
        (6, 10),
        (19, 13),
        (4, 17),
        (0, 9),
        (6, 13),
        (15, 17),
        (0, 8),
        (16, 6),
        (16, 16),
        (16, 12),
        (1, 6),
        (18, 19),
        (11, 5),
        (13, 5),
        (12, 16),
        (16, 7),
        (0, 7),
        (3, 16),
        (5, 7),
        (19, 10),
        (19, 12),
        (15, 16),
        (19, 11),
        (3, 17),
        (3, 5),
        (5, 16),
        (7, 14),
        (18, 18),
        (3, 13),
        (1, 5),
        (13, 18),
        (1, 4),
        (13, 19),
        (0, 6),
        (1, 3),
        (2, 3),
        (14, 16),
        (10, 2),
        (10, 1),
        (1, 2),
        (3, 3),
        (0, 12),
        (6, 14),
        (3, 6),
        (4, 3),
        (0, 3),
        (16, 18),
        (0, 4),
        (0, 5),
        (1, 1),
        (3, 7),
        (3, 10),
        (14, 19),
        (0, 13),
        (12, 18),
        (1, 0),
        (10, 0),
        (2, 12),
    ]


class BadTestSquarePuzzle7379886256663183349(
        _square_base.SquareBase, _base.BaseTestPuzzleCreation):
    puzzle_kwargs = dict(_square_base.SquareBase.puzzle_kwargs, **{
        'seed': 7379886256663183349,
    })


class BadTestKeySequenceSquarePuzzle7379886256663183349(
        _base.BaseTestBadKeySequencePuzzleCreation,
        BadTestSquarePuzzle7379886256663183349):
    key_sequence = [
        (10, 10),
        (9, 10),
        (8, 10),
        (10, 11),
        (10, 12),
        (9, 11),
        (7, 10),
        (11, 11),
        (10, 13),
        (11, 10),
        (10, 9),
        (11, 9),
        (10, 14),
        (10, 15),
        (6, 10),
        (5, 10),
        (4, 10),
        (12, 10),
        (13, 10),
        (3, 10),
        (10, 16),
        (10, 17),
        (2, 10),
        (1, 10),
        (10, 18),
        (14, 10),
        (11, 12),
        (10, 8),
        (10, 7),
        (10, 6),
        (0, 10),
        (15, 10),
        (12, 11),
        (16, 10),
        (10, 5),
        (9, 9),
        (9, 5),
        (17, 10),
        (8, 5),
        (11, 13),
        (7, 5),
        (18, 10),
        (9, 8),
        (6, 5),
        (13, 11),
        (5, 5),
        (4, 5),
        (12, 12),
        (5, 4),
        (5, 3),
        (8, 9),
        (6, 4),
        (19, 10),
        (5, 2),
        (10, 19),
        (3, 11),
        (3, 5),
        (5, 11),
        (5, 12),
        (5, 13),
        (4, 4),
        (6, 3),
        (18, 11),
        (19, 11),
        (2, 5),
        (5, 14),
        (4, 11),
        (5, 1),
        (5, 15),
        (5, 16),
        (6, 11),
        (1, 5),
        (5, 17),
        (0, 5),
        (4, 12),
        (5, 0),
        (5, 18),
        (5, 19),
        (4, 1),
        (18, 12),
        (3, 1),
        (0, 9),
        (6, 2),
        (18, 13),
        (9, 6),
        (2, 1),
        (9, 18),
        (3, 0),
        (2, 0),
        (2, 2),
        (1, 9),
        (7, 2),
        (3, 9),
        (4, 0),
        (3, 8),
        (9, 17),
        (17, 12),
        (9, 19),
        (4, 2),
        (3, 7),
        (10, 4),
        (14, 11),
        (4, 19),
        (0, 6),
        (2, 11),
        (18, 14),
        (19, 13),
        (4, 3),
        (0, 7),
        (9, 12),
        (15, 11),
        (2, 9),
        (19, 14),
        (4, 18),
        (19, 12),
        (6, 18),
        (8, 2),
        (17, 11),
        (2, 3),
        (0, 8),
        (3, 2),
        (9, 2),
        (7, 18),
        (2, 7),
        (9, 1),
        (9, 0),
        (3, 18),
        (3, 3),
        (2, 18),
        (1, 11),
        (1, 3),
        (1, 18),
        (0, 3),
        (6, 9),
        (7, 11),
        (3, 4),
        (0, 11),
        (9, 16),
        (8, 11),
        (16, 11),
        (6, 8),
        (2, 8),
        (6, 7),
        (9, 4),
        (2, 19),
        (19, 9),
        (19, 8),
        (0, 4),
        (0, 18),
        (11, 16),
        (19, 7),
        (19, 6),
        (1, 4),
        (19, 5),
        (3, 19),
        (3, 12),
        (7, 9),
        (2, 4),
        (19, 4),
        (19, 3),
        (4, 13),
        (8, 6),
        (7, 3),
        (19, 2),
        (12, 16),
        (9, 7),
        (6, 12),
        (1, 8),
        (13, 9),
        (13, 16),
        (16, 9),
        (13, 8),
        (13, 7),
        (9, 14),
        (16, 8),
        (8, 14),
        (7, 4),
        (11, 6),
        (14, 16),
        (1, 19),
        (8, 1),
        (8, 0),
        (5, 9),
        (0, 19),
        (6, 17),
        (7, 14),
        (4, 9),
        (16, 7),
        (13, 6),
        (19, 1),
        (16, 6),
        (11, 8),
        (16, 5),
        (13, 5),
        (11, 19),
        (8, 4),
        (9, 13),
        (19, 0),
        (12, 13),
        (13, 4),
    ]


class BadTestSquarePuzzle7651849153216427233(
        _square_base.SquareBase, _base.BaseTestPuzzleCreation):
    puzzle_kwargs = dict(_square_base.SquareBase.puzzle_kwargs, **{
        'seed': 7651849153216427233,
    })


class BadTestKeySequenceSquarePuzzle7651849153216427233(
        _base.BaseTestBadKeySequencePuzzleCreation,
        BadTestSquarePuzzle7651849153216427233):
    key_sequence = [
        (10, 10),
        (9, 10),
        (8, 10),
        (9, 9),
        (11, 10),
        (8, 11),
        (10, 11),
        (9, 8),
        (11, 11),
        (8, 9),
        (11, 9),
        (11, 8),
        (9, 11),
        (10, 9),
        (10, 8),
        (7, 11),
        (6, 11),
        (5, 11),
        (8, 8),
        (12, 11),
        (6, 12),
        (7, 10),
        (6, 13),
        (12, 12),
        (8, 7),
        (12, 9),
        (13, 9),
        (7, 12),
        (11, 7),
        (12, 10),
        (10, 12),
        (13, 12),
        (11, 12),
        (12, 8),
        (4, 11),
        (6, 14),
        (14, 9),
        (15, 9),
        (11, 13),
        (11, 6),
        (15, 10),
        (8, 12),
        (11, 14),
        (11, 15),
        (14, 8),
        (5, 13),
        (12, 14),
        (5, 10),
        (9, 7),
        (10, 7),
        (16, 10),
        (12, 13),
        (7, 9),
        (12, 7),
        (6, 15),
        (5, 9),
        (7, 13),
        (11, 16),
        (9, 12),
        (14, 7),
        (15, 8),
        (5, 15),
        (6, 10),
        (17, 10),
        (15, 7),
        (4, 13),
        (5, 12),
        (9, 6),
        (4, 10),
        (5, 14),
        (13, 8),
        (6, 9),
        (18, 10),
        (10, 6),
        (11, 17),
        (10, 16),
        (11, 18),
        (9, 16),
        (13, 10),
        (17, 9),
        (13, 13),
        (3, 13),
        (10, 15),
        (4, 12),
        (17, 11),
        (16, 11),
        (11, 19),
        (3, 12),
        (19, 10),
        (10, 17),
        (15, 6),
        (3, 11),
        (17, 8),
        (13, 11),
        (7, 7),
        (17, 7),
        (16, 9),
        (11, 5),
        (8, 16),
        (14, 6),
        (18, 9),
        (7, 8),
        (17, 6),
        (15, 11),
        (11, 4),
        (16, 8),
        (3, 10),
        (3, 14),
        (4, 14),
        (8, 13),
        (11, 3),
        (17, 5),
        (18, 5),
        (11, 2),
        (12, 4),
        (16, 7),
        (13, 4),
        (16, 6),
        (3, 15),
        (14, 10),
        (2, 14),
        (3, 16),
        (12, 3),
        (3, 17),
        (1, 14),
        (4, 15),
        (13, 7),
        (13, 6),
        (11, 1),
        (14, 4),
        (10, 4),
        (6, 16),
        (3, 18),
        (6, 17),
        (9, 4),
        (10, 5),
        (10, 2),
        (8, 4),
        (10, 19),
        (15, 4),
        (12, 6),
        (7, 4),
        (12, 5),
        (4, 16),
        (15, 3),
        (6, 18),
        (9, 2),
        (6, 4),
        (16, 12),
        (5, 16),
        (3, 19),
        (15, 2),
        (18, 8),
        (13, 3),
        (18, 7),
        (10, 13),
        (13, 14),
        (19, 5),
        (19, 8),
        (18, 11),
        (1, 13),
        (1, 12),
        (4, 17),
        (10, 3),
        (5, 4),
        (16, 13),
        (13, 5),
        (19, 9),
        (4, 19),
        (19, 11),
        (11, 0),
        (4, 4),
        (16, 14),
        (12, 18),
        (14, 5),
        (14, 3),
        (15, 1),
        (16, 15),
        (9, 19),
        (16, 2),
        (8, 19),
        (13, 18),
        (2, 13),
        (9, 15),
        (12, 17),
        (3, 9),
        (19, 7),
        (0, 13),
        (12, 19),
        (6, 19),
        (2, 12),
        (12, 16),
        (17, 14),
        (9, 1),
        (19, 4),
        (9, 17),
        (16, 3),
        (5, 19),
        (3, 8),
        (15, 14),
    ]
