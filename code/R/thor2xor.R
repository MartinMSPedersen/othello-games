library(stringr)

tournaments <- NULL
players <- NULL
DEBUG <- FALSE

get_tournaments <- function(filename) {
  f <- file(filename, "rb", raw = TRUE)
  tournament_input <<- as.integer(readBin(f, "raw", file.size(filename)))
  close(f)
  idx <- 17
  while (idx < file.size(filename)) {
      name <- tournament_input[idx:(idx+25)]
    if (any(name == 0)) {
      name <- name[1:(which(name == 0)[[1]]-1)]
    }
    name <- intToUtf8(name)
    tournaments <<- append(tournaments, name)
    idx <- idx + 26
  }
}

get_players <- function(filename) {
  f <- file(filename, "rb", raw = TRUE)
  players_input <<- as.integer(readBin(filename, "raw", file.size(filename)))
  close(f)
  idx <- 17
  while (idx < file.size(filename)) {
    name <- players_input[idx:(idx+19)]
    if (any(name == 0)) {
      name <- name[1:(which(name == 0)[[1]]-1)]
    }
    name <- intToUtf8(name)
    players <<- append(players, name)
    idx <- idx + 20
  }
}

setwd("/home/tusk/gits/thor2sgf/games/thor/")
get_tournaments("WTHOR.TRN")
get_players("WTHOR.JOU")

for (game_file in list.files(pattern = "*.wtb")) {
  f <- file(game_file, "rb", raw = TRUE)
  game_input <- as.integer(readBin(f, "raw", file.size(game_file)))
  close(f)
  year <- str_replace_all(game_file, "[^0-9]", "")
  
  file_creation_date <- c(game_input[[1]],game_input[[2]],"-",game_input[[3]],"-",game_input[[4]])
  n1 <- game_input[[8]] 
  n1 <- n1*256 + game_input[[7]] 
  n1 <- n1*256 + game_input[[6]] 
  n1 <- n1*256 + game_input[[5]] 
  
  n2 <- game_input[[10]] 
  n2 <- n2*256 + game_input[[9]] 
  
  year <- game_input[[12]] 
  year <- year*256 + game_input[[11]]
  
  p1 <- game_input[[13]]
  p2 <- game_input[[14]]
  p3 <- game_input[[15]]
  
  
  if (DEBUG) {
    cat("game_input:\n", sep="")
    cat("  File creation data:   ",file_creation_date,"\n", sep = "")
    cat("  Number of records n1: ",n1,"\n", sep = "")
    cat("  Number of records n2: ",n2,"\n", sep = "")
    cat("  Year:                 ",year,"\n", sep = "")
    cat("  Size game board;      ",p1,"\n", sep = "")
    cat("  Type of parts:        ",p2,"\n", sep = "")
    cat("  Depth:                ",p3,"\n", sep = "")
  }
  
  for (idx in 0:(n1-1)) {
  #for (idx in 0:1)  {
    tournament <- game_input[[idx*68 + 18]]
    tournament <- tournament*256 + game_input[[idx*68 + 17]] + 1
    black_player_id <- game_input[[idx*68 + 20]]
    black_player_id <- black_player_id*256 + game_input[[idx*68 + 19]] + 1
    white_player_id <- game_input[[idx*68 + 22]]
    white_player_id <- white_player_id*256 + game_input[[idx*68 + 21]] + 1
    black_score <- game_input[[idx*68 + 23]]
    white_score <- 64 - black_score
    moves <- game_input[(idx*68+25):(idx*68+83)]
    if (any(moves == 0)) {
      moves <- moves[1:(which(moves == 0)[[1]]-1)]
    }
  
    moves <- sapply(moves, function(move) {
               paste0(LETTERS[[as.integer(substr(move,2,2))]],substr(move,1,1))
             })
    
      if (tournament <= length(tournaments)) {
        cat("    Tournament:        ",tournaments[[tournament]]," - ",year,"\n", sep = "")
      } else {
        cat("    Tournament:        ",tournament,"\n",sep="")
      } 
      if (black_player_id <= length(players)) {
        cat("    Black player:      ",players[[black_player_id]],"\n",sep="")
      } else {
        cat("    Black player:      ",black_player_id,"\n",sep="")
      }
      if (white_player_id <= length(players)) {
        cat("    White player:      ",players[[white_player_id]],"\n",sep="")
      } else {
        cat("    White player:      ",white_player_id,"\n",sep="")
      }
      cat("    Score:             ",black_score,"-",white_score,"\n",sep="")
      cat("    Moves:             ",moves,"\n",sep="")
      cat("============================\n", sep = "")
    
  }
}