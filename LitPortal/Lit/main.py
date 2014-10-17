from LitGame import LitGame

if __name__ == "__main__":

    litgame = LitGame()
    litgame.initializeGame()
    while not litgame.isGameOver():
        litgame.playNextMove()
