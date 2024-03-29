import datetime
import sys
import threading
from datetime import timedelta
from django.utils import timezone

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, resolve_url as r


# Create your views here.
import Sugestao.core.models
from django.conf import settings
from Sugestao.config.forms import AdForm, SetorForm, PessoaForm, EmailForm, TestEmailForm
from Sugestao.core.models import Config, Setor, Pessoa, Sugestao, Resposta
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def Administracao(request):
    if dict(request.session).get('nomesugestao'):
        return render(request, 'config/administracao.html', {
            'title': 'Administração',
            'itemselec': 'ADMINISTRAÇÃO',
        })
    return redirect(r('Login'))


def Dados_ad(request):
    if not dict(request.session).get('nomesugestao'):
        return redirect(r('Login'))

    if dict(request.session).get('usertip') == 'admin':
        try:
            model = (Config.objects.get(id=1))
            # Vefirica se veio aolgo pelo POST
            if request.method == 'POST':
                # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
                form = AdForm(request, data=request.POST)
                # Checa se os dados são válidos:
                if form.is_valid():
                    # Chama a página novamente
                    messages.success(request, 'Configurações salvas com sucesso!')
                return render(request, 'config/admin_config_ad.html', {'form': form})
            else:
                form = AdForm(request, initial={
                    'dominio': model.dominio,
                    'endservidor': model.endservidor,
                    'gadmin': model.gadmin,
                    'ou': model.ou, 'filter': model.filter
                })
                return render(request, 'config/admin_config_ad.html', {
                    'title': 'Config. LDAP',
                    'itemselec': 'ADMINISTRAÇÃO',
                    'form': form,
                })
        except ObjectDoesNotExist:
            model = ''
            messages.error(request, sys.exc_info())
            return redirect(r('Administracao'))
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect(r('Home'))

def ConfEmail(request):
    if dict(request.session).get('usertip') == 'admin':
        try:
            config = Config.objects.get(id=1)
            # Vefirica se veio algo pelo POST
            if request.method == 'POST':
                # cria uma instancia do formulario
                form = EmailForm(request, data=request.POST)
                # Checa se os dados são válidos:
                if form.is_valid():
                    # Chama a página novamente
                    messages.success(request, 'Configurações salvas com sucesso!')
                return render(request, 'config/admin_config_email.html', {'form': form})
            else:
                form = EmailForm(request, initial={
                    'email_host': config.email_host,
                    'email_host_password': config.email_host_password,
                    'email_host_user': config.email_host_user,
                    'email_port': config.email_port
                })
                return render(request, 'config/admin_config_email.html', {
                    'title': 'Config. Email',
                    'itemselec': 'ADMINISTRAÇÃO',
                    'form': form,
                })
        except ObjectDoesNotExist:
            model = ''
            messages.error(request, sys.exc_info())
            return redirect(r('Administracao'))
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect(r('Home'))

def ConfEmailTest(request):
    if dict(request.session).get('usertip') == 'admin':
        try:
            # Vefirica se veio algo pelo POST
            if request.method == 'POST':
                # cria uma instancia do formulario
                form = TestEmailForm(request, data=request.POST)
                # Checa se os dados são válidos:
                if form.is_valid():
                    # Chama a página novamente
                    #tenta enviar e-mail
                    mail = request.POST['destinatario']
                    # Envio da msg
                    _send_email('Sugestão ',
                                [settings.DEFAULT_FROM_EMAIL, ], mail,
                                'sugerir/sugestao_test_email.html',{'texto': request.POST['texto']})
                    # add msg
                    messages.success(request, 'E-mail enviado com sucesso!')
                return render(request, 'config/admin_config_email_test.html', {'form': form})
            else:
                form = TestEmailForm(request)
                return render(request, 'config/admin_config_email_test.html', {
                    'title': 'Config. Email',
                    'itemselec': 'ADMINISTRAÇÃO',
                    'form': form,
                })
        except ObjectDoesNotExist:
            model = ''
            messages.error(request, sys.exc_info())
            return redirect(r('Administracao'))
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect(r('Home'))


def ConfEmailEnvioLembretes(request, enviar):
    if dict(request.session).get('usertip') == 'admin':
        try:
            dias = timezone.now() - timedelta(days=5)
            sugestoes = Sugestao.objects.prefetch_related('sugestoes').filter(sugestoes=None, datahora__lte=dias)
            form = TestEmailForm(request)

            if (enviar == 'sim'):
                #pega a data de hoje
                hj = datetime.datetime.now()
                for sugestao in sugestoes:
                    contexto = dict()
                    contexto['id'] = sugestao.id
                    contexto['senha'] = sugestao.senha
                    contexto['imagem'] = sugestao.imagem
                    contexto['setor'] = sugestao.setor
                    contexto['pessoa'] = sugestao.pessoa
                    contexto['descricao'] = sugestao.descricao
                    contexto['titulo'] = "Lembrete de sugestão não respondida"
                    contexto['texto'] = "Estamos enviando um lebrete pois a sugestão número: "+str(sugestao.id)+" ainda não foi respondida"
                    contexto['data'] = sugestao.datahora
                    contexto['dias'] = (hj - sugestao.datahora).days

                    # Envio da msg
                    mail = sugestao.setor.email
                    # Abrir Thread
                    t = threading.Thread(target=_thread_email, args=(request, 'Sugestão '+str(sugestao.id), [settings.DEFAULT_FROM_EMAIL, ], mail, 'sugerir/lembrete_email.html', contexto), kwargs={})
                    t.setDaemon(True)
                    t.start()

            return render(request, 'config/admin_config_email_envio_lembretes.html', {
                'title': 'Config. Email',
                'itemselec': 'ADMINISTRAÇÃO',
                'sugestoes': sugestoes,
                'form': form,
            })
        except ObjectDoesNotExist:
            model = ''
            messages.error(request, sys.exc_info())
            return redirect(r('Administracao'))
    else:
        messages.error(request, "Você não tem permissão para acessar essa página, redirecionando para HOME")
        return redirect(r('Home'))


