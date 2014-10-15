from django.conf.urls import patterns, url

# All URLs are specified here
urlpatterns = patterns('',
    url(r'^$', 'Lit.views.home', name='home'),
    url(r'^play(?P<n_players>\d+)/$','Lit.views.startgame',name='startgame'),
)
