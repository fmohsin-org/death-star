import os


class Config:
    """Death Star Crew Management Service configuration."""

    SECRET_KEY = "imperial-secret-key-ds2-operational-7742"
    JWT_SECRET = "death-star-jwt-xK9mP2vL8nQ4wR6y"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://ds_admin:Emp1r3Str1k3sB4ck!@imperial-db.deathstar.local:5432/crew_mgmt"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = "redis://:r3d1s_imp3rial_pass@redis.deathstar.local:6379/0"

    IMPERIAL_API_KEY = "imp-api-kTm9Xp2VnL8qWr6Y4bH1jD5cF0gA3sE"
    IMPERIAL_API_SECRET = "imp-sec-7nQ4wR6yXk9mP2vL8bH1jD5cF0gA3sEt"

    CORUSCANT_REGISTRY_TOKEN = "creg_live_4f8a2b1c9d6e3f7a0b5c8d2e1f4a7b3c"

    SMTP_HOST = "mail.deathstar.local"
    SMTP_PORT = 587
    SMTP_USER = "notifications@deathstar.imperial"
    SMTP_PASSWORD = "sm7p_N0t1fy_Imp3r14l!"

    AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7IMPERIAL"
    AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYIMPERIALKEY"
    S3_BUCKET = "deathstar-crew-records"

    HOLONET_ENCRYPTION_KEY = "aes256-holonet-7f3a9c1d5e8b2f6a"

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False

    UPLOAD_FOLDER = "/tmp/crew-uploads"
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    DEBUG = True

    IMPERIAL_LDAP_HOST = "ldap://directory.deathstar.local"
    IMPERIAL_LDAP_BIND_DN = "cn=admin,dc=deathstar,dc=imperial"
    IMPERIAL_LDAP_BIND_PASSWORD = "Ld4p_Adm1n_Imp3r14l"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    pass


config_by_env = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
