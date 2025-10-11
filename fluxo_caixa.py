import json
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- IMPORTS DE FUNÇÕES AUXILIARES ---
from calcular_sac import calcular_sac
from calcular_price import calcular_price

# --- CONFIGURAÇÃO DE CAMINHO ---
DIRETORIO_PROJETO = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_STATIC = os.path.join(DIRETORIO_PROJETO, 'static')
os.makedirs(DIRETORIO_STATIC, exist_ok=True)


class FluxoCaixa:
    """Gerencia o fluxo de caixa pessoal mensal e gera projeções financeiras."""
    
    def __init__(self, renda_mensal: float):
        self.renda_mensal = renda_mensal
        self.entradas_extras = []
        self.despesas_fixas = []
        self.despesas_variaveis = []
        self.dividas = []
    
    def adicionar_despesa_fixa(self, descricao: str, valor: float, dia_vencimento: int):
        self.despesas_fixas.append({"descricao": descricao, "valor": valor, "dia_vencimento": dia_vencimento, "tipo": "despesa_fixa"})
    
    def adicionar_despesa_variavel(self, descricao: str, valor: float, mes: int, ano: int):
        self.despesas_variaveis.append({"descricao": descricao, "valor": valor, "mes": mes, "ano": ano, "tipo": "despesa_variavel"})
    
    def adicionar_entrada_extra(self, descricao: str, valor: float, mes: int, ano: int):
        self.entradas_extras.append({"descricao": descricao, "valor": valor, "mes": mes, "ano": ano, "tipo": "entrada_extra"})
    
    def vincular_divida(self, nome_divida: str, parcelas: List[Dict], mes_inicio: int, ano_inicio: int):
        if not parcelas:
             raise ValueError(f"A dívida '{nome_divida}' não possui parcelas.")
        self.dividas.append({"nome": nome_divida, "parcelas": parcelas, "mes_inicio": mes_inicio, "ano_inicio": ano_inicio})

    def _calcular_meses_diferenca(self, mes1: int, ano1: int, mes2: int, ano2: int) -> int:
        return (ano2 - ano1) * 12 + (mes2 - mes1)

    def calcular_fluxo_mensal(self, mes: int, ano: int) -> Dict[str, Any]:
        total_entradas = self.renda_mensal
        entradas_detalhadas = [{"descricao": "Salário/Renda", "valor": self.renda_mensal}]
        
        # Adicionar entradas extras do mês
        for entrada in self.entradas_extras:
            if entrada["mes"] == mes and entrada["ano"] == ano:
                total_entradas += entrada["valor"]
                entradas_detalhadas.append(entrada)
        
        # Calcular despesas fixas (todas ocorrem todo mês)
        total_despesas_fixas = sum(d["valor"] for d in self.despesas_fixas)
        
        # Calcular despesas variáveis do mês específico
        despesas_variaveis_mes = [d for d in self.despesas_variaveis if d["mes"] == mes and d["ano"] == ano]
        total_despesas_variaveis = sum(d["valor"] for d in despesas_variaveis_mes)
        
        # Calcular parcelas de dívidas do mês
        parcelas_mes = []
        total_parcelas_dividas = 0
        for divida in self.dividas:
            meses_desde_inicio = self._calcular_meses_diferenca(divida["mes_inicio"], divida["ano_inicio"], mes, ano)
            if 0 <= meses_desde_inicio < len(divida["parcelas"]):
                parcela_atual = divida["parcelas"][meses_desde_inicio]
                parcelas_mes.append({
                    "nome_divida": divida["nome"], 
                    "parcela_numero": parcela_atual["parcela"],
                    "valor": parcela_atual["prestacao"], 
                    "juros": parcela_atual["juros"],
                    "amortizacao": parcela_atual["amortizacao"]
                })
                total_parcelas_dividas += parcela_atual["prestacao"]
        
        # Totais
        total_despesas = total_despesas_fixas + total_despesas_variaveis + total_parcelas_dividas
        saldo_mensal = total_entradas - total_despesas
        
        # Percentuais
        percentual_dividas = (total_parcelas_dividas / total_entradas * 100) if total_entradas > 0 else 0
        percentual_despesas_fixas = (total_despesas_fixas / total_entradas * 100) if total_entradas > 0 else 0
        percentual_despesas_variaveis = (total_despesas_variaveis / total_entradas * 100) if total_entradas > 0 else 0
        
        return {
            "mes": mes, 
            "ano": ano, 
            "entradas": {"total": total_entradas, "detalhamento": entradas_detalhadas},
            "despesas": {
                "fixas": {"total": total_despesas_fixas, "percentual": percentual_despesas_fixas, "detalhamento": self.despesas_fixas},
                "variaveis": {"total": total_despesas_variaveis, "percentual": percentual_despesas_variaveis, "detalhamento": despesas_variaveis_mes},
                "dividas": {"total": total_parcelas_dividas, "percentual": percentual_dividas, "detalhamento": parcelas_mes},
                "total": total_despesas
            },
            "saldo_mensal": saldo_mensal, 
            "status": "positivo" if saldo_mensal >= 0 else "negativo"
        }
    
    def gerar_projecao(self, meses: int, mes_inicio: int = None, ano_inicio: int = None) -> List[Dict]:
        if mes_inicio is None or ano_inicio is None:
            agora = datetime.now()
            mes_inicio = agora.month
            ano_inicio = agora.year
        
        projecao = []
        mes_atual = mes_inicio
        ano_atual = ano_inicio
        
        for _ in range(meses):
            fluxo = self.calcular_fluxo_mensal(mes_atual, ano_atual)
            projecao.append(fluxo)
            
            # Avançar para o próximo mês
            mes_atual += 1
            if mes_atual > 12:
                mes_atual = 1
                ano_atual += 1
        
        return projecao
    
    def gerar_relatorio_impacto_dividas(self, meses: int = 12) -> Dict[str, Any]:
        projecao = self.gerar_projecao(meses)
        
        total_gasto_dividas = sum(p["despesas"]["dividas"]["total"] for p in projecao)
        total_entradas = sum(p["entradas"]["total"] for p in projecao)
        media_percentual_comprometimento = sum(p["despesas"]["dividas"]["percentual"] for p in projecao) / len(projecao)
        
        meses_negativos = [p for p in projecao if p["saldo_mensal"] < 0]
        meses_positivos = [p for p in projecao if p["saldo_mensal"] >= 0]
        
        impacto_por_divida = {}
        for divida in self.dividas:
            nome = divida["nome"]
            parcelas = divida["parcelas"]
            parcelas_no_periodo = [p for i, p in enumerate(parcelas) if i < meses]
            
            total_divida_paga = sum(p["prestacao"] for p in parcelas_no_periodo)
            total_juros_pago = sum(p["juros"] for p in parcelas_no_periodo)
            
            impacto_por_divida[nome] = {
                "total_pago_no_periodo": round(total_divida_paga, 2),
                "total_juros_no_periodo": round(total_juros_pago, 2),
                "numero_parcelas_restantes": len(parcelas) - len(parcelas_no_periodo),
                "percentual_juros_pago_periodo": round((total_juros_pago / total_divida_paga * 100), 2) if total_divida_paga > 0 else 0
            }
        
        recomendacoes = self._gerar_recomendacoes(media_percentual_comprometimento, meses_negativos, meses_positivos)
        alertas = self._gerar_alertas(projecao)
        
        return {
            "data_geracao": datetime.now().isoformat(),
            "periodo_analisado": f"{meses} meses",
            "resumo_geral": {
                "total_entradas": round(total_entradas, 2),
                "total_gasto_dividas": round(total_gasto_dividas, 2),
                "percentual_comprometimento_medio": round(media_percentual_comprometimento, 2),
                "meses_com_saldo_positivo": len(meses_positivos),
                "meses_com_saldo_negativo": len(meses_negativos),
                "saldo_total_periodo": round(sum(p["saldo_mensal"] for p in projecao), 2)
            },
            "impacto_por_divida": impacto_por_divida,
            "projecao_mensal": projecao,
            "recomendacoes": recomendacoes,
            "alertas": alertas
        }

    def _gerar_recomendacoes(self, percentual_comprometimento: float, meses_negativos: List, meses_positivos: List) -> List[str]:
        recomendacoes = []
        
        if percentual_comprometimento > 30:
            recomendacoes.append("⚠️ CRÍTICO: Suas dívidas comprometem mais de 30% da renda. Considere renegociação imediata.")
        elif percentual_comprometimento > 20:
            recomendacoes.append("⚡ ATENÇÃO: Comprometimento acima de 20%. Evite novas dívidas e foque na quitação.")
        else:
            recomendacoes.append("✅ Comprometimento saudável. Continue monitorando e investindo.")
        
        if len(meses_negativos) > len(meses_positivos):
            recomendacoes.append("🚨 Muitos meses com saldo negativo. Revise despesas e considere aumentar renda.")
        elif len(meses_negativos) > 0:
            recomendacoes.append(f"📉 {len(meses_negativos)} mês(es) com saldo negativo. Planeje-se para esses períodos.")
        else:
            recomendacoes.append("🎉 Excelente! Todos os meses com saldo positivo. Considere investir o excedente.")
        
        return recomendacoes
    
    def _gerar_alertas(self, projecao: List[Dict]) -> List[Dict]:
        alertas = []
        for mes in projecao:
            if mes["saldo_mensal"] < -500:  # Déficit significativo
                alertas.append({
                    "tipo": "saldo_negativo_grave",
                    "severidade": "alta",
                    "mes": f"{mes['mes']}/{mes['ano']}",
                    "mensagem": f"Déficit grave de R$ {abs(mes['saldo_mensal']):.2f}"
                })
            elif mes["saldo_mensal"] < 0:
                alertas.append({
                    "tipo": "saldo_negativo",
                    "severidade": "media",
                    "mes": f"{mes['mes']}/{mes['ano']}",
                    "mensagem": f"Déficit de R$ {abs(mes['saldo_mensal']):.2f}"
                })
            
            if mes["despesas"]["dividas"]["percentual"] > 40: 
                alertas.append({
                    "tipo": "comprometimento_muito_alto",
                    "severidade": "alta",
                    "mes": f"{mes['mes']}/{mes['ano']}",
                    "mensagem": f"Dívidas comprometem {mes['despesas']['dividas']['percentual']:.1f}% da renda"
                })
            elif mes["despesas"]["dividas"]["percentual"] > 30:
                alertas.append({
                    "tipo": "comprometimento_alto",
                    "severidade": "media",
                    "mes": f"{mes['mes']}/{mes['ano']}",
                    "mensagem": f"Dívidas comprometem {mes['despesas']['dividas']['percentual']:.1f}% da renda"
                })
        return alertas


