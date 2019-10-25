import re
KEYS = set(['schools', 'crime', 'commute', 'shop & eat'])
def remove_empty(l):
    '''Remove items which evaluate to False (such as empty strings) from the input list.'''
    return [x for x in l if x]

def remove_key_words(l):
    return [x for x in l if x.lower() not in KEYS]

def get_number_from_string(string, number_type=float):
    '''Remove commas from the input string and parse as a number'''
    string = string.replace('$', '')
    return number_type(string.replace(',', ''))

def match_quote(l):
    result = re.findall('.*\"(.*)\".*', l)
    if len(result) > 0:
        return result[0]
    else:
        return ''