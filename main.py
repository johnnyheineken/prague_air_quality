from credentials.credentials import Credentials

from bot.main import AirQualityBot


def main():
    bot = AirQualityBot(credentials=Credentials, mock=True)
    bot.run()


if __name__ == "__main__":
    main()
