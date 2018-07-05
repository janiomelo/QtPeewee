from QPeewee import (
    QFormulario, QCharEdit, QFormDialog, QDateWithCalendarEdit, QTableDialog,
    QResultList, QListDialog, QFkComboBox, QResultTable, run, app)
from peewee import Model, CharField, DateField, ForeignKeyField, fn


class BaseModel(Model):
    class Meta:
        database = app.db


class Tipo(BaseModel):
    descricao = CharField()

    def __str__(self):
        return self.descricao


class Cliente(BaseModel):
    nome = CharField()
    email = CharField()
    tipo = ForeignKeyField(Tipo)


class Funcionario(BaseModel):
    nome = CharField()
    nascimento = DateField()
    tipo = ForeignKeyField(Tipo)


class FormularioCliente(QFormulario):
    ENTIDADE = Cliente

    def __init__(self):
        super(FormularioCliente, self).__init__()
        self.nome = QCharEdit(
            column_name='nome', max_lenght=100, required=True)
        self.email = QCharEdit(column_name='email')
        self.tipo = QFkComboBox(entity=Tipo, column_name='tipo')


class ClienteDialog(QFormDialog):
    FORMULARIO = FormularioCliente


class FormularioFuncionario(QFormulario):
    ENTIDADE = Funcionario

    def __init__(self):
        super(FormularioFuncionario, self).__init__()
        self.nome = QCharEdit(
            column_name='nome', max_lenght=100, required=True)
        self.nascimento = QDateWithCalendarEdit(column_name='nascimento')
        self.tipo = QFkComboBox(entity=Tipo, column_name='tipo')


class FuncionarioDialog(QFormDialog):
    FORMULARIO = FormularioFuncionario


class FormularioTipo(QFormulario):
    ENTIDADE = Tipo

    def __init__(self):
        super(FormularioTipo, self).__init__()
        self.descricao = QCharEdit(
            column_name='descricao', max_lenght=100, required=True)


class TipoDialog(QFormDialog):
    FORMULARIO = FormularioTipo


# -----------------------------------------------------------------------------

class ClientesList(QResultTable):
    FORM = ClienteDialog

    def get_value(self, obj):
        return obj.nome

    def get_all(self):
        return Cliente.select().join(
            Tipo, on=Tipo.id == Cliente.tipo).order_by(fn.lower(Cliente.nome))

    def columns(self):
        return [
            Cliente.id, Cliente.nome, Cliente.email, Tipo.descricao
        ]


class ClientesListDialog(QTableDialog):
    LIST = ClientesList

# -----------------------------------------------------------------------------


class FuncionariosList(QResultList):
    FORM = FuncionarioDialog

    def get_value(self, obj):
        return obj.nome

    def get_all(self):
        return Funcionario.select().order_by(Funcionario.nome)


class FuncionariosListDialog(QListDialog):
    LIST = FuncionariosList

# -----------------------------------------------------------------------------


class TiposList(QResultList):
    FORM = TipoDialog

    def get_value(self, obj):
        return obj.descricao

    def get_all(self):
        return Tipo.select().order_by(Tipo.descricao)


class TiposListDialog(QListDialog):
    LIST = TiposList


def abrir_cliente(e):
    dialog = ClientesListDialog()
    dialog.exec_()


def abrir_funcionario(e):
    dialog = FuncionariosListDialog()
    dialog.exec_()


def abrir_tipo(e):
    dialog = TiposListDialog()
    dialog.exec_()


if __name__ == '__main__':
    Tipo.create_table()
    Cliente.create_table()
    Funcionario.create_table()

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
