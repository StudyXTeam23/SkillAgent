"""
Task 1.1 测试 - 测试 FastAPI 应用基础设施

测试内容：
1. 应用启动和配置加载
2. 健康检查端点
3. CORS 配置
4. 根路径响应
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


class TestApplicationSetup:
    """测试应用基础设施"""
    
    def test_app_initialization(self):
        """测试应用能够正常初始化"""
        assert app is not None
        assert app.title == "Skill Agent Demo API"
        assert app.version == "1.0.0"
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "Skill Agent Demo API"
        assert data["version"] == "1.0.0"
        assert "gemini_model" in data
        assert "s3_enabled" in data
    
    def test_root_endpoint(self, client):
        """测试根路径端点"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["message"] == "Welcome to Skill Agent Demo API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
    
    def test_cors_headers(self, client):
        """测试 CORS 配置"""
        # 发送带 Origin 的 OPTIONS 请求（预检请求）
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # 检查 CORS 头部
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_openapi_docs_available(self, client):
        """测试 OpenAPI 文档可访问"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Skill Agent Demo API"


class TestConfiguration:
    """测试配置管理"""
    
    def test_settings_loaded(self):
        """测试环境变量是否正确加载"""
        assert settings.GEMINI_API_KEY is not None
        assert settings.GEMINI_MODEL == "gemini-2.5-flash"
        assert settings.PORT == 8000
    
    def test_s3_configuration(self):
        """测试 S3 配置"""
        # 检查 S3 相关配置存在
        assert hasattr(settings, "USE_S3_STORAGE")
        assert hasattr(settings, "AWS_S3_BUCKET")
        assert hasattr(settings, "S3_MEMORY_FOLDER")
        assert hasattr(settings, "S3_SESSION_FOLDER")
        
        # 验证文件夹名称
        assert settings.S3_MEMORY_FOLDER == "memory_profiles"
        assert settings.S3_SESSION_FOLDER == "session_contexts"
    
    def test_cors_origins_parsing(self):
        """测试 CORS origins 解析"""
        origins = settings.cors_origins_list
        
        assert isinstance(origins, list)
        assert len(origins) > 0
        assert "http://localhost:5173" in origins


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

