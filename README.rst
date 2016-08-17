Slithering solver
=====

A solver for Slithering puzzles

So far, it can only create Square and Hexagonal puzzles:

.. role:: python(code)
   :language: python

Square:

.. code-block:: python

  import square_puzzle
  puzzle = square_puzzle.SquarePuzzle(20, 20)
  puzzle.create_random_puzzle()
  puzzle.create_svg(25)

.. image:: demo/SquarePuzzle.png?raw=True

`SVG image
<demo/SquarePuzzle.svg>`_

Hexagonal:

.. code-block:: python

  import hexagonal_puzzle
  puzzle = hexagonal_puzzle.HexagonalPuzzle(20, 20)
  puzzle.create_random_puzzle()
  puzzle.create_svg(25)

.. image:: demo/HexagonalPuzzle.png?raw=True

`SVG image
<demo/HexagonalPuzzle.svg>`_
