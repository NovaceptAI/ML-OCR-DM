# app/config.py

import os
import logging
from app.config.db_config import db

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Base configuration with default settings."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    UPLOAD_FOLDER = 'app/tmp'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    DATABASE_URI = os.environ.get('DEV_DATABASE_URI', 'sqlite:///dev.db')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = os.environ.get('TEST_DATABASE_URI', 'sqlite:///test.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///prod.db')


def get_config(env):
    """Return the configuration class based on the environment."""
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig


def get_aws_creds():
    try:
        creds_cursor = db.creds.find_one({"service": "aws"})
        if creds_cursor:
            aws_access_key_id = creds_cursor.get('aws_access_key_id')
            aws_secret_access_key = creds_cursor.get('aws_secret_access_key')
            bucket_name = creds_cursor.get('bucket_name')
            region_name = creds_cursor.get('region_name')

            if all([aws_access_key_id, aws_secret_access_key, bucket_name, region_name]):
                logger.info("AWS credentials retrieved successfully.")
                return {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                    "bucket_name": bucket_name,
                    "region_name": region_name
                }
            else:
                logger.error("Incomplete AWS credentials found.")
                return None
        else:
            logger.error("AWS credentials not found in the database.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving AWS credentials: {e}")
        return None
