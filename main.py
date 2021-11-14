import credentials.credentials as cred

from bot.main import AirQualityBot


def main():
    bot = AirQualityBot(credentials=cred)
    data = bot.run()
    data.to_csv('out/tables/current_data.csv', index=False)

if __name__ == "__main__":
    main()
