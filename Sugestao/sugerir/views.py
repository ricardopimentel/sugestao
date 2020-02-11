from django.shortcuts import render
from django.shortcuts import render, redirect, resolve_url as r, render_to_response

# Create your views here.
from Sugestao.core.models import sugestao


def FazerSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            pass
    except KeyError:
        return redirect(r('Login'))
    sugestoes = sugestao.objects.all()
    return render(request, 'sugerir/cadastro_sugestao.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'HOME'})
