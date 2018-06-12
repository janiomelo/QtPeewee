import re

from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QWidget, QMessageBox, QDateEdit, QDialog,
    QDialogButtonBox, QVBoxLayout, QGroupBox, QListWidget, QListWidgetItem)
import peewee


def empty(str_test):
    return str_test is None or len(str(str_test).replace(' ', '')) == 0


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

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            self.setDate(valor)
        else:
            self.setDate(QDate(1910, 1, 1))
            self.destaca()

    def get_valor(self):
        return self.date().toString('yyyy-MM-dd')


class QHiddenEdit(QLineEdit):
    def __init__(self, parent=None, column_name=None):
        QLineEdit.__init__(self, parent=parent)
        self.column_name = column_name
        self.hide()

    def set_valor(self, valor):
        self.setText(valor)

    def get_valor(self):
        return self.text()


class QFormulario(QFormLayout):
    ENTIDADE = None

    def __init__(self, objeto=None):
        super(QFormulario, self).__init__()
        self.id = QHiddenEdit(column_name='id')
        self.objeto = objeto

    def __valor_campo(self, campo):
        if self.objeto is not None:
            return self.objeto.__dict__['__data__'].get(campo)

    def __constroi(self):
        for k, v in self.__dict__.items():
            if (not isinstance(v, QHiddenEdit) and
                    isinstance(v, QWidget)):
                valor = self.__valor_campo(v.column_name)
                if valor is not None:
                    v.set_valor(valor)
                self.addRow(QLabel(v.column_name), v)

    @classmethod
    def get(cls, objeto=None):
        b = cls()
        b.objeto = objeto
        b.__constroi()
        return b


class QFormDialog(QDialog):
    FORMULARIO = QFormulario

    def __init__(self, pk=None):
        super(QFormDialog, self).__init__()
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

        self.pk = pk

        try:
            objeto = self.form.ENTIDADE.get_by_id(self.pk)
        except peewee.DoesNotExist:
            objeto = None

        self.instancia_formulario = self.form.get(objeto)

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
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Preencha todos os campos obrigatórios')
            msg.setWindowTitle('Impossível salvar os dados')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
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
        if text is None:
            text = parent.get_value(objeto)
        QListWidget.__init__(self, text, parent, *args, **kwargs)

    def setObjeto(self, objeto):
        self.__objeto = objeto

    def getObjeto(self):
        return self.__objeto

    def text(self):
        return self.parent.get_value(self.__objeto)


class QResultList(QListWidget):
    QUERY = None
    FORM = QFormDialog

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent=parent)
        self.popular_lista()
        self.itemClicked.connect(self.on_click)
        self.itemDoubleClicked.connect(self.on_double_click)

    def get_all(self):
        return self.QUERY

    def popular_lista(self):
        self.clear()
        for item in self.get_all():
            self.addItem(MyQListWidgetItem(self, objeto=item))

    def get_value(self, obj):
        return obj

    def selected(self):
        try:
            return self.selectedItems()[0].getObjeto()
        except Exception:
            return None

    def on_click(self):
        pass

    def on_double_click(self):
        self.FORM(self.selected().id).exec()


class QListDialog(QDialog):
    LIST = QResultList

    def __init__(self, pk=None):
        super(QListDialog, self).__init__()
        self.instancia_lista = self.lista(self)
        self.setWindowTitle("Lista")

    @property
    def lista(self):
        return self.LIST
