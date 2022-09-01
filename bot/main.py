import json
import random
from datetime import datetime

import pandas as pd
import requests
from requests_oauthlib import OAuth1Session

from bot.helpers import create_logger
from bot.messages import AQI_MESSAGES, AQI_VALUES

REFERENCE_VALUES = {
    'co': 4000,
    'no2': 25,
    'o3': 100,
    'so2': 40,
    'pm2_5': 15,
    'pm10': 45
}

NAME_MAPPING = {
    'co': 'CO',
    'no': 'NO',
    'no2': 'NO₂',
    'o3': 'O₃',
    'so2': 'SO₂',
    'pm2_5': 'PM₂.₅',
    'pm10': 'PM₁₀'
}


class AirQualityBot:
    def __init__(self, credentials, lat='50.042', lon='14.411', mock=False, logger=None):
        self.credentials = credentials
        self.lat = lat
        self.lon = lon
        if logger is None:
            logger = create_logger('AirQuality', keboola=True)
        self.logger = logger
        self.mock = mock

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
        data = r.json()['list']
        if data:
            result = data[0]['components']
        else:
            self.logger.warning('NO OPEN WEATHER API DATA DOWNLOADED.')
            result = {
                'co': float('nan'),
                'no': float('nan'),
                'no2': float('nan'),
                'o3': float('nan'),
                'so2': float('nan'),
                'pm2_5': float('nan'),
                'pm10': float('nan'),
                'nh3': float('nan'),
            }
        return result

    def send_tweet(self, message):
        if self.mock:
            print(message)
            return
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

    def get_reference_value_message(self, ow_data):
        references = []
        for name, reference_value in REFERENCE_VALUES.items():
            value = ow_data[name]
            if value != value:
                continue
            if (multiple := value / reference_value) > 1.5:
                references += [f'{NAME_MAPPING[name]} ({multiple:.1f}x)']
        if references:
            final_message = '\nPřekračující hodnoty jsou: ' + ', '.join(references)
        else:
            final_message = ''

        return final_message

    def create_message(self, aq_data, ow_data):
        aqi = aq_data['aqi']

        message = random.choice(AQI_MESSAGES).format(aqi=aqi)
        message += self.get_reference_value_message(ow_data)

        for aqi_value, aqi_message in AQI_VALUES.items():
            if aqi_value <= aqi:
                message += '\n\n' + random.choice(aqi_message)

                break
        return message

    @staticmethod
    def save_data(ow_data, aq_data):
        data = ow_data
        data['aqius'] = aq_data['aqi']
        data['timestamp'] = datetime.now()
        data = pd.Series(data)
        data.index.name = 'stat'
        data = pd.DataFrame(data).T
        data.to_csv('out/tables/current_data.csv', index=False)

    def run(self):
        try:
            aq_data = self.get_aqi_data()
            ow_data = self.get_ow_data()
            message = self.create_message(aq_data, ow_data)
            self.save_data(ow_data, aq_data)
            if int(aq_data['aqi']) == 0:
                pass
            elif 0 < int(aq_data['aqi']) < 30:
                import random
                if random.random() < 0.1:
                    self.send_tweet(message=message)
            else:
                self.send_tweet(message=message)

        except:
            self.send_tweet(message='Something broke. @janhynek should do something about that')
            raise
