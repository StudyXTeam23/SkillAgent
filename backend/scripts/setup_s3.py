"""
S3 存储桶初始化脚本

功能：
1. 检查存储桶是否存在
2. 如果不存在，自动创建存储桶
3. 配置存储桶策略（private）
"""
import os
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings


def setup_s3_bucket():
    """设置 S3 存储桶"""
    print("=" * 60)
    print("S3 Storage Bucket Setup")
    print("=" * 60)
    
    # 检查配置
    print(f"\n📋 Configuration:")
    print(f"  USE_S3_STORAGE: {settings.USE_S3_STORAGE}")
    print(f"  AWS_REGION: {settings.AWS_REGION}")
    print(f"  AWS_S3_BUCKET: {settings.AWS_S3_BUCKET}")
    
    if not settings.USE_S3_STORAGE:
        print("\n⚠️  S3 storage is disabled (USE_S3_STORAGE=false)")
        print("   Enable it in .env to use S3 storage")
        return
    
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        print("\n❌ boto3 is not installed!")
        print("   Install it with: pip install boto3")
        return
    
    # 初始化 S3 客户端
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        print("\n✅ S3 client initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize S3 client: {e}")
        return
    
    bucket_name = settings.AWS_S3_BUCKET
    region = settings.AWS_REGION
    
    # 检查存储桶是否存在
    print(f"\n🔍 Checking if bucket '{bucket_name}' exists...")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists!")
        
        # 显示存储桶信息
        try:
            location = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = location['LocationConstraint'] or 'us-east-1'
            print(f"   Region: {bucket_region}")
        except Exception as e:
            print(f"   Could not get bucket location: {e}")
        
        return
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"⚠️  Bucket '{bucket_name}' does not exist")
            print(f"   Creating bucket in region '{region}'...")
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("   Check your AWS credentials")
            return
        else:
            print(f"❌ Error checking bucket: {e}")
            return
    
    # 创建存储桶
    try:
        if region == 'us-east-1':
            # us-east-1 不需要 LocationConstraint
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            # 其他区域需要指定 LocationConstraint
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ Bucket '{bucket_name}' created successfully!")
        
        # 设置存储桶为私有
        print(f"\n🔒 Setting bucket to private...")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"✅ Bucket is now private")
        
        # 启用版本控制（可选）
        print(f"\n📦 Enabling versioning...")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✅ Versioning enabled")
        
        # 设置生命周期策略（可选）- 30 天后删除旧版本
        print(f"\n🗑️  Setting lifecycle policy...")
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'DeleteOldVersions',  # 注意：AWS API 要求大写 ID
                        'Status': 'Enabled',
                        'NoncurrentVersionExpiration': {'NoncurrentDays': 30},
                        'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 7}
                    }
                ]
            }
        )
        print(f"✅ Lifecycle policy set (old versions deleted after 30 days)")
        
        print(f"\n" + "=" * 60)
        print(f"🎉 S3 Bucket Setup Complete!")
        print(f"=" * 60)
        print(f"\nBucket Name: {bucket_name}")
        print(f"Region: {region}")
        print(f"Status: ✅ Ready to use")
        print(f"\n💡 You can now use S3 storage in your application")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket '{bucket_name}' already exists and is owned by you!")
        elif error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket name '{bucket_name}' is already taken by someone else")
            print(f"   Try a different bucket name in .env")
        else:
            print(f"❌ Failed to create bucket: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    setup_s3_bucket()

