import json
import locale
import re
import sys
import hashlib

from PyQt5.QtCore import (
    Qt, QDate, QRegExp, QDateTime, QFileInfo, QSize)
from PyQt5.QtGui import (
    QDoubleValidator, QIntValidator, QRegExpValidator, QPalette,
    QTextDocumentWriter, QKeySequence)
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QWidget, QMessageBox, QDateEdit, QDialog,
    QDialogButtonBox, QVBoxLayout, QGroupBox, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QMainWindow, QAction, QApplication, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateTimeEdit, QGridLayout,
    QFrame, QFileDialog, QTextEdit, QToolBar, QDockWidget, QStackedLayout,
    QDesktopWidget)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
import peewee
from playhouse.hybrid import hybrid_property
import qtawesome as qta
from jinja2 import Template


def empty(str_test):
    return str_test is None or len(str(str_test).replace(' ', '')) == 0


def title_label(label):
    return label.title().replace('_', ' ')


def stretch(widget):
    widget.setMinimumSize(QSize(0, 0))
    widget.setMaximumSize(QSize(16777215, 16777215))
    return widget


def stretch_label(widget):
    widget.setAlignment(Qt.AlignRight)
    return stretch(widget)


class CalculatedField:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return str(self.value)


class hybrid_property_field(hybrid_property):
    def __init__(self, fget, fset=None, fdel=None, expr=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.expr = expr or fget

    def __get__(self, instance, instance_type):
        if instance is None:
            value = self.expr(instance_type)
        else:
            value = self.fget(instance)
        f = CalculatedField(name=self.fget.__name__, value=value)
        return f


class ChoiceField(peewee.IntegerField):
    def __init__(self, values: list, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.values = values


class QVBoxLayoutWithoutMargins(QVBoxLayout):
    def __init__(self):
        QVBoxLayout.__init__(self)
        self.setSpacing(5)
        self.setContentsMargins(0, 0, 0, 0)


class QVBoxLayoutWithMargins(QVBoxLayout):
    def __init__(self):
        QVBoxLayout.__init__(self)
        self.setSpacing(5)
        self.setContentsMargins(10, 10, 10, 10)


class QHBoxLayoutWithoutMargins(QHBoxLayout):
    def __init__(self):
        QHBoxLayout.__init__(self)
        self.setSpacing(5)
        self.setContentsMargins(0, 0, 0, 0)


class QHBoxLayoutWithMargins(QHBoxLayout):
    def __init__(self):
        QHBoxLayout.__init__(self)
        self.setSpacing(5)
        self.setContentsMargins(10, 10, 10, 10)


class QDockWidgetN(QDockWidget):
    def __init__(self, *args):
        QDockWidget.__init__(self, *args)

    def setWidget(self, widget):
        widget.dock = self
        QDockWidget.setWidget(self, widget)


class QPrincipal(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setDockNestingEnabled(True)
        self.setDockOptions(QMainWindow.ForceTabbedDocks)
        self.import_env_vars()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        locale.setlocale(locale.LC_ALL, self.env('locale'))
        self.initUI()
        self.dock_widgets = []

    def import_env_vars(self):
        with open('environment.json') as f:
            data = json.load(f)
        self.__env_vars = data

    def add_dock(self, name, class_name=None, object=None):
        dock = QDockWidgetN(name)
        dock.setWidget(class_name() if class_name is not None else object)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        dock.visibilityChanged.connect(self.update_dock_positions)
        if len(self.dock_widgets) > 0:
            self.tabifyDockWidget(self.dock_widgets[-1], dock)
        else:
            self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.dock_widgets.append(dock)

    def update_dock_positions(self):
        if len(self.dock_widgets) > 0 and not self.dock_widgets[-1].isVisible():
            self.dock_widgets[-1].raise_()

    def env(self, key):
        if self.__env_vars is None:
            raise Exception("Environment variables not defined.")
        if key not in self.__env_vars.keys():
            raise Exception("Key '{0}' not defined.".format(key))
        return self.__env_vars[key]

    def new_menu(self, label: str):
        return self.menubar.addMenu(label)

    def new_action(
            self, parent, text, form_action, icon=None, tinytxt=None,
            tip=None):
        if icon is not None:
            action = QAction(icon, text, self)
        else:
            action = QAction(text, self)
        if tinytxt is not None:
            action.setShortcut(tinytxt)
        if tip is not None:
            action.setStatusTip(tip)
        text = text.replace('&', '')
        action.triggered.connect(lambda: self.add_dock(text, class_name=form_action))
        parent.addAction(action)

    def initUI(self, icon=None):
        self.statusBar()
        self.menubar = self.menuBar()
        fileMenu = self.new_menu('&Arquivo')
        self.new_action(
            fileMenu, '&Sair', self.close,
            icon=qta.icon('fa.sign-out', color='black'),
            tinytxt='Ctrl+Q', tip='Sair da aplicação.')
        # x, y, w, h
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('### DEFINIR ###')
        self.showMaximized()


class QPeeweeApp(QApplication):
    PRINCIPAL_FORM = QPrincipal

    def __init__(self, argv, db):
        QApplication.__init__(self, argv)
        self.__principal = self.PRINCIPAL_FORM()
        self.__db = db
        self.count_field = 0
        self.setStyleSheet(open("qss/style.qss", "r").read())

    def set_title(self, title):
        self.formPrincipal.setWindowTitle(title)

    @property
    def db(self):
        return self.__db

    @property
    def formPrincipal(self):
        return self.__principal


app = QPeeweeApp(sys.argv, peewee.SqliteDatabase('app.db'))


class BaseModel(peewee.Model):
    class Meta:
        database = app.db


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


class QPreview(QDialog):
    def __init__(self, parent=None):
        super(QPreview, self).__init__(parent)
        if self.template() is None:
            raise Exception("TEMPLATE is required.")
        self.init()

    def close(self):
        super().close()
        self.dock.close()

    def template(self):
        return None

    def render(self, **kwargs):
        template = Template(open(self.template(), 'r').read())
        self.load(template.render(**kwargs))

    def init(self):
        l = QVBoxLayout()
        self.setLayout(l)
        self.text_edit = QTextEdit()
        self.text_edit.setFocus()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(
            'background-color: white; border-width: 1px')
        l.addWidget(self.create_toolbar())
        l.addWidget(self.text_edit)

        self.before_render()

    def load(self, source=None):
        if source is not None:
            self.text_edit.setHtml(source)
        self.setCurrentFileName()
        return True

    def setCurrentFileName(self, fileName=''):
        self.fileName = fileName
        self.text_edit.document().setModified(False)

        if not fileName:
            shownName = 'untitled.txt'
        else:
            shownName = QFileInfo(fileName).fileName()

        self.setWindowTitle(self.tr("%s[*] - %s" % (shownName, "Rich Text")))
        self.setWindowModified(False)

    def fileSaveDoc(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "Save as...", None,
            "ODF files (*.odt)")

        if not fn:
            return False

        lfn = fn.lower()
        if not lfn.endswith(('.odt')):
            # The default.
            fn += '.odt'

        self.setCurrentFileName(fn)
        return self.fileSave()

    def fileSave(self):
        if not self.fileName:
            return self.fileSaveAs()

        writer = QTextDocumentWriter(self.fileName)
        success = writer.write(self.text_edit.document())
        if success:
            self.text_edit.document().setModified(False)

        return success

    def fileSaveHtml(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "Save as...", None,
            "HTML-Files (*.htm *.html)")

        if not fn:
            return False

        lfn = fn.lower()
        if not lfn.endswith(('.htm', '.html')):
            # The default.
            fn += '.html'

        self.setCurrentFileName(fn)
        return self.fileSave()

    def filePrint(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)

        if self.text_edit.textCursor().hasSelection():
            dlg.addEnabledOption(QPrintDialog.PrintSelection)

        dlg.setWindowTitle("Print Document")

        if dlg.exec_() == QPrintDialog.Accepted:
            self.text_edit.print_(printer)

        del dlg

    def filePrintPreview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.printPreview)
        preview.exec_()

    def printPreview(self, printer):
        self.text_edit.print_(printer)

    def filePrintPdf(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", None, "PDF files (*.pdf)")

        if fn:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.text_edit.document().print_(printer)

    def create_toolbar(self):
        tb = QToolBar(self)
        tb.setWindowTitle("File Actions")

        self.actionSaveDoc = QAction(
            qta.icon('fa.file-word-o', color='black'),
            "Save &Doc...", self, priority=QAction.LowPriority,
            shortcut=Qt.CTRL + Qt.SHIFT + Qt.Key_D,
            triggered=self.fileSaveDoc)
        tb.addAction(self.actionSaveDoc)

        self.actionSaveDoc = QAction(
            qta.icon('fa.globe', color='black'),
            "Save &HTML...", self, priority=QAction.LowPriority,
            shortcut=Qt.CTRL + Qt.SHIFT + Qt.Key_H,
            triggered=self.fileSaveHtml)
        tb.addAction(self.actionSaveDoc)

        self.actionPrint = QAction(
            qta.icon('fa.print', color='black'),
            "&Print...", self, priority=QAction.LowPriority,
            shortcut=QKeySequence.Print, triggered=self.filePrint)
        tb.addAction(self.actionPrint)

        self.actionPrintPreview = QAction(
            qta.icon('fa.eye', color='black'),
            "Print Preview...", self, triggered=self.filePrintPreview,
            shortcut=Qt.CTRL + Qt.SHIFT + Qt.Key_P)
        tb.addAction(self.actionPrintPreview)

        self.actionPrintPdf = QAction(
            qta.icon('fa.file-pdf-o', color='black'),
            "&Export PDF...", self, priority=QAction.LowPriority,
            shortcut=Qt.CTRL + Qt.Key_D, triggered=self.filePrintPdf)
        tb.addAction(self.actionPrintPdf)

        self.actionQuit = QAction(
            qta.icon('fa.sign-out', color='black'),
            "&Quit", self, shortcut=QKeySequence.Quit, triggered=self.close)
        tb.addAction(self.actionQuit)

        return tb


class BaseEdit:
    CHAR = 'char'
    INTEGER = 'int'
    DATE = 'date'
    DATETIME = 'datetime'
    DECIMAL = 'decimal'

    def __init__(
            self, max_length=225, is_required=True, field_type=CHAR,
            force_null=False, x=0, y=0, nx=1, ny=1, *args, **kwargs):
        self.order = app.count_field
        app.count_field += 1
        self.x = x
        self.y = y
        self.nx = nx
        self.ny = ny
        self.max_length = max_length
        if force_null:
            self.is_required = False
        else:
            self.is_required = is_required
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
        if self.is_required and empty(value):
            return False
        return True

    def validates(self, value):
        if self.is_valid(value):
            self.retira_destaque()
        else:
            self.destaca()

    def get_valor(self):
        raise NotImplementedError

    def set_valor(self, valor):
        raise NotImplementedError


class QCharEdit(QLineEdit, BaseEdit):
    def __init__(self, field, parent=None, *args, **kwargs):
        QLineEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, max_length=field.max_length, is_required=not field.null,
            *args, **kwargs)
        self.column_name = field.column_name

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            valor = str(valor)
            if len(valor) > self.max_length:
                valor = valor[:self.max_length]
            self.setText(valor)

    def get_valor(self):
        return self.text()

    def keyPressEvent(self, event):
        if (len(self.get_valor()) < self.max_length or
                event.key() == Qt.Key_Backspace or
                event.key() == Qt.Key_Left or
                (event.key() == Qt.Key_Right and
                    self.cursorPosition() <= self.max_length)):
            super(QCharEdit, self).keyPressEvent(event)

    def focusOutEvent(self, event):
        self.validates(self.get_valor())
        super(QCharEdit, self).focusOutEvent(event)


class QIntEdit(QLineEdit, BaseEdit):
    def __init__(self, field, parent=None, *args, **kwargs):
        QLineEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=not field.null, field_type=BaseEdit.INTEGER,
            *args, **kwargs)
        self.column_name = field.column_name
        if self.is_required:
            self.setText('0')
        self.setValidator(QIntValidator())

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            self.setText(str(valor))

    def get_valor(self):
        return int(self.text()) if not self.text() == '' else None

    def is_valid(self, value=None):
        value = value or 0
        if BaseEdit.is_valid(self, value):
            if self.field_type == self.INTEGER and not self.is_int(value):
                return False
        return True


class QFkComboBox(QComboBox, BaseEdit):
    def __init__(
            self, entity, field, form_new=None, form_edit=None, parent=None,
            field_type=BaseEdit.INTEGER, *args, **kwargs):
        QComboBox.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=not field.null, field_type=field_type, *args,
            **kwargs)
        self.column_name = field.column_name
        self.entity = entity
        self.values = []
        self.form_new = form_new
        self.form_edit = form_edit
        self.update_values()

    def get_all(self):
        return self.entity.select()

    def update_values(self):
        self.clear()
        self.values = []
        if not self.is_required:
            self.addItem('')
        for i in self.get_all():
            self.values.append(i)
            self.addItem(self.get_value(i))

    def get_value(self, obj) -> str:
        return str(obj)

    def set_valor(self, id):
        i = 0
        if not self.is_required:
            i += 1
        for obj in self.values:
            if obj.get_id() == id:
                self.setCurrentIndex(i)
            i += 1

    def get_valor(self):
        try:
            i = self.currentIndex() - 1
            if not self.is_required:
                i -= 1
            return self.values[i]
        except Exception:
            return None


