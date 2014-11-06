import random
from Card import Card
from LitPlayer import LitPlayer
from LitPlay import LitPlay

class LitGame:
    """
    A class for a particular game of Literature.
    """

    def __init__(self, n_players = 4, n_sets = 8):


        self.n_sets = n_sets

        self.players = [] #Should be a list of LitPlayer elements.
        for i in range(n_players):
            self.players.append(LitPlayer(self,i,i%2))


        setnames = ["Clubs Minor", "Clubs Major", "Diamonds Minor", "Diamonds Major", "Hearts Minor", "Hearts Major", "Spades Minor", "Spades Major"]
        self.setnames = []
        for i in range(n_sets):
            self.setnames.append(setnames[i])

        #The won/lost/inplay status of each set
        #-1 if it's still in play.
        #else the number of the team that won it.
        self.setstatus = []
        for i in range(n_sets):
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
        for suit in range(self.n_sets/2):
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
        return [i for i in range(len(self.players)) if not self.players[i].hasCompleted()]

    def getAllCards(self):
        toreturn = []
        for p in self.players:
            toreturn.append(p.getAllCards())
        return toreturn

    def initializeGame(self):
        self.distributeCards()
        self.printCards()
        self.turn = random.randint(0,len(self.players)-1)  #Initial turn goes to a random player
        self.initialiseTeamScores()
        self.playhistory = []

    def playNextMove(self):


        if not self.isGameOver():

            if self.players[self.turn].hasCompleted():
                self.turn = random.choice(self.getCompletedPlayers())

            print 'Number of moves: ', len(self.playhistory)
            toprint = []
            for p in self.players:
                toprint.append(sum([len(s) for s in p.cards]))
            print toprint
            if len(self.playhistory) % 10000 == 0:
                self.printCards()
                raw_input()

            #Ask everyone if they'd like to put down a set
            for (player_i,player) in enumerate(self.players):
                setno = player.putDownSet()
                if setno is not None:
                    if self.verifySetWon(player.team, setno):
                        player.cards[setno] = [] #TODO - Quick fix.
                        self.setstatus[setno] = player.team 
                        self.teamscores[player.team] += (5 if setno%2 == 0 else 10)
                        self.turn = player_i
                        return

            (target,card) = self.players[self.turn].getQuery()
            self.doCardExchange(target,card)


        else:
            print 'GAME OVER!'

    def doCardExchange(self,target,card):
        if target.hasCard(card):
            target.removeCard(card)
            self.players[self.turn].addCard(card)                
            self.playhistory.append(LitPlay(self.players[self.turn],target,card,True))
        else:
            self.playhistory.append(LitPlay(self.players[self.turn],target,card,False))
            self.turn = self.players.index(target)


