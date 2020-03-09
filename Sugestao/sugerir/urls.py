from django.conf.urls import url
from Sugestao.sugerir import views

urlpatterns = [
    url(r'^fazersugestao/$', views.FazerSugestao, name='FazerSugestao'),
    url(r'^detalharsugestao/(?P<id>.+)$', views.DetalharSugestao, name='DetalharSugestao'),
    url(r'^editarsugestao/(?P<id>.+)$', views.EditarSugestao, name='EditarSugestao'),
]