class QChoicesComboBox(QComboBox, BaseEdit):
    def __init__(self, field, parent=None, *args, **kwargs):
        QComboBox.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=not field.null, field_type=field.field_type,
            *args, **kwargs)
        self.column_name = field.column_name
        self.values = field.values
        self.update_values()

    def update_values(self):
        self.clear()
        if not self.is_required:
            self.addItem('')
        for i in self.values:
            self.addItem(self.get_value(i))

    def get_value(self, item) -> str:
        return str(item['name'])

    def set_valor(self, value_id):
        i = 0
        for v in self.values:
            if v['id'] == value_id:
                self.setCurrentIndex(i)
                return
            i += 1

    def get_valor(self):
        try:
            i = self.currentIndex()
            if not self.is_required:
                i = i - 1 if i > 0 else 0
            return self.values[i]['id']
        except Exception:
            return None


class QRegExpEdit(QLineEdit, BaseEdit):
    def __init__(
            self, regex, is_required=True, column_name=None,
            parent=None, *args, **kwargs):
        QLineEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=is_required, field_type=BaseEdit.CHAR, *args,
            **kwargs)
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
        if BaseEdit.is_valid(self, value):
            if (value == re.match(str(self.regex), str(value))):
                return True
        return False


class QDecimalEdit(QLineEdit, BaseEdit):
    def __init__(
            self, decimals=2, is_required=True, column_name=None,
            parent=None, *args, **kwargs):
        QLineEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=is_required, field_type=BaseEdit.DECIMAL, *args,
            **kwargs)
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
        if BaseEdit.is_valid(self, value):
            if self.field_type == self.DECIMAL and not self.is_float(value):
                return False
        return True


