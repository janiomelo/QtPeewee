from qtpeewee import (
    QFormulario, QCharEdit, QFormWidget, QDateWithCalendarEdit, QTableShow,
    QResultList, QListShow, QFkComboBox, QResultTable, run, app, QSearchForm,
    QDateTimeWithCalendarEdit, BaseModel)
from peewee import (
    CharField, DateField, ForeignKeyField, fn, DateTimeField)


class PessoaJuridica(BaseModel):
    razao_social = CharField()

    def __str__(self):
        return str(self.razao_social)


class Estabelecimento(BaseModel):
    pessoa_juridica = ForeignKeyField(PessoaJuridica)


class Empregador(BaseModel):
    pessoa_juridica = ForeignKeyField(PessoaJuridica)


class PessoaFisica(BaseModel):
    nome = CharField()

    def __str__(self):
        return str(self.nome)

class Vinculo(BaseModel):
    pessoa_fisica = ForeignKeyField(PessoaFisica)
    empregador = ForeignKeyField(Empregador)
    estabelecimento = ForeignKeyField(Estabelecimento)

class PerfilCobranca(BaseModel):
    pessoa_juridica = ForeignKeyField(PessoaJuridica, null=True)
    pessoa_fisica = ForeignKeyField(PessoaFisica, null=True)


class Associado(BaseModel):
    pessoa_juridica = ForeignKeyField(PessoaJuridica, null=True)
    pessoa_fisica = ForeignKeyField(PessoaFisica, null=True)


class FormularioPF(QFormulario):
    ENTIDADE = PerfilCobranca
    TITLE = 'Editar Pessoa Física'

    def meta(self):
        return {
            'pessoa_fisica': {
                'form_new': None,
                'form_edit': None
            }
        }


class PFWidget(QFormWidget):
    FORMULARIO = FormularioPF


class PFListShow(QListShow):
    TITLE = 'Lista de pessoas físicas'
    FORM = PFWidget

    def filters(self):
        return [{
            "entity": PessoaFisica.nome,
            "type": QCharEdit,
            "operator": "%",
            "label": "Nome"
        }]

    def get_all(self):
        return PessoaFisica.select()

    def order(self):
        return PessoaFisica.nome

    def get_value(self, obj):
        return obj.nome


if __name__ == '__main__':
    PessoaFisica.create_table()
    PessoaJuridica.create_table()
    Estabelecimento.create_table()
    Empregador.create_table()
    Vinculo.create_table()
    Associado.create_table()
    PerfilCobranca.create_table()

    app.set_title('Aplicação de Exemplo')

    pfMenu = app.formPrincipal.new_menu('&Pessoas Físicas')
    app.formPrincipal.new_action(
        pfMenu, 'Pessoas &Físicas', PFListShow,
        tinytxt='Ctrl+F', tip='Consulta ao cadastro de pessoas físicas.')

    run()
