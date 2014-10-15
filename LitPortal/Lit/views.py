from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from LitGame import LitGame

litgame = None

# Create your views here.
def home(request):
    return render_to_response('index.html',locals())


def startgame(request,n_players):

    #First move
    if litgame is None:
        litgame = LitGame(int(n_players))
        litgame.initializeGame()
