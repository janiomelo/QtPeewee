from datetime import date
import os
import sys
import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from qtpeewee import (
    QCharEdit, QDateWithCalendarEdit, QIntEdit, QHiddenEdit, MyQListWidgetItem,
    QFormulario, QDialogButtonBox, QDecimalEdit, QRegExpEdit, QFormWidget,
    QResultList)
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField


app = QApplication(sys.argv)
estilo_invalido = 'border: 1px solid red; border-radius: 4px'


class QCharEditTest(unittest.TestCase):
    def test_define_valor(self):
        widget = QCharEdit()
        widget.set_valor('Olá')
        self.assertEqual(widget.get_valor(), 'Olá')

    def test_nao_avisa_se_valido(self):
        widget = QCharEdit()
        widget.set_valor('Olá')
        self.assertEqual(widget.styleSheet(), '')

    def test_se_valor_excede_grava_apenas_limite(self):
        widget = QCharEdit(max_lenght=5)
        widget.set_valor('ADOLETA')
        self.assertEqual(widget.get_valor(), 'ADOLE')

    def test_obrigatorio_avisa_se_nulo(self):
        widget = QCharEdit(required=True)
        widget.set_valor(None)
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_avisa_se_vazio(self):
        widget = QCharEdit(required=True)
        widget.set_valor('')
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_avisa_se_espaco(self):
        widget = QCharEdit(required=True)
        widget.set_valor('  ')
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_nao_avisa_se_zero(self):
        widget = QCharEdit(required=True)
        widget.set_valor(0)
        self.assertEqual(widget.get_valor(), '0')

    def test_nao_obrigatorio_aceita_nulo(self):
        widget = QCharEdit(required=False)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), '')


class QRegExpEditTest(unittest.TestCase):

    def regex(self):
        return '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'

    def test_define_valor(self):
        widget = QRegExpEdit(regex=self.regex())
        widget.set_valor('teste@email.com.br')
        self.assertEqual(widget.get_valor(), 'teste@email.com.br')

    def test_nao_avisa_se_valido(self):
        widget = QRegExpEdit(regex=self.regex())
        widget.set_valor('teste@email.com.br')
        self.assertEqual(widget.styleSheet(), '')

    def test_obrigatorio_avisa_se_nulo(self):
        widget = QRegExpEdit(required=True, regex=self.regex())
        widget.set_valor(None)
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_avisa_se_vazio(self):
        widget = QRegExpEdit(required=True, regex=self.regex())
        widget.set_valor('')
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_avisa_se_espaco(self):
        widget = QRegExpEdit(required=True, regex=self.regex())
        widget.set_valor('  ')
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_obrigatorio_nao_avisa_se_zero(self):
        widget = QRegExpEdit(required=True, regex=self.regex())
        widget.set_valor(0)
        self.assertEqual(widget.get_valor(), '0')

    def test_nao_obrigatorio_aceita_nulo(self):
        widget = QRegExpEdit(required=False, regex=self.regex())
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), '')

    def test_obrigatorio_avisa_se_invalido(self):
        widget = QRegExpEdit(regex=self.regex())
        widget.set_valor('jose.melo')
        self.assertEqual(widget.styleSheet(), estilo_invalido)


class QIntEditTest(unittest.TestCase):
    def test_define_valor(self):
        widget = QIntEdit()
        widget.set_valor(15)
        self.assertEqual(widget.get_valor(), 15)

    def test_nao_avisa_se_valido(self):
        widget = QIntEdit()
        widget.set_valor(15)
        self.assertEqual(widget.styleSheet(), '')

    def test_obrigatorio_nao_interrompe_se_zero(self):
        widget = QIntEdit(required=True)
        widget.set_valor('0')
        self.assertEqual(widget.get_valor(), 0)

    def teste_aceita_string_numerica(self):
        widget = QIntEdit()
        widget.set_valor('120')
        self.assertEqual(widget.get_valor(), 120)

    def test_nulo_vira_zero(self):
        widget = QIntEdit(required=False)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), 0)
        widget = QIntEdit(required=True)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), 0)


class QDecimalEditTest(unittest.TestCase):
    def test_define_valor(self):
        widget = QDecimalEdit()
        widget.set_valor(15.20)
        self.assertEqual(widget.get_valor(), 15.20)

    def test_nao_avisa_se_valido(self):
        widget = QDecimalEdit()
        widget.set_valor(15.20)
        self.assertEqual(widget.styleSheet(), '')

    def test_obrigatorio_nao_interrompe_se_zero(self):
        widget = QDecimalEdit(required=True)
        widget.set_valor(0.00)
        self.assertEqual(widget.get_valor(), 0.00)

    def teste_aceita_string_numerica(self):
        widget = QDecimalEdit()
        widget.set_valor('120.12')
        self.assertEqual(widget.get_valor(), 120.12)

    def test_nulo_vira_zero(self):
        widget = QDecimalEdit(required=False)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), 0.00)
        widget = QDecimalEdit(required=True)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), 0.00)


