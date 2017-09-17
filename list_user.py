import leveldb, json

user_db = leveldb.LevelDB('./user_db')
cnt = 0;
for k,v in user_db.RangeIter():
    obj = json.loads(v.decode('utf8'))
    print(cnt, k, obj['PlayerName'])
    cnt += 1