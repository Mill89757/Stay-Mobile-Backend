import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db  
from database import Base  
import models

# 配置测试数据库
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = f"postgresql://STAY:STAY-1234@database-stay-mobile.cmgzgzmw0sul.ap-southeast-2.rds.amazonaws.com:5432/stay-mobile"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# 覆盖 get_db 依赖项
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 创建 TestClient
client = TestClient(app)

# 测试 create_challenge
def test_create_challenge():
    response = client.post(
        "/challenges/",
        json={"title": "New Challenge", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Challenge"
    assert "id" in data

# 测试 get_challenge
def test_get_challenge():
    response = client.get("/challenges/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "New Challenge"

# 测试 get_challenges
def test_get_challenges():
    response = client.get("/challenges/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# 测试 update_challenge
def test_update_challenge():
    response = client.put(
        "/challenges/1",
        json={"title": "Updated Challenge", "description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Challenge"

# 测试 delete_challenge
def test_delete_challenge():
    response = client.delete("/challenges/1")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Challenge deleted successfully"

# 在测试结束时清除测试数据
@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing database."""
    def remove_test_db():
        os.unlink(SQLALCHEMY_DATABASE_URL.split("///")[-1])
    request.addfinalizer(remove_test_db)
