import pytest
from unittest.mock import patch
# Ajuste o caminho de importação conforme a sua estrutura de diretórios
from src.calculadoras.calcular_sam import calcular_sam

# --- Teste de Validação (Erros) ---

@pytest.mark.parametrize("valor, taxa, prazo, carencia, expected_error", [
    # Valor inválido
    (0, 0.01, 10, 0, "Valor do empréstimo deve ser positivo"),
    (-100, 0.01, 10, 0, "Valor do empréstimo deve ser positivo"),
    # Prazo inválido
    (1000, 0.01, 0, 0, "Prazo deve ser positivo"),
    (1000, 0.01, -5, 0, "Prazo deve ser positivo"),
    # Taxa inválida
    (1000, -0.01, 10, 0, "Taxa não pode ser negativa"),
    # Carência inválida
    (1000, 0.01, 10, -1, "Período de carência não pode ser negativo"),
    # Carência maior ou igual ao prazo de amortização
    (1000, 0.01, 3, 3, "Período de carência deve ser menor que o prazo de amortização"),
    (1000, 0.01, 3, 4, "Período de carência deve ser menor que o prazo de amortização"),
])
def test_calcular_sam_validacao_erros(valor, taxa, prazo, carencia, expected_error):
    """Testa se a função levanta ValueError para dados de entrada inválidos."""
    with pytest.raises(ValueError) as excinfo:
        calcular_sam(valor, taxa, prazo, carencia)
    assert expected_error in str(excinfo.value)

# --------------------------------------------------------------------------------

# --- Testes de Casos Base e de Borda (Sem Carência) ---

def test_calcular_sam_caso_base_sem_carencia():
    """Testa o SAM básico (Valor 1000, Taxa 1%, Prazo 5, Sem Carência)."""
    valor = 1000.00
    taxa = 0.01  # 1%
    prazo = 5

    resultado = calcular_sam(valor, taxa, prazo, 0)
    assert len(resultado) == prazo

    juros_mensal = round(valor * taxa, 2) # 10.00

    # Parcelas 1 a 4 (só juros)
    for i in range(prazo - 1):
        parcela = resultado[i]
        assert parcela["parcela"] == i + 1
        assert parcela["prestacao"] == pytest.approx(juros_mensal)
        assert parcela["juros"] == pytest.approx(juros_mensal)
        assert parcela["amortizacao"] == 0.00
        assert parcela["saldo_devedor"] == valor

    # Última parcela (juros + principal)
    ultima = resultado[-1]
    assert ultima["parcela"] == 5
    assert ultima["prestacao"] == pytest.approx(juros_mensal + valor)
    assert ultima["amortizacao"] == pytest.approx(valor)
    assert ultima["saldo_devedor"] == 0.00

def test_calcular_sam_prazo_1():
    """Testa o SAM para um único período (prazo=1), onde a quitação é imediata."""
    valor = 500
    taxa = 0.10  # 10%
    prazo = 1

    resultado = calcular_sam(valor, taxa, prazo, 0)
    assert len(resultado) == 1

    juros_mensal = round(valor * taxa, 2) # 50.00

    # Única parcela (deve ser a quitação total)
    unica_parcela = resultado[0]
    assert unica_parcela["parcela"] == 1
    assert unica_parcela["prestacao"] == pytest.approx(juros_mensal + valor)
    assert unica_parcela["juros"] == pytest.approx(juros_mensal)
    assert unica_parcela["amortizacao"] == pytest.approx(valor)
    assert unica_parcela["saldo_devedor"] == 0.00

def test_calcular_sam_taxa_zero():
    """Testa o SAM com taxa de juros zero (apenas o principal na última parcela)."""
    valor = 2000
    taxa = 0.00
    prazo = 4

    resultado = calcular_sam(valor, taxa, prazo, 0)
    assert len(resultado) == prazo

    # Parcelas 1 a 3 (juros zero)
    for i in range(prazo - 1):
        parcela = resultado[i]
        assert parcela["prestacao"] == 0.00
        assert parcela["juros"] == 0.00
        assert parcela["amortizacao"] == 0.00
        assert parcela["saldo_devedor"] == valor

    # Última parcela (principal)
    ultima = resultado[-1]
    assert ultima["parcela"] == 4
    assert ultima["prestacao"] == pytest.approx(valor)
    assert ultima["juros"] == 0.00
    assert ultima["amortizacao"] == pytest.approx(valor)
    assert ultima["saldo_devedor"] == 0.00

# --------------------------------------------------------------------------------

# --- Testes de Integração com Mock (Carência) ---

