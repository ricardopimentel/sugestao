from django import forms
from django.core.exceptions import ObjectDoesNotExist

from Sugestao.core.models import Config, Setor, Pessoa
from Sugestao.core.libs.conexaoAD3 import conexaoAD


class AdForm(forms.ModelForm):
    # Cria dois campos que não estão no banco de dados, são eles: usuário e senha. Os dados desses campos são providos pelo Active Directory
    usuario = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    senha = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    filter = forms.CharField(label="Filtro", widget=forms.Textarea)

    class Meta:  # Define os campos vindos do Model
        model = Config
        fields = ('dominio', 'endservidor', 'gadmin', 'ou')

    def __init__(self, request, *args, **kwargs):  # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(AdForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['dominio'].widget = forms.TextInput(attrs={
            'placeholder': 'Dominio',
            'title': 'Dominio'})
        self.fields['endservidor'].widget = forms.TextInput(attrs={
            'placeholder': 'Endereço Servidor',
            'title': 'Endereço IP do controlador de dominio'})
        self.fields['gadmin'].widget = forms.TextInput(attrs={
            'placeholder': 'Grupo Administradores',
            'title': 'Grupo dos administradores do sistema'})
        self.fields['ou'].widget = forms.TextInput(attrs={
            'placeholder': 'Base',
            'title': 'Estrutura completa de onde o sistema irá buscar os elementos'})
        self.fields['dominio'].label = ""
        self.fields['endservidor'].label = ""
        self.fields['gadmin'].label = ""
        self.fields['ou'].label = ""

    def clean(self):
        # Inicializa váriaveis com os dados digitados no formulario
        cleaned_data = self.cleaned_data
        Usuario = cleaned_data.get("usuario")
        Senha = cleaned_data.get("senha")
        Dominio = cleaned_data.get("dominio")
        Endservidor = cleaned_data.get("endservidor")
        Gadmin = cleaned_data.get("gadmin")
        Ou = cleaned_data.get("ou")
        Filter = cleaned_data.get("filter")

        if Usuario and Senha:  # Usuário e senha OK
            # Cria Conexão LDAP ou = 'OU=ca-paraiso, OU=reitoria, OU=ifto, DC=ifto, DC=local'
            c = conexaoAD(Usuario, Senha)
            result = c.PrimeiroLogin(Usuario, Senha, Dominio, Endservidor, Filter)  # tenta login no ldap e salva resultado em result
            if (result == ('i')):  # Credenciais invalidas (usuario e/ou senha)
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Usuário ou senha incorretos", code='invalid')
            elif (result == ('n')):  # Server Down
                # Adiciona erro na validação do formulário
                raise forms.ValidationError("Erro na Conexão", code='invalid')
            else:  # se logou
                try:  # Tenta salvar tudo no banco de dados no id 1
                    # Pega uma instancia do item conf do banco de dados
                    config = Config.objects.get(id=1)
                    config.dominio = Dominio
                    config.endservidor = Endservidor
                    config.gadmin = Gadmin
                    config.ou = Ou
                    config.filter = Filter
                    config.save()
                except ObjectDoesNotExist:  # caso não exista nada no bd cria um id 1 com os dados passados
                    config = Config(id=1, dominio=Dominio, endservidor=Endservidor, gadmin=Gadmin, ou=Ou, filter=Filter)
                    config.save()
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data


class SetorForm(forms.ModelForm):

    class Meta:  # Define os campos vindos do Model
        model = Setor
        fields = ('nome', 'responsavel', 'email')

    def __init__(self, request, *args, **kwargs):  # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(SetorForm, self).__init__(*args, **kwargs)
        self.fields['nome'].widget = forms.TextInput(attrs={'placeholder': 'Nome do Setor', 'title': 'Nome do Setor'})
        self.fields['nome'].label = ""
        self.fields['email'].widget = forms.TextInput(attrs={'placeholder': 'E-mail', 'title': 'e-mail do setor'})
        self.fields['email'].label = ""


class PessoaForm(forms.ModelForm):

    class Meta:  # Define os campos vindos do Model
        model = Pessoa
        fields = ('nome', 'usuario', 'email', 'status')

    def __init__(self, request, *args, **kwargs):  # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(PessoaForm, self).__init__(*args, **kwargs)
        self.fields['nome'].widget = forms.TextInput(attrs={'placeholder': 'Nome da Pessoa', 'title': 'Nome da Pessoa'})
        self.fields['nome'].label = ""
        self.fields['usuario'].widget = forms.TextInput(attrs={'placeholder': 'Usuário', 'title': 'Usuário Pessoa'})
        self.fields['usuario'].label = ""
        self.fields['email'].widget = forms.TextInput(attrs={'placeholder': 'E-mail', 'title': 'e-mail da pessoa'})
        self.fields['email'].label = ""
        self.fields['status'].label = "Ativo?"


class EmailForm(forms.ModelForm):

    class Meta:  # Define os campos vindos do Model
        model = Config
        fields = ('email_host', 'email_port', 'email_host_user', 'email_host_password')
    
    def __init__(self, request, *args, **kwargs):  # INIT define caracteristicas para os campos de formulário vindos do Model (banco de dados)
        super(EmailForm, self).__init__(*args, **kwargs)
        self.fields['email_host'].widget = forms.TextInput(attrs={'placeholder': 'Host do Email', 'title': 'Host do Email'})
        self.fields['email_host'].label = ""
        self.fields['email_port'].widget = forms.TextInput(attrs={'placeholder': 'Porta', 'title': 'Porta'})
        self.fields['email_port'].label = ""
        self.fields['email_host_user'].widget = forms.TextInput(attrs={'placeholder': 'Usuário', 'title': 'Usuário'})
        self.fields['email_host_user'].label = ""
        self.fields['email_host_password'].widget = forms.TextInput(attrs={'placeholder': 'Senha', 'title': 'Senha'})
        self.fields['email_host_password'].label = ""

    def clean(self):
        # Inicializa váriaveis com os dados digitados no formulario
        cleaned_data = self.cleaned_data
        Host = cleaned_data.get("email_host")
        Port = cleaned_data.get("email_port")
        User = cleaned_data.get("email_host_user")
        Password = cleaned_data.get("email_host_password")
       
        try:
            config = Config.objects.get(id=1)
            config.email_host = Host
            config.email_port = Port
            config.email_host_user = User
            config.email_host_password = Password
            config.save()
        except ObjectDoesNotExist:  # caso não exista nada no bd cria um id 1 com os dados passados
            config = Config(id=1, email_host = Host, email_port = Port, email_host_user = User, email_host_password = Password)
            config.save()
        # Sempre retorne a coleção completa de dados válidos.
        return cleaned_data


class TestEmailForm(forms.Form):
    texto = forms.CharField(label="Texto", widget=forms.Textarea())
    destinatario = forms.EmailField(label="", widget=forms.EmailInput(attrs={'placeholder': 'Destino'}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(TestEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        texto = cleaned_data.get('texto')
        destinatario = cleaned_data.get("testinatario")

        return cleaned_data