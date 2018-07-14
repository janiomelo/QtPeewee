import json
import locale
import re
import sys
import hashlib

from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import (
    QDoubleValidator, QIntValidator, QRegExpValidator, QIcon)
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QWidget, QMessageBox, QDateEdit, QDialog,
    QDialogButtonBox, QVBoxLayout, QGroupBox, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QMainWindow, QAction, QApplication, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView)
import peewee


def empty(str_test):
    return str_test is None or len(str(str_test).replace(' ', '')) == 0


class ImplementationError(RuntimeError):
    pass


def notifica(text, title, icon, buttons):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(buttons)
    return msg.exec()


def notifica_erro(text, title):
    notifica(text, title, QMessageBox.Critical, QMessageBox.Ok)


def notifica_confirmacao(text, title):
    return notifica(
        text, title, QMessageBox.Question, QMessageBox.Yes | QMessageBox.No)


class Centralize:
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


class Validation:
    CHAR = 'char'
    INTEGER = 'int'
    DATE = 'date'
    DECIMAL = 'decimal'

    def __init__(self, max_lenght=225, required=True, field_type=CHAR):
        self.max_lenght = max_lenght
        self.required = required
        self.field_type = field_type

    def destaca(self):
        self.setStyleSheet("border: 1px solid red; border-radius: 4px")

    def retira_destaque(self):
        self.setStyleSheet(None)

    def is_int(self, value):
        try:
            int(value)
            return True
        except Exception:
            return False

    def is_float(self, value):
        try:
            float(value)
            return True
        except Exception:
            return False

    def is_valid(self, value=None):
        if value is None:
            value = self.get_valor()
        if self.required and empty(value):
            return False
        return True

    def validates(self, value):
        if self.is_valid(value):
            self.retira_destaque()
        else:
            self.destaca()


class QCharEdit(QLineEdit, Validation):
    def __init__(self, max_lenght=225, required=True, column_name=None,
                 parent=None):
        QLineEdit.__init__(self, parent=parent)
        Validation.__init__(self, max_lenght=max_lenght, required=required)
        self.column_name = column_name

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            valor = str(valor)
            if len(valor) > self.max_lenght:
                valor = valor[:self.max_lenght]
            self.setText(valor)

    def get_valor(self):
        return self.text()

    def keyPressEvent(self, event):
        if (len(self.get_valor()) < self.max_lenght or
                event.key() == Qt.Key_Backspace or
                event.key() == Qt.Key_Left or
                (event.key() == Qt.Key_Right and
                    self.cursorPosition() <= self.max_lenght)):
            super(QCharEdit, self).keyPressEvent(event)

    def focusOutEvent(self, event):
        self.validates(self.get_valor())
        super(QCharEdit, self).focusOutEvent(event)


class QIntEdit(QLineEdit, Validation):
    def __init__(self, required=True, column_name=None, parent=None):
        QLineEdit.__init__(self, parent=parent)
        Validation.__init__(self, required=required,
                            field_type=Validation.INTEGER)
        self.column_name = column_name
        self.setText('0')
        self.setValidator(QIntValidator())

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            self.setText(str(valor))

    def get_valor(self):
        return int(self.text())

    def is_valid(self, value=None):
        value = value or 0
        if Validation.is_valid(self, value):
            if self.field_type == self.INTEGER and not self.is_int(value):
                return False
        return True


class QFkComboBox(QComboBox, Validation):
    def __init__(
            self, entity, required=True, column_name=None, parent=None,
            form_new=None, field_type=Validation.INTEGER):
        QComboBox.__init__(self, parent=parent)
        Validation.__init__(self, required=required, field_type=field_type)
        self.column_name = column_name
        self.entity = entity
        self.values = []
        self.form_new = form_new
        self.update_values()

    def get_all(self):
        return self.entity.select()

    def update_values(self):
        self.clear()
        self.values = []
        if not self.required:
            self.addItem('')
        for i in self.get_all():
            self.values.append(i)
            self.addItem(self.get_value(i))

    def get_value(self, obj) -> str:
        return str(obj)

    def set_valor(self, id):
        i = 0
        for obj in self.values:
            if obj.get_id() == id:
                self.setCurrentIndex(i)
            i += 1

    def get_valor(self):
        try:
            i = self.currentIndex()
            if not self.required:
                i = i - 1 if i > 0 else 0
            return self.values[i]
        except Exception:
            return None


