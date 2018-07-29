from qtpeewee import (
    QFormulario, QCharEdit, QFormWidget, QDateWithCalendarEdit, QTableShow,
    QResultList, QListShow, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDecimalEdit, QDateTimeWithCalendarEdit, QChoicesComboBox, ChoiceField,
    QGridForm, QIntEdit, hybrid_property_field, QPreview)
from peewee import (
    Model, CharField, DateField, ForeignKeyField, fn, FloatField,
    DateTimeField, JOIN)


class BaseModel(Model):
    class Meta:
        database = app.db


class Tipo(BaseModel):
    nome = CharField()

    def __str__(self):
        return str(self.nome)


class Recurso(BaseModel):
    nome = CharField()
    tipo = ForeignKeyField(Tipo, null=False)

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
    prazo = DateField()

    def __str__(self):
        return str(self.cliente.sigla) + ' - ' +str(self.nome)


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


class TipoWidget(QFormWidget):
    FORMULARIO = FormularioTipo
    TITLE = 'Cadastro de Tipo de Recurso'


class FormularioRecurso(QFormulario):
    ENTIDADE = Recurso

    def fields(self):
        self.nome = QCharEdit(field=Recurso.nome)
        self.tipo = QFkComboBox(
            Tipo, field=Recurso.tipo, form_new=TipoWidget,
            form_edit=TipoWidget)


class RecursoWidget(QFormWidget):
    FORMULARIO = FormularioRecurso
    TITLE = 'Cadastro de Recurso'


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente

    def fields(self):
        self.sigla = QCharEdit(field=Cliente.sigla)
        self.nome = QCharEdit(field=Cliente.nome)


class ClienteWidget(QFormWidget):
    FORMULARIO = FormularioCliente
    TITLE = 'Cadastro de Cliente'


class FormularioProjeto(QFormulario):
    ENTIDADE = Projeto

    def fields(self):
        self.nome = QCharEdit(field=Projeto.nome)
        self.cliente = QFkComboBox(
            Cliente, field=Projeto.cliente, form_new=ClienteWidget,
            form_edit=ClienteWidget)
        self.prazo = QDateWithCalendarEdit(field=Projeto.prazo)


class ProjetoWidget(QFormWidget):
    FORMULARIO = FormularioProjeto
    TITLE = 'Cadastro de Projeto'


class FormularioTarefa(QFormulario):
    ENTIDADE = Tarefa

    def fields(self):
        self.projeto = QFkComboBox(
            Projeto, field=Tarefa.projeto, form_new=ProjetoWidget,
            form_edit=ProjetoWidget)
        self.titulo = QCharEdit(field=Tarefa.titulo)
        self.descricao = QCharEdit(field=Tarefa.descricao)
        self.data_limite = QDateWithCalendarEdit(field=Tarefa.data_limite)
        self.prioridade = QChoicesComboBox(field=Tarefa.prioridade)
        self.prioridade.set_valor(1)
        self.realizado = QDecimalEdit(
            column_name='realizado')
        self.data_conclusao = QDateWithCalendarEdit(
            field=Tarefa.data_conclusao)


class TarefaWidget(QFormWidget):
    FORMULARIO = FormularioTarefa
    TITLE = 'Cadastro de Tarefa'


class FormularioAlocacao(QGridForm):
    ENTIDADE = Alocacao

    def fields(self):
        self.tarefa = QFkComboBox(
            Tarefa, field=Alocacao.tarefa, form_new=TarefaWidget,
            form_edit=TarefaWidget)
        self.recurso = QFkComboBox(
            Recurso, field=Alocacao.recurso, form_new=RecursoWidget,
            form_edit=RecursoWidget, x=1, y=0)
        self.inicio = QDateTimeWithCalendarEdit(
            field=Alocacao.inicio, x=0, y=1)
        self.fim = QDateTimeWithCalendarEdit(field=Alocacao.fim, x=1, y=1)


class AlocacaoWidget(QFormWidget):
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
    FORM = TipoWidget

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Tipo.nome

    def get_all(self):
        return Tipo.select()


class TipoListShow(QListShow):
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
    FORM = RecursoWidget

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Recurso.nome

    def get_all(self):
        return Recurso.select()


class RecursosListShow(QListShow):
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
    FORM = ClienteWidget

    def get_value(self, obj):
        return '({0}) {1}'.format(obj.sigla, obj.nome)

    def order(self):
        return Cliente.nome

    def get_all(self):
        return Cliente.select()