class QDateTimeWithCalendarEdit(QDateTimeEdit, BaseEdit):
    def __init__(self, field, parent=None, *args, **kwargs):
        QDateTimeEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=not field.null, field_type=BaseEdit.DATETIME,
            *args, **kwargs)
        self.column_name = field.column_name
        self.clear()
        self.setCalendarPopup(True)

    def null_datetime(self):
        if self.dateTime() == self.minimumDateTime():
            return None
        return self.dateTime()

    def set_valor(self, valor):
        self.validates(valor)
        if valor is not None:
            if isinstance(valor, str):
                self.setDateTime(
                    QDateTime.fromString(valor, 'yyyy-MM-dd hh:mm:ss'))
            else:
                self.setDateTime(valor)
        else:
            self.setDateTime(self.minimumDateTime())
            self.destaca()

    def clear(self):
        self.setDateTime(self.minimumDateTime())
        self.setSpecialValueText(" ")

    def is_null(self):
        if self.null_datetime() is None:
            return True
        return False

    def date_to_string(self, view_format, valid_null=True):
        if valid_null and self.is_null():
            return None
        return self.null_datetime().toString(view_format)

    def get_valor(self, view_format='yyyy-MM-dd hh:mm:ss'):
        return self.date_to_string(view_format)

    def mousePressEvent(self, event):
        if self.is_null():
            self.set_valor(QDateTime.currentDateTime())
            self.setSelectedSection(QDateEdit.DaySection)
        QDateTimeEdit.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        if self.is_null():
            self.set_valor(QDateTime.currentDateTime())
            self.setSelectedSection(QDateEdit.DaySection)
        QDateTimeEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Delete:
            self.clear()