class QRegExpEdit(QLineEdit, Validation):
    def __init__(
            self, regex, required=True, column_name=None,
            parent=None):
        QLineEdit.__init__(self, parent=parent)
        Validation.__init__(
            self, required=required, field_type=Validation.CHAR)
        self.column_name = column_name
        self.regex = regex
        self.setValidator(QRegExpValidator(regExp=QRegExp(regex)))

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            self.setText(str(valor))

    def get_valor(self):
        return self.text()

    def is_valid(self, value=None):
        if Validation.is_valid(self, value):
            if (value == re.match(str(self.regex), str(value))):
                return True
        return False


class QDecimalEdit(QLineEdit, Validation):
    def __init__(
            self, decimals=2, required=True, column_name=None,
            parent=None):
        QLineEdit.__init__(self, parent=parent)
        Validation.__init__(self, required=required,
                            field_type=Validation.DECIMAL)
        self.column_name = column_name
        self.decimals = decimals
        self.setText('0.00')
        self.setValidator(QDoubleValidator())

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            if isinstance(valor, float):
                valor = str(round(valor, self.decimals))
            self.setText(valor)

    def get_valor(self):
        return float(self.text())

    def is_valid(self, value=None):
        value = value or 0
        if Validation.is_valid(self, value):
            if self.field_type == self.DECIMAL and not self.is_float(value):
                return False
        return True


class QDateWithCalendarEdit(QDateEdit, Validation):
    def __init__(self, required=True, column_name=None, parent=None):
        QDateEdit.__init__(self, parent=parent)
        Validation.__init__(self, required=required,
                            field_type=Validation.DATE)
        self.column_name = column_name
        self.clear()
        self.setCalendarPopup(True)

    def null_date(self):
        if self.date() == self.minimumDate():
            return None
        return self.date()

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            self.setDate(valor)
        else:
            self.setDate(self.minimumDate())
            self.destaca()

    def clear(self):
        self.setDate(self.minimumDate())
        self.setSpecialValueText(" ")

    def is_null(self):
        if self.null_date() is None:
            return True
        return False

    def get_valor(self):
        if not self.is_null():
            return self.null_date().toString('yyyy-MM-dd')
        return None

    def keyPressEvent(self, event):
        if self.is_null():
            self.set_valor(QDate.currentDate())
            self.setSelectedSection(QDateEdit.DaySection)
        QDateEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Delete:
            self.clear()


class QHiddenEdit(QLineEdit):
    def __init__(self, parent=None, column_name=None):
        QLineEdit.__init__(self, parent=parent)
        self.column_name = column_name
        self.hide()

    def set_valor(self, valor):
        self.setText(valor)

    def get_valor(self):
        return self.text()


class QComboWithAddFormLayout(QHBoxLayout):
    def __init__(self, add_func, *args, **kwargs):
        super(QComboWithAddFormLayout, self).__init__(*args, **kwargs)
        self.setSpacing(5)
        self.setContentsMargins(0, 0, 0, 0)
        add_button = QPushButton('+')
        add_button.clicked.connect(add_func)
        add_button.setFixedWidth(25)
        self.insertWidget(1, add_button)

    def fieldWidget(self, field):
        self.insertWidget(0, field)


class QFormulario(QFormLayout):
    ENTIDADE = None

    def __init__(self, objeto=None, has_id=True):
        super(QFormulario, self).__init__()
        if has_id:
            self.id = QHiddenEdit(column_name='id')
        self.objeto = objeto

    def __valor_campo(self, campo):
        if self.objeto is not None:
            return self.objeto.__dict__['__data__'].get(campo)

    def _constroi(self):
        for k, v in self.__dict__.items():
            if (not isinstance(v, QHiddenEdit) and
                    isinstance(v, QWidget)):
                valor = self.__valor_campo(v.column_name)
                if valor is not None:
                    v.set_valor(valor)
                if isinstance(v, QFkComboBox) and v.form_new is not None:
                    campo = v
                    v = QWidget()
                    v_layout = QComboWithAddFormLayout(
                        lambda: self.novo(campo))
                    v_layout.fieldWidget(campo)
                    v.setLayout(v_layout)
                    v.column_name = campo.column_name
                self.addRow(QLabel(v.column_name), v)

    def novo(self, campo):
        form = campo.form_new()
        form.buttonBox.accepted.connect(campo.update_values)
        form.exec()

    @classmethod
    def get(cls, objeto=None):
        b = cls()
        b.objeto = objeto
        b._constroi()
        return b


