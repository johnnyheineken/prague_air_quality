import random

import credentials.aqi
import credentials.openweather
import credentials.twitter

from api.aqi import get_aqi_data
from api.openweather import get_ow_data
from api.twitter import send_tweet

DAILY_RECOMMENDED_PM25_VALUE = 15

AQI_VALUES = {
    300: ['To je stejné, jak v Indii na Diwali 💀'],
    250: ["Podobné hodnoty má Hotan - nejznečištěnejší město Číny 💀"],
    200: ["Aneb pěkný den z Lahore v Pakistanu! 💀"],
    150: ["Takový pěkný den v Dhace, hlavním městě Bangladéše! ☣️", "Zima v Sarajevu je podobná. ☣️",
          "Orzesze v polském Slezsku je na tom podobně ☣️", "V Pekingu by už zavřeli fabriky. ☣️"],
    110: ["Jak špatný den v Ostravě ❌", "Průměrný den v Pekingu ❌",
          "V tomhle počasí by venku sportoval jen sebevrah ❌", "V Asii by respirátor nesundali ani venku ❌",
          "29% úmrtí na rakovinu plic je způsobeno špinavým vzduchem. ❌",
          "To způsobuje 24% úmrtí na mrtvici. ❌",
          "43% úmrtí na onemocnění plic je způsobeno špinavým vzduchem. ❌"
          ],
    80: ["Podobně, jako špatný den v Šanghaji 🛑",
         "Průměrný den v Ostravě 🛑",
         "Stejné ovzduší je UVNITŘ auta 🛑",
         "Bacha, doporučuje se nechodit ven a nevětrat 🛑",
         "To je na roušku i venku 🛑",
         "29% úmrtí na rakovinu plic je způsobeno špinavým vzduchem. 🛑",
         "To způsobuje 24% úmrtí na mrtvici. 🛑",
         "43% úmrtí na onemocnění plic je způsobeno špinavým vzduchem. 🛑"],
    60: ["Podobně, jako dobrý den v Šanghaji ⚠️",
         "Takový pražský průměr. ⚠️",
         "Omezte větrání, a citlivé skupiny by neměly chodit ven ⚠️",
         "Podle WHO max 3-4 takové dny ročně ⚠️",
         "29% úmrtí na rakovinu plic je způsobeno špinavým vzduchem. ⚠️",
         "43% úmrtí na onemocnění plic je způsobeno špinavým vzduchem. ⚠️",
         "V Londýně špinavý vzduch zapříčinil 3500-9400 úmrtí v 2010. ⚠️",
         "Špinavý vzduch V Londýně stál zdravotnictví £3.7 miliard v 2010. ⚠️"
         ],
    40: ["Na horách by bylo lépe, ale dobrý ✔️",
         "Dobrý, ale lidi po COVIDu by si měli dávat bacha ✔️"],
    20: ["Tak hurá ven! ✅", "Takhle to má vypadat ✅", "Doporučený dlouhodobý průměr podle WHO ✅"],
    0: ["Vsadím se, že fouká 💚", "Lepší, než doporučení WHO! 💚", "To je paráda 💚"]
}

PM25_COMPARISONS = ['PM₂₅ překračuje maximální hodnoty WHO {multiplicator:.1f}x ({pm25:.1f}/15 µg/m3). ',
                    "To je {multiplicator:.1f} násobek maximálního PM₂₅ ({pm25:.1f}/15 µg/m3). "]

AQI_MESSAGES = ["Dnešní kvalita vzduchu v Praze je {aqi} AQI. ",
                "Dnešní pražský Air Quality Index je {aqi}. ",
                "Dnes bylo v Praze naměřeno {aqi} AQI. ",
                "Dnešní kvalita vzduchu v Praze je {aqi}. "]


def create_message(aq_data, ow_data):
    aqi = aq_data['aqi']
    pm25 = ow_data['pm25']

    message = random.choice(AQI_MESSAGES).format(aqi=aqi)
    multiplicator = pm25 / DAILY_RECOMMENDED_PM25_VALUE
    for aqi_value, aqi_message in AQI_VALUES.items():
        if aqi_value <= aqi:
            if multiplicator > 1.2:
                message += '\n' + random.choice(PM25_COMPARISONS).format(multiplicator=multiplicator, pm25=pm25)
            message += '\n\n' + random.choice(aqi_message)

            break
    return message


def main():
    try:
        aq_data = get_aqi_data(credentials.aqi)
        ow_data = get_ow_data(credentials.openweather)
        message = create_message(aq_data, ow_data)

        send_tweet(message=message, credentials=credentials.twitter)
    except:
        send_tweet(message='Man, something broke. @janhynek should do something about that',
                   credentials=credentials.twitter)
        raise


if __name__ == "__main__":
    main()
