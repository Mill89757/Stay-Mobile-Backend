from p2_functions import *

print()
print()
print(datetime.datetime.now())
print()

# for category in range(5):
#     posts = r.hget('category_posts', category)
#     print(f'new post for category {category} are: {posts}')

# print()
# print()


for user_id in range(1,3):
    categories, posts = get_recommended_post(user_id)
    print(f"User = {user_id},  Categories = {categories}")
    print('Recommended Posts = ')
    print(posts)
    print()
