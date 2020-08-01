from __future__ import unicode_literals

from django.db import models
from tinymce import models as tinymce_models

# Create your models here.
class pessoa (models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.CharField(max_length=11, unique=True)
    email = models.CharField(max_length=70)
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
    email_host = models.CharField(max_length=20)
    email_port = models.CharField(max_length=10)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=50)
    email_host_password = models.CharField(max_length=100)


class setor(models.Model):
    nome = models.CharField(max_length=200)
    responsavel = models.ForeignKey(pessoa)
    email = models.EmailField(max_length=200)


    def __str__(self):
        return self.nome


class sugestao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = tinymce_models.HTMLField(max_length=10000)
    imagem = models.ImageField('Imagem', upload_to='uploads/', default='uploads/default.png')
    datahora = models.DateTimeField('Data')
    setor = models.ForeignKey(setor)
    pessoa = models.ForeignKey(pessoa)
    senha = models.CharField(max_length=8, default='*')
    status = models.BooleanField()


class obs(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(sugestao)


class resposta(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(sugestao)
    imagem = models.ImageField('Imagem', upload_to='uploads/', default='uploads/default.png')
    pessoa = models.ForeignKey(pessoa)


class edicao(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(sugestao)


class finalizacao(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(sugestao)
    pessoa = models.ForeignKey(pessoa)
