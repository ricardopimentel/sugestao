from __future__ import unicode_literals

from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class Pessoa (models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=70)
    status = models.BooleanField()

    def __str__(self):
        return str(self.nome)


class Administrador (models.Model):
    id_pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)

    def __str__(self):
        return str(Pessoa.nome)


class User (models.Model):
    id_pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)

    def __str__(self):
        return str(Pessoa.nome)


class Config(models.Model):
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


class Setor(models.Model):
    nome = models.CharField(max_length=200, unique=True)
    responsavel = models.ForeignKey(Pessoa, on_delete=models.PROTECT, limit_choices_to={'status': True})
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.nome


class Sugestao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = HTMLField(max_length=10000)
    imagem = models.ImageField('Imagem', upload_to='uploads/', default='uploads/default.png')
    datahora = models.DateTimeField('Data')
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)
    senha = models.CharField(max_length=8, default='*')
    status = models.BooleanField()


class Obs(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(Sugestao, on_delete=models.PROTECT)


class Resposta(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.OneToOneField(Sugestao, on_delete=models.PROTECT, related_name='sugestoes')
    imagem = models.ImageField('Imagem', upload_to='uploads/', default='uploads/default.png')
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)


class Edicao(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(Sugestao, on_delete=models.PROTECT)


class Redirecionamento(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.ForeignKey(Sugestao, on_delete=models.PROTECT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)
    depara = models.CharField(max_length=1000)


class Finalizacao(models.Model):
    descricao = models.CharField(max_length=1000)
    datahora = models.DateTimeField('Data')
    sugestao = models.OneToOneField(Sugestao, on_delete=models.PROTECT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)
