from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.cache import (
    DASHBOARD_METRICS_CACHE_KEY,
    DASHBOARD_METRICS_TTL_SECONDS,
    get_json_cache,
    set_json_cache,
)
from app.core.database import get_db
from app.models import ClienteModel, LeadModel, UsuarioModel

router = APIRouter(prefix="/dashboard", tags=["Dashboard Comercial"])


@router.get("/metricas")
def obter_metricas_comerciais(
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Retorna indicadores consolidados do comercial."""
    cached_metrics = get_json_cache(DASHBOARD_METRICS_CACHE_KEY)
    if cached_metrics is not None:
        return cached_metrics

    total_clientes = db.query(func.count(ClienteModel.id)).filter(ClienteModel.ativo.is_(True)).scalar() or 0
    total_leads = db.query(func.count(LeadModel.id)).scalar() or 0
    valor_total_pipeline = db.query(func.coalesce(func.sum(LeadModel.valor), 0)).scalar() or 0

    etapas = (
        db.query(LeadModel.etapa, func.count(LeadModel.id))
        .group_by(LeadModel.etapa)
        .order_by(LeadModel.etapa.asc())
        .all()
    )
    etapas_contagem = {etapa: quantidade for etapa, quantidade in etapas}

    leads_fechados = etapas_contagem.get("Fechado", 0)
    taxa_conversao = (leads_fechados / total_leads * 100) if total_leads > 0 else 0.0

    metricas = {
        "clientes": {
            "total_ativos": total_clientes,
        },
        "pipeline": {
            "total_oportunidades": total_leads,
            "valor_total_estimado": float(valor_total_pipeline),
            "distribuicao_por_etapa": etapas_contagem,
        },
        "desempenho": {
            "taxa_conversao_percentual": round(taxa_conversao, 2),
        },
    }
    set_json_cache(DASHBOARD_METRICS_CACHE_KEY, metricas, DASHBOARD_METRICS_TTL_SECONDS)
    return metricas
