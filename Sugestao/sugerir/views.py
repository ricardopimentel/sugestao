import os
import random
import threading

from PIL import Image
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, resolve_url as r, render_to_response
from django.template.loader import render_to_string
from django.utils.datetime_safe import datetime

# import Sugestao
from django.conf import settings
from Sugestao.core.models import Setor, Pessoa, Sugestao, Edicao, Resposta, Finalizacao, Config
from Sugestao.sugerir.forms import SugestaoForm, SugestaoEdicaoForm


def FazerSugestao(request):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    #Preencher Formulário
    SETORES = []
    setores = Setor.objects.all()
    SETORES.append(('', 'Para qual setor é a sugestão?'))
    for setor in setores:
        SETORES.append((setor.id, setor.nome))
    PESSOAS = []
    pessoas = Pessoa.objects.filter(nome="Anônimo") | Pessoa.objects.filter(nome=request.session['nomesugestao']) #Filtra o objeto pessoa, anonima e a pessoa logada
    PESSOAS.append(('', 'Você deseja se identificar?'))
    for pessoa in pessoas:
        PESSOAS.append((pessoa.id, pessoa.nome))
    form = SugestaoForm(request, SETORES, PESSOAS)

    if request.method == 'POST':
        form = SugestaoForm(request, SETORES, PESSOAS, request.POST, request.FILES)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            senhasugestao = '*' #para visualizar uma sugestao anonima é preciso ter uma senha que identifica o criador
            if Pessoa.objects.get(id=request.POST['pessoa']).usuario == '000000': #verifica se a sugestão é anonima
                senhasugestao = GerarSenha()
            if request.FILES:
                sugestao = Sugestao(status='1', titulo=request.POST['titulo'], setor=Setor.objects.get(id=request.POST['setor']), pessoa=Pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], imagem=request.FILES['imagem'], datahora=datetime.now(), senha=senhasugestao)
            else:
                sugestao = Sugestao(status='1', titulo=request.POST['titulo'], setor=Setor.objects.get(id=request.POST['setor']), pessoa=Pessoa.objects.get(id=request.POST['pessoa']), descricao=request.POST['descricao'], datahora=datetime.now(), senha=senhasugestao)
            sugestao.save()

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = sugestao.id
            contexto['senha'] = sugestao.senha
            contexto['imagem'] = sugestao.imagem
            contexto['setor'] = sugestao.setor
            contexto['pessoa'] = sugestao.pessoa

            # tenta recuperar o email do criador da sugestão
            mail = sugestao.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Sugestão '+ str(sugestao.id),
                sugestao.setor.email, mail,
                'sugerir/sugestao_email.html',
                contexto)
            # add msg
            messages.success(request, 'Sugestão número '+ str(sugestao.id)+ ' salva com sucesso!')

            #Se foi realizado upload de imagem
            if not str(sugestao.imagem) == 'uploads/default.png':
                #Diminuir resolução da imagem
                t = threading.Thread(target=comprimir, args=(request, sugestao.imagem), kwargs={})
                t.setDaemon(True)
                t.start()
            return redirect(r('DetalharSugestao', str(sugestao.id), sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'FazerSugestao', 'err': '','form': form, 'itemselec': 'HOME', 'titulo': 'Deixe Sua Sugestão'})


def EditarSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    #Preencher Formulário

    sugestao = Sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestao.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            edicao = Edicao(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.objects.get(id=id))
            edicao.save()
            messages.success(request, 'Edição salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestao.id), edicao.sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'EditarSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME', "titulo": 'Editar Sugestão: '+ id})


def ResponderSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    #Preencher Formulário

    sugestao = Sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestao.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            resposta = Resposta(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.objects.get(id=id), pessoa=Pessoa.objects.get(usuario=request.session['userl']))
            resposta.save()

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = resposta.sugestao.id
            contexto['senha'] = resposta.sugestao.senha
            contexto['pessoa'] = resposta.pessoa.nome
            contexto['titulo'] = "A Sugestão "+str(resposta.sugestao.id) +" foi respondida"

            # tenta recuperar o email do criador da sugestão
            mail = resposta.sugestao.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Sugestão '+ str(resposta.sugestao.id),
                sugestao.setor.email, mail,
                'sugerir/resposta_email.html',
                contexto)

            messages.success(request, 'Resposta salva com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestao.id), resposta.sugestao.senha))

    return render(request, 'sugerir/cadastro_sugestao.html', {'URL': 'ResponderSugestao', 'err': '','id': id, 'form': form, 'itemselec': 'HOME', 'titulo': 'Responder Sugestão: '+ id})


def FinalizarSugestao(request, id):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            pass
    except KeyError:
        return redirect(r('Login'))

    #Preencher Formulário

    sugestao = Sugestao.objects.get(id=id)#Buscar dados da sugestão a ser alterada

    #criar instancia do formulário preencido
    form = SugestaoEdicaoForm(initial={'descricao': sugestao.descricao})
    #Verifica se vieram dados pelo post
    if request.method == 'POST':
        form = SugestaoEdicaoForm(request.POST)
        if form.is_valid():# se dados do formulário são válidos, salva os dados na linha abaixo
            finalizacao = Finalizacao(descricao=request.POST['descricao'], datahora=datetime.now(), sugestao=Sugestao.objects.get(id=id), pessoa=Pessoa.objects.get(usuario=request.session['userl']))
            finalizacao.save()
            sugestao.status=False
            sugestao.save()

            # Send email
            # Preparação de contexto
            contexto = form.cleaned_data
            contexto['id'] = finalizacao.sugestao.id
            contexto['senha'] = finalizacao.sugestao.senha
            contexto['pessoa'] = finalizacao.pessoa.nome
            contexto['titulo'] = "A Sugestão "+str(finalizacao.sugestao.id) +" foi finalizada"

            # tenta recuperar o email do criador da sugestão
            mail = finalizacao.sugestao.pessoa.email
            if mail == 'Não informado':
                mail = ''
            # Envio da msg
            _send_email('Sugestão '+ str(finalizacao.sugestao.id),
                sugestao.setor.email, mail,
                'sugerir/finalizacao_email.html',
                contexto)

            messages.success(request, 'Sugestão finalizada com sucesso!')
            return redirect(r('DetalharSugestao', str(sugestao.id), finalizacao.sugestao.senha))

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
        sugestao = Sugestao.objects.get(id=id)
    except:
        messages.success(request, 'Não encontrada')
        return redirect(r('Sugestoes'))

    editar = ''
    responder = ''
    visualizar = ''
    finalizar = ''

    try:
        resposta = Resposta.objects.get(sugestao=sugestao.id) # verifica se há uma resposta
        if sugestao.pessoa.usuario == request.session['userl']: #O usuário pode editar a sugestão
            visualizar = 'visualizar'
        if sugestao.setor.responsavel == Pessoa.objects.get(usuario=request.session['userl']): #O usuário pode finalizar a sugestão
            finalizar = 'finalizar'
    except:
        if sugestao.pessoa.usuario == request.session['userl']: #O usuário pode editar a sugestão
            editar = 'editar'
        if sugestao.setor.responsavel == Pessoa.objects.get(usuario=request.session['userl']): #O usuário pode responder a sugestão
            responder = 'responder'
    if sugestao.pessoa.usuario == '000000':# foi criada anonimamente
        visualizar = 'visualizar'
        msganonima = "Sugestões anônimas não aparecem na sua lista de sugestões. Para acompanhar o feedback delas, você deve guardar o seu número ("+id+") e a chave de acesso ("+sugestao.senha+"). Sugerimos imprimir ou salvar essa página em PDF."
        # Verifica a senha no caso de mensagens anomimas
        if (not sugestao.senha == senha) and (finalizar == '' and responder == ''):# Redireciona para pedir a senha caso ela não esteja correta, só precisa por senha se a sugestão não for para você
            messages.error(request, 'Informe uma chave de acesso válida para visualizar essa sugestão')
            return render(request, 'sugerir/senha_sugestao.html', {'err': '', 'itemselec': 'SUGESTÕES', 'sugestao': sugestao, 'id': id})

    if editar == '' and responder == '' and visualizar == '' and finalizar =='': #Apessoa não tem direito a visializar essa sugestão, redireciona para a página de sugestões
        messages.error(request, 'Você não pode acessar essa página')
        return redirect(r('Sugestoes'))
    edicao = Edicao.objects.filter(sugestao=id).order_by('-datahora')
    resposta = Resposta.objects.filter(sugestao=id)
    finalizacao = Finalizacao.objects.filter(sugestao=id)

    return render(request, 'sugerir/detalhar_sugestao.html', {'err': '', 'editar': editar, 'responder': responder, 'finalizar': finalizar, 'itemselec': 'SUGESTÕES', 'sugestao': sugestao, 'edicoes': edicao, 'respostas': resposta, 'finalizacoes': finalizacao, 'msganonima': msganonima})


def SugestoesPraMim(request, view):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            idpessoa = Pessoa.objects.get(usuario=request.session['userl'])
            if view == '1':
                sugestoesparamim = Sugestao.objects.filter(setor__responsavel=idpessoa, status='1') #filtra as sugestões atribuidas ao setor que eu sou responsável
            else:
                sugestoesparamim = Sugestao.objects.filter(setor__responsavel=idpessoa) #filtra as sugestões atribuidas ao setor que eu sou responsável
            return render(request, 'sugerir/list_sugestoes.html', {'err': '', 'itemselec': 'SUGESTÕES', 'sugestoesparamim': sugestoesparamim, 'titulo': 'Sugestões Para Mim', 'URL': 'SugestoesPraMim', 'view': view})

    except KeyError:
        return redirect(r('Login'))


def MinhasSugestoes(request, view):
    try:# Verificar se usuario esta logado
        if request.session['nomesugestao']:
            if view == '1':
                sugestoes = Sugestao.objects.filter(pessoa__usuario=request.session['userl'], status='1') #filtra as sugestões para mostrar somente as realizadas por esse usuário, e estejam ativas
            else:
                sugestoes = Sugestao.objects.filter(pessoa__usuario=request.session['userl']) #filtra as sugestões para mostrar somente as realizadas por esse usuário
            return render(request, 'sugerir/list_sugestoes.html', {'err': '','sugestoes': sugestoes, 'itemselec': 'SUGESTÕES', 'titulo': 'Minhas Sugestões', 'URL': 'MinhasSugestoes', 'view': view})

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


def _send_email(subject, to, copy, template_name, context):

    config = Config.objects.get(id=1)
    setattr(settings, 'EMAIL_HOST', config.email_host)
    setattr(settings, 'EMAIL_PORT', config.email_port)
    setattr(settings, 'EMAIL_HOST_USER', config.email_host_user)
    setattr(settings, 'EMAIL_HOST_PASSWORD', config.email_host_password)

    body = render_to_string(template_name, context)
    #mail.send_mail(subject, body, from_, to, html_message=body)

    email = EmailMessage(
            subject,
            body,
            [to],
            [copy],
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
