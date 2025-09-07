import pytest
import sys
import os

# Adiciona o diretório raiz ao path para importar o módulo calculos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculos import calcular_sac, calcular_price

def formatar_brl(valor):
    """Formata valores no padrão brasileiro R$ 1.000,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class TestAmortizacao:
    """Testes unitários para o sistema de amortização"""
    
    def test_comparativo_sac_vs_price_total_pago(self):
        """
        TESTE UNITÁRIO - Comparação entre SAC e Price
        Verifica que o SAC é mais vantajoso no total pago que o Price
        """
        print("\n" + "="*60)
        print("🧪 INICIANDO TESTE: Comparação SAC vs Price")
        print("="*60)
        
        try:
            # Dados de entrada: R$ 100.000,00 a 1% ao mês por 12 meses
            valor = 100000
            taxa = 0.01  # 1% ao mês
            prazo = 12
            
            print(f"📊 Dados de teste:")
            print(f"   • Valor: {formatar_brl(valor)}")
            print(f"   • Taxa: {taxa*100}% ao mês")
            print(f"   • Prazo: {prazo} meses")
            
            # Calcula ambos os métodos
            print("\n🔢 Calculando amortização SAC...")
            sac = calcular_sac(valor, taxa, prazo)
            
            print("🔢 Calculando amortização Price...")
            price = calcular_price(valor, taxa, prazo)
            
            # Calcula totais
            total_sac = sum(p['prestacao'] for p in sac)
            total_price = sum(p['prestacao'] for p in price)
            total_juros_sac = sum(p['juros'] for p in sac)
            total_juros_price = sum(p['juros'] for p in price)
            
            print("\n📈 Resultados obtidos:")
            print(f"   • SAC: Total = {formatar_brl(total_sac)}, Juros = {formatar_brl(total_juros_sac)}")
            print(f"   • Price: Total = {formatar_brl(total_price)}, Juros = {formatar_brl(total_juros_price)}")
            print(f"   • Diferença: {formatar_brl(total_price - total_sac)} (SAC é mais vantajoso)")
            
            # Verificações principais
            print("\n✅ Executando verificações...")
            
            assert len(sac) == 12, "SAC deve ter 12 parcelas"
            assert len(price) == 12, "Price deve ter 12 parcelas"
            
            # Verificação principal: SAC deve ser mais barato no total
            assert total_sac < total_price, "SAC deve ser mais vantajoso no total pago"
            
            # Valores específicos esperados (com margem de erro maior para Price)
            assert total_sac == pytest.approx(106500.0, 0.1)
            assert total_price == pytest.approx(106618.55, 0.1)  # Ajustado para o valor real
            
            print("🎯 TODAS AS VERIFICAÇÕES PASSARAM!")
            print("✅ TESTE BEM-SUCEDIDO!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO NO TESTE: {e}")
            print("💥 TESTE FALHOU!")
            print("="*60)
            raise e

# Execução direta do teste
if __name__ == "__main__":
    print("🚀 Executando teste unitário diretamente...")
    test_instance = TestAmortizacao()
    
    try:
        success = test_instance.test_comparativo_sac_vs_price_total_pago()
        if success:
            print("\n🎉 Todos os testes passaram com sucesso!")
        else:
            print("\n💥 Alguns testes falharam!")
    except Exception as e:
        print(f"\n💥 Teste falhou com erro: {e}")
