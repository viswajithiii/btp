import random
from Card import Card
from LitPlayer import LitPlayer
from LitPlay import LitPlay

class LitGame:
    """
    A class for a particular game of Literature.
    """

    def __init__(self, n_players = 4, config = "default"):

        self.players = [] #Should be a list of LitPlayer elements.
        for i in range(n_players):
            self.players.append(LitPlayer(self,i,i%2))

        self.config = config
        if self.config == "default":
            self.setnames = ["Clubs Minor", "Clubs Major", "Diamonds Minor", "Diamonds Major", "Hearts Minor", "Hearts Major", "Spades Minor", "Spades Major"]

        #The won/lost/inplay status of each set
        #-1 if it's still in play.
        #else the number of the team that won it.
        self.setstatus = []
        for i in range(8):
            self.setstatus.append(-1)

    def getSetFromCard(self,card):

        #For default config
        toreturn = card.suit*2
        if card.value >= 6: #major
            toreturn += 1
        return toreturn
        
    def getSetName(self,set_index):
        return self.setnames[set_index]
        
    def distributeCards(self):

        cards = []
        for suit in range(4):
            for value in range(13):
                cards.append(Card(suit,value))

        player_i = 0 
        while len(cards) > 0:
            rand_i = random.randint(0,len(cards)-1)
            self.players[player_i].addCard(cards[rand_i])
            del cards[rand_i]
            player_i = (player_i+1)%(len(self.players))

    def printCards(self):
        for player in self.players:
            player.printCards()

    def isGameOver(self):
        for status in self.setstatus:
            if status == -1:
                return False
        return True

    def initialiseTeamScores(self):
        self.teamscores = {}
        for player in self.players:
            self.teamscores[player.team] = 0

    def verifySetWon(self,team,setno):

        assert self.setstatus[setno] == -1

        targetcount = 6 if setno%2 == 0 else 7
        realcount = 0
        for player in self.players:
            if player.team == team:
                realcount += len(player.cards[setno])
            
        return realcount == targetcount

    def getCompletedPlayers(self):
        return [i for i in range(len(self.players)) if self.players[i].hasCompleted()]

    def startGame(self):
        self.distributeCards()
        self.printCards()

        turn = random.randint(0,len(self.players)-1) #Initial turn goes to a random player
        self.initialiseTeamScores()
        self.playhistory = []

        while not self.isGameOver():
            print 'Number of moves: ', len(self.playhistory)

            #Ask everyone if they'd like to put down a set
            for (player_i,player) in enumerate(self.players):
                setno = player.putDownSet()
                if setno is not None:
                    if self.verifySetWon(player.team, setno):
                        self.setstatus[setno] = player.team 
                        self.teamscores[player.team] += (6 if setno%2 == 0 else 7)
                        turn = player_i

            if self.players[turn].hasCompleted():
                turn = random.choice(self.getCompletedPlayers())

            (target,card) = self.players[turn].getQuery()

            if target.hasCard(card):
                target.removeCard(card)
                self.players[turn].addCard(card)                
                self.playhistory.append(LitPlay(self.players[turn],target,card,True))
            else:
                self.playhistory.append(LitPlay(self.players[turn],target,card,False))
                turn = self.players.index(target)
