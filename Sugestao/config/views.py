import sys
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, resolve_url as r


# Create your views here.
from Sugestao.config.forms import AdForm, SetorForm, PessoaForm
from Sugestao.core.models import config, setor, pessoa


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
            model = (config.objects.get(id=1))
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
    setores = setor.objects.all()
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
            obj = setor.objects.get(id=id)
            editar = True
            form = SetorForm(request, initial={'nome': obj.nome, 'responsavel': obj.responsavel, 'email': obj.email})

        if request.method == 'POST':
            form = SetorForm(request, data=request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                if editar:
                    obj.nome = request.POST['nome']
                    obj.responsavel = pessoa.objects.get(id=request.POST['responsavel'])
                    obj.email = request.POST['email']
                    obj.save()
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
    pessoas = pessoa.objects.all()
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
            obj = pessoa.objects.get(id=id)
            editar = True
            form = PessoaForm(request, initial={'nome': obj.nome, 'usuario': obj.usuario, 'status': obj.status, 'email': obj.email})

        if request.method == 'POST':
            form = PessoaForm(request, data=request.POST)
            # Checa se os dados são válidos:
            if form.is_valid():
                if editar:
                    obj.nome = request.POST['nome']
                    obj.usuario = request.POST['usuario']
                    obj.status = request.POST['status']
                    obj.email = request.POST['email']
                    obj.save()
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
