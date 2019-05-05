# import flask dependencies
from flask import *
from stockfish import Stockfish
import chess
import os

singleplayer_Var = False
multiplayer_Var = False

# initialize the flask app
app = Flask(__name__)

#Handle the logic from all of the functions
def logicHandler():
    global singleplayer_Var
    if (gameCheck() == 'singleplayer' or 'single'):
        if (singleplayer_Var == False):
            singleplayer_Var = True
            return {'fulfillmentText': 'Okay single player is selected'}
        elif(singleplayer_Var==True):
            return results()
    elif(gameCheck() == 'multiplayer' or 'multi'):
        multiplayer_Var = True
        return multiplayer()

#Check the gametype
def gameCheck():

    if (os.stat("gameType.txt").st_size == 0):
        req = request.get_json(force=True)
        mode = req.get('queryResult').get('parameters').get('player')
        writeFile = open("gameType", "w")
        writeFile.write(str(mode))
        writeFile.close();
    else:
        readFile = open('queryResult', "r")
        mode = readFile.read()
        readFile.close()

    return mode

def multiplayer():

    board = chess.Board()
    legalMove = board.legal_moves

    # build a request object
    req = request.get_json(force=True)

    oldPositionPlayer1 = req.get('queryResult').get('parameters').get('oldPosition')
    newPositionPlayer1 = req.get('queryResult').get('parameters').get('newPosition')
    checkmate = req.get('queryResult').get('queryText')

    # fetch action from json
    action = req.get('queryResult').get('action')

    if (os.stat("fenState.txt").st_size == 0):
        # If file fenState is empty, Write initial state of board to fenState
        writeFile = open("fenState.txt", "w")
        strBoardFen = board.fen()
        writeFile.write(str(strBoardFen))
        writeFile.close()

        # Then, read the state of the file
        readFile = open("fenState.txt", "r")
        boardState = readFile.read()
        board = chess.Board(boardState)

    else:
        # Otherwise, Read initial state of board
        readFile = open("fenState.txt", "r")
        boardState = readFile.read()
        readFile.close()
        board = chess.Board(boardState)

    if (chess.Move.from_uci(str(oldPositionPlayer1 + newPositionPlayer1)) in board.legal_moves):
        board.push_san(oldPositionPlayer1 + newPositionPlayer1)

        # Get Fen position
        fenPosition = board.fen()

        # Write State to file (Debugging)
        writeFile = open("state.txt", "w")
        strBoard = str(board)
        writeFile.write(strBoard)
        writeFile.close()

        # Write FenState to file (State saving between moves)
        writeFile = open("fenState.txt", "w")
        boardFen = board.fen()
        strBoardFen = boardFen
        writeFile.write(strBoardFen)
        writeFile.close()

        if (str(checkmate) == 'checkmate' and board.is_checkmate() == True):
            finalReturn = "Checkmate!, and game over"
        elif (board.is_checkmate() == False and str(checkmate) == 'checkmate'):
            finalReturn = "You Can't Checkmate bro"

    else:
        finalReturn = "This move is wrong"

        writeFile = open("move.txt", "w+")
        Position = str(oldPositionPlayer1 + newPositionPlayer1)
        writeFile.write(Position)
        writeFile.close()



    # return a fulfillment response
    return {'fulfillmentText': finalReturn}


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


    if (chess.Move.from_uci(str(oldPosition) + str(newPosition)) in board.legal_moves):
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
    return make_response(jsonify(logicHandler()))

# run the app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6000, debug=True)
