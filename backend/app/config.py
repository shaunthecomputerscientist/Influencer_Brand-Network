import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

current_file_path = os.path.abspath(__file__)

# Get the directory of the current file
current_dir = os.path.dirname(current_file_path)

# Move up to the root directory of the backend app
backend_root = os.path.abspath(os.path.join(current_dir, '..'))

# Define separate configuration subclasses to organize settings

class JWTConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_SECURE = True
    # JWT_COOKIE_CSRF_PROTECT = True



class SQLAlchemyConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = 86400  # 24-hour 'remember me' cookie


class MailConfig:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class RedisConfig:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


class CeleryConfig:
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


class TrackingConfig:
    TRACKING_METHODS = ['influencerSocials', 'brandSocials', 'utmLinks']
    GOALS_NAME_MAPPING = {
        '(brand/product/service) awareness': 'goal_id_1',
        'engagement & community building': 'goal_id_2',
        'website traffic generation': 'goal_id_3',
        # 'lead generation & sales': 'goal_id_4',
        # 'increase customer loyalty': 'goal_id_5',
        # 'generate market insights & feedback': 'goal_id_6'
    }
    GOALS = list(GOALS_NAME_MAPPING.keys())


class ExternalAPIsConfig:
    INSTAGRAM_SCRAPING_ACCOUNTS = [
        {'username': os.getenv('ACCOUNT1_USERNAME'), 'password': os.getenv('ACCOUNT1_PASSWORD')},
    ]
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    GEONAMES_USERNAME = os.getenv('GEONAMES_USERNAME')

class PlatformDataConfig:

    NICHES = [
    "Beauty",
    "Finance",
    "Travel",
    "Fitness",
    "Dating & Relationships",
    "Video Games",
    "Marketing",
    "Pets & Animals",
    "Technology",
    "Weight Loss & Nutrition",
    "Entertainment & Pop Culture",
    "Food & Cooking",
    "Real Estate & Property",
    "Parenting & Maternity",
    "DIY & Crafts",
    "Health & Wellness",
    "Personal Development & Self-Help",
    "Sports & Fitness",
    "Skin Care & Acne Treatment",
    "Alcohol & Beverage",
    "Art & Design",
    "Fashion & Style",
    "Bodybuilding & Strength Training",
    "Literature & Books",
    "Home Improvement & Decor",
    "Politics"
    ]

    INDUSTRIES = [
            "Technology", "Healthcare", "Retail", "Finance", "Education",
            "Entertainment", "Fashion", "Food & Beverage", "Travel & Tourism", 
            "Real Estate", "Automotive", "Media & Publishing", "E-commerce",
            "Non-Profit", "Telecommunications"
        ]
    
    LANGUAGES = [
            "English", "Spanish", "French", "German", "Chinese", 
            "Hindi", "Arabic", "Portuguese", "Russian", "Japanese", 
            "Korean", "Italian", "Dutch", "Turkish", "Swedish"
        ]
    
    PLATFORMS = [
            "Instagram", "YouTube"
        ]
    
            # "TikTok", "Twitter", "Facebook", 
            # "LinkedIn", "Snapchat", "Pinterest", "Reddit", "Twitch",
            # "WhatsApp", "WeChat", "Telegram", "Discord", "Clubhouse"
    GENDER = [
        'male', 'female', 'non-binary', 'other'
    ]

class Config(
    JWTConfig,
    SQLAlchemyConfig,
    MailConfig,
    RedisConfig,
    CeleryConfig,
    TrackingConfig,
    ExternalAPIsConfig,
    PlatformDataConfig
):
    # Additional general settings
    
    PROFILE_IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profile_images')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(backend_root, 'app', 'instance', 'influgram.db')}"

# class DevelopmentConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_DB_USER')}:{os.getenv('POSTGRES_DB_PASSWORD')}@{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/{os.getenv('POSTGRES_DB_NAME')}"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_DB_USER')}:{os.getenv('POSTGRES_DB_PASSWORD')}@{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/{os.getenv('POSTGRES_DB_NAME')}"
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
