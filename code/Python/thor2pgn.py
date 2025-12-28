import os
import struct
import glob
import argparse
import json
from dataclasses import dataclass

from utils.utils_logger import setup_logger, configure_logging

# Global lists to store tournament and player names

TOURNAMENT_NAMES_FILENAME = "WTHOR.TRN"
PLAYER_NAMES_FILENAME = "WTHOR.JOU"
SAVE_IN_SAME_DIR = "..."
DEFAULT_DATA_DIR = "../../wthor"

@dataclass
class THORMetadata:
    file_creation_date: str
    n1: int
    n2: int
    year_val: int
    size_game_board: int    # p1
    type_of_parts: int      # p2
    depth: int              # p3

    def __repr__(self):
        sep = "="*28
        return "\n".join([
            f"{sep}" + "\n"
            f"    File creation date:   {self.file_creation_date}\n"
            f"    Number of records n1: {self.n1}\n"
            f"    Number of records n2: {self.n2}\n"
            f"    Year:                 {self.year_val}\n"
            f"    Size game board;      {self.size_game_board}\n"
            f"    Type of parts:        {self.type_of_parts}\n"
            f"    Depth:                {self.depth}\n"
            f"{sep}"
            ])
    
    def display(self):
        print(self.__repr__())


@dataclass
class THORGame:
    tournament: str
    black_player: str
    white_player: str
    black_score: int
    white_score: int
    moves: list

    def __repr__(self):
       sep = "="*40
       return (
            f"{sep}" + "\n"
            f"    Tournament:        {self.tournament}\n"
            f"    Black player:      {self.black_player}\n"
            f"    White player:      {self.white_player}\n"
            f"    Score:             {self.black_score}-{self.white_score}\n"
            f"    Moves:             {' '.join(self.moves) if self.moves else ''}\n"
            f"{sep}"
            )
    
    def display(self):
        print(self.__repr__())


