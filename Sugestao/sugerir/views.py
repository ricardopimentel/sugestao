from django.contrib import messages
from django.shortcuts import render, redirect, resolve_url as r, render_to_response
from Sugestao.core.models import sugestao
from Sugestao.sugerir.forms import SugestaoForm


def FazerSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            pass
    except KeyError:
        return redirect(r('Login'))

    form = SugestaoForm()
    if request.method == 'POST':
        form = SugestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect(r('FazerSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'err': '','form': form, 'itemselec': 'HOME'})
