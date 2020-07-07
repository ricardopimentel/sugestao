from django.conf.urls import url
from Sugestao.sugerir import views

urlpatterns = [
    url(r'^fazersugestao/$', views.FazerSugestao, name='FazerSugestao'),
    url(r'^sugestoes/$', views.Sugestoes, name='Sugestoes'),
    url(r'^minhassugestoes/(?P<view>.+)$', views.MinhasSugestoes, name='MinhasSugestoes'),
    url(r'^sugestoespmim/(?P<view>.+)$', views.SugestoesPraMim, name='SugestoesPraMim'),
    url(r'^detalharsugestao/(?P<id>.+)/(?P<senha>.+)$', views.DetalharSugestao, name='DetalharSugestao'),
    url(r'^editarsugestao/(?P<id>.+)$', views.EditarSugestao, name='EditarSugestao'),
    url(r'^respondersugestao/(?P<id>.+)$', views.ResponderSugestao, name='ResponderSugestao'),
    url(r'^finalizarsugestao/(?P<id>.+)$', views.FinalizarSugestao, name='FinalizarSugestao'),
    url(r'^goto/$', views.VaParaSugestao, name='VaParaSugestao'),
]