class QDateWithCalendarEdit(QDateEdit, BaseEdit):
    def __init__(self, field, parent=None, *args, **kwargs):
        QDateEdit.__init__(self, parent=parent)
        BaseEdit.__init__(
            self, is_required=not field.null, field_type=BaseEdit.DATE, *args,
            **kwargs)
        self.column_name = field.column_name
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

    def date_to_string(self, format, valid_null=True):
        if valid_null and self.is_null():
            return None
        return self.null_date().toString(format)

    def get_valor(self, format='yyyy-MM-dd'):
        return self.date_to_string(format)

    def keyPressEvent(self, event):
        if self.is_null():
            self.set_valor(QDate.currentDate())
            self.setSelectedSection(QDateEdit.DaySection)
        QDateEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Delete:
            self.clear()

    def mousePressEvent(self, event):
        if self.is_null():
            self.set_valor(QDate.currentDate())
            self.setSelectedSection(QDateEdit.DaySection)
        QDateEdit.mousePressEvent(self, event)


class QHiddenEdit(QLineEdit, BaseEdit):
    def __init__(
            self, column_name, is_required=False, parent=None, *args,
            **kwargs):
        QLineEdit.__init__(self, parent=parent)
        BaseEdit.__init__(self, is_required=is_required, *args, **kwargs)
        self.column_name = column_name
        self.hide()

    def set_valor(self, valor):
        self.setText(valor)

    def get_valor(self):
        return self.text()


