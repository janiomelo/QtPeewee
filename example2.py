from qtpeewee import (
    QFormulario, QCharEdit, QFormDialog, QDateWithCalendarEdit, QTableDialog,
    QResultList, QListDialog, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDecimalEdit, QDateTimeWithCalendarEdit, QChoicesComboBox, ChoiceField,
    QGridForm)
from peewee import (
    Model, CharField, DateField, ForeignKeyField, fn, FloatField,
    DateTimeField)


class BaseModel(Model):
    class Meta:
        database = app.db


class Tipo(BaseModel):
    nome = CharField()

    def __str__(self):
        return str(self.nome)


class Recurso(BaseModel):
    nome = CharField()
    tipo = ForeignKeyField(Tipo)

    def __str__(self):
        return str(self.nome)


class Cliente(BaseModel):
    nome = CharField()
    sigla = CharField()

    def __str__(self):
        return str(self.nome)


class Projeto(BaseModel):
    nome = CharField()
    cliente = ForeignKeyField(Cliente)

    def __str__(self):
        return str(self.nome)


class Tarefa(BaseModel):
    projeto = ForeignKeyField(Projeto)
    titulo = CharField()
    descricao = CharField(null=True)
    data_limite = DateField()
    prioridade = ChoiceField(values=[
        {"id": 2, "name": "High"},
        {"id": 1, "name": "Normal"},
        {"id": 0, "name": "Low"}
    ], default=1)
    realizado = FloatField(default=0)
    data_conclusao = DateField(null=True)

    def status(self):
        if self.data_conclusao is None:
            return 'Pendente'
        return 'Concluída'

    def __str__(self):
        return str(self.titulo)


class Alocacao(BaseModel):
    tarefa = ForeignKeyField(Tarefa)
    recurso = ForeignKeyField(Recurso)
    inicio = DateTimeField()
    fim = DateTimeField()


class FormularioTipo(QFormulario):
    ENTIDADE = Tipo

    def __init__(self):
        super(FormularioTipo, self).__init__()
        self.nome = QCharEdit(column_name='nome', max_lenght=100)


class TipoDialog(QFormDialog):
    FORMULARIO = FormularioTipo
    TITLE = 'Cadastro de Tipo de Recurso'


class FormularioRecurso(QFormulario):
    ENTIDADE = Recurso

    def __init__(self):
        super(FormularioRecurso, self).__init__()
        self.nome = QCharEdit(column_name='nome', max_lenght=100)
        self.tipo = QFkComboBox(
            Tipo, column_name='tipo', form_new=TipoDialog,
            form_edit=TipoDialog)


class RecursoDialog(QFormDialog):
    FORMULARIO = FormularioRecurso
    TITLE = 'Cadastro de Recurso'


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente

    def __init__(self):
        super(FormularioCliente, self).__init__()
        self.sigla = QCharEdit(column_name='sigla', max_lenght=3)
        self.nome = QCharEdit(column_name='nome', max_lenght=100)


class ClienteDialog(QFormDialog):
    FORMULARIO = FormularioCliente
    TITLE = 'Cadastro de Cliente'


class FormularioProjeto(QFormulario):
    ENTIDADE = Projeto

    def __init__(self):
        super(FormularioProjeto, self).__init__()
        self.nome = QCharEdit(column_name='nome', max_lenght=100)
        self.cliente = QFkComboBox(
            Cliente, column_name='cliente', form_new=ClienteDialog,
            form_edit=ClienteDialog)


class ProjetoDialog(QFormDialog):
    FORMULARIO = FormularioProjeto
    TITLE = 'Cadastro de Projeto'


class FormularioTarefa(QFormulario):
    ENTIDADE = Tarefa

    def __init__(self):
        super(FormularioTarefa, self).__init__()
        self.projeto = QFkComboBox(
            Projeto, column_name='projeto', form_new=ProjetoDialog,
            form_edit=ProjetoDialog)
        self.titulo = QCharEdit(column_name='titulo', max_lenght=100)
        self.descricao = QCharEdit(column_name='descricao', required=False)
        self.data_limite = QDateWithCalendarEdit(column_name='data_limite')
        self.prioridade = QChoicesComboBox(Tarefa.prioridade)
        self.prioridade.set_valor(1)
        self.realizado = QDecimalEdit(
            column_name='realizado')
        self.data_conclusao = QDateWithCalendarEdit(
            required=False, column_name='data_conclusao')


class TarefaDialog(QFormDialog):
    FORMULARIO = FormularioTarefa
    TITLE = 'Cadastro de Tarefa'


class FormularioAlocacao(QGridForm):
    ENTIDADE = Alocacao

    def __init__(self):
        super(FormularioAlocacao, self).__init__()
        self.tarefa = QFkComboBox(
            Tarefa, column_name='tarefa', form_new=TarefaDialog,
            form_edit=TarefaDialog)
        self.recurso = QFkComboBox(
            Recurso, column_name='recurso', form_new=RecursoDialog,
            form_edit=RecursoDialog, x=1, y=0)
        self.inicio = QDateTimeWithCalendarEdit(column_name='inicio', x=0, y=1)
        self.fim = QDateTimeWithCalendarEdit(column_name='fim', x=1, y=1)


