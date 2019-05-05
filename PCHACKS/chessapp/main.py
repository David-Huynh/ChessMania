# import flask dependencies
from flask import *
from stockfish import Stockfish
import chess
import os

# initialize the flask app
app = Flask(__name__)


# function for responses
def results():

    stockfish = Stockfish('/Users/faizaanmadhani/Desktop/PCHACKS/chessapp/stockfish-10-mac/Mac/stockfish-10-64')

    board = chess.Board()
    legalMove = board.legal_moves

    # build a request object
    req = request.get_json(force=True)

    oldPosition = req.get('queryResult').get('parameters').get('oldPosition')
    newPosition = req.get('queryResult').get('parameters').get('newPosition')
    checkmate = req.get('queryResult').get('queryText')



    # fetch action from json
    action = req.get('queryResult').get('action')

    if (os.stat("fenState.txt").st_size == 0):
        #If file fenState is empty, Write initial state of board to fenState
        writeFile = open("fenState.txt", "w")
        strBoardFen = board.fen()
        writeFile.write(str(strBoardFen))
        writeFile.close()

        #Then, read the state of the file
        readFile = open("fenState.txt", "r")
        boardState = readFile.read()
        board = chess.Board(boardState)

    else:
        #Otherwise, Read initial state of board
        readFile = open("fenState.txt", "r")
        boardState = readFile.read()
        board = chess.Board(boardState)


    if (chess.Move.from_uci(str(oldPosition + newPosition)) in board.legal_moves):
        board.push_san(oldPosition+newPosition)

        #Get Fen position
        fenPosition = board.fen()

        #Engine makes their move
        stockfish.set_fen_position(fenPosition)
        bestmove = stockfish.get_best_move()
        board.push_san(bestmove)
        finalReturn= "I have moved " + bestmove

        #Write State to file (Debugging)
        writeFile = open("state.txt", "w")
        strBoard = str(board)
        writeFile.write(strBoard)
        writeFile.close()

        #Write FenState to file (State saving between moves)
        writeFile = open("fenState.txt", "w")
        boardFen = board.fen()
        strBoardFen = boardFen
        writeFile.write(strBoardFen)
        writeFile.close()

        if (str(checkmate) == 'checkmate' and board.is_checkmate() == True):
            finalReturn="Checkmate!, and game over"
        elif(board.is_checkmate() == False and str(checkmate) == 'checkmate'):
            finalReturn="You Can't Checkmate bro"

    else:
        finalReturn = "This move is wrong"

        writeFile = open("move.txt", "w+")
        Position = str(oldPosition + newPosition)
        writeFile.write(Position)
        writeFile.close()




    # return a fulfillment response
    return {'fulfillmentText': finalReturn}


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    Make_Response_Var = make_response(jsonify(results()))
    return Make_Response_Var

# run the app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6000, debug=True)