def _gerar_grafico_fluxo_mensal(projecao: List[Dict], nome_arquivo: str):
    """Gera um gráfico de linhas visualizando o fluxo de caixa projetado."""
    df = pd.DataFrame(projecao)
    df['data'] = df.apply(lambda row: f"{row['mes']:02d}/{str(row['ano'])[-2:]}", axis=1)
    df['total_entradas'] = df['entradas'].apply(lambda x: x['total'])
    df['total_despesas'] = df['despesas'].apply(lambda x: x['total'])
    df['saldo_mensal'] = df['saldo_mensal']

    plt.figure(figsize=(14, 8))
    
    # Criar subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfico 1: Entradas vs Despesas
    ax1.plot(df['data'], df['total_entradas'], marker='o', label='Total Entradas', color='tab:blue', linewidth=3)
    ax1.plot(df['data'], df['total_despesas'], marker='s', label='Total Despesas', color='tab:red', linewidth=2)
    ax1.set_title('Projeção Mensal - Entradas vs Despesas (12 meses)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Valores (R$)', fontsize=12)
    ax1.grid(axis='y', linestyle=':', alpha=0.7)
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Saldo Mensal
    colors = ['green' if x >= 0 else 'red' for x in df['saldo_mensal']]
    bars = ax2.bar(df['data'], df['saldo_mensal'], color=colors, alpha=0.7)
    ax2.axhline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_title('Saldo Mensal Líquido', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Mês/Ano', fontsize=12)
    ax2.set_ylabel('Saldo (R$)', fontsize=12)
    ax2.grid(axis='y', linestyle=':', alpha=0.7)
    ax2.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, df['saldo_mensal']):
        height = bar.get_height()
        if valor >= 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'R$ {valor:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='green')
        else:
            ax2.text(bar.get_x() + bar.get_width()/2., height - 150,
                    f'R$ {valor:.0f}', ha='center', va='top', fontsize=9, fontweight='bold', color='red')
    
    plt.tight_layout()
    
    # Salvar gráfico
    caminho_completo = os.path.join(DIRETORIO_STATIC, nome_arquivo)
    plt.savefig(caminho_completo, dpi=300, bbox_inches='tight')
    plt.close()
    
    link_frontend = f"/static/{nome_arquivo}"
    print(f"✅ Gráfico gerado com sucesso no caminho: {caminho_completo}")
    print(f"   => Acessível pelo Frontend em: {link_frontend}")


