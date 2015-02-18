import random
from Card import Card
from LitPlayer import LitPlayer
from LitPlay import LitPlay

class LitGame:
    """
    A class for a particular game of Literature.
    """

    def __init__(self, n_players = 4, n_sets = 8,verbose=True):


        self.n_sets = n_sets

        self.players = [] #Should be a list of LitPlayer elements.
        for i in range(n_players):
            if i%2 == 0:
                level = 'epistemic'
            else:
                level = 'default'
            self.players.append(LitPlayer(self,i,i%2,level))

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

        self.cards = []

        self.verbose = verbose

    def getSetFromCard(self,card):

        #For default config
        toreturn = card.suit*2
        if card.value >= 6: #major
            toreturn += 1
        return toreturn
        
    def getSetName(self,set_index):
        return self.setnames[set_index]
        
    def isSetMajor(self,set_no):
        return set_no%2 == 1


    #Creates all our card objects.
    def createCards(self):
        for suit in range(self.n_sets/2):
            for value in range(13):
                self.cards.append(Card(suit,value))

    def distributeCards(self):

        self.createCards()
        shuffled_cards = list(self.cards)
        random.shuffle(shuffled_cards)


        player_i = 0 
        for shuffled_card in shuffled_cards:
            self.players[player_i].addCard(shuffled_card)
            player_i  = (player_i+1)%(len(self.players))
        
    def getCard(self,suit,value):
        return self.cards[suit*13+value]

    def getCardsOfSet(self,setno):
        start_index = (setno/2)*13
        if self.isSetMajor(setno):
            start_index += 6
            end_index = start_index + 7
        else:
            end_index = start_index + 6
        return self.cards[start_index:end_index]

    def printCards(self):
        for player in self.players:
            player.printCards()

    def getCardsByPlayer(self):
        toreturn = []
        for p in self.players:
            toreturn.append(p.getAllCards())
        return toreturn

    def isGameOver(self):
        return self.isGameEffectivelyOver()
        for status in self.setstatus:
            if status == -1:
                return False
        return True

    def isGameEffectivelyOver(self):
        for (set_i, status) in enumerate(self.setstatus):
            if status == -1:
                #Check if the cards of the set are with the same team
                scores = [0,0]
                for player in self.players:
                    scores[player.team] += len(player.cards[set_i])
                if min(scores) > 0:
                    return False
        return True


    def initializeTeamScores(self):
        self.teamscores = {}
        for player in self.players:
            self.teamscores[player.team] = 0

    def getSetTotalCount(self,setno):
        if self.isSetMajor(setno):
            return 7
        else:
            return 6

    def verifySetWon(self,team,setno):

        assert self.setstatus[setno] == -1

        targetcount = self.getSetTotalCount(setno)
        realcount = 0
        for player in self.players:
            if player.team == team:
                realcount += len(player.cards[setno])
            
        return realcount == targetcount

    def getRemainingPlayers(self):
        return [i for i in range(len(self.players)) if not self.players[i].hasCompleted()]

    def initializeGame(self):
        self.distributeCards()
        if self.verbose:
            self.printCards()
        self.turn = random.randint(0,len(self.players)-1)  #Initial turn goes to a random player
        self.initializeTeamScores()
        self.playhistory = []
        for p in self.players:
            p.initialize()

    def playNextMove(self):

        if self.verbose:
            print 'Number of moves: ', len(self.playhistory)
            toprint = []
            for p in self.players:
                toprint.append(sum([len(s) for s in p.cards]))
            print toprint
            if len(self.playhistory) > 0:
                print self.playhistory[-1]

        if not self.isGameOver():

            if self.players[self.turn].hasCompleted():
                self.turn = random.choice(self.getRemainingPlayers())

            #Ask everyone if they'd like to put down a set
            for (player_i,player) in enumerate(self.players):
                setno = player.putDownSet()
                if setno is not None:
                    if self.verifySetWon(player.team, setno):
                        for p in self.players:
                            p.cards[setno] = []
                        self.setstatus[setno] = player.team 
                        self.teamscores[player.team] += (5 if setno%2 == 0 else 10)
                        self.turn = player_i
                        return

            (target,card) = self.players[self.turn].getQuery()
            self.doCardExchange(target,card)

            #So that all the players can update based on the latest move
            self.updatePlayers(self.playhistory[-1])

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

    def updatePlayers(self,play):
        for p in self.players:
            p.updateWithPlay(play)
