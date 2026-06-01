# src/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET_KEY: str = "changeme_super_secret_key_please_update_in_env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    SUPABASE_URL: str = ""

    # VNPAY
    VNPAY_TMN_CODE: str = ""
    VNPAY_HASH_SECRET: str = ""
    VNPAY_PAYMENT_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Ngrok SDK
    NGROK_AUTHTOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"  # Cho phép các biến môi trường khác không khai báo

settings = Settings()
