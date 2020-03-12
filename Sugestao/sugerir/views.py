from django.contrib import messages
from django.shortcuts import render, redirect, resolve_url as r, render_to_response
from django.utils.datetime_safe import datetime

import Sugestao
from Sugestao.core.models import setor, pessoa, sugestao, edicao, resposta, finalizacao
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
            if request.FILES:
                sugestaoobj = sugestao(status='1', titulo=request.POST['titulo'], setor=Sugestao.core.models.setor.objects.get(id=request.POST['setor']), pessoa=Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], imagem=request.FILES['imagem'], datahora=datetime.now())
            else:
                sugestaoobj = sugestao(status='1', titulo=request.POST['titulo'], setor=Sugestao.core.models.setor.objects.get(id=request.POST['setor']), pessoa=Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], datahora=datetime.now())
            sugestaoobj.save()
            messages.success(request, 'Sugestão número '+ str(sugestaoobj.id)+ ' salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id)))
        else:
            messages.success(request, 'Erro ao salvar sua sugestão')
            return redirect(r('FazerSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FazerSugestao', 'err': '','form': form, 'itemselec': 'HOME'})


def DetalharSugestao(request, id):
    # Verificar se foi aberto por mim ou para mim
    sugestaoobj = sugestao.objects.get(id=id)
    editar = ''
    responder = ''
    visualizar = ''
    if sugestaoobj.pessoa.usuario == request.session['userl']: #O usuário pode editar a sugestão
        editar = 'editar'
    if sugestaoobj.setor.responsavel == pessoa.objects.get(usuario=request.session['userl']): #O usuário pode responder a sugestão
        responder = 'responder'
    if sugestaoobj.pessoa.usuario == '000000':
        visualizar = 'visualizar'

    if editar == '' and responder == '' and visualizar == '': #Apessoa não tem direito a visializar essa sugestão, redireciona para a home
        messages.success(request, 'Você não pode acessar essa página')
        return redirect(r('Sugestoes'))
    edicaoobj = edicao.objects.filter(sugestao=id).order_by('-datahora')
    respostaobj = resposta.objects.filter(sugestao=id)
    finalizacaoaobj = finalizacao.objects.filter(sugestao=id)

    return render(request, 'sugerir/detalhar_sugestao.html', {'err': '', 'editar': editar, 'responder': responder, 'itemselec': 'HOME', 'sugestao': sugestaoobj, 'edicoes': edicaoobj, 'respostas': respostaobj, 'finalizacoes': finalizacaoaobj})


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


def ResponderSugestao(request, id):
    #Preencher Formulário

    sugestaoobj = sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestaoobj.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            respostaobj = resposta(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.core.models.sugestao.objects.get(id=id), pessoa=pessoa.objects.get(usuario=request.session['userl']))
            respostaobj.save()
            messages.success(request, 'Resposta salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id)))
        else:
            messages.success(request, 'Erro ao salvar sua resposta')
            return redirect(r('ResponderSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'ResponderSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME'})


def FinalizarSugestao(request, id):
    #Preencher Formulário

    sugestaoobj = sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestaoobj.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            finalizacaoobj = finalizacao(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.core.models.sugestao.objects.get(id=id), pessoa=pessoa.objects.get(usuario=request.session['userl']))
            finalizacaoobj.save()
            sugestaoobj.status=False
            sugestaoobj.save()
            messages.success(request, 'Sugestão finalizada com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id)))
        else:
            messages.success(request, 'Erro ao salvar')
            return redirect(r('FinalizarSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FinalizarSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME'})


def Sugestoes(request):
    try:# Verificar se usuario esta logado
        if request.session['nome']:
            sugestoes = sugestao.objects.filter(pessoa__usuario=request.session['userl'], status='1') #filtra as sugestões para mostrar somente as realizadas por esse usuário, e estejam ativas
            idpessoa = pessoa.objects.get(usuario=request.session['userl'])
            sugestoesparamim = sugestao.objects.filter(setor__responsavel=idpessoa, status='1') #filtra as sugestões atribuidas ao setor que eu sou responsável            print(sugestoesparamim)
            return render(request, 'sugerir/sugestoes.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'HOME', 'sugestoesparamim': sugestoesparamim})

    except KeyError:
        return redirect(r('Login'))
