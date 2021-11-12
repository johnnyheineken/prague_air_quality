import requests


def get_aqi_data(credentials):
    token = credentials.TOKEN
    address = f'http://api.airvisual.com/v2/city?city=Prague&state=Praha&country=Czech Republic&key={token}'
    r = requests.get(address)
    return r.json()['data']['current']['pollution']['aqius']
