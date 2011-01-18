import datetime

TODAYS_KEYWORD = {
    'Monday': 'walrus',
    'Tuesday': 'wombat',
    'Wednesday': 'donkey',
    'Thursday': 'gazelle',
    'Friday': 'snake',
    'Saturday': 'tiger',
    'Sunday': 'swan'
}[datetime.datetime.now().strftime("%A")]