class QSearchForm(QFormulario):
    def __init__(self):
        super(QSearchForm, self).__init__(has_id=False)
        self._filters = []

    def _constroi(self):
        for f in self.fields():
            if f["type"] == QFkComboBox:
                obj_field = f["type"](
                    entity=f["entity"].rel_model, required=False)
            else:
                obj_field = f["type"](required=False)
            setattr(
                self, f["entity"].name,
                obj_field)
            f["field"] = getattr(self, f["entity"].name)
            if "label" in f.keys():
                label = f["label"]
            else:
                label = '{0} {1}'.format(
                    f["entity"].name, f["entity"].model._meta.table_name)
            self.addRow(QLabel(label), f["field"])
            self._filters.append(f)

    @property
    def filters(self):
        return self._filters

    def fields(self):
        return []


class QFormDialog(QDialog, Centralize):
    FORMULARIO = QFormulario

    def __init__(self, pk=None):
        super(QFormDialog, self).__init__()
        super(Centralize, self).__init__()
        self.createFormGroupBox()

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Formulário")
        self.setGeometry(100, 100, 600, 400)

        self.pk = pk

        try:
            objeto = self.form.ENTIDADE.get_by_id(self.pk)
        except peewee.DoesNotExist:
            objeto = None

        self.instancia_formulario = self.form.get(objeto)
        self.center()

    @property
    def form(self):
        return self.FORMULARIO

    def is_valid(self):
        for k, v in self.instancia_formulario.__dict__.items():
            if (isinstance(v, Validation)):
                if not v.is_valid():
                    return False
        return True

    def atualiza_destaque(self):
        for k, v in self.instancia_formulario.__dict__.items():
            if (isinstance(v, Validation)):
                if v.is_valid():
                    v.retira_destaque()
                else:
                    v.destaca()

    def accept(self, *args, **kwargs):
        if self.is_valid():
            self.salva_dados()
            super(QFormDialog, self).accept(*args, **kwargs)
        else:
            notifica_erro(
                text='Preencha todos os campos obrigatórios',
                title='Impossível salvar os dados')
        self.atualiza_destaque()

    def salva_dados(self):
        form = self.instancia_formulario
        if form.objeto is None:
            form.objeto = form.ENTIDADE()
        for k, v in form.__dict__.items():
            if (not isinstance(v, QHiddenEdit) and
                    isinstance(v, QWidget)):
                setattr(form.objeto, k, v.get_valor())
        form.objeto.save()

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")

    def set_layout_default(self, layout):
        self.formGroupBox.setLayout(layout)

    def exec(self):
        self.set_layout_default(self.instancia_formulario)
        super(QFormDialog, self).exec()


class MyQListWidgetItem(QListWidgetItem):
    def __init__(self, parent, text=None, objeto=None, *args, **kwargs):
        self.__objeto = objeto
        self.parent = parent
        if text is None:
            text = self.parent.get_value(objeto)
        QListWidget.__init__(self, text, parent, *args, **kwargs)

    def setObjeto(self, objeto):
        self.__objeto = objeto

    def getObjeto(self):
        return self.__objeto

    def text(self):
        return self.parent.get_value(self.__objeto)


class QResultList(QListWidget):
    FORM = QFormDialog

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent=parent)
        self.filtros = []
        self.update_result_set()
        self.itemClicked.connect(self.on_click)
        self.itemDoubleClicked.connect(self.on_double_click)

    def get_all(self):
        return []

    def order(self):
        return None

    def get_all_with_filter(self):
        resultlist = self.get_all()
        if len(self.filtros) > 0:
            for f in self.filtros:
                if (f["field"].get_valor() is None or
                        f["field"].get_valor() == ''):
                    continue
                if f["operator"] == "%":
                    w = (f["entity"].contains(f["field"].get_valor()))
                elif f["operator"] == "=":
                    w = (f["entity"] == f["field"].get_valor())
                resultlist = resultlist.where(w)
        if self.order() is not None:
            resultlist = resultlist.order_by(self.order())
        return resultlist

    def update_result_set(self):
        self.clear()
        for item in self.get_all_with_filter():
            self.addItem(MyQListWidgetItem(self, objeto=item))

    def get_value(self, obj) -> str:
        return str(obj)

    def selected(self):
        try:
            return self.selectedItems()[0].getObjeto()
        except Exception:
            return None

    def on_click(self):
        pass

    def on_double_click(self):
        self.abrir_formulario(self.selected().id)

    def abrir_formulario(self, id=None):
        formulario = self.FORM(id)
        formulario.buttonBox.accepted.connect(self.update_result_set)
        formulario.exec()


