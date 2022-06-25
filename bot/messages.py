BASE_MESSAGES = [
    # https://www.eea.europa.eu/media/newsreleases/many-europeans-still-exposed-to-air-pollution-2015/premature-deaths-attributable-to-air-pollution
    "Špinavý vzduch je důvod 11 000 předčasných úmrtí v ČR. ",
    # https://ourworldindata.org/data-review-air-pollution-deaths
    "Znečištění venkovního vzduchu způsobuje 4.5 milionu úmrtí celosvětově. ",
    # Heft-Neal et al. (2018) in Nature: Air pollution and infant mortality in Africa
    "450 000 novorozenců v Africe zemřelo kvůli špinavému vzduchu. ",
    "Zvýšení koncentrace PM2.5 o 10μg/m³ je spojeno s 9% nárůstem úmrtí novorozenců. ",
    # https://twitter.com/emollick/status/1471686533791031298
    "Ve dnech s horší kvalitou vzduchu dělají šachisti více chyb. ",
    "Tradeři mají o 7% horší výkonnost během dnů se špatnou kvalitou vzduchu. ",
    # https://read.oecd-ilibrary.org/environment/the-rising-cost-of-ambient-air-pollution-thus-far-in-the-21st-century_d1b2b844-en#page23
    "OECD odhaduje, že špinavý vzduch ČR stojí 6.8% HDP ročně. Hůř na tom je jen Polsko, Maďarsko a Lotyšsko. "
    # https://read.oecd-ilibrary.org/economics/the-economic-cost-of-air-pollution-evidence-from-europe_56119490-en#page27
    "OECD: 10% nárůst PM₂₅ odpovídá 0.8% poklesu HDP."]

AQI_VALUES = {
    300: ['To je stejné, jak v Indii na Diwali 💀'],
    250: ["Podobné hodnoty má Hotan - nejznečištěnejší město Číny 💀"],
    200: ["Aneb pěkný den z Lahore v Pakistanu! 💀"],
    150: ["Takový pěkný den v Dhace, hlavním městě Bangladéše! ☣️", "Zima v Sarajevu je podobná. ☣️",
          "Orzesze v polském Slezsku je na tom podobně ☣️", "V Pekingu by už zavřeli fabriky. ☣️"],
    110: ["Jak špatný den v Ostravě ❌", "Průměrný den v Pekingu ❌",
          "V tomhle počasí by venku sportoval jen sebevrah ❌"] + [i + '❌' for i in BASE_MESSAGES],
    70: ["Podobně, jako špatný den v Šanghaji 🛑",
         "Průměrný den v Ostravě 🛑",
         "Stejné ovzduší je UVNITŘ auta 🛑",
         "Bacha, doporučuje se nechodit ven a nevětrat 🛑"] + [i + '🛑' for i in BASE_MESSAGES],
    50: ["Podobně, jako dobrý den v Šanghaji ⚠️",
         "Takový pražský průměr. ⚠️",
         ] + [i + '⚠️' for i in BASE_MESSAGES],
    30: ["Na horách by bylo lépe, ale dobrý."] + BASE_MESSAGES,
    15: ["Tak hurá ven! ✅", "Takhle to má vypadat ✅", "Doporučený dlouhodobý průměr podle WHO ✅"],
    0: ["Lepší, než doporučení WHO! 💚", "To je paráda 💚"]
}

PM25_COMPARISONS = ['PM₂₅ překračuje maximální hodnoty WHO {multiplicator:.1f}x ({pm25:.1f} µg/m3). ',
                    "To je {multiplicator:.1f} násobek maximálního PM₂₅ ({pm25:.1f} µg/m3). "]

AQI_MESSAGES = ["Aktuální kvalita vzduchu v Praze je {aqi} AQI. ",
                "Současný pražský Air Quality Index je {aqi}. ",
                "Teď bylo v Praze naměřeno {aqi} AQI. ",
                "Pražský Air Quality Index má nyní hodnotu {aqi}. "]
