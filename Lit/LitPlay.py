class LitPlay:
    """
    A class modelling one particular play; ie, one particular turn.
    """
    def __init__(self, subject, target, card, result):
        """
        subject: the player who asks
        target: the player who is asked
        card: the card that's asked
        result: True if target has card, else False
        """
        self.subject = subject
        self.target = target
        self.card = card
        self.result = result
