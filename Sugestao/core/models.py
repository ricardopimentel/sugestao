from __future__ import unicode_literals

from django.db import models
from tinymce import models as tinymce_models

# Create your models here.
class pessoa (models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.CharField(max_length=11, unique=True)
    status = models.BooleanField()


    def __str__(self):
        return str(self.nome)


class administrador (models.Model):
    id_pessoa = models.ForeignKey(pessoa)


    def __str__(self):
        return str(pessoa.nome)


class user (models.Model):
    id_pessoa = models.ForeignKey(pessoa)


    def __str__(self):
        return str(pessoa.nome)


class config(models.Model):
    dominio = models.CharField(max_length=200)
    endservidor = models.CharField(max_length=200)
    gadmin = models.CharField(max_length=200)
    ou = models.CharField(max_length=200)
    filter = models.TextField('Filtro')


class setor(models.Model):
    nome = models.CharField(max_length=200)
    responsavel = models.ForeignKey(pessoa)
    email = models.EmailField(max_length=200)


    def __str__(self):
        return self.nome


class sugestao(models.Model):
    descricao = tinymce_models.HTMLField(max_length=10000)
    imagem = models.ImageField('Imagem', upload_to='uploads/', default='uploads/default.png')
    datahora = models.DateTimeField('Data')
    setor = models.ForeignKey(setor)
    pessoa = models.ForeignKey(pessoa)


class obs(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    setor = models.ForeignKey(sugestao)
