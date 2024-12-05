# Made by https://gist.github.com/iahuang
# Original source code: https://gist.github.com/iahuang/909b8557765c1cb6d53a3ebe70c98c6b
from datetime import tzinfo
from zoneinfo import ZoneInfo

import requests
import re
import datetime

from CababasBot.config_manager import Settings


class SchoolType:
    PUBLIC = 0
    URBAN_PUBLIC = 0.4
    RURAL_PUBLIC = -0.4
    PRIVATE = -0.4
    BOARDING = 1


def datetime_to_daycode(day: datetime.datetime):
    return '{0:%Y%m%d}'.format(day)


async def get_current_time(config:dict|None=None):
    return datetime.datetime.now(tz=ZoneInfo(str(await Settings.get_key_data(Settings.SEC_SNOWDAY, Settings.KEY_TIMEZONE, None, config))))

class Prediction:
    def __init__(self):
        self.data = {}

    def _set_data(self, daycode, chance):
        self.data[daycode] = min(99, chance)

    def chance(self, day):
        daycode = datetime_to_daycode(day)
        if daycode in self.data:
            return self.data[daycode]

        return None

    async def chance_today(self, config:dict|None=None):
        return self.chance(await get_current_time(config))

    async def chance_tmrw(self, config:dict|None=None):
        return self.chance(await get_current_time(config) + datetime.timedelta(days=1))


def predict(zipcode: str, snowdays: int = 0, schooltype: int = SchoolType.PUBLIC):
    response = requests.get(
        'https://www.snowdaycalculator.com/prediction.php',
        {
            'zipcode': zipcode,
            'snowdays': snowdays,
            'extra': schooltype
        }
    ).text
    js_predictions = re.findall(r'theChance\[\d+] = [\d.]+;', response)

    result = Prediction()

    for pred in js_predictions:
        key, value = pred.split(" = ")
        daycode = re.findall(r'\d+', key)[0]
        chance = float(re.findall(r'[\d+.]+', value)[0])

        result._set_data(daycode, chance)

    return result