class QDateWithCalendarEditTest(unittest.TestCase):
    def test_define_valor(self):
        widget = QDateWithCalendarEdit()
        data = date.today()
        widget.set_valor(data)
        self.assertEqual(widget.get_valor(), data.strftime('%Y-%m-%d'))

    def test_nao_avisa_se_valido(self):
        widget = QDateWithCalendarEdit()
        widget.set_valor(date.today())
        self.assertEqual(widget.styleSheet(), '')

    def test_obrigatorio_avisa_se_nulo(self):
        widget = QDateWithCalendarEdit(required=True)
        widget.set_valor(None)
        self.assertEqual(widget.styleSheet(), estilo_invalido)

    def test_nao_obrigatorio_aceita_nulo(self):
        widget = QDateWithCalendarEdit(required=False)
        widget.set_valor(None)
        self.assertEqual(widget.get_valor(), None)


class QHiddenEditTest(unittest.TestCase):
    def test_define_valor(self):
        widget = QHiddenEdit()
        widget.set_valor('teste')
        self.assertEqual(widget.get_valor(), 'teste')

    def test_nao_eh_visivel(self):
        widget = QHiddenEdit()
        self.assertEqual(widget.isVisible(), False)

try:
    os.remove('test.db')
except Exception:
    pass


db = SqliteDatabase('test.db')


class User(Model):
    nome = CharField()
    username = CharField(unique=True)
    email = CharField()
    idade = IntegerField()
    data = DateField()

    class Meta:
        database = db


User.create_table()


class FormularioUser(QFormulario):
    ENTIDADE = User

    def __init__(self):
        super(FormularioUser, self).__init__()
        self.nome = QCharEdit(column_name='nome', max_lenght=30, required=True)
        self.username = QCharEdit(column_name='username')
        self.email = QRegExpEdit(
            column_name='email', regex='(^[.]+@[.]+\.[.]+$)')
        self.idade = QIntEdit(column_name='idade')
        self.data = QDateWithCalendarEdit(column_name='data')


class UserWidget(QFormWidget):
    FORMULARIO = FormularioUser


def user_factory(nome=None, username=None, email=None, idade=None, data=None):
    if nome is None:
        nome = 'Mariza da Silva'
    if username is None:
        username = 'mariza'
    if email is None:
        email = 'mariza.silva@email.com'
    if idade is None:
        idade = 30
    if data is None:
        data = date.today()

    u = User.create(
        nome=nome,
        username=username,
        email=email,
        idade=idade,
        data=data)
    u.save()
    return u


class QFormDialogTest(unittest.TestCase):
    def setUp(self):
        self.form = UserWidget

    def limpa_base(self):
        User.delete().execute()

    def test_exibe_campos(self):
        form_dict = self.form().instancia_formulario.__dict__
        self.assertTrue('nome' in form_dict.keys())
        self.assertTrue('username' in form_dict.keys())
        self.assertTrue('email' in form_dict.keys())
        self.assertTrue('idade' in form_dict.keys())
        self.assertTrue('data' in form_dict.keys())

    def test_visualiza_dados(self):
        self.limpa_base()
        u = user_factory()
        form = self.form(u.id).instancia_formulario
        self.assertEqual(form.nome.get_valor(), 'Mariza da Silva')
        self.assertEqual(form.username.get_valor(), 'mariza')
        self.assertEqual(form.email.get_valor(), 'mariza.silva@email.com')
        self.assertEqual(form.idade.get_valor(), 30)
        self.assertEqual(
            form.data.get_valor(), date.today().strftime('%Y-%m-%d'))

    def test_avisa_se_invalido(self):
        self.limpa_base()
        u = user_factory()
        f = self.form(u.id)
        okWidget = f.buttonBox.button(QDialogButtonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

    def test_edita_dados(self):
        self.limpa_base()
        u = user_factory()
        f = self.form(u.id)
        form = f.instancia_formulario
        form.nome.set_valor('Maria de Souza')
        form.username.set_valor('souza')
        form.email.set_valor('maria.souza@email.com')
        form.idade.set_valor(25)
        form.data.set_valor(date.today())
        okWidget = f.buttonBox.button(QDialogButtonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)
        form = self.form(u.id).instancia_formulario
        self.assertEqual(form.nome.get_valor(), 'Maria de Souza')
        self.assertEqual(form.username.get_valor(), 'souza')
        self.assertEqual(form.email.get_valor(), 'maria.souza@email.com')
        self.assertEqual(form.idade.get_valor(), 25)
        self.assertEqual(
            form.data.get_valor(), date.today().strftime('%Y-%m-%d'))

    def test_inclui_dados(self):
        self.limpa_base()
        f = self.form()
        form = f.instancia_formulario
        form.nome.set_valor('Maria de Souza')
        form.username.set_valor('souza')
        form.email.set_valor('maria.souza@email.com')
        form.idade.set_valor(25)
        form.data.set_valor(date.today())
        okWidget = f.buttonBox.button(QDialogButtonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)
        form = self.form(1).instancia_formulario
        self.assertEqual(form.nome.get_valor(), 'Maria de Souza')
        self.assertEqual(form.username.get_valor(), 'souza')
        self.assertEqual(form.email.get_valor(), 'maria.souza@email.com')
        self.assertEqual(form.idade.get_valor(), 25)
        self.assertEqual(
            form.data.get_valor(), date.today().strftime('%Y-%m-%d'))


class MyQListWidgetItemTest(unittest.TestCase):
    def limpa_base(self):
        User.delete().execute()

    def test_exibe_texto_correto(self):
        self.limpa_base()
        objeto = user_factory()
        op = MyQListWidgetItem(QResultList(), objeto=objeto)
        self.assertEqual(op.text(), str(objeto))

unittest.main(argv=sys.argv)
