import json
import random

import requests
import pandas as pd
from requests_oauthlib import OAuth1Session

from bot.messages import AQI_MESSAGES, AQI_VALUES, PM25_COMPARISONS
from bot.helpers import create_logger
DAILY_RECOMMENDED_PM25_VALUE = 15


class AirQualityBot:
    def __init__(self, credentials, lat='50.042', lon='14.411', logger=None):
        self.credentials = credentials
        self.lat = lat
        self.lon = lon
        if logger is None:
            logger= create_logger('AirQuality')
        self.logger = logger

    def get_aqi_data(self):
        token = self.credentials.AirQualityCredentials.TOKEN
        address = f'http://api.airvisual.com/v2/nearest_city' \
                  f'?lat={self.lat}&lon={self.lon}' \
                  f'&key={token}'
        self.logger.info(f'Sending GET to {address}')
        r = requests.get(address)
        result = {"aqi": r.json()['data']['current']['pollution']['aqius']}
        return result

    def get_ow_data(self):
        token = self.credentials.OpenWeatherCredentials.TOKEN
        address = f"http://api.openweathermap.org/data/2.5/air_pollution" \
                  f"?lat={self.lat}&lon={self.lon}" \
                  f"&appid={token}"

        self.logger.info(f'Sending GET to {address}')
        r = requests.get(address)
        # {'co': 507.36,
        #  'no': 14.08,
        #  'no2': 20.22,
        #  'o3': 4.2,
        #  'so2': 5.25,
        #  'pm2_5': 26.43,
        #  'pm10': 31.59,
        #  'nh3': 1.58}
        result = r.json()['list'][0]['components']
        return result

    def send_tweet(self, message):
        oauth_tokens = self.credentials.TwitterCredentials.OAUTH_TOKENS
        consumer_key = self.credentials.TwitterCredentials.CONSUMER_KEY
        consumer_secret = self.credentials.TwitterCredentials.CONSUMER_SECRET
        payload = {"text": message}
        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]
        address = "https://api.twitter.com/2/tweets"
        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        # Making the request
        self.logger.info(f'Sending POST to {address} with {payload}')
        response = oauth.post(
            address,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))

    def create_message(self, aq_data, ow_data):
        aqi = aq_data['aqi']
        pm25 = ow_data['pm2_5']

        message = random.choice(AQI_MESSAGES).format(aqi=aqi)
        multiplicator = pm25 / DAILY_RECOMMENDED_PM25_VALUE
        for aqi_value, aqi_message in AQI_VALUES.items():
            if aqi_value <= aqi:
                if multiplicator > 1.2:
                    message += '\n' + random.choice(PM25_COMPARISONS).format(multiplicator=multiplicator, pm25=pm25)
                message += '\n\n' + random.choice(aqi_message)

                break
        return message

    def run(self):
        try:
            aq_data = self.get_aqi_data()
            ow_data = self.get_ow_data()
            message = self.create_message(aq_data, ow_data)

            self.send_tweet(message=message)
            final_data = ow_data
            final_data['aqius'] = aq_data['aqi']
            data = pd.Series(final_data)
            data.index.name = 'stat'
            return data
        except:
            self.send_tweet(message='Man, something broke. @janhynek should do something about that')
            raise
