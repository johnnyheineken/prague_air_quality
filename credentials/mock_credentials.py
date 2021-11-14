from dataclasses import dataclass


@dataclass
class AirQualityCredentials:
    TOKEN = 'insert_air_quality_credentials'


@dataclass
class OpenWeatherCredentials:
    TOKEN = "insert_open_weather_credentials"


@dataclass
class TwitterCredentials:
    CONSUMER_KEY = 'insert_twitter_developer_consumer_key'
    CONSUMER_SECRET = 'insert_twitter_conusmer_secret'
    BEARER = 'add_bearer_token_(not_needed)'
    OAUTH_TOKENS = {'oauth_token': 'add_generated_OAUTH_token',
                    'oauth_token_secret': 'add_generated_oauth_token_secret',
                    'user_id': 'your_user_id',
                    'screen_name': 'app_name'}