def exemplo_uso_com_grafico():
    """Cria uma simulaçãocom valores médios do Brasil 2024."""
    
    fluxo = FluxoCaixa(renda_mensal=3200.00)  # Salário médio
    
    # DESPESAS FIXAS (valores mensais)
    fluxo.adicionar_despesa_fixa("Aluguel", 900.00, 5)           # Aluguel
    fluxo.adicionar_despesa_fixa("Condomínio", 200.00, 10)       # Condomínio básico
    fluxo.adicionar_despesa_fixa("Energia Elétrica", 120.00, 15) # Consumo moderado
    fluxo.adicionar_despesa_fixa("Água e Esgoto", 60.00, 12)     # Tarifa média
    fluxo.adicionar_despesa_fixa("Internet", 90.00, 8)           # Banda larga
    fluxo.adicionar_despesa_fixa("Plano de Saúde", 300.00, 20)   # Plano básico
    fluxo.adicionar_despesa_fixa("Transporte", 250.00, 25)       # Ônibus/combustível
    fluxo.adicionar_despesa_fixa("Alimentação", 800.00, 1)       # Mercado básico
    fluxo.adicionar_despesa_fixa("Educação", 200.00, 5)          # Escola/material
    
    # DESPESAS VARIÁVEIS (ocorrem em meses específicos)
    fluxo.adicionar_despesa_variavel("IPVA", 600.00, mes=1, ano=2026)           # IPVA parcelado
    fluxo.adicionar_despesa_variavel("Material Escolar", 300.00, mes=2, ano=2026) 
    fluxo.adicionar_despesa_variavel("Manutenção Veicular", 400.00, mes=6, ano=2026)
    fluxo.adicionar_despesa_variavel("Vestuário", 200.00, mes=4, ano=2026)      # Roupas básicas
    
    # ENTRADAS EXTRAS
    fluxo.adicionar_entrada_extra("13º Salário", 3200.00, mes=12, ano=2025)
    fluxo.adicionar_entrada_extra("Férias", 2133.00, mes=7, ano=2026)  # 2/3 do salário
    fluxo.adicionar_entrada_extra("Bonus", 800.00, mes=6, ano=2026)    # Bonus
    
    # DÍVIDAS
    divida_carro = calcular_sac(valor=25000, taxa=0.015, prazo=36, periodo_carencia=0)
    fluxo.vincular_divida("Financiamento Carro Popular", divida_carro, mes_inicio=1, ano_inicio=2025)

    divida_consignado = calcular_price(valor=8000, taxa=0.022, prazo=24, carencia=0)
    fluxo.vincular_divida("Empréstimo Consignado", divida_consignado, mes_inicio=3, ano_inicio=2025)
    
    divida_eletro = calcular_price(valor=2000, taxa=0.029, prazo=10, carencia=0)
    fluxo.vincular_divida("Eletrodomésticos", divida_eletro, mes_inicio=5, ano_inicio=2025)
    
    # Gerar relatório
    relatorio = fluxo.gerar_relatorio_impacto_dividas(meses=12)
    
    # Exibir resumo
    print(f"\n📊 RESUMO DA PROJEÇÃO:")
    print(f"   Renda Mensal: R$ {fluxo.renda_mensal:,.2f}")
    print(f"   Meses Positivos: {relatorio['resumo_geral']['meses_com_saldo_positivo']}")
    print(f"   Meses Negativos: {relatorio['resumo_geral']['meses_com_saldo_negativo']}")
    print(f"   Saldo Total do Período: R$ {relatorio['resumo_geral']['saldo_total_periodo']:,.2f}")
    print(f"   Comprometimento Médio com Dívidas: {relatorio['resumo_geral']['percentual_comprometimento_medio']:.1f}%")
    
    # Gerar gráfico
    nome_grafico = "fluxo_caixa_projecao_exemplo.png"
    _gerar_grafico_fluxo_mensal(relatorio['projecao_mensal'], nome_grafico)
    
    return relatorio


if __name__ == "__main__":
    print("=" * 70)
    print("           RELATÓRIO FINANCEIRO - PERFIL EXEMPLO")
    print("=" * 70)
    
    try:
        relatorio = exemplo_uso_com_grafico()
        
        print(f"\n✅ Simulação concluída com sucesso!")
        print(f"📈 {relatorio['resumo_geral']['meses_com_saldo_positivo']} meses com saldo POSITIVO")
        print(f"📉 {relatorio['resumo_geral']['meses_com_saldo_negativo']} meses com saldo negativo")
        print(f"💰 Saldo acumulado: R$ {relatorio['resumo_geral']['saldo_total_periodo']:,.2f}")
        
        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in relatorio['recomendacoes']:
            print(f"   • {rec}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()