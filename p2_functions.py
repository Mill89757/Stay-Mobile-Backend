from p1_load_data import *
from datetime import datetime, timedelta
import pytz

sydney_tz = pytz.timezone('Australia/Sydney')
DATE_TODAY = datetime.now(sydney_tz).date()
DATE_YESTERDAY = DATE_TODAY - timedelta(days=1) 



def classify_new_posts_by_category():

    for instance in POST:

        # get data for challenge_id, post_id, is_breaking_day

        challenge_id = instance.challenge_id
        post_id = instance.id
        is_breaking_day = False
        if instance.written_text == 'I have a break today.':
            is_breaking_day = True
    
        # get challenge detail 
        clg_detail = r.hget('on_clg_info', challenge_id)
         
        # add new challenge's detail to on_clg_info 
        if clg_detail == None:
            clg_record = CHALLENGE.filter(models.Challenge.id == challenge_id).first()
            clg_category = clg_record.category
            clg_isPublic = clg_record.is_public
            clg_done_by = clg_record.finished_time
            clg_done_by = datetime.datetime.strptime(clg_done_by.split(' ')[0], '%Y-%m-%d')

            r.hset('on_clg_info', challenge_id, 
                   f'{clg_category},{clg_isPublic},{clg_done_by}')
            clg_detail = r.hget('on_clg_info', challenge_id)
        
        
        category, isPublic, doneby = decoding(clg_detail).split(',')
        category = int(category[1:])
        doneby = datetime.datetime.strptime(doneby[:-1], '%Y-%m-%d')
        
        # add public, non-break post to the list 
        if isPublic and is_breaking_day==False:
            post_by_category[category].append(post_id)

        # check whether we should remove this challenge 
        if doneby == DATE_TODAY:
            challenge_to_be_removed.append(challenge_id)


def record_userLike_data_under_challenge():
    for i in range(start_row_like, len(LIKE_ALL)):
        like_record = LIKE_ALL.iloc[i]
        challenge = like_record['challenge_id']
        user = like_record['user_id']
        is_cancelled = like_record['is_cancelled']
        try:
            k = ongoing_challenges.index(challenge) 
        except ValueError:
            pass
        else: 
            if not is_cancelled:
                challenge_recent_like_data[k][-1].append(user)


def record_likerID_under_challengeID():
    for instance in LIKE:
        challenge_id = instance.challenge_id
        user_id = instance.user_id
        is_cancelled = instance.is_cancelled

        clg_detail = r.hget('on_clg_info', challenge_id)
        if not clg_detail: pass

        if not is_cancelled:
            current_user_id = r.hget('like_record_5', challenge_id)

            # initialise challenge like records
            if current_user_id == None: 
                for i in range(1,6):
                    r.hset('like_record_'+str(i), challenge_id,'')
            
            # 