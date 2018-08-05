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

    def __str__(self):
        if self.pessoa_fisica is not None:
            return self.pessoa_fisica.nome
        return self.pessoa_juridica.razao_social


class FormularioPF(QFormulario):
    ENTIDADE = PessoaFisica
    TITLE = 'Editar Pessoa Física'


class FormularioPJ(QFormulario):
    ENTIDADE = PessoaJuridica
    TITLE = 'Editar Pessoa Jurídica'


class FormularioAssociado(QFormulario):
    ENTIDADE = Associado
    TITLE = 'Editar Associado'

    def meta(self):
        return {
            'pessoa_fisica': {
                'form_new': FormularioPF,
                'form_edit': FormularioPF
            },
            'pessoa_juridica': {
                'form_new': FormularioPJ,
                'form_edit': FormularioPJ
            }
        }


class AssociadoListShow(QListShow):
    TITLE = 'Lista de associados'
    FORM = FormularioAssociado

    def get_value(self, obj):
        return str(obj)

    def get_all(self):
        return Associado.select()


class PJListShow(QListShow):
    TITLE = 'Lista de pessoas jurídicas'
    FORM = FormularioPJ

    def get_all(self):
        return PessoaJuridica.select()

    def get_value(self, obj):
        return obj.razao_social


class PFListShow(QListShow):
    TITLE = 'Lista de pessoas físicas'
    FORM = FormularioPF

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

    cadastroMenu = app.formPrincipal.new_menu('&Cadastro')
    app.formPrincipal.new_action(
        cadastroMenu, 'Pessoas &Físicas', PFListShow,
        tinytxt='Ctrl+F', tip='Consulta ao cadastro de pessoas físicas.'
    )

    app.formPrincipal.new_action(
        cadastroMenu, 'Pessoas &Jurídicas', PJListShow,
        tinytxt='Ctrl+J', tip='Consulta ao cadastro de pessoas jurídicas.'
    )

    app.formPrincipal.new_action(
        cadastroMenu, '&Associados', AssociadoListShow,
        tinytxt='Ctrl+A'
    )

    run()
