from django import forms

from Sugestao.core.models import sugestao


class SugestaoForm(forms.ModelForm):
    descricao = forms.CharField(label="Sugestão", widget=forms.Textarea())
    imagem = forms.ImageField(label="", required=False, widget=forms.FileInput(attrs={'accept': 'image/*'}))
    datahora = forms.DateTimeField(label='')

    class Meta:  # Define os campos vindos do Model
        model = sugestao
        fields = ('setor', 'pessoa', 'descricao', 'imagem', 'datahora')
