from django import forms
from django.utils.datetime_safe import datetime

import Sugestao
from Sugestao.core.models import sugestao


class SugestaoForm(forms.Form):
    titulo = forms.CharField(label='Título')
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
        titulo = cleaned_data.get('titulo')
        setor = cleaned_data.get("setor")
        pessoa = cleaned_data.get("pessoa")
        descricao = cleaned_data.get("descricao")
        imagem = cleaned_data.get("imagem")

        return cleaned_data


class SugestaoEdicaoForm(forms.Form):
    descricao = forms.CharField(label="Sugestão", widget=forms.Textarea())


    def clean(self):
        cleaned_data = self.cleaned_data
        descricao = cleaned_data.get("descricao")

        return cleaned_data
