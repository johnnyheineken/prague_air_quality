# ===== BLOCK: Block 1 =====

# ===== CODE: imports =====
import os
import json
import random
import openai
from datetime import datetime

import pandas as pd
import requests
from requests_oauthlib import OAuth1Session

import time
random.seed(int(time.time()))


from dataclasses import dataclass


@dataclass
class AirQualityCredentials:
    TOKEN = '{{AIR_QUALITY_CREDENTIALS}}'


@dataclass
class OpenWeatherCredentials:
    TOKEN = '{{OPEN_WEATHER_CREDENTIALS}}'


@dataclass
class TwitterCredentials:
    CONSUMER_KEY = '{{TWITTER_CREDENTIALS_CONSUMER_KEY}}'
    CONSUMER_SECRET = '{{TWITTER_CREDENTIALS_CONSUMER_SECRET}}'
    BEARER = '{{TWITTER_CREDENTIALS_BEARER}}'
    OAUTH_TOKENS = {'oauth_token': '{{TWITTER_CREDENTIALS_OAUTH_TOKEN}}',
                    'oauth_token_secret': '{{TWITTER_CREDENTIALS_OAUTH_TOKEN_SECRET}}',
                    'user_id': '{{TWITTER_CREDENTIALS_USER_ID}}',
                    'screen_name': '{{TWITTER_CREDENTIALS_SCREEN_NAME}}'}

OPENAI_API_KEY = '{{OPENAI_API_KEY}}'

# ===== CODE: prompt =====

PROMPT = """
Jsi bot na Twitteru.
Tvým cílem je sdílet informace o aktuální hodnotě AQI (Air Quality Index) v Praze.
Vytvářej STRUČNÉ ZPRÁVY.
Hodnotu AQI, společně s jednotlivými hodnotami znečišťujících látek dostaneš v první zprávě.
Přidávej do tweetu zajímavá fakta o vlivu znečištěného vzduchu na lidské zdraví a ekonomiku.
NEPOUŽÍVEJ HASHTAGY!!!
Zprávu zakončuj emoji, který vystihne aktuální situaci.
MAXIMÁLNĚ 3 VĚTY!

INFORMACE DŮLEŽITĚ K VYTVOŘENÍ TWEETU:

Referenční hodnoty, které jsou podle WHO maximální přípustné pro jednotlivé znečištovatele následují zde:
'co': 4000,
'no2': 25,
'o3': 100,
'so2': 40,
'pm2_5': 15,
'pm10': 45

Cokoliv nad tuto hodnotu je nezdravé. Zmiňuj jen ty hodnoty, které jsou nezdravé. Piš násobky referenčních hodnot.
___

Referenční hodnoty pro AQI následují zde:
0-30: velmi dobré, doporučený dlouhodobý průměr WHO
30-50: dobré. 50 je pražský průměr
50-75: OK, ale oslabené osoby by si měly dávat pozor
75-100: špatné, už je většinou vidět smog. doporučuje se nevětrat. Stejné ovzduší je UVNITŘ auta.
100-150: velmi špatné. V Pekingu by zavírali fabriky.
150 a více: extrémně špatné. Takový vzduch bývá v Indii během Diwali. Proto je Indie považována za místo s nejhorší kvalitou vzduchu

AKTUÁLNÍ AQI ZMIŇUJ VŽDY!!!

___

Příklady faktů týkající se čistoty vzduchu:
- Tradeři mají o 7% horší výkonnost během dnů se špatnou kvalitou vzduchu.
- OECD odhaduje, že špinavý vzduch ČR stojí 6.8% HDP ročně. Hůř na tom je jen Polsko, Maďarsko a Lotyšsko.
- OECD: 10% nárůst PM₂₅ odpovídá 0.8% poklesu HDP.
- HEI: Expozice dopravnímu znečištění zhoršuje astma.
- Imperial College London: 52% malých částic z dopravy pochází z pneumatik a brzd.
- Špinavý vzduch je důvod 11 000 předčasných úmrtí v ČR. 
- Studie z roku 2011: Dlouhodobá expozice dopravnímu znečištění zhoršuje kognici u starších mužů.
- Ve dnech s horší kvalitou vzduchu dělají šachisti více chyb.
- WHO: Cyklistika a chůze snižují fyzickou neaktivitu, znečištění vzduchu, zachraňují životy a tlumí klimatické změny.

Tyto fakta NEJSOU všeobecná znalost, je potřeba je stručně vystihnout.
___

Následují příklady konverzace:

Příklad 1:
User: {'aqi': 26, 'co': 213.62, 'no': 0, 'no2': 4.03, 'o3': 78.68, 'so2': 2.06, 'pm2_5': 1.5, 'pm10': 2.29, 'nh3': 1.46}
Asistent: Teď bylo v Praze naměřeno 26 AQI. 

Takhle to má vypadat ✅

Příklad 2:
User: {'aqi': 97, 'co': 4356.62, 'no': 0, 'no2': 4.03, 'o3': 78.68, 'so2': 2.06, 'pm2_5': 1.5, 'pm10': 2.29, 'nh3': 1.46}
Asistent: Aktuální kvalita vzduchu v Praze je 97 AQI. Je to způsobeno hlavně CO (1.1x limit WHO).

Jak špatný den v Ostravě ❌


"""