def ConfigInicial(request):
    form = AdForm(request)
    if request.method == 'POST':
        # cria uma instancia do formulario de preenchimento dos dados do AD com os dados vindos do request POST:
        form = AdForm(request, data=request.POST)
        # Checa se os dados são válidos:
        if form.is_valid():
            return redirect(r('Login'))
    return render(request, 'config/admin_config_ad_inicial.html', {
        'title': 'Config. Inicial',
        'itemselec': 'ADMINISTRAÇÃO',
        'form': form,
    })


def GerenciarSetores(request):
    setores = Setor.objects.all()
    if dict(request.session).get('nomesugestao'):
        return render(request, 'config/gerenciar_setor.html', {
            'title': 'Administração',
            'itemselec': 'ADMINISTRAÇÃO',
            'setores': setores,
        })
    return redirect(r('Login'))


def CadastroSetor(request, id):
    if dict(request.session).get('nomesugestao'):
        editar =False

        if id == 'cadastro': # verifica se é para cadastrar ou alterar
            form = SetorForm(request)
        else: # se for para alterar cria um formulário já preenchido
            setor = Setor.objects.get(id=id)
            editar = True
            form = SetorForm(request, initial={'nome': setor.nome, 'responsavel': setor.responsavel, 'email': setor.email})

        if request.method == 'POST':
            if editar:
                setor = Setor.objects.get(id=id)
                form = SetorForm(request, request.POST, instance=setor)
            else:
                form = SetorForm(request, request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                if editar:
                    setor.nome = request.POST['nome']
                    setor.responsavel = Pessoa.objects.get(id=request.POST['responsavel'])
                    setor.email = request.POST['email']
                    setor.save()
                else:
                    form.save()
                messages.success(request, "Sucesso!")
                return redirect(r('GerenciarSetores'))

        return render(request, 'config/admin_cadastro_setor.html', {
            'title': 'Administração',
            'itemselec': 'ADMINISTRAÇÃO',
            'id': id,
            'titulo': 'Cadastro de Setor',
            'form': form,
        })
    return redirect(r('Login'))


def GerenciarPessoas(request):
    pessoas = Pessoa.objects.all().exclude(usuario='000000')
    if dict(request.session).get('nomesugestao'):
        return render(request, 'config/gerenciar_pessoa.html', {
            'title': 'Administração',
            'itemselec': 'ADMINISTRAÇÃO',
            'pessoas': pessoas,
        })
    return redirect(r('Login'))


def CadastroPessoa(request, id):
    if dict(request.session).get('nomesugestao'):
        editar =False

        if id == 'cadastro': # verifica se é para cadastrar ou alterar
            form = PessoaForm(request)
        else: # se for para alterar cria um formulário já preenchido
            editar = True
            pessoa = Pessoa.objects.get(id=id)
            form = PessoaForm(request, initial={'nome': pessoa.nome, 'usuario': pessoa.usuario, 'status': pessoa.status, 'email': pessoa.email})

        if request.method == 'POST':
            if editar:
                pessoa = Pessoa.objects.get(id=id)
                form = PessoaForm(request, request.POST, instance=pessoa)
            else:
                form = PessoaForm(request, request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                if editar:
                    pessoa.nome = request.POST['nome']
                    pessoa.usuario = request.POST['usuario']
                    if dict(request.POST).get('status'):
                        pessoa.status = request.POST['status']
                    else:
                        pessoa.status = False
                    pessoa.email = request.POST['email']
                    pessoa.save()
                else:
                    form.save()
                messages.success(request, "Sucesso!")
                return redirect(r('GerenciarPessoas'))
        return render(request, 'config/admin_cadastro_pessoa.html', {
            'title': 'Administração',
            'itemselec': 'ADMINISTRAÇÃO',
            'id': id,
            'titulo': 'Cadastro de Pessoas',
            'form': form,
        })
    return redirect(r('Login'))


def _thread_email(request, subject, from_, to, template_name, context):
    try:
        config = Config.objects.get(id=1)
        setattr(settings, 'EMAIL_HOST', config.email_host)
        setattr(settings, 'EMAIL_PORT', config.email_port)
        setattr(settings, 'EMAIL_HOST_USER', config.email_host_user)
        setattr(settings, 'EMAIL_HOST_PASSWORD', config.email_host_password)

        body = render_to_string(template_name, context)
        # mail.send_mail(subject, body, from_, to, html_message=body)

        email = EmailMessage(
            subject,
            body,
            from_,
            [to],
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)

        print('\nTerminado\n')
    except:
        messages.error(request, sys.exc_info())
        return redirect(r('Home'))


def _send_email(subject, from_, to, template_name, context):

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
            from_,
            [to],
        )
    email.content_subtype = "html"
    email.send(fail_silently=True)
