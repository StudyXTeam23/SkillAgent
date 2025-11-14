"""
pytest 配置文件 - 定义全局 fixtures
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    """FastAPI 测试客户端（同步）"""
    return TestClient(app)


@pytest.fixture
async def test_app():
    """FastAPI 测试客户端（异步）"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def test_user_id():
    """测试用户 ID"""
    return "test_user_123"


@pytest.fixture
def test_session_id():
    """测试会话 ID"""
    return "test_session_456"

