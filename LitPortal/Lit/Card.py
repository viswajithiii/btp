class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def printName(self):
        """
        Prints the human-readable card name.
        """
        print self.getName()

    def getName(self):
        SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
        VALUES = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        return VALUES[self.value] + " of " + SUITS[self.suit] 
 

    def getShortName(self):

        SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
        VALUES = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        return SUITS[self.suit][0]+VALUES[self.value]

    def __repr__(self):
        return self.getName()
