from random import choice

from discord import Activity, ActivityType, Status


def get_random_status() -> Status:
    return choice([
        Status.idle,
        Status.online,
        Status.dnd
    ])

class Loading(Activity):
    def __init__(self):
        super().__init__(name='Loading...',details='loading up cool bot :D',type=ActivityType.playing)

class PlayingWithFood(Activity):
    def __init__(self):
        super().__init__(name='with food',details='Cameluo Cababas loves food!',type=ActivityType.playing)