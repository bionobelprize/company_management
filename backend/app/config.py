"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "biotech_inventory")

# Application Configuration
APP_TITLE = "生物公司进销存管理系统"
APP_DESCRIPTION = "蛋白抗原抗体及相关合成服务的进销存管理"
APP_VERSION = "1.0.0"
