from django.conf.urls import url
from Sugestao.sugerir import views

urlpatterns = [
    url(r'^fazersugestao/$', views.FazerSugestao, name='FazerSugestao'),
    url(r'^fazersugestoes/$', views.Sugestoes, name='Sugestoes'),
    url(r'^detalharsugestao/(?P<id>.+)$', views.DetalharSugestao, name='DetalharSugestao'),
    url(r'^editarsugestao/(?P<id>.+)$', views.EditarSugestao, name='EditarSugestao'),
    url(r'^respondersugestao/(?P<id>.+)$', views.ResponderSugestao, name='ResponderSugestao'),
    url(r'^finalizarsugestao/(?P<id>.+)$', views.FinalizarSugestao, name='FinalizarSugestao'),
]
