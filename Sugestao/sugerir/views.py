from django.contrib import messages
from django.shortcuts import render, redirect, resolve_url as r, render_to_response
from django.utils.datetime_safe import datetime

import Sugestao
from Sugestao.core.models import setor, pessoa, sugestao, edicao
from Sugestao.sugerir.forms import SugestaoForm, SugestaoEdicaoForm


def FazerSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            pass
    except KeyError:
        return redirect(r('Login'))


    #Preencher Formulário
    SETORES = []
    setorobj = setor.objects.all()
    for set in setorobj:
        SETORES.append((set.id, set.nome))
    PESSOAS = []
    pessoaobj = pessoa.objects.filter(nome="Anônimo") | pessoa.objects.filter(nome=request.session['nome'])
    for pess in pessoaobj:
        PESSOAS.append((pess.id, pess.nome))
    form = SugestaoForm(request, SETORES, PESSOAS)

    if request.method == 'POST':
        form = SugestaoForm(request, SETORES, PESSOAS, request.POST, request.FILES)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            sugestaoobj = sugestao(status='1', titulo=request.POST['titulo'], setor=Sugestao.core.models.setor.objects.get(id=request.POST['setor']), pessoa=Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], imagem=request.FILES['imagem'], datahora=datetime.now())
            sugestaoobj.save()
            messages.success(request, 'Sugestão número '+ str(sugestaoobj.id)+ ' salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id)))
        else:
            messages.success(request, 'Erro ao salvar sua sugestão')
            return redirect(r('FazerSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FazerSugestao', 'err': '','form': form, 'itemselec': 'HOME'})


def DetalharSugestao(request, id):
    sugestaoobj = sugestao.objects.get(id=id)
    tipopessoa = ''
    if sugestaoobj.pessoa.usuario == request.session['userl']:
        tipopessoa = 'editar'
    if sugestaoobj.setor.responsavel == pessoa.objects.get(usuario=request.session['userl']):
        if tipopessoa == 'editar':
            tipopessoa = 'ambos'
        else:
            tipopessoa = 'responder'


    edicaoobj = edicao.objects.filter(sugestao=id).order_by('-datahora')
    return render(request, 'sugerir/detalhar_sugestao.html', {'err': '', 'tipopessoa': tipopessoa, 'itemselec': 'HOME', 'sugestao': sugestaoobj, 'edicoes': edicaoobj})


def EditarSugestao(request, id):
    #Preencher Formulário

    sugestaoobj = sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestaoobj.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            edicaoobj = edicao(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.core.models.sugestao.objects.get(id=id))
            edicaoobj.save()
            messages.success(request, 'Edição salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id)))
        else:
            messages.success(request, 'Erro ao salvar sua edição')
            return redirect(r('EditarSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'EditarSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME'})