@dataclass
class PGNGame:
    event: str
    date: str
    black_player: str
    white_player: str
    score: str
    moves: list
    line_index: bool = False
    add_result: bool = False

    def header(self):
        return "\n".join([
            f"[Event \"{self.event}\"]",
            f"[Date \"{self.date}\"]",
            f"[Black \"{self.black_player}\"]",
            f"[White \"{self.white_player}\"]",
            f"[Result \"{self.score}\"]"
        ])
    
    def move_list(self, line_index=None, add_result=None):
        line_index = self.line_index if line_index is None else line_index
        add_result = self.add_result if add_result is None else add_result

        moves_str = ""
        indice = lambda i: (i + 1) if line_index else 2*i+1

        for i in range(len(self.moves) // 2):
            moves_str += f"{indice(i)}. {self.moves[2*i]} {self.moves[2*i+1]}\n"
        if len(self.moves) % 2:
            moves_str += f"{indice(i+1)}. {self.moves[-1]}\n"

        if add_result:
            moves_str += self.score

        return moves_str
        
    def __repr__(self):
        return self.header() + "\n" + self.move_list()


def read_data_file(filename, record_size):
    """Reads the date from the file."""
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found.")
        return -1

    data = []
    try:
        with open(filename, "rb") as f:
            content = f.read()
        
        # Header is 16 bytes
        idx = 16
        file_size = len(content)
        
        while idx < file_size:
            if idx + record_size > file_size:
                break
                
            name_bytes = content[idx : idx + record_size]
            # Find null terminator if any
            if 0 in name_bytes:
                name_bytes = name_bytes[:name_bytes.index(0)]
            
            # Decode name. R's intToUtf8 on bytes suggests Latin-1 mapping (0-255 -> Unicode)
            try:
                name = name_bytes.decode('latin-1')
            except:
                name = name_bytes.decode('utf-8', errors='replace')
                
            data.append(name)
            idx += record_size
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return -1
    
    return data


def get_tournaments(
        path,
        tournament_names_filename = TOURNAMENT_NAMES_FILENAME
        ):
    """Reads the tournament names from the TOURNAMENT_NAMES_FILENAME file."""
    return read_data_file(os.path.join(path, tournament_names_filename), 26)
    

def get_players(
        path,
        player_names_filename = PLAYER_NAMES_FILENAME
):
    """Reads the player names from the PLAYER_NAMES_FILENAME file."""
    return read_data_file(os.path.join(path, player_names_filename), 20)


def extract_meta(game_input):
    # Header parsing
    # n1: 4 bytes at offset 4 (little endian) - Number of games
    n1 = struct.unpack_from("<I", game_input, 4)[0]
    
    # n2: 2 bytes at offset 8 - Number of records (often same as n1 or unused)
    n2 = struct.unpack_from("<H", game_input, 8)[0]
    
    # year: 2 bytes at offset 10
    year_val = struct.unpack_from("<H", game_input, 10)[0]
    
    # p1, p2, p3: bytes at 12, 13, 14
    p1 = game_input[12]
    p2 = game_input[13]
    p3 = game_input[14]

    file_creation_date = f"{game_input[0]}{game_input[1]}-{game_input[2]}-{game_input[3]}"

    return THORMetadata(
        file_creation_date=file_creation_date,
        n1=n1,
        n2=n2,
        year_val=year_val,
        size_game_board=p1,
        type_of_parts=p2,
        depth=p3
    )


def extract_game(game_input, base_offset, meta, tournaments, players):            
    # Tournament: 2 bytes at offset 0 of record
    tournament_id = struct.unpack_from("<H", game_input, base_offset)[0]
    
    # Black player: 2 bytes at offset 2
    black_player_id = struct.unpack_from("<H", game_input, base_offset + 2)[0]
    
    # White player: 2 bytes at offset 4
    white_player_id = struct.unpack_from("<H", game_input, base_offset + 4)[0]
    
    # Black score: 1 byte at offset 6
    black_score = game_input[base_offset + 6]
    white_score = 64 - black_score
    
    # Moves: offset 8 to 67 (60 bytes)
    # R code used a slightly shorter range (59 bytes), but WTHOR standard is 60.
    # We read 60 bytes and stop at the first 0.
    moves_bytes = game_input[base_offset + 8 : base_offset + 68]
    
    real_moves = []
    for m in moves_bytes:
        if m == 0:
            break
        real_moves.append(m)
    
    # Convert moves to standard notation (e.g., F5)
    formatted_moves = []
    for m in real_moves:
        s_m = str(m)
        # WTHOR move format: 10*row + col. 
        # e.g. 56 -> Row 5, Col 6.
        # R logic: substr(move, 2, 2) is col, substr(move, 1, 1) is row.
        # If m=56, "56"[1] is '6', "56"[0] is '5'.
        
        if len(s_m) == 2:
            col_idx = int(s_m[1])
            row_char = s_m[0]
            
            # Convert column index to Letter (1->A, 2->B, ...)
            if 1 <= col_idx <= 8:
                col_char = chr(ord('A') + col_idx - 1)
                formatted_moves.append(f"{col_char}{row_char}")
            else:
                formatted_moves.append(s_m)
        else:
            # Should not happen for valid moves (11-88)
            formatted_moves.append(s_m)

    moves = formatted_moves
    
    # Resolve names
    if tournament_id < len(tournaments):
        tournament = f"{tournaments[tournament_id]} - {meta.year_val}"
    else:
        tournament = str(tournament_id)
    
    if black_player_id < len(players):
        black_player = players[black_player_id]
    else:
        black_player = str(black_player_id)
        
    if white_player_id < len(players):
        white_player = players[white_player_id]
    else:
        white_player = str(white_player_id)

    return THORGame(
        tournament=tournament,
        black_player=black_player,
        white_player=white_player,
        black_score=black_score,
        white_score=white_score,
        moves=moves
    )


def is_wthor_file(filename):
    """Check if the file is a valid WTHOR file by checking the header."""
    return filename.lower().endswith(".wtb")

def is_directory(path):
    """Check if the given path is a directory."""
    return os.path.isdir(path)

def main(args):
    logger = setup_logger("main", debug=args.debug)
    
    if not os.path.exists(args.data_dir):
        logger.error(f"Error: Directory {args.data_dir} does not exist.")
        return

    # Load database files
    tournaments = get_tournaments(args.data_dir)
    if tournaments == -1:
        logger.error(f"File not found or error loading tournament names from {os.path.join(args.data_dir, TOURNAMENT_NAMES_FILENAME)}")
        return
    players = get_players(args.data_dir)
    if players == -1:
        logger.error(f"File not found or error loading player names from {os.path.join(args.data_dir, PLAYER_NAMES_FILENAME)}")
        return
   
    if is_wthor_file(args.file):
        wtb_files = [args.file]
        # Process all .wtb files in the current directory
    elif is_directory(args.file):
        wtb_files = glob.glob("*.wtb", root_dir=args.file)
        filepath = args.file

    logger.debug(f"Found {len(wtb_files)} WTB files to process.")

    ## Save PGN files in a specific directory
    global_filename = None
    if args.save_pgn and args.save_pgn != SAVE_IN_SAME_DIR:
            os.makedirs(os.path.dirname(args.save_pgn), exist_ok=True)
            ## All games saved in a single file
            if os.path.basename(args.save_pgn) != "":
                global_filename = args.save_pgn
                pgn_output = open(args.save_pgn, "w", encoding="utf-8")

    # Loop over WTB file(s)
    for i, game_file in enumerate(wtb_files):
        if not os.path.dirname(game_file):
            game_file = os.path.join(filepath, game_file)

        logger.info(f"file {i+1:03d}: '{game_file}'")

        try:
            with open(game_file, "rb") as f:
                game_input = f.read()
                
            if len(game_input) < 16:
                print(f"Skipping {game_file}: File too small.")
                continue

            ## Open PGN file if saving and not using a global one
            if args.save_pgn and global_filename is None:
                ## Save PGN in the same directory as the WTB file
                if args.save_pgn == SAVE_IN_SAME_DIR:
                    pgn_filepath = os.path.dirname(game_file)
                ## Save the games in this file to a single specified file
                else:
                    pgn_filepath = args.save_pgn
                pgn_filename = os.path.join(
                        pgn_filepath,
                        os.path.splitext(os.path.basename(game_file))[0] + ".pgn"
                    )
                pgn_output = open(pgn_filename, "w", encoding="utf-8")

            
            meta = extract_meta(game_input)
            logger.debug(f"Meta \n" + str(meta))

            # Loop over games
            for idx in range(meta.n1):
                base_offset = 16 + idx * 68
                # Safety check
                if base_offset + 68 > len(game_input):
                    break
                
                # Extract THOR game
                thor_game = extract_game(
                    game_input, base_offset, meta, tournaments, players
                    )
                if args.debug:        
                    logger.debug(f"Game {idx+1:03d}\n" + str(thor_game))

                # Convert to PGN
                pgn_game = PGNGame(
                    event=thor_game.tournament,
                    date=meta.year_val,
                    black_player=thor_game.black_player,
                    white_player=thor_game.white_player,
                    score=f"{thor_game.black_score}-{thor_game.white_score}",
                    moves=thor_game.moves,
                    line_index=args.line_index,
                    add_result=args.add_result
                )
                
                logger.debug("PGN\n" + str(pgn_game))

                if not args.save_pgn and not args.debug:
                    logger.info(f"Game {idx+1:03d} PGN\n" + str(pgn_game) + "\n" + "-"*40 + "\n")
                
                ## Save PGN
                if args.save_pgn:
                    pgn_output.write(str(pgn_game) + "\n")
            
            ## Close PGN file if not using a global one
            if args.save_pgn and global_filename is None:
                pgn_output.close()

        except Exception as e:
            logger.error(f"Error processing {game_file}: {e}")

    ## Close global PGN file if opened
    if args.save_pgn and global_filename:
        pgn_output.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert THOR files to PGN.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-f", "--file", required=True, type=str, help="Specific WTB file to process")
    parser.add_argument("--data-dir", type=str, help=f"Directory containing references files {TOURNAMENT_NAMES_FILENAME} and {PLAYER_NAMES_FILENAME}. By default '{DEFAULT_DATA_DIR}'", default=DEFAULT_DATA_DIR)
    parser.add_argument("--save-pgn", type=str, default=None, const=SAVE_IN_SAME_DIR, nargs="?", help="Output PGN file to save the converted games")
    parser.add_argument("--add-result", action="store_true", help="Add game result at the end of move list in PGN output")
    parser.add_argument("--line-index", action="store_true", help="Set number put in each move line as line index or index of the first move in PGN output")

    args = parser.parse_args()

    configure_logging(debug=args.debug)
    logger = setup_logger(__name__, debug=args.debug)

    logger.debug("Args: " + json.dumps(vars(args), indent=4))

    main(args)
