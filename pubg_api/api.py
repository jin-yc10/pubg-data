def get_key(PATH):
    key = ''
    with open(PATH) as k:
        key = k.readline()
    return key

if __name__ == '__main__':
    k = get_key('../.PRIVATE')
    import requests, json
    url = 'https://pubgtracker.com/api/profile/pc/Yhyoek'
    headers = {
        'TRN-API-KEY': k
    }
    r = requests.get(url, headers=headers)
    user = json.loads(r.text)
    print(user['PlayerName'])
