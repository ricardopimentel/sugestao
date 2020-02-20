from django.contrib import messages
from django.shortcuts import render, redirect, resolve_url as r, render_to_response

import Sugestao
from Sugestao.core.models import setor, pessoa, sugestao
from Sugestao.sugerir.forms import SugestaoForm


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
        if form.is_valid():
            #sugestaoobj = sugestao(setor=Sugestao.core.models.setor.objects.get(id=setor), pessoa=Sugestao.core.models.pessoa.objects.get(id=pessoa), descricao=descricao, imagem=imagem, datahora=datetime.now())
            #sugestaoobj.save()
            #print(sugestaoobj.id)
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect(r('FazerSugestao'))
        else:
            messages.success(request, 'Erro ao salvar sua sujestão')
            return redirect(r('FazerSugestao'))
    return render(request, 'sugerir/cadastro_sugestao.html', {'err': '','form': form, 'itemselec': 'HOME'})
