#!/usr/bin/env python3
"""
S3 结构迁移脚本

从旧结构：s3://skill-agent-demo/artifacts/user_kimi/...
迁移到新结构：s3://skill-agent-demo/user_kimi/...

使用方法：
    python3 migrate_s3_structure.py

功能：
1. 列出旧结构中的所有文件
2. 将它们复制到新结构
3. 可选：删除旧文件
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boto3
from botocore.exceptions import ClientError
from app.config import settings

def migrate_s3_structure():
    """迁移 S3 结构"""
    
    # 初始化 S3 客户端
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        bucket = settings.AWS_S3_BUCKET
        
        print(f"✅ Connected to S3 bucket: {bucket}")
    except Exception as e:
        print(f"❌ Failed to connect to S3: {e}")
        return
    
    # 列出所有 artifacts/ 下的文件
    print(f"\n📋 Listing old structure files (artifacts/)...")
    
    old_prefix = "artifacts/"
    old_files = []
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=old_prefix)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if key != old_prefix:  # 排除目录本身
                        old_files.append(key)
        
        print(f"📊 Found {len(old_files)} files in old structure")
        
        if not old_files:
            print("✅ No files to migrate")
            return
        
        # 显示一些示例文件
        print(f"\n📁 Sample files:")
        for i, key in enumerate(old_files[:5]):
            print(f"  - {key}")
        if len(old_files) > 5:
            print(f"  ... and {len(old_files) - 5} more")
        
    except ClientError as e:
        print(f"❌ Failed to list files: {e}")
        return
    
    # 询问用户是否继续
    print(f"\n🔄 This will:")
    print(f"  1. Copy {len(old_files)} files to new structure (without 'artifacts/' prefix)")
    print(f"  2. Keep old files (you can delete them manually later)")
    
    response = input(f"\n⚠️  Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled")
        return
    
    # 迁移文件
    print(f"\n🚀 Starting migration...")
    
    migrated = 0
    failed = 0
    
    for old_key in old_files:
        # 计算新的 key（移除 artifacts/ 前缀）
        new_key = old_key.replace(old_prefix, "", 1)
        
        try:
            # 复制文件
            copy_source = {'Bucket': bucket, 'Key': old_key}
            s3_client.copy_object(
                CopySource=copy_source,
                Bucket=bucket,
                Key=new_key
            )
            
            migrated += 1
            print(f"✅ Migrated: {old_key} → {new_key}")
        
        except ClientError as e:
            failed += 1
            print(f"❌ Failed to migrate {old_key}: {e}")
    
    # 总结
    print(f"\n" + "="*80)
    print(f"📊 Migration Summary:")
    print(f"  ✅ Migrated: {migrated} files")
    print(f"  ❌ Failed: {failed} files")
    print(f"="*80)
    
    if failed == 0:
        print(f"\n🎉 Migration completed successfully!")
        print(f"\n💡 Old files are still in '{old_prefix}' - you can delete them manually if needed")
        print(f"   Command: aws s3 rm s3://{bucket}/{old_prefix} --recursive")
    else:
        print(f"\n⚠️  Some files failed to migrate. Please check the errors above.")


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║   S3 Structure Migration - Remove 'artifacts/' prefix                     ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    migrate_s3_structure()

