from qtpeewee import (
    QFormulario, QCharEdit, QFormDialog, QDateWithCalendarEdit, QTableDialog,
    QResultList, QListDialog, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDecimalEdit, QDateTimeWithCalendarEdit, QChoicesComboBox, ChoiceField,
    QGridForm, QIntEdit, hybrid_property_field)
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
        return '({0}) {1}'.format(self.sigla, self.nome)


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

    @hybrid_property_field
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
        self.nome = QCharEdit(field=Tipo.nome)


class TipoDialog(QFormDialog):
    FORMULARIO = FormularioTipo
    TITLE = 'Cadastro de Tipo de Recurso'


class FormularioRecurso(QFormulario):
    ENTIDADE = Recurso

    def __init__(self):
        super(FormularioRecurso, self).__init__()
        self.nome = QCharEdit(field=Recurso.nome)
        self.tipo = QFkComboBox(
            Tipo, field=Recurso.tipo, form_new=TipoDialog,
            form_edit=TipoDialog)


class RecursoDialog(QFormDialog):
    FORMULARIO = FormularioRecurso
    TITLE = 'Cadastro de Recurso'


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente

    def __init__(self):
        super(FormularioCliente, self).__init__()
        self.sigla = QCharEdit(field=Cliente.sigla)
        self.nome = QCharEdit(field=Cliente.nome)


class ClienteDialog(QFormDialog):
    FORMULARIO = FormularioCliente
    TITLE = 'Cadastro de Cliente'


class FormularioProjeto(QFormulario):
    ENTIDADE = Projeto

    def __init__(self):
        super(FormularioProjeto, self).__init__()
        self.nome = QCharEdit(field=Projeto.nome)
        self.cliente = QFkComboBox(
            Cliente, field=Projeto.cliente, form_new=ClienteDialog,
            form_edit=ClienteDialog)


class ProjetoDialog(QFormDialog):
    FORMULARIO = FormularioProjeto
    TITLE = 'Cadastro de Projeto'


class FormularioTarefa(QFormulario):
    ENTIDADE = Tarefa

    def __init__(self):
        super(FormularioTarefa, self).__init__()
        self.projeto = QFkComboBox(
            Projeto, field=Tarefa.projeto, form_new=ProjetoDialog,
            form_edit=ProjetoDialog)
        self.titulo = QCharEdit(field=Tarefa.titulo)
        self.descricao = QCharEdit(field=Tarefa.descricao)
        self.data_limite = QDateWithCalendarEdit(field=Tarefa.data_limite)
        self.prioridade = QChoicesComboBox(field=Tarefa.prioridade)
        self.prioridade.set_valor(1)
        self.realizado = QDecimalEdit(
            column_name='realizado')
        self.data_conclusao = QDateWithCalendarEdit(
            field=Tarefa.data_conclusao)


class TarefaDialog(QFormDialog):
    FORMULARIO = FormularioTarefa
    TITLE = 'Cadastro de Tarefa'


class FormularioAlocacao(QGridForm):
    ENTIDADE = Alocacao

    def __init__(self):
        super(FormularioAlocacao, self).__init__()
        self.tarefa = QFkComboBox(
            Tarefa, field=Alocacao.tarefa, form_new=TarefaDialog,
            form_edit=TarefaDialog)
        self.recurso = QFkComboBox(
            Recurso, field=Alocacao.recurso, form_new=RecursoDialog,
            form_edit=RecursoDialog, x=1, y=0)
        self.inicio = QDateTimeWithCalendarEdit(
            field=Alocacao.inicio, x=0, y=1)
        self.fim = QDateTimeWithCalendarEdit(field=Alocacao.fim, x=1, y=1)


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
        }, {
            "entity": Recurso.tipo,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Tipo"
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
        return '({0}) {1}'.format(obj.sigla, obj.nome)

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
        }, {
            "entity": Tarefa.realizado,
            "type": QIntEdit,
            "operator": "<",
            "label": "Realizado ( < )"
        }]


class TarefasList(QResultTable):
    FORM = TarefaDialog

    def order(self):
        return fn.lower(Tarefa.prioridade)

    def get_all(self):
        return Tarefa.select().join(
            Projeto, on=(Projeto.id == Tarefa.projeto)).join(
            Cliente, on=(Cliente.id == Projeto.cliente))

    def columns(self):
        return [
            Tarefa.titulo, Tarefa.data_limite, (Tarefa.prioridade, 'name'),
            Tarefa.realizado, (Tarefa.projeto, 'nome'), Tarefa.status,
            (Tarefa.projeto, 'cliente')
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
        }, {
            "entity": Alocacao.recurso.tipo,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Tipo de Recurso"
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
            (Alocacao.tarefa, 'titulo'), (Alocacao.recurso, 'nome'),
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
