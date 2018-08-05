from qtpeewee import (
    QFormulario, QCharEdit, QFormWidget, QDateWithCalendarEdit, QTableShow,
    QResultList, QListShow, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDecimalEdit, QDateTimeWithCalendarEdit, QChoicesComboBox, ChoiceField,
    QGridForm, QIntEdit, hybrid_property_field, QPreview, BaseModel)
from peewee import (
    CharField, DateField, ForeignKeyField, fn, FloatField, DoesNotExist,
    DateTimeField, JOIN, TextField)
from datetime import datetime, timedelta


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
            if self.esta_em_andamento():
                return 'Em andamento'
            return 'Pendente'
        return 'Concluída'

    def __str__(self):
        return str(self.titulo)

    @hybrid_property_field
    def tempo(self):
        try:
            tarefa = Tarefa.raw(
                'SELECT COALESCE(SUM((julianday(apontamento.fim)-julianday(apontamento.inicio)) * 86400.0), 0) arg '
                'FROM tarefa LEFT JOIN apontamento ON apontamento.tarefa_id=tarefa.id '
                'WHERE apontamento.fim IS NOT NULL AND tarefa.id = %i' % self.id
            ).get()
            return str(timedelta(seconds=tarefa.arg)).split('.')[0]
        except (DoesNotExist, TypeError):
            return 0

    def esta_em_andamento(self):
        try:
            apontamenos = Tarefa.raw(
                'select * from apontamento where tarefa_id = %i and fim is null;' %
                self.id
            ).get()
            return True if apontamenos is not None else False
        except DoesNotExist:
            return False


class Alocacao(BaseModel):
    tarefa = ForeignKeyField(Tarefa)
    recurso = ForeignKeyField(Recurso)
    inicio = DateTimeField()
    fim = DateTimeField()


class Apontamento(BaseModel):
    tarefa = ForeignKeyField(Tarefa)
    recurso = ForeignKeyField(Recurso)
    inicio = DateTimeField()
    fim = DateTimeField(null=True)
    observacao = TextField(null=True)


class FormularioTipo(QFormulario):
    ENTIDADE = Tipo
    TITLE = 'Cadastro de Tipo de Recurso'


class FormularioRecurso(QFormulario):
    ENTIDADE = Recurso
    TITLE = 'Cadastro de Recurso'

    def meta(self):
        return {
            'tipo': {
                'form_new': FormularioTipo,
                'form_edit': FormularioTipo
            }
        }


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente
    TITLE = 'Cadastro de Cliente'


class FormularioProjeto(QFormulario):
    ENTIDADE = Projeto
    TITLE = 'Cadastro de Projeto'

    def meta(self):
        return {
            'cliente': {
                'form_new': FormularioCliente,
                'form_edit': FormularioCliente
            }
        }


class FormularioTarefa(QFormulario):
    ENTIDADE = Tarefa
    TITLE = 'Cadastro de Tarefa'

    def meta(self):
        # self.realizado = QDecimalEdit(column_name='realizado')
        self.prioridade.set_valor(1)
        return {
            'projeto': {
                'form_new': FormularioProjeto,
                'form_edit': FormularioProjeto
            }
        }


class FormularioAlocacao(QGridForm):
    ENTIDADE = Alocacao
    TITLE = 'Cadastro de Alocação'

    def meta(self):
        return {
            'tarefa': {
                'form_new': FormularioTarefa,
                'form_edit': FormularioTarefa
            },
            'recurso': {
                'form_new': FormularioRecurso,
                'form_edit': FormularioRecurso,
                'x': 1,
                'y': 0
            },
            'inicio': {
                'x': 0,
                'y': 1
            },
            'fim': {
                'x': 1,
                'y': 1
            }
        }


class TipoListShow(QListShow):
    TITLE = 'Consulta de tipos de recurso'
    FORM = FormularioTipo

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Tipo.nome

    def get_all(self):
        return Tipo.select()

    def filters(self):
        return [{
            "entity": Tipo.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class RecursosListShow(QListShow):
    FORM = FormularioRecurso
    TITLE = 'Consulta de recursos'

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Recurso.nome

    def get_all(self):
        return Recurso.select()

    def filters(self):
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


class ClientesListShow(QListShow):
    FORM = FormularioCliente
    TITLE = 'Consulta de clientes'

    def filters(self):
        return [{
            "entity": Cliente.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]

    def get_value(self, obj):
        return '({0}) {1}'.format(obj.sigla, obj.nome)

    def order(self):
        return Cliente.nome

    def get_all(self):
        return Cliente.select()


class ProjetosListShow(QListShow):
    TITLE = 'Consulta de projetos'
    FORM = FormularioProjeto

    def get_value(self, obj):
        return '{0} - Prazo: {1}'.format(
            obj.nome, obj.prazo.strftime('%d/%m/%Y'))

    def order(self):
        return Projeto.nome

    def get_all(self):
        return Projeto.select()

    def filters(self):
        return [{
            "entity": Projeto.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]


class TarefasListDialog(QTableShow):
    TITLE = 'Consulta de tarefas'
    FORM = FormularioTarefa

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
            (Tarefa.projeto, 'nome'), Tarefa.status, Tarefa.tempo,
            (Tarefa.projeto, 'cliente'),
            (Tarefa.data_conclusao, 'dd/MM/yyyy')
        ]

    def actions(self):
        return [
            {
                "label": "",
                "icon": "ei.time",
                "callback": self.registrar_tempo
            }
        ]

    def registrar_tempo(self):
        tarefa = self.selected()
        if tarefa is None:
            return
        if tarefa.esta_em_andamento():
            apontamento = Apontamento.get(
                (Apontamento.tarefa == tarefa) & (
                    Apontamento.fim.is_null()))
            apontamento.fim = datetime.now()
        else:
            apontamento = Apontamento(
                tarefa=tarefa,
                recurso=Recurso.get(Recurso.id == 1),
                inicio=datetime.now(),
                observacoes=None
            )
        apontamento.save()
        self.update_result_set()

    def filters(self):
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


class AlocacoesListDialog(QTableShow):
    TITLE = 'Consulta de alocações'
    FORM = FormularioAlocacao

    def order(self):
        return fn.lower(Alocacao.inicio)

    def get_all(self):
        return Alocacao.select().join(
            Tarefa, on=(Tarefa.id == Alocacao.tarefa)).join(
            Recurso, on=(Recurso.id == Alocacao.recurso))

    def columns(self):
        return [
            (Alocacao.tarefa, 'titulo'), (Alocacao.recurso, 'nome'),
            (Alocacao.inicio, 'dd-MM hh:mm'),
            (Alocacao.fim, 'dd-MM hh:mm')
        ]

    def filters(self):
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


class QPreviewProjetos(QPreview):
    def template(self):
        return 'example.html'

    def before_render(self):
        query = Projeto.select(
            Projeto.id, Projeto.nome, Projeto.cliente,
            fn.Count(Tarefa.id).alias('n_tarefas_pendentes')
        ).join(Tarefa, JOIN.LEFT_OUTER).where(
            Tarefa.data_conclusao >> None
        ).group_by(
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
    Apontamento.create_table()

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
