import sys

from PyQt5.QtWidgets import QApplication
from QPeewee import (
    QFormulario, QCharEdit, QFormDialog, QIntEdit, QDateWithCalendarEdit,
    QRegExpEdit, QResultList, QListDialog)
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField

db = SqliteDatabase('my_app.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    nome = CharField()
    username = CharField(unique=True)
    email = CharField()
    idade = IntegerField()
    data = DateField()

    def __str__(self):
        return self.nome


class FormularioUser(QFormulario):
    ENTIDADE = User

    def __init__(self):
        super(FormularioUser, self).__init__()
        self.nome = QCharEdit(
            column_name='nome', max_lenght=100, required=True)
        self.username = QCharEdit(column_name='username')
        self.email = QRegExpEdit(
            column_name='email', regex='^[A-Z0-9._%+-]+@[A-Z0-9._%+-]+$')
        self.idade = QIntEdit(column_name='idade')
        self.data = QDateWithCalendarEdit(column_name='data')


class UserDialog(QFormDialog):
    FORMULARIO = FormularioUser


class UsersList(QResultList):
    QUERY = User.select().order_by(User.nome)
    FORM = UserDialog

    def get_value(self, obj):
        return str(obj)


class UsersListDialog(QListDialog):
    LIST = UsersList


if __name__ == '__main__':
    User.create_table()
    app = QApplication(sys.argv)
    dialog = UsersListDialog()
    sys.exit(dialog.exec())
