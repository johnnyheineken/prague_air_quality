import requests


def get_ow_data(credentials):
    token = credentials.TOKEN
    address = f"http://api.openweathermap.org/data/2.5/air_pollution?lat=50.042&lon=14.411&appid={token}"

    r = requests.get(address)
    result = {"pm25": r.json()['list'][0]['components']['pm2_5']}
    return result
