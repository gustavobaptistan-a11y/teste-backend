from fastapi import APIRouter
from app.api.clientes import banco_de_clientes_falso
from app.api.kanban import banco_de_leads_falso

router = APIRouter(prefix="/dashboard", tags=["Dashboard Comercial"])

@router.get("/metricas")
def obter_metricas_comerciais():
    """
    Retorna os indicadores consolidados para o Dashboard Comercial:
    - Total de clientes cadastrados / ativos
    - Volume total e financeiro de oportunidades no Kanban
    - Métricas separadas por etapa do funil de vendas
    """
    # 1. Métricas de Clientes
    total_clientes = len(banco_de_clientes_falso)
    
    # 2. Métricas do Kanban / Pipeline de Vendas
    total_leads = len(banco_de_leads_falso)
    valor_total_pipeline = sum(lead["valor"] for lead in banco_de_leads_falso)
    
    # Contagem de leads por etapa do funil
    etapas_contagem = {}
    for lead in banco_de_leads_falso:
        etapa = lead["etapa"]
        etapas_contagem[etapa] = etapas_contagem.get(etapa, 0) + 1

    # 3. Cálculo de Conversão Simples (Exemplo: Leads na etapa "Fechado" / Total de Leads)
    leads_fechados = etapas_contagem.get("Fechado", 0)
    taxa_conversao = (leads_fechados / total_leads * 100) if total_leads > 0 else 0.0

    return {
        "clientes": {
            "total_ativos": total_clientes
        },
        "pipeline": {
            "total_oportunidades": total_leads,
            "valor_total_estimado": valor_total_pipeline,
            "distribuicao_por_etapa": etapas_contagem
        },
        "desempenho": {
            "taxa_conversao_percentual": round(taxa_conversao, 2)
        }
    }