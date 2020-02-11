from django.conf.urls import url

from Sugestao.sugerir import views

urlpatterns = [
    url(r'^fazersugestao/$', views.FazerSugestao, name='FazerSugestao'),
]
