#  Othello games archive (PGN)

## Last update (15 dec. 2025)
Update adding python script to convert Thor to [PGN](https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm), applied on [the last archive from ffothello.org](https://www.ffothello.org/informatique/la-base-wthor/) (using unzipped files (section "Fichiers non zippés" in French), from 1977 to 2025). This is a kind of convertion from the R code to python, with some new features and improvements.

`pgn_lastest.zip` contains all the game files in PGN format (one file per year, from 1977 to 2025, available in `./png/with_python_code`).

### Generated PNG Format
A PGN file contains one or more games in the following format:

**The generated header**
```
[Event "Event - Year"]
[Date "Year"]
[Black "Black player's name"]
[White "White player's name"]
[Result "Black score-White score"]
```
and then

**The move list**
The number of the line and the presence of the score depends on the arguments `--line-index` and `--add-result` : either the number of the line (1, 2, 3, ..., 30) or the index of the first move in a line (1, 3, 5, ..., 59).
The score, already presents in the header, can be added at the end of the move list.
```
1. F5 D6
3. C3 F3
5. F4 D3
7. C4 G6
9. F6 E6
11. C5 C6
13. D7 D8
15. E7 G5
17. E3 D2
19. G4 H3
21. F7 B5
23. H5 G3
25. B4 B6
27. C8 B8
29. C7 E8
31. F8 G8
33. H4 H6
35. E2 D1
37. C1 A3
39. A6 A5
41. E1 F2
43. G7 C2
45. A4 H8
47. A2 B7
49. F1 B3
51. B1 B2
53. H7 A7
55. A8 A1
57. G1 G2
59. H2 H1
34-30
```

### Description of the script options
```
  -h, --help            show this help message and exit
  --debug               Enable debug mode
  -f FILE, --file FILE  Specific WTB file to process
  --data-dir DATA_DIR   Directory containing references files WTHOR.TRN and WTHOR.JOU. By default '../../wthor'
  --save-pgn [SAVE_PGN] Output PGN file to save the converted games
  --add-result          Add game result at the end of move list in PGN output
  --line-index          Set number put in each move line as line index or index of the first move in PGN output
```

### How to use it:
**Note that you need two specific files** from the archive: [WTHOR.JOU](https://www.ffothello.org/wthor/base/WTHOR.JOU) the player file and [WTHOR.THR](https://www.ffothello.org/wthor/base/WTHOR.TRN) the tournament name file. 

Assuming you are testing the script from the `./code/Python/` directory in a clone of this repo:
- I want to see the PGN translation of a single file (eg : `../../wthor/WTH_1977.wtb`):
```bash
python thor2pgn.py -f ../../wthor/WTH_1977.wtb
```
I get:
```
Game 001 PGN
[Event "World Championship - 1977"]
[Date "1977"]
[Black "Inoue Hiroshi"]
[White "Heiberg Thomas"]
[Result "34-30"]
1. F5 D6
3. C3 F3
5. F4 D3
...
55. A8 A1
57. G1 G2
59. H2 H1

----------------------------------------
...
```

- I want to translate a file in the same directory (I get the file `../../wthor/WTH_1977.pgn`):
```bash
python thor2pgn.py -f ../../wthor/WTH_1977.wtb --save-pgn
```

- I want to set the move index instead of the line index as number in each move line:
```bash
python thor2pgn.py -f ../../wthor/WTH_1977.wtb --line-index
```
I get:
```
Game 001 PGN
[Event "World Championship - 1977"]
[Date "1977"]
[Black "Inoue Hiroshi"]
[White "Heiberg Thomas"]
[Result "34-30"]
1. F5 D6
2. C3 F3
3. F4 D3
...
28. A8 A1
29. G1 G2
30. H2 H1

----------------------------------------
...
```

- I want to add the score at the end of the move list:
```bash
python thor2pgn.py -f ../../wthor/WTH_1977.wtb --add-result
```
I get:
```
Game 001 PGN
[Event "World Championship - 1977"]
[Date "1977"]
[Black "Inoue Hiroshi"]
[White "Heiberg Thomas"]
[Result "34-30"]
1. F5 D6
3. C3 F3
5. F4 D3
...
55. A8 A1
57. G1 G2
59. H2 H1
34-30
----------------------------------------
...
```

- I want to translate all files in the directory and save them in a specific directory (**note**: **don't forget the last slash** in `../../wthor/` and `../../pgn_games/`):
```bash
python thor2pgn.py -f ../../wthor/ --save-pgn ../../pgn_games/
```

- I want to translate all files in a directory and gather all PGN outputs in one file (eg: `../../pgn_games/all_games.pgn`):
```bash
python thor2pgn.py -f ../../wthor/ --save-pgn ../../pgn_games/all_games.pgn
```

## Initial repository
From initial repo [MartinMSPedersen/othello-games]( https://github.com/MartinMSPedersen/othello-games)

http://www.ffothello.org/informatique/la-base-wthor/ contains a large archive of Othello games.
But the games is saved in a format called Thor which is hard to read for humans.

So I have converted the archive into PGN-files and put them here.