class AlocacaoDialog(QFormDialog):
    FORMULARIO = FormularioAlocacao
    TITLE = 'Cadastro de Alocação'


# -----------------------------------------------------------------------------

class TipoFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Tipo.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class TipoList(QResultList):
    FORM = TipoDialog

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Tipo.nome

    def get_all(self):
        return Tipo.select()


class TipoListDialog(QListDialog):
    LIST = TipoList
    FORM_FILTER = TipoFilterForm
    TITLE = 'Consulta de tipos de recurso'

# -----------------------------------------------------------------------------


class RecursosFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Recurso.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class RecursosList(QResultList):
    FORM = RecursoDialog

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Recurso.nome

    def get_all(self):
        return Recurso.select()


class RecursosListDialog(QListDialog):
    LIST = RecursosList
    FORM_FILTER = RecursosFilterForm
    TITLE = 'Consulta de recursos'


# -----------------------------------------------------------------------------

class ClientesFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Cliente.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class ClientesList(QResultList):
    FORM = ClienteDialog

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Cliente.nome

    def get_all(self):
        return Cliente.select()


class ClientesListDialog(QListDialog):
    LIST = ClientesList
    FORM_FILTER = ClientesFilterForm
    TITLE = 'Consulta de clientes'

#----------------------------------------------------------------------------


class ProjetosFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Projeto.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class ProjetosList(QResultList):
    FORM = ProjetoDialog

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Projeto.nome

    def get_all(self):
        return Projeto.select()


class ProjetosListDialog(QListDialog):
    LIST = ProjetosList
    FORM_FILTER = ProjetosFilterForm
    TITLE = 'Consulta de projetos'

#-------------------------------------------------------


class TarefasFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Tarefa.projeto,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Projeto"
        }]


class TarefasList(QResultTable):
    FORM = TarefaDialog

    def order(self):
        return fn.lower(Tarefa.prioridade)

    def get_all(self):
        return Tarefa.select().join(Projeto)

    def columns(self):
        return [
            Tarefa.titulo, Tarefa.data_limite, (Tarefa.prioridade, 'name'),
            Tarefa.realizado, (Tarefa.projeto, 'nome')
        ]


class TarefasListDialog(QTableDialog):
    LIST = TarefasList
    FORM_FILTER = TarefasFilterForm
    TITLE = 'Consulta de tarefas'


#-------------------------------------------------------


class AlocacoesFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Alocacao.recurso,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Recurso"
        }, {
            "entity": Alocacao.tarefa,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Tarefa"
        }]


class AlocacoesList(QResultTable):
    FORM = AlocacaoDialog

    def order(self):
        return fn.lower(Alocacao.inicio)

    def get_all(self):
        return Alocacao.select().join(
            Tarefa, on=(Tarefa.id == Alocacao.tarefa)).join(
            Recurso, on=(Recurso.id == Alocacao.recurso))

    def columns(self):
        return [
            (Alocacao.recurso, 'nome'), (Alocacao.tarefa, 'titulo'),
            Alocacao.inicio, Alocacao.fim
        ]


class AlocacoesListDialog(QTableDialog):
    LIST = AlocacoesList
    FORM_FILTER = AlocacoesFilterForm
    TITLE = 'Consulta de alocações'


def abrir_recursos(e):
    dialog = RecursosListDialog()
    dialog.exec()


def abrir_tarefas(e):
    dialog = TarefasListDialog()
    dialog.exec()


def abrir_clientes(e):
    dialog = ClientesListDialog()
    dialog.exec()


def abrir_projetos(e):
    dialog = ProjetosListDialog()
    dialog.exec()


def abrir_alocacoes(e):
    dialog = AlocacoesListDialog()
    dialog.exec()


def abrir_tipo_recurso(e):
    dialog = TipoListDialog()
    dialog.exec()


if __name__ == '__main__':
    Tipo.create_table()
    Recurso.create_table()
    Cliente.create_table()
    Projeto.create_table()
    Tarefa.create_table()
    Alocacao.create_table()

    app.set_title('Meus Projetos')

    cadastrosMenu = app.formPrincipal.new_menu('&Cadastros')

    app.formPrincipal.new_action(
        cadastrosMenu, 'T&ipos de Recurso', abrir_tipo_recurso,
        tinytxt='Ctrl+I', tip='Consulta ao cadastro de tipos de recurso.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Recursos', abrir_recursos, tinytxt='Ctrl+R',
        tip='Consulta ao cadastro de recursos.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Clientes', abrir_clientes, tinytxt='Ctrl+C',
        tip='Consulta ao cadastro de clientes.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Projetos', abrir_projetos, tinytxt='Ctrl+P',
        tip='Consulta ao cadastro de projetos.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Tarefas', abrir_tarefas, tinytxt='Ctrl+T',
        tip='Consulta ao cadastro de tarefas.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Alocação', abrir_alocacoes, tinytxt='Ctrl+A',
        tip='Consultar alocações.')

    run()
