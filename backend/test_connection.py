from sqlalchemy import text

from app.core.database import engine

try:
    with engine.connect() as connection:
        resultado = connection.execute(text("SELECT version();"))

        print("\n===================================")
        print("✅ Conexão realizada com sucesso!")
        print("===================================")

        print("\nVersão do PostgreSQL:\n")
        print(resultado.scalar())

except Exception as erro:
    print("\n❌ Erro ao conectar:")
    print(erro)