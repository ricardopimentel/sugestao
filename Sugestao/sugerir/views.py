import os
import platform
import random
import shutil
import threading

from PIL import Image
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, resolve_url as r, render_to_response
from django.template.loader import render_to_string
from django.utils.datetime_safe import datetime

import Sugestao
from Sugestao import settings
from Sugestao.core.models import setor, pessoa, sugestao, edicao, resposta, finalizacao, config
from Sugestao.sugerir.forms import SugestaoForm, SugestaoEdicaoForm


def FazerSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    #Preencher Formulário
    SETORES = []
    setorobj = setor.objects.all()
    SETORES.append(('', 'Para qual setor é a sugestão?'))
    for set in setorobj:
        SETORES.append((set.id, set.nome))
    PESSOAS = []
    pessoaobj = pessoa.objects.filter(nome="Anônimo") | pessoa.objects.filter(nome=request.session['nomesugestao']) #Filtra o objeto pessoa, anonima e a pessoa logada
    PESSOAS.append(('', 'Você deseja se identificar?'))
    for pess in pessoaobj:
        PESSOAS.append((pess.id, pess.nome))
    form = SugestaoForm(request, SETORES, PESSOAS)

    if request.method == 'POST':
        form = SugestaoForm(request, SETORES, PESSOAS, request.POST, request.FILES)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            senhasugestao = '*' #para visualizar uma sugestao anonima é preciso ter uma senha que identifica o criador
            if Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']).usuario == '000000': #verifica se a sugestão é anonima
                senhasugestao = GerarSenha()
            if request.FILES:
                sugestaoobj = sugestao(status='1', titulo=request.POST['titulo'], setor=Sugestao.core.models.setor.objects.get(id=request.POST['setor']), pessoa=Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], imagem=request.FILES['imagem'], datahora=datetime.now(), senha=senhasugestao)
            else:
                sugestaoobj = sugestao(status='1', titulo=request.POST['titulo'], setor=Sugestao.core.models.setor.objects.get(id=request.POST['setor']), pessoa=Sugestao.core.models.pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], datahora=datetime.now(), senha=senhasugestao)
            sugestaoobj.save()

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = sugestaoobj.id
            contexto['senha'] = sugestaoobj.senha
            contexto['imagem'] = sugestaoobj.imagem
            contexto['setor'] = sugestaoobj.setor
            contexto['pessoa'] = sugestaoobj.pessoa

            # tenta recuperar o email do criador da sugestão
            mail = sugestaoobj.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Não responda essa mensagem '+ str(sugestaoobj.id),
                [settings.DEFAULT_FROM_EMAIL, ],
                sugestaoobj.setor.email, mail,
                'sugerir/sugestao_email.html',
                contexto)
            # add msg
            messages.success(request, 'Sugestão número '+ str(sugestaoobj.id)+ ' salva com sucesso!')

            #Se foi realizado upload de imagem
            if not str(sugestaoobj.imagem) == 'uploads/default.png':
                #Diminuir resolução da imagem
                t = threading.Thread(target=comprimir, args=(request, sugestaoobj.imagem), kwargs={})
                t.setDaemon(True)
                t.start()
            return redirect(r('DetalharSugestao', str(sugestaoobj.id), sugestaoobj.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FazerSugestao', 'err': '','form': form, 'itemselec': 'HOME', 'titulo': 'Deixe Sua Sugestão'})


def EditarSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

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
            return redirect(r('DetalharSugestao', str(sugestaoobj.id), edicaoobj.sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'EditarSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME', "titulo": 'Editar Sugestão: '+ id})


def ResponderSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

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

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = respostaobj.sugestao.id
            contexto['senha'] = respostaobj.sugestao.senha
            contexto['pessoa'] = respostaobj.pessoa.nome
            contexto['titulo'] = "A Sugestão "+str(respostaobj.sugestao.id) +" foi respondida"

            # tenta recuperar o email do criador da sugestão
            mail = respostaobj.sugestao.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Não responda essa mensagem '+ str(respostaobj.sugestao.id),
                [settings.DEFAULT_FROM_EMAIL, ],
                sugestaoobj.setor.email, mail,
                'sugerir/resposta_email.html',
                contexto)

            messages.success(request, 'Resposta salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id), respostaobj.sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'ResponderSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME', 'titulo': 'Responder Sugestão: '+ id})


def FinalizarSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

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

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = finalizacaoobj.sugestao.id
            contexto['senha'] = finalizacaoobj.sugestao.senha
            contexto['pessoa'] = finalizacaoobj.pessoa.nome
            contexto['titulo'] = "A Sugestão "+str(finalizacaoobj.sugestao.id) +" foi finalizada"

            # tenta recuperar o email do criador da sugestão
            mail = finalizacaoobj.sugestao.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Não responda essa mensagem '+ str(finalizacaoobj.sugestao.id),
                [settings.DEFAULT_FROM_EMAIL, ],
                sugestaoobj.setor.email, mail,
                'sugerir/finalizacao_email.html',
                contexto)

            messages.success(request, 'Sugestão finalizada com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestaoobj.id), finalizacaoobj.sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FinalizarSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME', 'titulo': 'Finalizar Sugestão: '+ id})


