from django.http import Http404
from django.shortcuts import render, redirect, resolve_url as r, render_to_response


# Create your views here.
from django.template import RequestContext

from Sugestao.core.models import sugestao


def Home(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            sugestoes = sugestao.objects.all()
            return render(request, 'index.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'HOME'})

    except KeyError:
        return redirect(r('Login'))
