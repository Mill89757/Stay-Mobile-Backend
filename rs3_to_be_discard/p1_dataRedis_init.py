import redis

r = redis.Redis(host='localhost', port=6379, db=0)

print()
print('r.keys() =', r.keys())
print()
print()

r.hset('db_len','clg',0)
r.hset('db_len','mmbr',0)
r.hset('db_len','post',0)
r.hset('db_len','like',0)
r.hset('db_len','track',0)



for i in range(1,6):
    field = 'like_record_' + str(i)
    r.hset(field,0,'')
    # r.hdel(field,0)


r.hset('user_contribution',0,0)
# r.hdel('user_contribution',0)

r.hset('user_like',0,0)
# r.hdel('user_like',0)



if __name__ == "__main__":
    pass 

    # in terminal 1: redis-server          # connect to redis server
    # in terminal 2: redis-cli FLUSHALL    # clear local data

    print('r.keys() =', r.keys())
    print()

    print("r.hgetall('db_len')  = ", r.hgetall('db_len'))
    print()

    for i in range(1,6):
        field = 'like_record_' + str(i)
        print(f" r.hgetall({field})  = ", r.hgetall(field))
    print()


    print("r.hgetall('user_like') = ", r.hgetall('user_like'))
    print()

    print( "r.hget('like_record_5',0) = ", 
        r.hget('like_record_5',0)
        )

    print( "r.hget('like_record_6',0) = ", 
        r.hget('like_record_6',0)
        )
