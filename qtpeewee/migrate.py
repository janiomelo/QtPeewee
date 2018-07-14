from example import Cliente, Funcionario


def up():
    Cliente.create_table()
    Funcionario.create_table()
