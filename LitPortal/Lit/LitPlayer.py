import random
from Card import Card

class LitPlayer:
    """
    Represents a particular player. Can be subclassed to make user-defined bots.
    """
    def __init__(self,litgame,uid,team):
        self.litgame = litgame
        self.uid = uid
        self.team = team
        self.cards = []
        for i in range(8):
            self.cards.append([])

    def addCard(self,newcard):

        assert len(self.cards) == 8
        set_i = self.litgame.getSetFromCard(newcard)
        insert_i = 0
        for card in self.cards[set_i]:
            if card.value > newcard.value:
                break
            insert_i += 1
        self.cards[set_i].insert(insert_i,newcard)


    def printCards(self):
        print 'Player ',self.uid,' has ',sum([len(s) for s in self.cards]), ' cards.'
        for set_ in self.cards:
            for card in set_:
                card.printName()

    def removeCard(self,cardtoremove):

        set_i = self.litgame.getSetFromCard(cardtoremove)
        for c in self.cards[set_i]:
            if c.value == cardtoremove.value:
                self.cards[set_i].remove(c)
                break

    def hasCard(self,cardtocheck):

        set_i = self.litgame.getSetFromCard(cardtocheck)
        for c in self.cards[set_i]:
            if c.value == cardtocheck.value:
                return True
        return False


    def putDownSet(self):                
        """
        If the player wants to return a set, return the set index. Else return None
        """
        for (s_no,s) in enumerate(self.cards):
            if s_no % 2 == 0 and len(s) == 6: #Minor
                return s_no
            elif s_no % 2 == 1 and len(s) == 7: #Major
                return s_no
        return None

    def hasCompleted(self):
        return sum([len(s) for s in self.cards]) == 0

    def getQuery(self):

        setsinhand = [i for i in range(len(self.cards)) if len(self.cards[i]) > 0]
        settoask = random.choice(setsinhand)

        possiblevalues = range(6) if settoask % 2 == 0 else range(6,13)

        for card in self.cards[settoask]:
            possiblevalues.remove(card.value)

        cardtoask = Card(settoask/2, random.choice(possiblevalues))
        possibleplayers = [x for x in self.litgame.players if x.team != self.team]
        playertoask = random.choice(possibleplayers)

        return (playertoask,cardtoask)