class ClientesListShow(QListShow):
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
    FORM = ProjetoWidget

    def get_value(self, obj):
        return '{0} - Prazo: {1}'.format(
            obj.nome, obj.prazo.strftime('%d/%m/%Y'))

    def order(self):
        return Projeto.nome

    def get_all(self):
        return Projeto.select()


class ProjetosListShow(QListShow):
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
            "label": "% Real. <"
        }]


class TarefasList(QResultTable):
    FORM = TarefaWidget

    def order(self):
        return fn.lower(Tarefa.prioridade)

    def get_all(self):
        return Tarefa.select().join(
            Projeto, on=(Projeto.id == Tarefa.projeto)).join(
            Cliente, on=(Cliente.id == Projeto.cliente))

    def columns(self):
        return [
            Tarefa.titulo, (Tarefa.data_limite, 'dd/MM/yyyy'),
            (Tarefa.prioridade, 'name'), Tarefa.realizado,
            (Tarefa.projeto, 'nome'), Tarefa.status,
            (Tarefa.projeto, 'cliente'), (Tarefa.data_conclusao, 'dd/MM/yyyy')
        ]

    def actions(self):
        return [
            {
                "label": "&Apontar",
                "icon": "ei.time",
                "callback": self.apontar_horas_trabalhadas
            }
        ]

    def apontar_horas_trabalhadas(self):
        a = self.selected()
        self.abrir_formulario(a)


class TarefasListDialog(QTableShow):
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
            "label": "Tipo"
        }]


class AlocacoesList(QResultTable):
    FORM = AlocacaoWidget

    def order(self):
        return fn.lower(Alocacao.inicio)

    def get_all(self):
        return Alocacao.select().join(
            Tarefa, on=(Tarefa.id == Alocacao.tarefa)).join(
            Recurso, on=(Recurso.id == Alocacao.recurso))

    def columns(self):
        return [
            (Alocacao.tarefa, 'titulo'), (Alocacao.recurso, 'nome'),
            (Alocacao.inicio, 'dd-MM hh:mm'), (Alocacao.fim, 'dd-MM hh:mm')
        ]


class AlocacoesListDialog(QTableShow):
    LIST = AlocacoesList
    FORM_FILTER = AlocacoesFilterForm
    TITLE = 'Consulta de alocações'


class QPreviewProjetos(QPreview):
    def template(self):
        return 'example.html'

    def before_render(self):
        query = Projeto.select(
            Projeto.id, Projeto.nome, Projeto.cliente,
            fn.Count(Tarefa.id).alias('n_tarefas_pendentes')
        ).join(Tarefa, JOIN.LEFT_OUTER).group_by(
            Projeto.id, Projeto.nome, Projeto.cliente
        ).order_by(Projeto.nome)

        n_tarefas_pendentes = 0
        for l in query:
            n_tarefas_pendentes += l.n_tarefas_pendentes
        self.render(
            projetos=query, total_projetos=len(query),
            n_tarefas_pendentes=n_tarefas_pendentes)


if __name__ == '__main__':
    Tipo.create_table()
    Recurso.create_table()
    Cliente.create_table()
    Projeto.create_table()
    Tarefa.create_table()
    Alocacao.create_table()

    app.set_title('Meus Projetos')

    cadastrosMenu = app.formPrincipal.new_menu('&Cadastros')
    relatoriosMenu = app.formPrincipal.new_menu('&Relatórios')

    app.formPrincipal.new_action(
        cadastrosMenu, 'T&ipos de Recurso', TipoListShow,
        tinytxt='Ctrl+I', tip='Consulta ao cadastro de tipos de recurso.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Recursos', RecursosListShow, tinytxt='Ctrl+R',
        tip='Consulta ao cadastro de recursos.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Clientes', ClientesListShow, tinytxt='Ctrl+C',
        tip='Consulta ao cadastro de clientes.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Projetos', ProjetosListShow, tinytxt='Ctrl+P',
        tip='Consulta ao cadastro de projetos.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Tarefas', TarefasListDialog, tinytxt='Ctrl+T',
        tip='Consulta ao cadastro de tarefas.')

    app.formPrincipal.new_action(
        cadastrosMenu, '&Alocação', AlocacoesListDialog, tinytxt='Ctrl+A',
        tip='Consultar alocações.')

    app.formPrincipal.new_action(
        relatoriosMenu, 'Previe&w', QPreviewProjetos, tinytxt='Ctrl+W',
        tip='Exibir preview')

    run()
