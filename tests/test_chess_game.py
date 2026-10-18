import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import chess

from chess_game import _play_game, find_stockfish, find_syzygy, parse_move, render_board


class ParseMoveTests(unittest.TestCase):
    def test_parses_uci_and_san(self):
        board = chess.Board()
        self.assertEqual(parse_move(board, "e2e4"), chess.Move.from_uci("e2e4"))
        self.assertEqual(parse_move(board, "e4"), chess.Move.from_uci("e2e4"))

    def test_rejects_illegal_moves(self):
        with self.assertRaisesRegex(ValueError, "not a legal move"):
            parse_move(chess.Board(), "e2e5")

    def test_parses_promotion_and_castling(self):
        promotion_board = chess.Board("7k/P7/8/8/8/8/8/7K w - - 0 1")
        self.assertEqual(
            parse_move(promotion_board, "a7a8q"),
            chess.Move.from_uci("a7a8q"),
        )

        castling_board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        self.assertEqual(parse_move(castling_board, "O-O"), chess.Move.from_uci("e1g1"))


class RenderBoardTests(unittest.TestCase):
    def test_renders_piece_silhouettes_in_ascii(self):
        rendered = render_board(chess.Board())
        self.assertIn("a     b     c     d     e     f     g     h", rendered)
        self.assertIn("  +  ", rendered)
        self.assertIn("  #  ", rendered)
        self.assertIn("+ + +", rendered)
        self.assertIn("# # #", rendered)
        self.assertEqual(len(rendered.splitlines()), 34)
        self.assertEqual(max(map(len, rendered.splitlines())), 51)


class GameFlowTests(unittest.TestCase):
    def test_threefold_repetition_is_claimable_not_automatically_ended(self):
        moves = iter(
            (
                "Nf3",
                "Nf6",
                "Ng1",
                "Ng8",
                "Nf3",
                "Nf6",
                "Ng1",
                "Ng8",
                "draw",
            )
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            _play_game(False, chess.WHITE, None, 0, lambda _prompt: next(moves))

        self.assertIn("Draw claimed.", output.getvalue())
        self.assertNotIn("A draw can be claimed by threefold repetition.", output.getvalue())


class EnginePathTests(unittest.TestCase):
    def test_finds_stockfish_in_source_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine = root / "src" / "stockfish.exe"
            engine.parent.mkdir()
            engine.touch()
            self.assertEqual(find_stockfish(root), engine)

    def test_finds_only_a_complete_syzygy_pair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tables = root / "Syzygy345"
            tables.mkdir()
            (tables / "KQvK.rtbw").touch()
            self.assertIsNone(find_syzygy(root))

            (tables / "KQvK.rtbz").touch()
            self.assertEqual(find_syzygy(root), tables)


if __name__ == "__main__":
    unittest.main()
