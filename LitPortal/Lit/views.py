from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from LitGame import LitGame

litgame = None

# Create your views here.
def home(request):
    return render_to_response('index.html',locals())

def startgame(request,n_players):

    def get_card_image_urls(cardlists):
        toreturn = []
        for cardlist in cardlists:
            toreturn.append(["/static/img/" +card.getShortName()+".png" for card in cardlist])
        return toreturn

    def get_set_status_list():
        toreturn = []
        for s in litgame.setstatus:
            if s == -1:
                toreturn.append("In play")
            else:
                toreturn.append(s)
        return toreturn
     
    def get_recent_moves(n = 5):
        toreturn = []
        n = -min(n, len(litgame.playhistory))
        while n < 0:
            p = litgame.playhistory[n]
            currstring = "Player " + str(p.subject.uid) + " asked player " + str(p.target.uid) + " for the " + str(p.card.getName()) +"."
            if p.result == True:
                currstring += " Success."
            else:
                currstring += " Failure."
            toreturn.append(currstring)
            n += 1
        return toreturn

    global litgame
    #First move
    if litgame is None:
        litgame = LitGame(int(n_players))
        litgame.initializeGame()

    if "next_move" in request.GET.keys():
        litgame.playNextMove()

    cardlists = get_card_image_urls(litgame.getAllCards())
    playercardlist = []
    for (p_i,cl) in enumerate(cardlists):
        playercardlist.append((litgame.players[p_i],cl))
    setnamelist = litgame.setnames
    setstatuslist = get_set_status_list()
    turn = litgame.turn
    recentmovelist = get_recent_moves()

    return render_to_response('game.html',locals())