class QListDialog(QDialog, Centralize):
    LIST = QResultList
    FORM_FILTER = None

    def __init__(self):
        super(QListDialog, self).__init__()
        super(Centralize, self).__init__()
        self.instancia_filtro = None
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Lista")
        window_layout = QVBoxLayout()
        if self.form_filter is not None:
            window_layout.addWidget(self.adiciona_filtro())
            button_save = QPushButton('Filtrar')
            button_save.clicked.connect(self.filtrar)
            window_layout.addWidget(button_save)
        title = QLabel("Exibe resultado da consulta")
        window_layout.addWidget(title)
        actions = self.adiciona_botoes()
        window_layout.addWidget(actions)
        self.instancia_lista = self.lista(self)
        window_layout.addWidget(self.instancia_lista)
        self.setLayout(window_layout)
        self.center()

    def filtrar(self):
        self.instancia_lista.filtros = self.instancia_filtro.filters
        self.instancia_lista.update_result_set()

    def adiciona_filtro(self):
        gb_layout = QGroupBox("Filtro")
        self.instancia_filtro = self.form_filter.get(None)
        gb_layout.setLayout(self.instancia_filtro)
        return gb_layout

    def adiciona_botoes(self):
        actions = QWidget()
        actions_layout = QHBoxLayout(self)
        button_novo = QPushButton('Novo')
        button_novo.clicked.connect(self.novo)
        actions_layout.addWidget(button_novo)
        button_editar = QPushButton('Editar')
        button_editar.clicked.connect(self.editar)
        actions_layout.addWidget(button_editar)
        button_excluir = QPushButton('Excluir')
        button_excluir.clicked.connect(self.excluir)
        actions_layout.addWidget(button_excluir)
        actions.setLayout(actions_layout)
        return actions

    def novo(self, *args, **kwargs):
        self.instancia_lista.abrir_formulario()

    def editar(self, *args, **kwargs):
        selecionado = self.instancia_lista.selected()
        if selecionado is not None:
            self.instancia_lista.abrir_formulario(selecionado)

    def excluir(self, *args, **kwargs):
        selecionado = self.instancia_lista.selected()
        if selecionado is not None:
            entidade = self.instancia_lista.FORM.FORMULARIO.ENTIDADE
            sql = entidade.delete().where(entidade.id == selecionado.id)

            op = notifica_confirmacao(
                text='Confirma a exclusão do registro selecionado?',
                title='Excluir registro')

            if op == QMessageBox.Yes:
                sql.execute()
                self.instancia_lista.update_result_set()

    @property
    def lista(self):
        return self.LIST

    @property
    def form_filter(self):
        return self.FORM_FILTER


