import random
from api.aqi import get_aqi_data
from api.twitter import send_tweet

import credentials.aqi
import credentials.twitter

AQI_values = {
    300: ['To je stejné, jak v Indii na Diwali 💀'],
    250: ["Podobné hodnoty má Hotan - nejznečištěnejší město Číny 💀"],
    200: ["Aneb pěkný den z Lahore v Pakistanu! 💀"],
    150: ["Takový pěkný den v Dhace, hlavním městě Bangladéše! ☣️", "Zima v Sarajevu je podobná. ☣️",
          "Orzesze v polském Slezsku je na tom podobně ☣️", "V Pekingu by už zavřeli fabriky. ☣️"],
    110: ["Jak špatný den v Ostravě ❌", "Průměrný den v Pekingu ❌",
          "V tomhle počasí by venku sportoval jen sebevrah ❌", "V Asii by respirátor nesundali ani venku ❌"],
    80: ["Podobně, jako špatný den v Šanghaji 🛑", "Průměrný den v Ostravě 🛑", "Stejné ovzduší je UVNITŘ auta 🛑",
         "Bacha, doporučuje se nechodit ven a nevětrat 🛑", "To je na roušku i venku 🛑"],
    60: ["Podobně, jako dobrý den v Šanghaji ⚠️", "Takový pražský průměr. ⚠️", "Průměrný den v Paříži ⚠️",
         "Omezte větrání, a citlivé skupiny by neměly chodit ven ⚠️", "Podle WHO max 3-4 takové dny ročně ⚠️"],
    40: ["Průměrný den v Amsterdamu ✔️", "Na horách by bylo lépe, ale dobrý ✔️",
         "Dobrý, ale lidi po COVIDu by si měli dávat bacha ✔️"],
    20: ["Tak hurá ven! ✅", "Takhle to má vypadat ✅", "Doporučený dlouhodobý průměr podle WHO ✅"],
    0: ["Vsadím se, že fouká 💚", "Lepší, než doporučení WHO! 💚", "To je paráda 💚"]
}

AQI_messages = ["Dnešní kvalita vzduchu v Praze je {aqi} AQI. ", "Dnešní pražský Air Quality Index je {aqi}. ",
                "Dnes bylo v Praze naměřeno {aqi} AQI. ", "Dnešní kvalita vzduchu v Praze je {aqi}. "]


def create_message(aqi):
    message = random.choice(AQI_messages).format(aqi=aqi)

    for aqi_value, aqi_message in AQI_values.items():
        if aqi_value <= aqi:
            message += random.choice(aqi_message)
            break
    return message




def main():
    aqi_value = get_aqi_data(credentials.aqi)
    message = create_message(aqi_value)
    send_tweet(message=message, credentials=credentials.twitter)

if __name__ == "__main__":
    main()