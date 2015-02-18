from LitGame import LitGame
import matplotlib.pyplot as plt

if __name__ == "__main__":

    gamelengths = []
    litgame = LitGame(n_players=4,n_sets = 8,verbose=True)
    litgame.initializeGame()
    while not litgame.isGameOver():
        litgame.players[0].reasoner.printStatus()
#        raw_input()
        litgame.playNextMove()
    print 'Game over! Total number of moves: ' + unicode(len(litgame.playhistory))
    litgame.printCards()
    print litgame.setstatus
