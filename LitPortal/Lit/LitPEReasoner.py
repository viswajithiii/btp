from math import log

class LitPEReasoner:
    """A class to define Probabilistic Epistemic models for a single Lit player.
       Can be passed to an update model and have its fields altered accordingly.
       Contains:
       At: set of propositional variables
       S: set of states
       Rels: Equivalence relations between states
       P: S -> (S -> Probspace): Probability functions
       V: At -> P(S). Set of states in which At is true
    """
    def __init__(self,player):

        self.player = player
        self.litgame = self.player.litgame

    def putDownSet(self):

        for set_i in range(self.litgame.n_sets):
            set_cards = self.litgame.getCardsOfSet(set_i)
            set_valid = True
            for card in set_cards:
                if not self.cardprobinfos[card].isWithinTeam():
                    set_valid = False
                    break
            if set_valid:
                return set_i

        return None

    def getQuery(self):
        """If it's this player's turn, figure out what to ask for."""
        
        #The sets this player has
        setsinhand = [i for i in range(len(self.player.cards)) if len(self.player.cards[i]) > 0]
        
        foundFeasibleSet = False
        while not foundFeasibleSet:

            #If there's no fruitful query in any set. TODO.
            if len(setsinhand) == 0:
                return self.player.getRandomQuery()

            #Current: Which set am I closest to winning in?
            min_cards = 8
            min_i = -1
            for set_i in setsinhand:
                set_remaining_cards = self.litgame.getSetTotalCount(set_i) - len(self.player.cards[set_i])
                for p in self.teammates:
                    set_remaining_cards -= self.playerinfos[p].lower_bounds[set_i]
                if set_remaining_cards < min_cards:
                    min_cards = set_remaining_cards
                    min_i = set_i

            #Which cards in this set could opponents possibly possess?
            possible_cards = self.litgame.getCardsOfSet(min_i)
            cards_to_remove = []
            for card in possible_cards:
                if self.cardprobinfos[card].isWithinTeam():
                    cards_to_remove.append(card) 
            for card in cards_to_remove:
                possible_cards.remove(card)

            if len(possible_cards) > 0:
                foundFeasibleSet = True
            else:
                setsinhand.remove(min_i)

        #Which card am I least uncertain about?
        least_entropy = 1.1
        least_entropy_i = -1
        for (i,card) in enumerate(possible_cards):
            entropy = self.cardprobinfos[card].getEntropy()
            if entropy < least_entropy:
                least_entropy = entropy
                least_entropy_i = i

        cardtoask = possible_cards[least_entropy_i]
        playertoask = self.cardprobinfos[cardtoask].getLikeliestOpponent()
        return (playertoask,cardtoask)

    def updateWithPlay(self,play):

        if play.subject.uid != self.player.uid:
            self.playerinfos[play.subject].updateSubject(play)
        if play.target.uid != self.player.uid:
            self.playerinfos[play.target].updateTarget(play)

        self.cardprobinfos[play.card].updateWithPlay(play)

    def initialize(self):
        """To initialize the models after the cards have been distributed."""
        self.playerinfos = {}
        for p in self.litgame.players:
            if p.uid == self.player.uid:
                continue
            self.playerinfos[p] = PlayerInfo(p,self)

        self.cardprobinfos = {}
        for card in self.litgame.cards:
            self.cardprobinfos[card] = CardProbabilisticInfo(card,self)

        #To speed things up
        self.teammates = []
        self.opponents = []
        for p in self.litgame.players:
            if p.uid == self.player.uid:
                continue
            if p.team == self.player.team:
                self.teammates.append(p)
            else:
                self.opponents.append(p)
            
    def addConfirmedCard(self,player,card):
        self.playerinfos[player].addConfirmedCard(card)

    def getUpperBound(self,player_uid,set_no):
        """The maximum number of cards of that set that player_uid can have."""
        p_info = self.playerinfos[self.litgame.players[player_uid]]
        count_others = self.litgame.getSetTotalCount(set_no) - len(self.player.cards[set_no])
        for p in self.litgame.players:
            if p.uid == self.player.uid or p.uid == player_uid:
                continue
            count_others -= self.getLowerBound(p.uid,set_no)
        
        count_player = self.litgame.players[player_uid].getTotalCardCount()
        for (set_i,lb) in enumerate(p_info.lower_bounds):
            if set_i == set_no:
                continue
            count_player -= lb

        return min(count_others,count_player)

    def getLowerBound(self,player_uid,set_no):
        return self.playerinfos[self.litgame.players[player_uid]].lower_bounds[set_no]
    
    def printStatus(self):
        """Print everything we know. For debug purposes."""
        print 'Player infos:'
        for p in self.litgame.players:
            if p.uid == self.player.uid:
                continue
            self.playerinfos[p].printStatus()
        for c in self.litgame.cards:
            self.cardprobinfos[c].printStatus() 