class QFieldWithActionsButton(QWidget):
    def __init__(
            self, field, *args, **kwargs):
        super(QFieldWithActionsButton, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayoutWithoutMargins()
        self.layout.insertWidget(0, field)
        self.field = field
        self.setLayout(self.layout)

    def add_button(self, action, fa_icon='fa.plus', field_param=False):
        icon = qta.icon(fa_icon, color='black')
        add_button = QPushButton(icon, '')
        add_button.setStyleSheet('font-size: 12px; min-width: 0px;')
        if field_param:
            add_button.clicked.connect(lambda: action(self.field))
        else:
            add_button.clicked.connect(action)
        add_button.setFixedWidth(25)
        add_button.setFixedHeight(25)
        self.layout.insertWidget(1, add_button)


FIELD_TO_EDIT = {
    peewee.CharField: QCharEdit,
    peewee.DateTimeField: QDateTimeWithCalendarEdit,
    peewee.TextField: QTextEdit,
    peewee.DecimalField: QDecimalEdit,
    peewee.ForeignKeyField: QFkComboBox,
    peewee.DateField: QDateWithCalendarEdit,
    ChoiceField: QChoicesComboBox,
    peewee.FloatField: QDecimalEdit,
    peewee.IntegerField: QIntEdit,
    peewee.IPField: QCharEdit,
    peewee.ManyToManyField: None,
    peewee.BooleanField: None,
}

class QFormBase:
    ENTIDADE = None

    def __init__(self, objeto=None, has_id=True):
        self.fields()
        self.__has_id = has_id
        if self.__has_id:
            self.id = QHiddenEdit(column_name='id', is_required=False)
        self.objeto = objeto

    def meta(self):
        return {}

    def fields(self):
        for k, v in self.ENTIDADE.__dict__.items():
            if (isinstance(v, peewee.FieldAccessor) and k != 'id'):
                field = getattr(self.ENTIDADE, k)
                cls = FIELD_TO_EDIT[field.__class__]
                if cls is None:
                    raise NotImplementedError(
                        'Field does not have a corresponding Edit.')
                if cls == QFkComboBox:
                    meta = self.meta()[k] if k in self.meta().keys() else {}
                    edit = cls(
                        entity=field.rel_model, field=field, **meta)
                else:
                    edit = cls(field=field)
                setattr(self, k, edit)

    def __valor_campo(self, campo):
        if self.objeto is not None:
            return self.objeto.__dict__['__data__'].get(campo)

    def _constroi(self):
        itens = sorted(
            self.__dict__.items(),
            key=lambda k: k[1].order if isinstance(
                k[1], BaseEdit
            ) else 0)
        for k, v in itens:
            self.add_field_in_row(k, v)

    def add_field_in_row(self, name, field):
        if (not isinstance(field, QHiddenEdit) and
                isinstance(field, QWidget) and
                not name[:1] == '_'):
            valor = self.__valor_campo(name)
            if valor is not None:
                field.set_valor(valor)
            if isinstance(field, QFkComboBox) and field.form_new is not None:
                f = field
                field = QFieldWithActionsButton(f)
                field.add_button(self.novo, field_param=True)
                if f.form_edit is not None:
                    field.add_button(
                        self.edit, fa_icon='fa.pencil', field_param=True)
            if (isinstance(field, QDateEdit) or
                    isinstance(field, QDateTimeEdit)):
                f = field
                field = QFieldWithActionsButton(f)
                field.add_button(
                    self.clear_date, fa_icon='fa.trash', field_param=True)
            label = QLabel(title_label(name))
            self.insert_in_layout(label, field)

    def insert_in_layout(self, label, field):
        raise NotImplementedError

    def novo(self, field):
        form = field.form_edit()
        form.buttonBox.accepted.connect(field.update_values)
        form.show()
        app.formPrincipal.add_dock(
            'Incluir {0}'.format(field.entity.__name__), object=form)

    def edit(self, field):
        form = field.form_edit(field.get_valor())
        form.buttonBox.accepted.connect(field.update_values)
        form.show()
        app.formPrincipal.add_dock(
            'Editar {0}'.format(field.entity.__name__), object=form)

    def clear_date(self, field):
        field.clear()

    @classmethod
    def get(cls, objeto=None):
        b = cls()
        b.objeto = objeto
        b._constroi()
        return b


class QGridForm(QStackedLayout, QFormBase):

    def __init__(self, objeto=None, has_id=True):
        QStackedLayout.__init__(self)
        QFormBase.__init__(self, objeto=objeto, has_id=has_id)
        self.setSpacing(6)
        self.setContentsMargins(0, 10, 0, 10)
        gl = QGridLayout()
        self.__w = QWidget()
        self.__w.setLayout(gl)
        self.addWidget(self.__w)
        self.lines = 0

    def update_layout_height(self, nrows):
        self.__w.setFixedHeight(nrows * 40)

    def tamanho_tela(self):
        return QDesktopWidget().screenGeometry().width()

    def insert_in_layout(self, label, field):
        w = QWidget()
        t = (self.tamanho_tela() / 2) - 70
        w.setFixedWidth(t)
        w.setFixedHeight(26)
        w.setBackgroundRole(QPalette.HighlightedText)
        l = QHBoxLayoutWithoutMargins()
        l.addWidget(stretch_label(label))
        l.addWidget(stretch(field))
        w.setLayout(l)
        if isinstance(field, QFieldWithActionsButton):
            field = field.field
        self.__w.layout().addWidget(
            w, field.y, field.x, field.ny, field.nx)
        if self.lines != (field.y + 1):
            self.lines += 1
        self.update_layout_height(self.lines)


class QFormulario(QFormLayout, QFormBase):
    def __init__(self, objeto=None, has_id=True):
        QFormLayout.__init__(self)
        QFormBase.__init__(self, objeto=objeto, has_id=has_id)
        app.count_field = 0
        self.setSpacing(6)
        self.setContentsMargins(10, 10, 10, 10)

    def insert_in_layout(self, label, field):
        self.addRow(label, field)


class QSearchForm(QGridForm):
    def __init__(self, fields: list):
        super(QSearchForm, self).__init__(has_id=False)
        self._filters = []
        self.__fields = fields

    def _constroi(self):
        x = 0
        y = 0
        for f in self.__fields:
            entity = f["entity"]
            if f["type"] == QFkComboBox:
                obj_field = f["type"](
                    entity=entity.rel_model, field=entity, force_null=True,
                    x=x, y=y)
            else:
                obj_field = f["type"](field=entity, force_null=True, x=x, y=y)
            setattr(self, entity.name, obj_field)
            f["field"] = getattr(self, entity.name)
            if "label" in f.keys():
                label = f["label"]
            else:
                label = '{0} {1}'.format(
                    entity.name, entity.model._meta.table_name)
            self.add_field_in_row(label, f["field"])
            self._filters.append(f)
            y = y + 1 if x == 1 else y
            x = 0 if x == 1 else 1

    @property
    def filters(self):
        return self._filters

    def fields(self):
        return []

    @classmethod
    def get(cls, objeto=None, fields=None):
        b = cls(fields if fields is not None else [])
        b.objeto = objeto
        b._constroi()
        return b


class QFormWidget(QWidget):
    def __init__(self, pk=None, dock=None, formulario=None):
        QWidget.__init__(self)
        self.form = formulario
        self.dock = dock
        self.createFormGroupBox()
        self.pk = pk

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        f = QFrame(self)
        mainLayout = QVBoxLayoutWithMargins()
        mainLayout.addWidget(self.formGroupBox)
        self.add_buttons(mainLayout)
        mainLayout.addWidget(self.buttonBox)
        f.setLayout(mainLayout)

        l = QVBoxLayoutWithMargins()
        l.addWidget(f)
        self.setLayout(l)

        self.adjustSize()


        try:
            objeto = self.form.ENTIDADE.get_by_id(
                self.pk
            )
        except (peewee.DoesNotExist, AttributeError):
            objeto = None
        self.instancia_formulario = self.form.get(objeto)
        self.setWindowTitle(self.form.TITLE)

    def add_buttons(self, mainLayout):
        if len(self.buttons()) == 0:
            return
        width = 30
        w = QWidget()
        w.setFixedHeight(50)
        btn_layout = QHBoxLayoutWithMargins()
        for b in self.buttons():
            if b['condition'] is None or b['condition']:
                width_btn = (len(b['label']) * 10)
                width += width_btn
                add_button = QPushButton(b['label'])
                add_button.clicked.connect(
                    lambda: self.action(b['form'], b['pk']))
                add_button.setFixedWidth(width_btn)
                btn_layout.addWidget(add_button)
        w.setFixedWidth(width)
        w.setLayout(btn_layout)
        mainLayout.addWidget(w)

    def action(self, form, pk):
        f = form(pk)
        f.exec()

    def buttons(self):
        return []

    def is_valid(self):
        for k, v in self.instancia_formulario.__dict__.items():
            if (isinstance(v, BaseEdit)):
                if not v.is_valid():
                    return False
        return True

    def atualiza_destaque(self):
        for k, v in self.instancia_formulario.__dict__.items():
            if (isinstance(v, BaseEdit)):
                if v.is_valid():
                    v.retira_destaque()
                else:
                    v.destaca()

    def before_out(self):
        pass

    def before_save(self):
        pass

    def reject(self, *args, **kwargs):
        self.before_out()
        if self.dock is not None:
            self.dock.close()

    def accept(self, *args, **kwargs):
        self.before_save()
        if self.is_valid():
            self.salva_dados()
            if self.dock is not None:
                self.before_out()
                self.dock.close()
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
                    isinstance(v, BaseEdit)):
                setattr(form.objeto, k, v.get_valor())
        form.objeto.save()

    def createFormGroupBox(self):
        self.formGroupBox = QWidget()
        self.formGroupBox.setStyleSheet('background: none')

    def set_layout_default(self, layout):
        self.formGroupBox.setLayout(layout)

    def show(self):
        self.set_layout_default(self.instancia_formulario)
        super(QFormWidget, self).show()


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
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent=parent)
        self.filtros = []
        self.update_result_set()
        self.itemClicked.connect(self.on_click)
        self.itemDoubleClicked.connect(self.on_double_click)

    def get_all(self):
        if self.parent() is not None:
            return self.parent().get_all()
        return []

    def order(self):
        if self.parent() is not None:
            return self.parent().order()
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
                elif f["operator"] == "<":
                    w = (f["entity"] < f["field"].get_valor())
                resultlist = resultlist.where(w)
        if self.order() is not None:
            resultlist = resultlist.order_by(self.order())
        return resultlist

    def update_result_set(self):
        self.clear()
        for item in self.get_all_with_filter():
            self.addItem(MyQListWidgetItem(self, objeto=item))

    def get_value(self, obj) -> str:
        if self.parent() is not None:
            return self.parent().get_value(obj)
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
        formulario = QFormWidget(pk=id, formulario=self.parent().FORM)
        formulario.buttonBox.accepted.connect(self.update_result_set)
        formulario.show()
        app.formPrincipal.add_dock(formulario.windowTitle(), object=formulario)


