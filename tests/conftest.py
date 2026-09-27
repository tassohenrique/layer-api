import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Cria as tabelas no banco de testes uma vez, no início da bateria."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    """Entrega uma sessão para o teste e limpa as tabelas no fim."""
    session = TestingSessionLocal()
    yield session
    session.close()
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture
def client(db_session):
    """Cliente HTTP de testes usando o banco de testes."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
