from discord import Activity, ActivityType


class Loading(Activity):
    def __init__(self):
        super().__init__(name='Loading...',details='loading up cool bot :D',type=ActivityType.playing)