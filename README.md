# Chess for the terminal

A simple compact, text-based chess game for Windows. With code by the Stockfish authors. Visual Studio Code and its Copilot wrote the additional code. Thanks to JC and them.
Play over the board with another person or against Stockfish. The game validates legal moves, accepts standard
algebraic notation (for example `Nf3`) and coordinate moves (`g1f3`), and
supports castling, en passant, and promotion.

## Build on Windows

1. Install Python 3.10 or newer.
2. Install [MSYS2](https://www.msys2.org/) and its MINGW64 GCC toolchain and
   make packages. In the MSYS2 MINGW64 terminal, run:

   ```sh
   pacman -S --needed mingw-w64-x86_64-gcc make
   ```

   Add the MSYS2 `mingw64\bin` and `usr\bin` directories to `PATH` before
   opening Command Prompt. Stockfish requires GCC 10 or newer. The old
   MinGW.org GCC 6 compiler is not supported.
3. Open Command Prompt in this folder and run:

   ```bat
   build.bat
   ```

The script builds Stockfish with the bundled neural-network file, runs the
game tests, installs the Python packages listed in `requirements.txt`, and
creates `dist\Chess.exe`, `dist\stockfish.exe`, and
`Chess-portable.zip`. The portable ZIP includes the game, Stockfish, and the
Stockfish license; it does not include the large Syzygy tablebases. Building
Stockfish needs internet access to download its official neural-network file
if it is not already present.

To run from the source folder without building the executable, install the
Python packages and start the game:

```bat
python -m pip install -r requirements.txt
python chess_game.py
```

To play on another computer, copy `Chess-portable.zip` there, extract all its files, and run `Chess.exe`.
Keep `Chess.exe`, `stockfish.exe`, `README.txt`, and `Copying.txt` together
after extracting. The packaged executables include their required runtime
libraries; an additional Python, Stockfish, or MSYS2 installation is not
required. To use optional Syzygy tablebases, place a `Syzygy345` folder next
to the extracted game.

In the game, enter a move such as `e2e4`, `e4`, or `Nf3`. Enter `help` during
a game to see available commands; enter `undo` to take back the last move (or
the last two plies in a game against Stockfish), `resign` to resign, and `quit`
to return to the main menu. An en passant capture or promotion may also be
entered in coordinate notation, for example `e5d6` or `a7a8q`.

The board uses compact, three-line ASCII silhouettes for each piece. Its
dimensions are designed to fit comfortably in a 720p terminal, although the
visible area depends on the terminal's font and window settings.

The engine uses up to five-piece Syzygy tablebases when `Syzygy345` contains
the corresponding `.rtbw` and `.rtbz` files. Tablebases are optional. The
game is playable without Stockfish in human-versus-human mode.

The Stockfish license is included as `Copying.txt` both in the project and in
the portable release.

### How to to play ###

Unix/Linux:

Just run it with ./Chess.exe

Windows:

Just run the Chess.exe

### Endgame libary ###

If you want, you can integrate a 5 pieces endgame library. Just download the files from here:

https://kdrive.infomaniak.com/app/share/1353016/e0d24252-8766-4af6-9a3e-4739c20c1dbd

and put them in the "Syzygy345" Folder.