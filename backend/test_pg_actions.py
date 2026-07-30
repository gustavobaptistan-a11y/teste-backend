from sqlalchemy import text
from app.core.database import engine

def run_test():
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            # Cria tabela temporária (se não existir)
            conn.execute(text(
                "CREATE TABLE IF NOT EXISTS test_connection_table (id SERIAL PRIMARY KEY, nome TEXT)"
            ))

            # Insere um registro de teste
            conn.execute(text("INSERT INTO test_connection_table (nome) VALUES (:n)"), {"n": "teste_operacao"})

            # Consulta o último registro inserido
            result = conn.execute(text("SELECT id, nome FROM test_connection_table ORDER BY id DESC LIMIT 1"))
            row = result.fetchone()
            print("Registro inserido:", row)

            # Reverte a transação para não deixar dados no banco
            trans.rollback()
            print("Rollback executado — alterações não persistiram.")

    except Exception as e:
        print("Erro durante o teste de operações no PostgreSQL:", e)

if __name__ == '__main__':
    run_test()
