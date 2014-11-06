from LitGame import LitGame

if __name__ == "__main__":

    litgame = LitGame(n_sets = 2)
    litgame.initializeGame()
    while not litgame.isGameOver():
        litgame.playNextMove()
