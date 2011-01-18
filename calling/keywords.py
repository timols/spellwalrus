import datetime

TODAYS_KEYWORD = {
    'Monday':       {'word': 'walrus',
                     'sentence': 'A walrus is a large flippered marine mammal.'},
    'Tuesday':      {'word': 'wombat',
                     'sentence': 'A wombat is a short-legged muscular quadruped.'},
    'Wednesday':    {'word': 'donkey',
                     'sentence': 'A donkey is a domesticated member of the Equidae family.'},
    'Thursday':     {'word': 'gazelle',
                     'sentence': 'A gazelle is a swift animal, mostly found in Africa.'},
    'Friday':       {'word': 'snake',
                     'sentence': 'A snake is a legless, carnivorous reptile.'},
    'Saturday':     {'word': 'tiger',
                     'sentence': 'A tiger is a big scary cat.'},
    'Sunday':       {'word': 'swan',
                     'sentence': 'A swan is a kind of like a big duck. Most of them are white.'}
}[datetime.datetime.now().strftime("%A")]
