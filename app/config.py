# app/config.py

import os


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