def DetalharSugestao(request, id, senha):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    msganonima = '' #mensagem que aparece para sugestões anônimas

    # Verificar se foi aberto por mim ou para mim
    try:
        sugestaoobj = sugestao.objects.get(id=id)
    except:
        messages.success(request, 'Não encontrada')
        return redirect(r('Sugestoes'))

    editar = ''
    responder = ''
    visualizar = ''
    finalizar = ''

    try:
        respostaobj = resposta.objects.get(sugestao=sugestaoobj.id) # verifica se há uma resposta
        if sugestaoobj.pessoa.usuario == request.session['userl']: #O usuário pode editar a sugestão
            visualizar = 'visualizar'
        if sugestaoobj.setor.responsavel == pessoa.objects.get(usuario=request.session['userl']): #O usuário pode finalizar a sugestão
            finalizar = 'finalizar'
    except:
        if sugestaoobj.pessoa.usuario == request.session['userl']: #O usuário pode editar a sugestão
            editar = 'editar'
        if sugestaoobj.setor.responsavel == pessoa.objects.get(usuario=request.session['userl']): #O usuário pode responder a sugestão
            responder = 'responder'
    if sugestaoobj.pessoa.usuario == '000000':# foi criada anonimamente
        visualizar = 'visualizar'
        msganonima = "Sugestões anônimas não aparecem na sua lista de sugestões. Para acompanhar o feedback delas, você deve guardar o seu número ("+id+") e a chave de acesso ("+sugestaoobj.senha+"). Sugerimos imprimir ou salvar essa página em PDF."
        # Verifica a senha no caso de mensagens anomimas
        if (not sugestaoobj.senha == senha) and (finalizar == '' and responder == ''):# Redireciona para pedir a senha caso ela não esteja correta, só precisa por senha se a sugestão não for para você
            messages.error(request, 'Informe uma chave de acesso válida para visualizar essa sugestão')
            return render(request, 'sugerir/senha_sugestao.html', {'err': '', 'itemselec': 'SUGESTÕES', 'sugestao': sugestaoobj, 'id': id})

    if editar == '' and responder == '' and visualizar == '' and finalizar =='': #Apessoa não tem direito a visializar essa sugestão, redireciona para a página de sugestões
        messages.error(request, 'Você não pode acessar essa página')
        return redirect(r('Sugestoes'))
    edicaoobj = edicao.objects.filter(sugestao=id).order_by('-datahora')
    respostaobj = resposta.objects.filter(sugestao=id)
    finalizacaoaobj = finalizacao.objects.filter(sugestao=id)

    return render(request, 'sugerir/detalhar_sugestao.html', {'err': '', 'editar': editar, 'responder': responder, 'finalizar': finalizar, 'itemselec': 'SUGESTÕES', 'sugestao': sugestaoobj, 'edicoes': edicaoobj, 'respostas': respostaobj, 'finalizacoes': finalizacaoaobj, 'msganonima': msganonima})


def SugestoesPraMim(request, view):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            idpessoa = pessoa.objects.get(usuario=request.session['userl'])
            if view == '1':
                sugestoesparamim = sugestao.objects.filter(setor__responsavel=idpessoa, status='1') #filtra as sugestões atribuidas ao setor que eu sou responsável
            else:
                sugestoesparamim = sugestao.objects.filter(setor__responsavel=idpessoa) #filtra as sugestões atribuidas ao setor que eu sou responsável
            return render(request, 'sugerir/list_sugestoes.html', {'err': '', 'itemselec': 'HOME', 'sugestoesparamim': sugestoesparamim, 'titulo': 'Sugestões Para Mim', 'URL': 'SugestoesPraMim', 'view': view})

    except KeyError:
        return redirect(r('Login'))


def MinhasSugestoes(request, view):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            if view == '1':
                sugestoes = sugestao.objects.filter(pessoa__usuario=request.session['userl'], status='1') #filtra as sugestões para mostrar somente as realizadas por esse usuário, e estejam ativas
            else:
                sugestoes = sugestao.objects.filter(pessoa__usuario=request.session['userl']) #filtra as sugestões para mostrar somente as realizadas por esse usuário
            return render(request, 'sugerir/list_sugestoes.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'HOME', 'titulo': 'Minhas Sugestões', 'URL': 'MinhasSugestoes', 'view': view})

    except KeyError:
        return redirect(r('Login'))


def Sugestoes(request):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            return render(request, 'sugerir/sugestoes.html', {'err': '', 'itemselec': 'SUGESTÕES', 'titulo': 'Sugestões',})

    except KeyError:
        return redirect(r('Login'))


def VaParaSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    if request.method == 'POST':
        if request.POST.get('id'):
            return redirect(r("DetalharSugestao", request.POST['id'], request.POST['key']))
    return redirect(r('Sugestoes'))


def _send_email(subject, from_, to, copy, template_name, context):

    cfg = config.objects.get(id=1)

    settings.EMAIL_HOST = cfg.email_host
    settings.EMAIL_PORT = cfg.email_port
    settings.EMAIL_HOST_USER = cfg.email_host_user
    settings.EMAIL_HOST_PASSWORD = cfg.email_host_password

    body = render_to_string(template_name, context)
    #mail.send_mail(subject, body, from_, to, html_message=body)

    email = EmailMessage(
            subject,
            body,
            from_,
            [to],
            [copy],
            reply_to=['cpd.paraiso@ifto.edu.br']
        )
    email.content_subtype = "html"
    email.send(fail_silently=True)


def GerarSenha():
    return(random.randint(10000000, 99999999)) #retorna uma senha aleatória


def comprimir(request, imagem):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    localimagem = os.path.join(BASE_DIR + '/media/'+ str(imagem))

    im = Image.open(localimagem)
    im.save(localimagem, dpi=(600, 600))

    print(localimagem)
    print('\nFinalizada a compressão\n')
