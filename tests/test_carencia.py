import pytest

from src.calculadoras.carencia import carencia

#teste unitario da carencia

class test_carencia():

    def test_da_carencia_que_deve_dar_certo(self):

        periodo_carencia = 3
        saldo_devedor = 1000
        taxa = 0.01
        dados = []
        dados=carencia(periodo_carencia,saldo_devedor,taxa)
        carencia_resultado = [
            {"parcela": 1, "prestacao": 10, "juros": 10, "amortizacao": 0, "saldo_devedor": 1000},
            {"parcela": 2, "prestacao": 10, "juros": 10, "amortizacao": 0, "saldo_devedor": 1000},
            {"parcela": 3, "prestacao": 10, "juros": 10, "amortizacao": 0, "saldo_devedor": 1000}
        ]
        assert dados == carencia_resultado

    # Suponha que sua função `carencia` está definida em outro arquivo ou no mesmo.
    def carencia(periodo_carencia, saldo_devedor, taxa):
        if periodo_carencia < 0:
            # A função lança (raise) a exceção quando a condição é atendida.
            raise ValueError("Período de carência não pode ser negativo")
        # ... Lógica da sua função continua aqui ...
        return saldo_devedor


    def test_da_carencia_que_deve_dar_errado_por_causa_periodo_de_carencia(self):
        # 1. Use `with pytest.raises()` para indicar que uma exceção é esperada.
        # 2. Passe o tipo de exceção que você espera, neste caso, `ValueError`.
        # 3. Use o parâmetro `match` para verificar se a mensagem do erro é a correta.
        with pytest.raises(ValueError, match="Período de carência não pode ser negativo"):
            # O código que deve causar o erro é colocado aqui dentro.
            periodo_carencia = -3
            saldo_devedor = 1000
            taxa = 0.01
            carencia(periodo_carencia, saldo_devedor, taxa)

    def test_da_carencia_que_deve_dar_errado_por_causa_saldo_do_devedor(self):
        # 1. Use `with pytest.raises()` para indicar que uma exceção é esperada.
        # 2. Passe o tipo de exceção que você espera, neste caso, `ValueError`.
        # 3. Use o parâmetro `match` para verificar se a mensagem do erro é a correta.
        with pytest.raises(ValueError, match="Saldo devedor deve ser positivo"):
            # O código que deve causar o erro é colocado aqui dentro.
            periodo_carencia = 3
            saldo_devedor = -1000
            taxa = 0.01
            carencia(periodo_carencia, saldo_devedor, taxa)

    def test_da_carencia_que_deve_dar_errado_por_causa_da_taxa(self):
        # 1. Use `with pytest.raises()` para indicar que uma exceção é esperada.
        # 2. Passe o tipo de exceção que você espera, neste caso, `ValueError`.
        # 3. Use o parâmetro `match` para verificar se a mensagem do erro é a correta.
        with pytest.raises(ValueError, match="Taxa não pode ser negativa"):
            # O código que deve causar o erro é colocado aqui dentro.
            periodo_carencia = 3
            saldo_devedor = 1000
            taxa = -0.01
            carencia(periodo_carencia, saldo_devedor, taxa)