class QListShow(QWidget):
    FORM = QFormulario
    LIST = QResultList
    TITLE = 'LIST'

    def __init__(self):
        super(QListShow, self).__init__()
        self.instancia_filtro = None
        self.adjustSize()
        self.setWindowTitle(self.TITLE)
        window_layout = QVBoxLayoutWithMargins()
        if len(self.filters()) > 0:
            window_layout.addWidget(self.adiciona_filtro())
            button_save = QPushButton(
                qta.icon('fa.search', color='black'), 'Filtrar')
            button_save.clicked.connect(self.filtrar)
            window_layout.addWidget(button_save)
        self.instancia_lista = self.lista(self)
        actions = self.adiciona_botoes()

        window_layout.addWidget(actions)
        window_layout.addWidget(self.instancia_lista)
        self.setLayout(window_layout)
        self.showMaximized()

    def filters(self):
        return []

    def get_all(self):
        return []

    def order(self):
        return None

    def get_value(self, obj):
        return 'UNDEFINED'

    def filtrar(self):
        self.instancia_lista.filtros = self.instancia_filtro.filters
        self.instancia_lista.update_result_set()

    def adiciona_filtro(self):
        gb = QGroupBox("Filtro")
        self.instancia_filtro = QSearchForm.get(None, self.filters())
        self.instancia_filtro.update_layout_height(2)
        gb.setLayout(self.instancia_filtro)
        gb.setFixedHeight(120)
        f = QFrame(self)
        mainLayout = QVBoxLayoutWithMargins()
        mainLayout.addWidget(gb)
        f.setLayout(mainLayout)
        f.setFixedHeight(140)
        return f

    def adiciona_botoes(self):
        actions = QWidget()
        actions_layout = QHBoxLayoutWithoutMargins()
        button_novo = QPushButton(qta.icon('fa.plus', color='black'), '&Novo')
        button_novo.clicked.connect(self.novo)
        actions_layout.addWidget(button_novo)
        button_editar = QPushButton(
            qta.icon('fa.pencil', color='black'), '&Editar')
        button_editar.clicked.connect(self.editar)
        actions_layout.addWidget(button_editar)
        button_excluir = QPushButton(
            qta.icon('fa.trash', color='black'), 'E&xcluir')
        button_excluir.clicked.connect(self.excluir)
        actions_layout.addWidget(button_excluir)

        if len(self.instancia_lista.actions()) > 0:
            for a in self.instancia_lista.actions():
                btn = QPushButton(
                    qta.icon(a['icon'], color='black'), a['label'])
                btn.clicked.connect(a['callback'])
                actions_layout.addWidget(btn)

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
            entidade = self.FORM.ENTIDADE
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
    FORM = QFormWidget

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent=parent)
        self.itemClicked.connect(self.on_click)
        self.itemDoubleClicked.connect(self.on_double_click)
        self.values = None
        self.filtros = []
        self.update_result_set()
        self.verticalHeader().hide()

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
                elif f["operator"] == "<":
                    w = (f["entity"] < f["field"].get_valor())
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
            if (isinstance(c, tuple) and
                    isinstance(c[0], peewee.ForeignKeyField)):
                label = c[1] + ' ' + label
            labels.append(title_label(label))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(labels)

    def txt_from_tuple(self, item, column_tuple):
        value = getattr(item, column_tuple[0].name)

        if isinstance(column_tuple[0], peewee.ForeignKeyField):
            fk_obj = column_tuple[0].rel_model.get_by_id(value)
            txt = str(getattr(fk_obj, column_tuple[1]))
        elif isinstance(column_tuple[0], ChoiceField):
            for v in column_tuple[0].values:
                if v['id'] == value:
                    txt = column_tuple[0].values[value][column_tuple[1]]
        elif (isinstance(column_tuple[0], peewee.DateField)
                and value is not None):
            txt = QDate(value).toString(column_tuple[1])
        elif (isinstance(column_tuple[0], peewee.DateTimeField)
                and value is not None):
            import time
            secs_since_epoch = time.mktime(value.timetuple()) * 1000
            txt = QDateTime.fromMSecsSinceEpoch(secs_since_epoch).toString(
                column_tuple[1])
        else:
            txt = value
        return txt

    def update_result_set(self):
        self.values = self.get_all_with_filter()
        self.clear()
        self.setColumnCount(len(self.columns()))
        self.setRowCount(self.values.count())
        self.set_headers()
        numRows = 0
        for item in self.values:
            i = 0
            for column in self.columns():
                if isinstance(column, tuple):
                    txt = self.txt_from_tuple(item, column)
                else:
                    txt = str(getattr(item, column.name))
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

    def actions(self):
        return []

    def on_double_click(self):
        self.abrir_formulario(self.selected().id)

    def abrir_formulario(self, id=None):
        formulario = self.FORM(id)
        formulario.buttonBox.accepted.connect(self.update_result_set)
        formulario.show()
        app.formPrincipal.add_dock(formulario.windowTitle(), object=formulario)


class QTableShow(QListShow):
    LIST = QResultTable
    FORM_FILTER = None
    TITLE = 'TABLE'

    def __init__(self):
        super(QTableShow, self).__init__()
        self.setWindowTitle(self.TITLE)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.instancia_lista.update_result_set()
        else:
            super(QTableShow, self).keyPressEvent(event)


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
