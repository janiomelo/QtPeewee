from qtpeewee import (
    QFormulario, QCharEdit, QFormWidget, QDateWithCalendarEdit, QTableShow,
    QResultList, QListShow, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDateTimeWithCalendarEdit)
from peewee import (
    Model, CharField, DateField, ForeignKeyField, fn, DateTimeField)


class BaseModel(Model):
    class Meta:
        database = app.db


class Tipo(BaseModel):
    descricao = CharField()

    def __str__(self):
        return str(self.descricao)


class Cliente(BaseModel):
    nome = CharField()
    email = CharField()
    entrada = DateTimeField()
    tipo = ForeignKeyField(Tipo)


class Funcionario(BaseModel):
    nome = CharField()
    nascimento = DateField()
    tipo = ForeignKeyField(Tipo)


class FormularioTipo(QFormulario):
    ENTIDADE = Tipo

    def fields(self):
        self.descricao = QCharEdit(field=Tipo.descricao)


class TipoWidget(QFormWidget):
    FORMULARIO = FormularioTipo
    TITLE = 'Editar Tipo'


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente

    def fields(self):
        self.nome = QCharEdit(field=Cliente.nome)
        self.email = QCharEdit(field=Cliente.email)
        self.tipo = QFkComboBox(entity=Tipo, field=Cliente.tipo)
        self.entrada = QDateTimeWithCalendarEdit(field=Cliente.entrada)


class ClienteWidget(QFormWidget):
    FORMULARIO = FormularioCliente
    TITLE = 'Editar Cliente'


class FormularioFuncionario(QFormulario):
    ENTIDADE = Funcionario

    def fields(self):
        self.nome = QCharEdit(field=Funcionario.nome)
        self.nascimento = QDateWithCalendarEdit(field=Funcionario.nascimento)
        self.tipo = QFkComboBox(entity=Tipo, field=Funcionario.tipo)


class FuncionarioWidget(QFormWidget):
    FORMULARIO = FormularioFuncionario
    TITLE = 'Editar Funcionário'

    def buttons(self):
        return [{
            "label": "Tipo",
            "form": TipoWidget,
            "pk": self.pk,
            "condition": None
        }, {
            "label": "Funcionário",
            "form": FuncionarioWidget,
            "pk": None,
            "condition": self.pk is not None
        }]


# -----------------------------------------------------------------------------


class ClientesFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Cliente.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Cliente"
        }, {
            "entity": Cliente.tipo,
            "type": QFkComboBox,
            "operator": "=",
            "label": "Tipo"
        }]


class ClientesList(QResultTable):
    FORM = ClienteWidget

    def order(self):
        return fn.lower(Cliente.nome)

    def get_all(self):
        return Cliente.select().join(Tipo)

    def columns(self):
        return [
            Cliente.id, Cliente.nome, Cliente.entrada,
            Cliente.email, (Cliente.tipo, 'descricao')
        ]


class ClientesListDialog(QTableShow):
    LIST = ClientesList
    FORM_FILTER = ClientesFilterForm
    TITLE = 'Lista de clientes'

# -----------------------------------------------------------------------------


class FuncionarioFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Funcionario.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }, {
            "entity": Funcionario.nascimento,
            "type": QDateWithCalendarEdit,
            "operator": "=",
            "label": "Dt. Nascimento"
        }]


class FuncionariosList(QResultList):
    FORM = FuncionarioWidget

    def get_value(self, obj):
        return obj.nome

    def order(self):
        return Funcionario.nome

    def get_all(self):
        return Funcionario.select()


class FuncionariosListShow(QListShow):
    LIST = FuncionariosList
    FORM_FILTER = FuncionarioFilterForm
    TITLE = 'Lista de funcionários'

# -----------------------------------------------------------------------------


class TiposFilterForm(QSearchForm):

    def fields(self):
        return [{
            "entity": Tipo.descricao,
            "type": QCharEdit,
            "operator": "%",
            "label": "Descrição"
        }]


class TiposList(QResultList):
    FORM = TipoWidget

    def get_value(self, obj):
        return obj.descricao

    def order(self):
        return Tipo.descricao

    def get_all(self):
        return Tipo.select()


class TiposListShow(QListShow):
    LIST = TiposList
    FORM_FILTER = TiposFilterForm
    TITLE = 'Lista de tipos'


def abrir_cliente(e):
    dialog = ClientesListDialog()
    dialog.exec_()


def abrir_funcionario(e):
    dialog = FuncionariosListShow()
    dialog.exec_()


def abrir_tipo(e):
    dialog = TiposListShow()
    dialog.exec_()


if __name__ == '__main__':
    Tipo.create_table()
    Cliente.create_table()
    Funcionario.create_table()
    app.set_title('Aplicação de Exemplo')

    clienteMenu = app.formPrincipal.new_menu('&Clientes')
    app.formPrincipal.new_action(
        clienteMenu, '&Consultar', abrir_cliente, icon=None,
        tinytxt='Ctrl+C', tip='Consulta ao cadastro de clientes.')

    funcionarioMenu = app.formPrincipal.new_menu('&Funcionários')
    app.formPrincipal.new_action(
        funcionarioMenu, '&Consultar', abrir_funcionario, icon=None,
        tinytxt='Ctrl+F', tip='Consulta ao cadastro de funcionários.')

    tipoMenu = app.formPrincipal.new_menu('&Tipo')
    app.formPrincipal.new_action(
        tipoMenu, '&Consultar', abrir_tipo, icon=None,
        tinytxt='Ctrl+T', tip='Consulta ao cadastro de tipos.')

    run()
