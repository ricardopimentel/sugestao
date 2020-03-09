from django.http import Http404
from django.shortcuts import render, redirect, resolve_url as r, render_to_response


# Create your views here.
from django.template import RequestContext

from Sugestao.core.models import sugestao, pessoa


def Home(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            sugestoes = sugestao.objects.filter(pessoa__usuario=request.session['userl'], status='1') #filtra as sugestões para mostrar somente as realizadas por esse usuário, e estejam ativas
            idpessoa = pessoa.objects.get(usuario=request.session['userl'])
            sugestoesparamim = sugestao.objects.filter(setor__responsavel=idpessoa, status='1') #filtra as sugestões atribuidas ao setor que eu sou responsável            print(sugestoesparamim)
            return render(request, 'index.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'HOME', 'sugestoesparamim': sugestoesparamim})

    except KeyError:
        return redirect(r('Login'))