# O patch deve referenciar onde a função aplicar_carencia é usada (dentro do módulo calcular_sam)
@patch("src.calculadoras.calcular_sam.aplicar_carencia")
def test_calcular_sam_com_carencia_aplicada(mock_carencia):
    """
    Testa se o cálculo do SAM aplica corretamente a carência,
    simulando a função aplicar_carencia com mock.
    """
    valor = 1000
    taxa = 0.05
    prazo = 3
    periodo_carencia = 2

    # Resultado simulado da função aplicar_carencia (Juros = 1000 * 0.05 = 50.00)
    carencia_resultado = [
        {"parcela": 1, "prestacao": 50.00, "juros": 50.00, "amortizacao": 0.00, "saldo_devedor": 1000.00},
        {"parcela": 2, "prestacao": 50.00, "juros": 50.00, "amortizacao": 0.00, "saldo_devedor": 1000.00},
    ]
    mock_carencia.return_value = carencia_resultado

    resultado = calcular_sam(valor, taxa, prazo, periodo_carencia, temcarencia=True)

    # Verifica se a função de carência foi chamada
    mock_carencia.assert_called_once_with(periodo_carencia, valor, taxa)

    # O número total de parcelas deve incluir carência + prazo (2 + 3 = 5)
    assert len(resultado) == periodo_carencia + prazo

    # As duas primeiras parcelas (carência)
    assert resultado[:periodo_carencia] == carencia_resultado

    juros_mensal = round(valor * taxa, 2) # 50.00

    # Parcelas 3 e 4 (SAM - só juros)
    for i in range(periodo_carencia, len(resultado) - 1):
        parcela = resultado[i]
        # O número da parcela (3 e 4)
        assert parcela["parcela"] == i + 1
        assert parcela["prestacao"] == pytest.approx(juros_mensal)
        assert parcela["amortizacao"] == 0.00
        assert parcela["saldo_devedor"] == valor

    # Última parcela (SAM - quitação total)
    ultima = resultado[-1]
    assert ultima["parcela"] == 5 # 2 + 3
    assert ultima["prestacao"] == pytest.approx(juros_mensal + valor)
    assert ultima["amortizacao"] == pytest.approx(valor)
    assert ultima["saldo_devedor"] == 0.00


# O patch deve referenciar onde a função aplicar_carencia é usada (dentro do módulo calcular_sam)
@patch("src.calculadoras.calcular_sam.aplicar_carencia")
def test_calcular_sam_sem_carencia_nao_chama_mock(mock_carencia):
    """
    Testa se o cálculo do SAM funciona normalmente sem carência (temcarencia=False)
    e se a função aplicar_carencia não é chamada.
    """
    valor = 1000
    taxa = 0.05
    prazo = 3
    periodo_carencia = 2 # Valor de carência existe, mas é ignorado

    resultado = calcular_sam(valor, taxa, prazo, periodo_carencia, temcarencia=False)

    # Garante que a função de carência não foi chamada
    mock_carencia.assert_not_called()

    # Deve ter apenas as 3 parcelas do prazo
    assert len(resultado) == prazo

    juros_mensal = round(valor * taxa, 2) # 50.00

    # As duas primeiras parcelas do prazo: apenas juros
    for parcela in resultado[:-1]:
        assert parcela["prestacao"] == pytest.approx(juros_mensal)
        assert parcela["juros"] == pytest.approx(juros_mensal)
        assert parcela["amortizacao"] == 0
        assert parcela["saldo_devedor"] == valor

    # Última parcela do prazo: quita o valor principal
    ultima = resultado[-1]
    assert ultima["prestacao"] == pytest.approx(juros_mensal + valor)
    assert ultima["amortizacao"] == valor
    assert ultima["saldo_devedor"] == 0.00
    #
    def test_calcular_sam_saldo_consistente():
        """Saldo devedor nunca deve aumentar durante o cálculo."""
        resultado = calcular_sam(1000, 0.05, 5, 0)
        saldos = [p["saldo_devedor"] for p in resultado]
        assert all(saldos[i] >= saldos[i+1] for i in range(len(saldos) - 1))
    def test_calcular_sam_prazo_longo():
        """Testa se o SAM suporta prazos longos sem erro."""
        resultado = calcular_sam(1000, 0.05, 120, 0)  # 10 anos
        assert len(resultado) == 120
        assert resultado[-1]["saldo_devedor"] == 0
    def test_calcular_sam_soma_amortizacoes():
        """A soma das amortizações deve ser igual ao valor inicial do empréstimo."""
        valor = 1000
        resultado = calcular_sam(valor, 0.05, 6, 0)
        soma_amortizacoes = sum(p["amortizacao"] for p in resultado)
        assert soma_amortizacoes == pytest.approx(valor)
    def test_calcular_sam_soma_juros():
        """A soma dos juros deve ser prazo * valor * taxa no SAM."""
        valor = 1000
        taxa = 0.05
        prazo = 4
        resultado = calcular_sam(valor, taxa, prazo, 0)
        soma_juros = sum(p["juros"] for p in resultado)
        assert soma_juros == pytest.approx(prazo * valor * taxa)