class QResultTable(QTableWidget):
    FORM = QFormDialog

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent=parent)
        self.itemClicked.connect(self.on_click)
        self.itemDoubleClicked.connect(self.on_double_click)
        self.values = None
        self.filtros = []
        self.update_result_set()
        self.verticalHeader().hide()
        self.show()

    def get_all(self):
        return []

    def get_all_with_filter(self):
        resultlist = self.get_all()
        if len(self.filtros) > 0:
            for f in self.filtros:
                if (f["field"].get_valor() is None or
                        f["field"].get_valor() == ''):
                    continue
                if f["operator"] == "%":
                    w = (f["entity"].contains(f["field"].get_valor()))
                elif f["operator"] == "=":
                    w = (f["entity"] == f["field"].get_valor())
                resultlist = resultlist.where(w)
        if self.order() is not None:
            resultlist = resultlist.order_by(self.order())
        return resultlist

    def columns(self):
        return []

    def set_headers(self):
        header = self.horizontalHeader()
        labels = []
        for i, c in enumerate(self.columns()):
            label = c[0].name if isinstance(c, tuple) else c.name
            labels.append(label.title())
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(labels)

    def update_result_set(self):
        self.values = self.get_all_with_filter()
        self.clear()
        self.setColumnCount(len(self.columns()))
        self.setRowCount(self.values.count())
        self.set_headers()
        numRows = 0
        for item in self.values:
            # self.insertRow(numRows)
            i = 0
            for column in self.columns():
                if isinstance(column, tuple):
                    fk_id = getattr(item, column[0].column_name)
                    fk_obj = column[0].rel_model.get_by_id(fk_id)
                    txt = str(getattr(fk_obj, column[1]))
                else:
                    txt = str(getattr(item, column.column_name))
                self.setItem(numRows, i, QTableWidgetItem(txt))
                i += 1
            numRows += 1

    def get_value(self, obj) -> str:
        return str(obj)

    def selected(self):
        try:
            return self.values[self.currentRow()]
        except Exception:
            return None

    def on_click(self):
        pass

    def on_double_click(self):
        self.abrir_formulario(self.selected().id)

    def abrir_formulario(self, id=None):
        formulario = self.FORM(id)
        formulario.buttonBox.accepted.connect(self.update_result_set)
        formulario.exec()


class QTableDialog(QListDialog, Centralize):
    LIST = QResultTable
    FORM_FILTER = None

    def __init__(self):
        super(QTableDialog, self).__init__()
        super(Centralize, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Tabela")
        self.center()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.instancia_lista.update_result_set()
        else:
            super(QTableDialog, self).keyPressEvent(event)


class QPrincipal(QMainWindow, Centralize):
    def __init__(self):
        super(QPrincipal, self).__init__()
        super(Centralize, self).__init__()
        self.import_env_vars()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        locale.setlocale(locale.LC_ALL, self.env('locale'))
        self.initUI()

    def import_env_vars(self):
        data = None
        with open('environment.json') as f:
            data = json.load(f)
        self.__env_vars = data

    def env(self, key):
        if self.__env_vars is None:
            raise Exception("Environment variables not defined.")
        if key not in self.__env_vars.keys():
            raise Exception("Key '{0}' not defined.".format(key))
        return self.__env_vars[key]

    def new_menu(self, label: str):
        return self.menubar.addMenu(label)

    def new_action(
            self, parent, text, event, icon=None, tinytxt=None, tip=None):
        if icon is not None:
            exitAction = QAction(icon, text, self)
        else:
            exitAction = QAction(text, self)
        if tinytxt is not None:
            exitAction.setShortcut(tinytxt)
        if tip is not None:
            exitAction.setStatusTip(tip)
        exitAction.triggered.connect(event)
        parent.addAction(exitAction)

    def initUI(self, icon=None):
        self.menubar = self.menuBar()
        fileMenu = self.new_menu('&Arquivo')
        self.new_action(
            fileMenu, '&Sair', self.close, icon=QIcon('exit.png'),
            tinytxt='Ctrl+Q', tip='Sair da aplicação.')
        self.statusBar().showMessage('Ready')
        # x, y, w, h
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('### DEFINIR ###')
        self.center()
        self.show()


class QPeeweeApp(QApplication):
    PRINCIPAL_FORM = QPrincipal

    def __init__(self, argv, db):
        QApplication.__init__(self, argv)
        self.__principal = self.PRINCIPAL_FORM()
        self.__db = db

    @property
    def db(self):
        return self.__db

    @property
    def formPrincipal(self):
        return self.__principal


app = QPeeweeApp(sys.argv, peewee.SqliteDatabase('app.db'))


class User(peewee.Model):
    login = peewee.CharField()
    password = peewee.CharField(max_length=32)

    class Meta:
        database = app.db


def default_hash(txt):
    m = hashlib.md5()
    m.update(txt)
    return m.hexdigest()


class ForbiddenException(Exception):
    pass


class AuthService:
    def __init__(self):
        self.__user = None

    @property
    def user(self):
        return self.__user

    def authenticate(self, login: str, password: str):
        try:
            user = User.get(User.login == login)
            if not user.password == default_hash(password):
                raise ForbiddenException()
            self.__user = user
            return self.user
        except peewee.DoesNotExist:
            raise ForbiddenException()


def run():
    sys.exit(app.exec())
