from django.conf.urls import url

from Sugestao.config import views

urlpatterns = [
    url(r'^$', views.Administracao, name='Administracao'),
    url(r'^activedirectory/$', views.Dados_ad, name='ConfigAD'),
    url(r'^configemail/$', views.ConfEmail, name='ConfigEmail'),
    url(r'^configuracaoinicial/$', views.ConfigInicial, name='ConfigInicial'),
    url(r'^gerenciarsetores/$', views.GerenciarSetores, name='GerenciarSetores'),
    url(r'^cadastrosetor/(?P<id>.+)$', views.CadastroSetor, name='CadastroSetor'),
    url(r'^gerenciarpessoas/$', views.GerenciarPessoas, name='GerenciarPessoas'),
    url(r'^cadastropessoa/(?P<id>.+)$', views.CadastroPessoa, name='CadastroPessoa'),
]
