#!/usr/bin/env python3
"""A small terminal chess game with optional Stockfish UCI opponent."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, TypeVar

import chess
import chess.engine


WELCOME = "Chess with code by the Stockfish authors. For Sofia"
PIECE_ART = {
    chess.PAWN: ("  x  ", " /x\\ ", " /x\\ "),
    chess.KNIGHT: (" /x  ", "/xxx ", "\\xxx/"),
    chess.BISHOP: ("  x  ", " /x\\ ", "/xxx\\"),
    chess.ROOK: ("x x x", " |x| ", " |x| "),
    chess.QUEEN: ("x x x", "\\xxx/", " xxx "),
    chess.KING: ("  x  ", " \\x/ ", " xxx "),
}
ENGINE_SECONDS = (0.25, 1.0, 3.0)
Choice = TypeVar("Choice")


def parse_move(board: chess.Board, text: str) -> chess.Move:
    """Parse a legal UCI or SAN move, raising ValueError for invalid input."""
    text = text.strip()
    try:
        move = chess.Move.from_uci(text)
        if move in board.legal_moves:
            return move
    except ValueError:
        pass

    try:
        return board.parse_san(text)
    except ValueError as exc:
        raise ValueError("That is not a legal move. Enter a move such as e2e4 or Nf3.") from exc


def render_board(board: chess.Board) -> str:
    """Return a compact, ASCII-only board with small piece silhouettes."""
    border = "  +" + "+".join("-----" for _ in range(8)) + "+"
    lines = [border]
    for rank in range(7, -1, -1):
        cells = []
        for file_index in range(8):
            piece = board.piece_at(chess.square(file_index, rank))
            if piece is None:
                cells.append(("     ",) * 3)
            else:
                marker = "+" if piece.color == chess.WHITE else "#"
                cells.append(
                    tuple(line.replace("x", marker) for line in PIECE_ART[piece.piece_type])
                )
        for art_row in range(3):
            label = f"{rank + 1} " if art_row == 1 else "  "
            lines.append(f"{label}|" + "|".join(cell[art_row] for cell in cells) + "|")
        lines.append(border)
    lines.append("   a     b     c     d     e     f     g     h")
    return "\n".join(lines)


def _game_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_stockfish(directory: Path | None = None) -> Path | None:
    root = directory or _game_directory()
    candidates = (root / "stockfish.exe", root / "src" / "stockfish.exe")
    return next((path for path in candidates if path.is_file()), None)


def find_syzygy(directory: Path | None = None) -> Path | None:
    root = directory or _game_directory()
    candidates = (root / "Syzygy345", root.parent / "Syzygy345")
    return next(
        (
            path
            for path in candidates
            if path.is_dir() and any(path.glob("*.rtbw")) and any(path.glob("*.rtbz"))
        ),
        None,
    )


def _ask_choice(
    prompt: str, choices: dict[str, Choice], input_func: Callable[[str], str]
) -> Choice | None:
    while True:
        answer = input_func(prompt).strip().lower()
        if answer in choices:
            return choices[answer]
        if answer in ("q", "quit"):
            return None
        print(f"Choose {', '.join(choices)} or enter q to go back.")


def _game_over_message(board: chess.Board) -> str:
    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        return f"Checkmate. {winner} wins."
    if board.is_stalemate():
        return "Draw by stalemate."
    if board.is_insufficient_material():
        return "Draw by insufficient material."
    if board.is_fivefold_repetition():
        return "Draw by fivefold repetition."
    if board.is_seventyfive_moves():
        return "Draw by the 75-move rule."
    if board.can_claim_threefold_repetition():
        return "A draw can be claimed by threefold repetition."
    if board.can_claim_fifty_moves():
        return "A draw can be claimed by the 50-move rule."
    return "Game over."


def _play_game(
    versus_engine: bool,
    human_color: chess.Color,
    engine: chess.engine.SimpleEngine | None,
    engine_seconds: float,
    input_func: Callable[[str], str],
) -> None:
    board = chess.Board()

    while True:
        print()
        print(render_board(board))
        side = "White" if board.turn == chess.WHITE else "Black"
        turn = len(board.move_stack) // 2 + 1
        status = f"Move {turn} | {side} to move"
        if board.is_check():
            status += " | CHECK"
        print(status)

        if board.is_game_over():
            print(_game_over_message(board))
            return

        if versus_engine and board.turn != human_color:
            assert engine is not None
            print("Stockfish is thinking...")
            result = engine.play(board, chess.engine.Limit(time=engine_seconds))
            if result.move is None:
                raise chess.engine.EngineError("Stockfish did not return a move.")
            san = board.san(result.move)
            board.push(result.move)
            print(f"Stockfish plays {san}.")
            continue

        try:
            text = input_func(f"{side} move (or help): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to the main menu.")
            return

        command = text.lower()
        if command in ("q", "quit"):
            return
        if command == "help":
            print("Moves: e2e4, e4, or Nf3. Commands: undo, resign, draw, quit.")
            continue
        if command == "resign":
            winner = "Black" if board.turn == chess.WHITE else "White"
            print(f"{side} resigns. {winner} wins.")
            return
        if command == "draw":
            if board.can_claim_draw():
                print("Draw claimed.")
                return
            print("A draw cannot be claimed in this position.")
            continue
        if command == "undo":
            plies = 2 if versus_engine else 1
            if len(board.move_stack) < plies:
                print("There are no moves to undo yet.")
                continue
            for _ in range(plies):
                board.pop()
            continue

        try:
            move = parse_move(board, text)
        except ValueError as exc:
            print(exc)
            continue
        board.push(move)


def run_game(input_func: Callable[[str], str] = input) -> None:
    print(WELCOME)
    while True:
        print("\n1. Human vs. human")
        print("2. Play Stockfish")
        print("3. Quit")
        mode = _ask_choice(
            "Choose an option: ",
            {"1": "human", "2": "engine", "3": "quit"},
            input_func,
        )
        if mode is None or mode == "quit":
            return
        if mode == "human":
            _play_game(False, chess.WHITE, None, 0, input_func)
            continue

        stockfish = find_stockfish()
        if stockfish is None:
            print("Stockfish was not found. Build it with build.bat or choose human vs. human.")
            continue

        color = _ask_choice(
            "Play as 1. White or 2. Black (q to go back): ",
            {"1": chess.WHITE, "2": chess.BLACK},
            input_func,
        )
        if color is None:
            continue
        strength = _ask_choice(
            "Engine speed: 1. Quick  2. Normal  3. Strong (q to go back): ",
            {"1": "quick", "2": "normal", "3": "strong"},
            input_func,
        )
        if strength is None:
            continue
        seconds = {
            "quick": ENGINE_SECONDS[0],
            "normal": ENGINE_SECONDS[1],
            "strong": ENGINE_SECONDS[2],
        }[strength]

        try:
            with chess.engine.SimpleEngine.popen_uci(str(stockfish), timeout=10) as engine:
                options: dict[str, object] = {"Threads": 1, "Hash": 64}
                syzygy = find_syzygy()
                if syzygy is not None and "SyzygyPath" in engine.options:
                    options["SyzygyPath"] = str(syzygy)
                    options["SyzygyProbeLimit"] = 5
                    print(f"Using five-piece Syzygy tablebases: {syzygy}")
                else:
                    print("No Syzygy tablebases found; Stockfish will play without them.")
                engine.configure(options)
                print(f"Playing Stockfish ({seconds:g} second(s) per move).")
                _play_game(True, color, engine, seconds, input_func)
        except (OSError, chess.engine.EngineError, chess.engine.EngineTerminatedError) as exc:
            print(f"Could not run Stockfish: {exc}")


def main() -> int:
    try:
        run_game()
    except EOFError:
        print("\nGoodbye.")
    except KeyboardInterrupt:
        print("\nGoodbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
