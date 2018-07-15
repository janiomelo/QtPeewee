from qtpeewee import (
    QFormulario, QCharEdit, QFormDialog, QDateWithCalendarEdit, QTableDialog,
    QResultList, QListDialog, QFkComboBox, QResultTable, run, app, QSearchForm,
    QIntEdit, QDecimalEdit, QDateTimeWithCalendarEdit)
from peewee import (
    Model, CharField, DateField, ForeignKeyField, fn, IntegerField, FloatField,
    DateTimeField)


class BaseModel(Model):
    class Meta:
        database = app.db


class Recurso(BaseModel):
    nome = CharField()

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
    prioridade = IntegerField(default=1)
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


class FormularioRecurso(QFormulario):
    ENTIDADE = Recurso

    def __init__(self):
        super(FormularioRecurso, self).__init__()
        self.nome = QCharEdit(column_name='nome', max_lenght=100)


class RecursoDialog(QFormDialog):
    FORMULARIO = FormularioRecurso


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
        self.prioridade = QIntEdit(column_name='prioridade')
        self.realizado = QDecimalEdit(
            column_name='realizado')
        self.data_conclusao = QDateWithCalendarEdit(
            required=False, column_name='data_conclusao')


class TarefaDialog(QFormDialog):
    FORMULARIO = FormularioTarefa
    TITLE = 'Cadastro de Tarefa'


class FormularioAlocacao(QFormulario):
    ENTIDADE = Alocacao

    def __init__(self):
        super(FormularioAlocacao, self).__init__()
        self.tarefa = QFkComboBox(
            Tarefa, column_name='tarefa', form_new=TarefaDialog,
            form_edit=TarefaDialog)
        self.recurso = QFkComboBox(
            Recurso, column_name='recurso', form_new=RecursoDialog,
            form_edit=RecursoDialog)
        self.inicio = QDateTimeWithCalendarEdit(column_name='inicio')
        self.fim = QDateTimeWithCalendarEdit(column_name='fim')


class AlocacaoDialog(QFormDialog):
    FORMULARIO = FormularioAlocacao
    TITLE = 'Cadastro de Alocação'


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
            "entity": Tarefa.projeto.nome,
            "type": QCharEdit,
            "operator": "%",
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
            Tarefa.titulo, Tarefa.data_limite,
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
            "entity": Alocacao.recurso.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Recurso"
        }, {
            "entity": Alocacao.tarefa.titulo,
            "type": QCharEdit,
            "operator": "%",
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


def abrir_recursos(e):
    dialog = RecursosListDialog()
    dialog.exec_()


def abrir_tarefas(e):
    dialog = TarefasListDialog()
    dialog.exec_()


def abrir_clientes(e):
    dialog = ClientesListDialog()
    dialog.exec_()


def abrir_projetos(e):
    dialog = ProjetosListDialog()
    dialog.exec_()


def abrir_alocacoes(e):
    dialog = AlocacoesListDialog()
    dialog.exec_()


if __name__ == '__main__':
    Recurso.create_table()
    Cliente.create_table()
    Projeto.create_table()
    Tarefa.create_table()
    Alocacao.create_table()

    app.set_title('Meus Projetos')

    cadastrosMenu = app.formPrincipal.new_menu('&Cadastros')

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
