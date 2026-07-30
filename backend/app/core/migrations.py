from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _table_columns(engine: Engine, table_name: str) -> set[str]:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def ensure_cliente_crm_columns(engine: Engine) -> None:
    columns_sql = {
        "empresa": "VARCHAR(255)",
        "origem": "VARCHAR(120)",
        "observacoes": "TEXT",
    }

    existing_columns = _table_columns(engine, "clientes")
    if not existing_columns:
        return

    with engine.begin() as connection:
        for column_name, column_type in columns_sql.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE clientes ADD COLUMN {column_name} {column_type}"))

        if engine.dialect.name == "postgresql":
            for legacy_column in ("carteirinha", "convenio", "endereco"):
                if legacy_column in existing_columns:
                    connection.execute(text(f"ALTER TABLE clientes ALTER COLUMN {legacy_column} DROP NOT NULL"))
