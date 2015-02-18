import random
from Card import Card
from LitPEReasoner import LitPEReasoner

class LitPlayer:
    """
    Represents a particular player. Can be subclassed to make user-defined bots.
    """
    def __init__(self,litgame,uid,team,level='default'):
        self.litgame = litgame
        self.uid = uid
        self.team = team
        self.cards = []
        for i in range(self.litgame.n_sets):
            self.cards.append([])
        self.reasoner = LitPEReasoner(self)
        self.level = level

    def addCard(self,newcard):

        assert len(self.cards) == self.litgame.n_sets
        set_i = self.litgame.getSetFromCard(newcard)
        insert_i = 0
        for card in self.cards[set_i]:
            if card.value > newcard.value:
                break
            insert_i += 1
        self.cards[set_i].insert(insert_i,newcard)

    def getAllCards(self):

        toreturn = []
        for s in self.cards:
            toreturn.extend(s)
        return toreturn

    def printCards(self):
        print 'Player ',self.uid,' has ',sum([len(s) for s in self.cards]), ' cards.'
        for set_ in self.cards:
            for card in set_:
                card.printName()

    def removeCard(self,cardtoremove):

        set_i = self.litgame.getSetFromCard(cardtoremove)
        self.cards[set_i].remove(cardtoremove)

    def hasCard(self,cardtocheck):

        set_i = self.litgame.getSetFromCard(cardtocheck)
        return cardtocheck in self.cards[set_i]


    def putDownSet(self):                
        """
        If the player wants to return a set, return the set index. Else return None
        """
        return None
        if self.level == 'epistemic':
            return self.reasoner.putDownSet()
        for (s_no,s) in enumerate(self.cards):
            if s_no % 2 == 0 and len(s) == 6: #Minor
                return s_no
            elif s_no % 2 == 1 and len(s) == 7: #Major
                return s_no
        return None

    def hasCompleted(self):
        return self.getTotalCardCount() == 0

    def getTotalCardCount(self):
        return sum([len(s) for s in self.cards])

    def getRandomQuery(self):
        """Randomly ask for some card from some set."""
        assert self.putDownSet() is None
        setsinhand = [i for i in range(len(self.cards)) if len(self.cards[i]) > 0]
        settoask = random.choice(setsinhand)

        possiblevalues = range(6,13) if self.litgame.isSetMajor(settoask) else range(6)

        for card in self.cards[settoask]:
            possiblevalues.remove(card.value)

        cardtoask = self.litgame.getCard(settoask/2, random.choice(possiblevalues))
        possibleplayers = [x for x in self.litgame.players if x.team != self.team]
        playertoask = random.choice(possibleplayers)

        return (playertoask,cardtoask)


    def getQuery(self):
        
        if self.level == 'epistemic':
            return self.reasoner.getQuery()

        return self.getRandomQuery()

    def updateWithPlay(self,play):
        self.reasoner.updateWithPlay(play)

    def initialize(self):
        """Signifies that the cards have been distributed and that play is about to begin."""
        self.reasoner.initialize()
