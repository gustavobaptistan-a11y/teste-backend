import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_lifeline.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("SQL_ECHO", "false")

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_lifeline.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    return TestClient(app)


def create_user(client: TestClient, email: str, senha: str = "Senha123"):
    return client.post(
        "/usuarios/",
        json={"nome": "Usuario Teste", "email": email, "senha": senha},
    )


def login_headers(client: TestClient, email: str, senha: str = "Senha123"):
    response = client.post("/auth/token", data={"username": email, "password": senha})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