class PlayerInfo:
    """A class that stores the information corresponding to a single player's cards."""

    def __init__(self,player,reasoner):
    
        self.player = player
        self.reasoner = reasoner

        #Lower_bounds stores the lower bound for the number of cards in each set. Count must include the confirmed_cards.
        self.lower_bounds = []       
        for i in range(reasoner.litgame.n_sets):
            self.lower_bounds.append(0)

        #The cards that we know this player has.
        self.confirmed_cards = []
        for i in range(reasoner.litgame.n_sets):
            self.confirmed_cards.append([])

    def updateSubject(self,play):

        #If this player got the card
        if play.result:
            self.addConfirmedCard(play.card)
            self.incrementLowerBound(play.card)
        else:
            #We know, at the very least, that this player has one card of the set
            self.setLowerBound(play.card)


    def updateTarget(self,play):

        #If this player had the card
        if play.result:
            #If we already knew this player had the card
            if self.isCardKnown(play.card):
                self.removeConfirmedCard(play.card)
            else:
                self.decrementLowerBound(play.card)

    def isCardKnown(self,card):

        setno = self.reasoner.litgame.getSetFromCard(card)
        return card in self.confirmed_cards[setno]

    def addConfirmedCard(self,card):

        setno = self.reasoner.litgame.getSetFromCard(card)
        insert_i = 0 
        for c in self.confirmed_cards[setno]:
            if c.value > card.value:
                break
            insert_i += 1
        self.confirmed_cards[setno].insert(insert_i,card)
        self.setLowerBound(card)
 
    def removeConfirmedCard(self,card):
        
        setno = self.reasoner.litgame.getSetFromCard(card)
        self.confirmed_cards[setno].remove(card)
        self.decrementLowerBound(card)

    def incrementLowerBound(self,card):

        setno = self.reasoner.litgame.getSetFromCard(card)
        self.lower_bounds[setno] += 1

    def setLowerBound(self,card):
        setno = self.reasoner.litgame.getSetFromCard(card)
        if self.lower_bounds[setno] == 0:
            self.lower_bounds[setno] = 1

    def decrementLowerBound(self,card):
        
        setno = self.reasoner.litgame.getSetFromCard(card)
        if self.lower_bounds[setno] > 0:
            self.lower_bounds[setno] -= 1

    def printStatus(self):
        print 'Player id: ', self.player.uid
        print 'Lower bounds: ', self.lower_bounds
        print 'Confirmed cards:'
        for (set_i,cc) in enumerate(self.confirmed_cards):
            print set_i, ': ', cc
      
class CardProbabilisticInfo:
    """A class that stores the probabilistic information corresponding to a particular card."""

    def __init__(self,card,reasoner):
        
        self.card = card
        self.reasoner = reasoner

        if self.reasoner.player.hasCard(card):
            self.confirmed = True
            self.owner = self.reasoner.player
        else:
            self.confirmed = False
            self.owner = None
            self.pvals = [float(1)]*(len(self.reasoner.litgame.players))
            self.pvals[self.reasoner.player.uid] = 0
            self.normalizeProbabilities()

    def updateWithPlay(self,play):

        if play.result:

            #Sanity check assertion
            if self.confirmed:
                assert self.owner == play.target

            self.confirmed = True
            self.owner = play.subject

        else:

            if self.confirmed:
                #Sanity check assertion. We don't learn anything (first order) from this play.
                assert self.owner != play.target and self.owner != play.subject
            else:
                self.confirmNotOwner(play.target)
                self.confirmNotOwner(play.subject)

    def confirmNotOwner(self,player):
        """Method should be called when we know that 'player' doesn't own self.card."""
        if self.confirmed:
            return
        self.pvals[player.uid] = 0
        non_zero_count = 0
        non_zero_id = -1
        for (player_i,pval) in enumerate(self.pvals):
            if pval > 0:
                non_zero_count += 1
                non_zero_id = player_i
            if non_zero_count >= 2:
                break

        assert non_zero_count > 0
        #We now know who has the card!
        if non_zero_count == 1:
            self.confirmed = True
            self.owner = self.reasoner.litgame.players[non_zero_id]
            self.reasoner.addConfirmedCard(self.owner,self.card)
        else:
            self.normalizeProbabilities()

    def normalizeProbabilities(self):
        self.pvals = [p/sum(self.pvals) for p in self.pvals]

    
    def getEntropy(self):

        if self.confirmed:
            return 0
        toreturn = 0
        for pval in self.pvals:
            if pval > 0:
                toreturn -= pval*log(pval,2)
        return toreturn

    def isWithinTeam(self):
        """Returns True if the card is definitely in our team."""     
        if self.confirmed:
            return self.owner.team == self.reasoner.player.team
        else:
            for opponent in self.reasoner.opponents:
                if self.pvals[opponent.uid] > 0:
                    return False
            return True
        
    
    def updatePvals(self):
        """Performs the probability update."""
        possible_owners = []
        for (pval_i,pval) in enumerate(self.pvals):
            if pval > 0:
                possible_owners.append(pval_i)
        total_ub = 0
        total_lb = 0
        setno = self.reasoner.litgame.getSetFromCard(self.card)
        for owner in possible_owners: 
            total_lb += self.reasoner.getLowerBound(owner,setno)
            total_ub += self.reasoner.getUpperBound(owner,setno)
        Z = total_ub - total_lb

        if Z > 0:
            for owner in possible_owners:
                self.pvals[owner] = self.reasoner.getLowerBound(owner,setno) + float(self.reasoner.getUpperBound(owner,setno) - self.reasoner.getLowerBound(owner,setno))/Z
            self.normalizeProbabilities()

    def getLikeliestOpponent(self):
        """Returns the opponent who is likeliest to have this card."""


        #Sanity check.
        assert not self.isWithinTeam()
        
        if self.confirmed:
            return self.owner

        self.updatePvals()
        max_pval = -1.0
        max_i = -1
        for (opp_i,opponent) in enumerate(self.reasoner.opponents):
            if self.pvals[opponent.uid] > max_pval:
                max_pval = self.pvals[opponent.uid]
                max_i = opp_i

        return self.reasoner.opponents[max_i]

    def printStatus(self):
        print 'Card status for ', self.card, ': ',
        if self.confirmed:
            print 'Confirmed. Owner: ', self.owner.uid
        else:
            print 'Not confirmed: Pvals: ', self.pvals
