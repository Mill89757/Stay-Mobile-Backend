import models
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta


DAYS_BACK = datetime.now() - timedelta(days=10)

def fetch_popular_posts(db = models.UserReactionLog):
    popular_posts = session.query(db.post_id).group_by(db.post_id).order_by(func.count().desc()).limit(50).all()
    return {post[0] for post in popular_posts}

def fetch_liked_post_ids(user_id, db = models.UserReactionLog):
    """
    find user's recent reacted post ids 
    """
    liked_posts = session.query(db.post_id).filter(db.user_id == user_id).all()
    return {article[0] for article in liked_posts}

def fetch_similar_users(liked_post_ids, db = models.UserReactionLog):
    """
    find users who liked the same articles
    """
    similar_users = session.query(db.user_id).filter(db.post_id.in_(liked_post_ids)).all()
    return {user[0] for user in similar_users}



def fetch_user_based_recommendations(user_id, reaction_db = models.UserReactionLog, post_db = models.Post):
    """
    user-based recommendations based on recent posts
    """
    liked_posts = fetch_liked_post_ids(user_id)
    similar_users = fetch_similar_users(liked_posts)

    user_based_recommendations = session.query(reaction_db.post_id)\
        .join(post_db, reaction_db.post_id == post_db.id)\
        .filter(reaction_db.user_id.in_(similar_users))\
        .filter(post_db.created_datetime >= DAYS_BACK)\
        .all()
    return {post[0] for post in user_based_recommendations}



def fetch_content_based_recommendations(user_id, post_db = models.Post, clg_db = models.Challenge ):
    """
    content-based recommendations based on recent articles
    """
    liked_posts = fetch_liked_post_ids(user_id)
    liked_challenges = session.query(post_db.challenge_id).filter(post_db.id.in_(liked_posts)).all()
    recent_challenges = session.query(clg_db.id).all()

    recommended_challenges = {challenge[0] for challenge in recent_challenges} \
                        - {challenge[0] for challenge in liked_challenges}
    
    content_based_recommendations = session.query(post_db.id)\
        .filter(post_db.challenge_id.in_(recommended_challenges))\
        .filter(post_db.created_datetime >= DAYS_BACK)\
        .all()
    
    return {post[0] for post in content_based_recommendations}


def get_interesting_articles(user_id):
    liked_article_ids = fetch_liked_post_ids(user_id)
    
    # collaborative filtering is not appropriate for cold start users. 
    if len(liked_article_ids) == 0:
        return set() 
    
    # perform user and content based collaborative filtering. 
    else:
        user_based_recommendations = fetch_user_based_recommendations(user_id)
        content_based_recommendations = fetch_content_based_recommendations(user_id)

        recommended_articles = user_based_recommendations.union(content_based_recommendations)
        recommended_articles = recommended_articles - liked_article_ids.intersection(recommended_articles)

    return recommended_articles








if __name__ == "__main__":
    load_dotenv()

    SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}/{os.environ['DATABASE_NAME']}"

    # Define your database connection here (SQLite for example)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)  

    # Base class for your model classes
    Base = declarative_base()

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()
    


    ###
    ###
    ###





    # Close the session
    session.close()
