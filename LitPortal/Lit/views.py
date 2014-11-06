from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from LitGame import LitGame
from Card import Card

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
    print request.POST
    print request.method
    #First move
    if litgame is None or "reset" in request.GET.keys():
        litgame = LitGame(int(n_players))
        litgame.initializeGame()

    if request.method=="GET" and "next_move" in request.GET.keys():
        litgame.playNextMove()
    if "movetextbox" in request.POST.keys():
        movestring = request.POST["movetextbox"].split() 
        targettoplay = litgame.players[int(movestring[0])]
        print 'HERE ',targettoplay.uid
        suitdict = {"C":0,"D":1,"H":2,"S":3}
        VALUES = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        cardtoplay=Card(suitdict[movestring[1][0]],VALUES.index(movestring[1][1]))
        litgame.doCardExchange(targettoplay,cardtoplay)
    cardlists = get_card_image_urls(litgame.getAllCards())
    playercardlist = []
    for (p_i,cl) in enumerate(cardlists):
        playercardlist.append((litgame.players[p_i],cl))
    setnamelist = litgame.setnames
    setstatuslist = get_set_status_list()
    turn = litgame.turn
    recentmovelist = get_recent_moves()

    return render_to_response('game.html',locals(),context_instance=RequestContext(request))
