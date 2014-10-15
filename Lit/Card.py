class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def printName(self):
        """
        Prints the human-readable card name.
        """
        SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
        VALUES = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        print VALUES[self.value] + " of " + SUITS[self.suit] 
