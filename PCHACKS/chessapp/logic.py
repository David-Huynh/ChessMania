from stockfish import Stockfish
import chess

# you should install the stockfish engine in your operating system globally or specify path to binary file in class constructor
stockfish = Stockfish('/Users/faizaanmadhani/Desktop/PCHACKS/chessapp/stockfish-10-mac/Mac/stockfish-10-64')

#Initialize board
board = chess.Board()
legalMove = board.legal_moves

# set position by FEN:
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")



bestmove= stockfish.get_best_move()



