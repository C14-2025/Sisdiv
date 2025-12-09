import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print()
print("Validação Fluxo de caixa contra valores negativos")


# Importa sua classe
from src.utils.fluxo_caixa import FluxoCaixa

class TestValidadorTDD:
    """Testes TDD para validação de valores negativos"""
    
    def test_01_nao_aceitar_renda_negativa(self):
        """TESTE 1: Não deve aceitar renda mensal negativa"""
        print("1️ TESTANDO: Renda negativa deve falhar...")
        try:
            # Tenta criar com renda negativa
            fluxo = FluxoCaixa(renda_mensal=-1000)
            print(" FALHOU: Aceitou renda negativa!")
            return False
        except ValueError as e:
            print(f"PASSOU: Bloqueou renda negativa - '{e}'")
            return True
        except:
            print("Erro diferente do esperado")
            return False
    
    def test_02_nao_aceitar_despesa_negativa(self):
        """TESTE 2: Não deve aceitar despesa com valor negativo"""
        print("\n2️TESTANDO: Despesa negativa deve falhar...")
        fluxo = FluxoCaixa(renda_mensal=3000)
        
        try:
            # Tenta adicionar despesa negativa
            fluxo.adicionar_despesa_fixa("Errada", -500, 10)
            print("FALHOU: Aceitou despesa negativa!")
            return False
        except ValueError as e:
            print(f"PASSOU: Bloqueou despesa negativa - '{e}'")
            return True
        except AttributeError:
            print("Método não existe ainda - TDD funcionando!")
            return False
        except:
            print("Erro diferente")
            return False
    
    def test_03_valores_positivos_funcionam(self):
        """TESTE 3: Valores positivos devem funcionar normalmente"""
        print("\n3️TESTANDO: Valores positivos funcionam...")
        try:
            fluxo = FluxoCaixa(renda_mensal=3000)
            fluxo.adicionar_despesa_fixa("Aluguel", 1000, 10)
            print("PASSOU: Valores positivos aceitos")
            return True
        except:
            print("FALHOU: Valores positivos não funcionam")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes e mostra resultado"""
        print("\n" + "=" * 60)
        print("TDD RED: TESTES FALHAM PRIMEIRO")
        print("=" * 60)
        
        resultados = []
        
        # Executa cada teste
        resultados.append(self.test_01_nao_aceitar_renda_negativa())
        resultados.append(self.test_02_nao_aceitar_despesa_negativa())
        resultados.append(self.test_03_valores_positivos_funcionam())
        
        # Resumo
        print("\n" + "=" * 60)
        print("RESULTADO DOS TESTES:")
        print(f" Passaram: {sum(resultados)}")
        print(f" Falharam: {len(resultados) - sum(resultados)}")
        
        if sum(resultados) == len(resultados):
            print("\nTODOS OS TESTES PASSARAM!")
        else:
            print("\nALGUNS TESTES FALHARAM - Isso é ESPERADO no TDD!")
        
        print("=" * 60)
        return resultados

# Executa durante a apresentação
if __name__ == "__main__":
    testador = TestValidadorTDD()
    testador.run_all_tests()
