import boto3
from botocore.exceptions import ClientError
from typing import Optional
import os
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET
        self.base_path = settings.S3_BASE_PATH

    def save_file(self, file_data: bytes, filename: str, content_type: str) -> Optional[str]:
        """
        保存文件到 S3
        
        Args:
            file_data: 文件内容（字节）
            filename: 文件名
            content_type: 文件类型
            
        Returns:
            str: S3 URL 或 None（如果上传失败）
        """
        try:
            # 生成唯一的文件名
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # 构建 S3 路径
            s3_key = f"{self.base_path}/{unique_filename}"
            
            # 上传文件
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type
            )
            
            # 生成 URL
            url = f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            return url
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None

    def save_attachment(self, attachment: dict) -> Optional[str]:
        """
        保存附件到 S3
        
        Args:
            attachment: 包含文件信息的字典
                {
                    'filename': str,
                    'mime_type': str,
                    'size': int,
                    'data': bytes
                }
                
        Returns:
            str: S3 URL 或 None（如果上传失败）
        """
        return self.save_file(
            file_data=attachment['data'],
            filename=attachment['filename'],
            content_type=attachment['mime_type']
        )

# 创建全局 S3 服务实例
s3_service = S3Service() 