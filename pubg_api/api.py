def get_key(PATH):
    key = ''
    with open(PATH) as k:
        key = k.readline()
    return key

