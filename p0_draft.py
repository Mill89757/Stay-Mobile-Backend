import redis 

r = redis.Redis(host='localhost', port=6379, db=0)

r.hset('like_record_1', 'clg1', 'user11')
r.hset('like_record_1', 'clg2', 'user12')
r.hset('like_record_1', 'clg3', 'user13')

r.hset('like_record_2', 'clg1', 'user21')
r.hset('like_record_2', 'clg2', 'user22')
r.hset('like_record_2', 'clg3', 'user23')

r.hset('like_record_3', 'clg1', 'user31')
r.hset('like_record_3', 'clg2', 'user32')
r.hset('like_record_3', 'clg3', 'user33')

r.hset('like_record_4', 'clg1', 'user41')
r.hset('like_record_4', 'clg2', 'user42')
r.hset('like_record_4', 'clg3', 'user43')

r.hset('like_record_5', 'clg1', 'user51')
r.hset('like_record_5', 'clg2', 'user52')
r.hset('like_record_5', 'clg3', 'user53')



# ---

print('current keys: ' , r.keys())

print()
print('current fields in [ like_record_1 ]: ')
print(r.hget('like_record_1', 'clg1'), end = ', ')
print(r.hget('like_record_1', 'clg2'), end = ', ')
print(r.hget('like_record_1', 'clg3'), end = ', ')

print()
print()

print('current fields in [ like_record_2 ]: ')
print(r.hget('like_record_2', 'clg1'), end = ', ')
print(r.hget('like_record_2', 'clg2'), end = ', ')
print(r.hget('like_record_2', 'clg3'), end = ', ')

print()
print()


# ---

ongoing_clg_id = r.hkeys('like_record_1')
print('ongoing_clg_id: ', ongoing_clg_id)

print()

print('test with binary data')


for clg in ongoing_clg_id:
    for day in range(1,5):
        day1 = 'like_record_' + str(day)
        day2 = 'like_record_' + str(day+1)
        r.hset(day1, clg, r.hget(day2, clg))
    r.hset('like_record_5', clg, '')




print('updated fields in [ like_record_2 ]: ')
print(r.hget('like_record_2', 'clg1'), end = ', ')
print(r.hget('like_record_2', 'clg2'), end = ', ')
print(r.hget('like_record_2', 'clg3'), end = ', ')

print('updated fields in [ like_record_5 ]: ')
print(r.hget('like_record_5', 'clg1'), end = ', ')
print(r.hget('like_record_5', 'clg2'), end = ', ')
print(r.hget('like_record_5', 'clg3'), end = ', ')
















# redis-server
# redis-cli FLUSHALL