import string


def chars_to_digits(word):
    "Given a string of characters, return the corresponding keypad digits"
    keypad_mapping = dict(zip(string.ascii_lowercase, 
                              "22233344455566677778889999"))
    return ''.join(str(keypad_mapping[l]) for l in word.lower())