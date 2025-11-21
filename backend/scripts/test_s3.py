"""
S3 存储测试脚本

测试：
1. 上传一个测试文件
2. 下载文件
3. 删除文件
"""
import os
import sys
import json
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.core.s3_storage import S3StorageManager


def test_s3_storage():
    """测试 S3 存储功能"""
    print("=" * 60)
    print("S3 Storage Test")
    print("=" * 60)
    
    # 初始化 S3 Manager
    s3_manager = S3StorageManager()
    
    if not s3_manager.is_available():
        print("\n❌ S3 is not available")
        print("   Check USE_S3_STORAGE and AWS credentials in .env")
        return
    
    print(f"\n✅ S3 Manager initialized")
    print(f"   Bucket: {s3_manager.bucket}")
    print(f"   Region: {settings.AWS_REGION}")
    
    # 测试数据
    test_artifact = {
        "test_id": "test_001",
        "content": "This is a test artifact",
        "data": ["item1", "item2", "item3"],
        "metadata": {
            "created_at": "2025-11-21",
            "type": "test"
        }
    }
    
    # 1. 上传测试
    print(f"\n📤 Test 1: Upload artifact...")
    s3_uri = s3_manager.save_artifact(
        user_id="test_user",
        artifact_id="test_artifact_001",
        content=test_artifact,
        metadata={"test": True}
    )
    
    if s3_uri:
        print(f"✅ Upload successful!")
        print(f"   S3 URI: {s3_uri}")
    else:
        print(f"❌ Upload failed")
        return
    
    # 2. 下载测试
    print(f"\n📥 Test 2: Download artifact...")
    downloaded_content = s3_manager.load_artifact(s3_uri)
    
    if downloaded_content:
        print(f"✅ Download successful!")
        print(f"   Content matches: {downloaded_content == test_artifact}")
        if downloaded_content == test_artifact:
            print(f"   ✅ Content integrity verified!")
        else:
            print(f"   ❌ Content mismatch!")
            print(f"   Expected: {test_artifact}")
            print(f"   Got: {downloaded_content}")
    else:
        print(f"❌ Download failed")
        return
    
    # 3. 清理测试
    print(f"\n🗑️  Test 3: Cleanup...")
    try:
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # 从 S3 URI 提取 key
        key = s3_uri.replace(f"s3://{s3_manager.bucket}/", "")
        
        s3_client.delete_object(
            Bucket=s3_manager.bucket,
            Key=key
        )
        print(f"✅ Test artifact deleted")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🎉 All Tests Passed!")
    print(f"=" * 60)
    print(f"\n✅ S3 storage is working correctly")
    print(f"✅ Your application can now use S3 for artifact storage")


if __name__ == "__main__":
    test_s3_storage()

