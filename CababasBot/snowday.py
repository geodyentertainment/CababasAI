# Made by https://gist.github.com/iahuang
# Original source code: https://gist.github.com/iahuang/909b8557765c1cb6d53a3ebe70c98c6b

import requests
import re
import datetime

class SchoolType:
    PUBLIC = 0
    URBAN_PUBLIC = 0.4
    RURAL_PUBLIC = -0.4
    PRIVATE = -0.4
    BOARDING = 1


def datetime_to_daycode(day: datetime.datetime):
    return '{0:%Y%m%d}'.format(day)


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

    def chance_today(self):
        return self.chance(datetime.datetime.today())

    def chance_tmrw(self):
        print(datetime.datetime.today())
        return self.chance(datetime.datetime.today() + datetime.timedelta(days=1))


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
        print(f'{daycode} = {chance}%')

    return result