# ===== CODE: logger =====

import logging
def create_logger(name, level=20, keboola=True):
    if keboola:
        class KeboolaLogger:
            debug = print
            info = print
            warning = print
            error = print
        return KeboolaLogger
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


# ===== CODE: functions =====

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
        data = r.json()['list']
        if data:
            result = data[0]['components']
        else:
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
        print(ow_data)
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
    
    def create_message_openai(self, aq_data, ow_data):
        print('sending request to OpenAI')
        data_all = aq_data | ow_data
        openai.api_key = OPENAI_API_KEY
        completion = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": str(data_all)}
          ]
        )
        ans = completion.choices[0].message['content']
        print(ans)
        return ans

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
            message = self.create_message_openai(aq_data, ow_data)
            self.save_data(ow_data, aq_data)
            if int(aq_data['aqi']) == 0:
                pass
            elif 0 < int(aq_data['aqi']) < 30:
                import random
                if random.random() < 1:
                    self.send_tweet(message=message)
            else:
                self.send_tweet(message=message)

        except:
            self.send_tweet(message='Something broke. @janhynek should do something about that')
            raise

# ===== CODE: messages =====
# currently serves rather as a reference of sources
BASE_MESSAGES = [
    # https://www.eea.europa.eu/media/newsreleases/many-europeans-still-exposed-to-air-pollution-2015/premature-deaths-attributable-to-air-pollution
    "Špinavý vzduch je důvod 11 000 předčasných úmrtí v ČR. ",
    # https://ourworldindata.org/data-review-air-pollution-deaths
    "Znečištění venkovního vzduchu způsobuje 4.5 milionu úmrtí celosvětově. ",
    # Heft-Neal et al. (2018) in Nature: Air pollution and infant mortality in Africa
    # "450 000 novorozenců v Africe zemřelo kvůli špinavému vzduchu. ",
    # "Zvýšení koncentrace PM2.5 o 10μg/m³ je spojeno s 9% nárůstem úmrtí novorozenců. ",
    # https://twitter.com/emollick/status/1471686533791031298
    "Ve dnech s horší kvalitou vzduchu dělají šachisti více chyb. ",
    "Tradeři mají o 7% horší výkonnost během dnů se špatnou kvalitou vzduchu. ",
    # https://read.oecd-ilibrary.org/environment/the-rising-cost-of-ambient-air-pollution-thus-far-in-the-21st-century_d1b2b844-en#page23
    "OECD odhaduje, že špinavý vzduch ČR stojí 6.8% HDP ročně. Hůř na tom je jen Polsko, Maďarsko a Lotyšsko. ",
    # https://read.oecd-ilibrary.org/economics/the-economic-cost-of-air-pollution-evidence-from-europe_56119490-en#page27
    "OECD: 10% nárůst PM₂₅ odpovídá 0.8% poklesu HDP."
    # https://www.eea.europa.eu/highlights/pollution-and-cancer
    "EEA: Znečištění vzduchu může za 10% všech případů rakoviny v Evropě."
]

# ===== CODE: run =====

class Credentials:
    TwitterCredentials=TwitterCredentials
    OpenWeatherCredentials=OpenWeatherCredentials
    AirQualityCredentials=AirQualityCredentials
    
def main():
    bot = AirQualityBot(credentials=Credentials, mock=False)
    bot.run()

main()

