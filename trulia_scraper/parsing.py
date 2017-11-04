def remove_empty(l):
    '''Remove items which evaluate to False (such as empty strings) from the input list.'''
    return [x for x in l if x]

def get_number_from_string(string, number_type=float):
    '''Remove commas from the input string and parse as a number'''
    return number_type(string.replace(',', ''))