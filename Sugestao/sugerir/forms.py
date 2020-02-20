from django import forms
from django.utils.datetime_safe import datetime

import Sugestao
from Sugestao.core.models import sugestao


class SugestaoForm(forms.Form):
    setor = forms.ChoiceField(label="Setor")
    pessoa = forms.ChoiceField(label="Pessoa")
    descricao = forms.CharField(label="Sugestão", widget=forms.Textarea())
    imagem = forms.ImageField(label="", required=False, widget=forms.FileInput(attrs={'accept': 'image/*'}))


    def __init__(self, request, SETORES, PESSOAS, *args, **kwargs):
        super(SugestaoForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['setor'].choices = SETORES
        self.fields['pessoa'].choices = PESSOAS


    def clean(self):
        cleaned_data = self.cleaned_data
        setor = cleaned_data.get("setor")
        pessoa = cleaned_data.get("pessoa")
        descricao = cleaned_data.get("descricao")
        imagem = cleaned_data.get("imagem")

        sugestaoobj = sugestao(setor=Sugestao.core.models.setor.objects.get(id=setor), pessoa=Sugestao.core.models.pessoa.objects.get(id=pessoa), descricao=descricao, imagem=imagem, datahora=datetime.now())
        sugestaoobj.save()
        print(sugestaoobj.id)

        return cleaned_data
