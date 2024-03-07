from cmath import asin
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.challenge as challenge_crud
from typing import List

# create routes for challenges operations and functions
router = APIRouter()

# create challenge
@router.post("/CreateChallenge/", response_model=schemas.ChallengeRead, status_code=status.HTTP_201_CREATED)
async def create_challenge_route(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    return challenge_crud.create_challenge(db=db, challenge=challenge)

# read challenge by id
@router.get("/GetChallenge/{challenge_id}", response_model=schemas.ChallengeRead)
async def get_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    """read challenge by id
    
    Args:
        challenge_id: id of challenge

    Returns:
        challenge
    
    Raises:
        HTTPException: challenge not found
    """
    challenge = challenge_crud.get_challenge(db=db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

@router.get("/GetChallengeByUserIdAndChallengeId/{user_id}/{challenge_id}", response_model=schemas.ChallengeRead)
async def get_challenge_by_user_and_challenge_route(user_id: int, challenge_id: int, db: Session = Depends(get_db)):
    """read challenge by challenge id and user id
    
    Args:
        user_id: id of user
        challenge_id: id of challenge

    Returns:
        challenge
    
    Raises:
        HTTPException: challenge not found
    """
    challenge = challenge_crud.get_challenge_by_user_id_and_challenge_id(db=db, user_id=user_id,challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

TIMEZONE_MAPPING = {
    "Sydney": ["Australia/Sydney", "Australia/Melbourne"],
    "Perth": ["Australia/Perth"],
    "Brisbane": ["Australia/Brisbane"],
    "Beijing": ["Asia/Shanghai"],
    # ... 其他映射
}
# update breaking days for specific challenges
@router.post("/test/update_breaking_days/{timezone}")
def test_update_breaking_days(timezone: str, db: Session = Depends(get_db)):
    
    # Attempt to get the list of timezones from the mapping
    timezones = TIMEZONE_MAPPING.get(timezone)
    
    # If the timezone is not found, use "UTC" as default
    if not timezones:
        full_timezone_str = "UTC"
    else:
        # If the timezone is found and it is a list, use the first entry
        full_timezone_str = timezones

    challenge_crud.update_breaking_days_for_specific_challenges(db, full_timezone_str)
    return {"message": f"Breaking days updated successfully for timezone {timezone}"}



# read all challenges of one user by user id 
@router.get("/GetUserChallenges/{user_id}", response_model=List[List[schemas.ChallengeWithBreakingDays]])
async def get_user_challenges_route(user_id: int, db: Session = Depends(get_db)):
    """read all challenges of one user by user id
    
    Args:
        user_id: id of user
    
    Returns:
        list of active challenges and finished challenges
    
    Raises:
        HTTPException: user not found
    """
    active_challenges = challenge_crud.get_active_challenges_by_user_id(db, user_id)
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(db, user_id)
    return [active_challenges, finished_challenges]

# read last challenge of one user by user id
@router.get("/GetUserLastChallenges{user_id}", response_model=schemas.ChallengeRead)
async def get_user_last_challenge(user_id: int, db: Session = Depends(get_db)):
    """read last challenge of one user by user id
    
    Args:
        user_id: id of user

    Returns:
        last_challenge: last challenge

    Raises:
        HTTPException: user not found
    """
    last_challenges = challenge_crud.get_last_challenge_by_user_id(db, user_id)
    return last_challenges

# read active challenges of one user by user id
@router.get("/GetUserActiveChallenges/{user_id}", response_model=List[schemas.ChallengeWithBreakingDays])
async def get_user_active_challenges_route(user_id: int, db: Session = Depends(get_db)):
    """read active challenges list of one user by user id
    
    Args:
        user_id: id of user
    
    Returns:
        active_challenges: list of active challenges

    Raises:
        HTTPException: user not found
    """
    active_challenges = challenge_crud.get_active_challenges_by_user_id(db, user_id)
    return active_challenges

# read challenges list by course id
@router.get("/GetChallengesWithCourseID/{course_id}", response_model=List[schemas.ChallengeRead])
async def get_challenge_courseID(course_id: int, db: Session = Depends(get_db)):
    """read challenges list by course id
    
    Args:
        course_id: id of course
        
    Returns:
        challenges_with_course_id: list of challenges
    
    Raises:
        HTTPException: Course not found
    """
    CourseID_related_challenges = challenge_crud.get_challenges_by_course_id(db, course_id)
    return CourseID_related_challenges

# read finished challenges list of one user by user id
@router.get("/GetUserFinishedChallenges/{user_id}", response_model=List[schemas.ChallengeWithBreakingDays])
async def get_user_finished_challenges_route(user_id: int, db: Session = Depends(get_db)):
    """read finished challenges list of one user by user id
    
    Args:
        user_id: id of user

    Returns:
        finished_challenges: list of finished challenges
    
    Raises:
        HTTPException: user not found
    """
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(db, user_id)
    return finished_challenges

@router.get("/GetAllChallenges/", response_model=list[schemas.ChallengeRead])
async def get_challenges_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return challenge_crud.get_challenges(db=db, skip=skip, limit=limit)

@router.get("/GetBreakingDaysLeftByUserIdAndChallengeId/{user_id}/{challenge_id}", response_model=schemas.GroupChallengeMembersRead)
async def get_challenge_breaking_days_left(user_id: int, challenge_id:int ,db: Session = Depends(get_db)):
    """read challenge breaking days left by user id and challenge id
    
    Args:
        user_id: id of user
        challenge_id: id of challenge
        
    Returns:
        challenge_breaking_days_left: challenge breaking days left
    
    Raises:
        HTTPException: user not found
        HTTPException: challenge not found
    """
    return challenge_crud.get_challenge_breaking_days_left(db, user_id, challenge_id)

@router.put("/UpdateChallenge/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_route(challenge_id: int, challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    updated_challenge = challenge_crud.update_challenge(db=db, challenge_id=challenge_id, challenge=challenge)
    if updated_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return updated_challenge

# delete challenges by challenge id
@router.delete("/DeleteChallenge/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    if not challenge_crud.delete_challenge(db=db, challenge_id=challenge_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Challenge deleted successfully"})

# 中途退出group challenge
@router.delete("/DeleteGroupChallengeMember/{challenge_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_challenge_member_route(challenge_id: int, user_id:int, db: Session = Depends(get_db)):
    """delete group challenge member by challenge id and user id

    Args:
        challenge_id: id of challenge
        user_id: id of user

    Raises:
        Challenge not found or member not found
    """
    if not challenge_crud.delete_group_challenge_member(db=db, challenge_id=challenge_id, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge or member not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Challenge member deleted successfully"})


@router.get("/SetInvitationCodeByChallengeID/{challenge_id}")
async def generate_invitation_code(challenge_id: int, db: Session = Depends(get_db)):
    """generate invitation code by challenge_id
    
    Args:
        challenge_id: id of challenge
        
    Returns:
        invitation code
    """
    result = challenge_crud.generate_invitation_code(db=db, challenge_id = challenge_id)
    return result


@router.get("/GetChallengeInfoByInvitationCode/{unique_token}")
async def get_challenge_info_by_invitation_code(unique_token: str, db: Session = Depends(get_db)):
    result = challenge_crud.get_challenge_info_by_code(db=db, unique_token = unique_token)
    return result


@router.post("/JoinGroupChallengeByInvite/{user_id}/{token}")
async def invitation(token: str, user_id:int, db: Session = Depends(get_db)):
    result = challenge_crud.join_group_challenge_by_token_and_user_id(db=db, unique_token=token, user_id=user_id)
    return result


# read discover challenges 拿discover challenge
@router.get("/GetDiscoverChallenges/")
async def get_discover_challenges(db: Session = Depends(get_db)):
    """read discover challenges"""
    discover_challenges = challenge_crud.get_discover_challenges(db)
    return discover_challenges


@router.get("/GetChallengeDetailsPartA/{challenge_id}")
async def get_challenge_details_first_half(challenge_id: int, db:Session = Depends(get_db)):
    """read first half information need by challenge details page by challenge_id
    
    Args:
        challenge_id: id of challenge
        
    Returns:
        result: first half information need by challenge details page
    
    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_details_page_first_half_by_challengeID(db, challenge_id)
    return result


@router.get("/GetChallengeDetailsPartB/{challenge_id}")
async def get_challenge_details_second_half(challenge_id: int, db:Session = Depends(get_db)):
    """read second half information need by challenge details page by challenge_id
    
    Args:
        challenge_id: id of challenge
        
    Returns:
        result: first half information need by challenge details page
    
    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_details_page_second_half_by_challengeID(db, challenge_id)
    return result


@router.get("/getChallengeCategoryDistribution/{user_id}")
def get_challenge_category_distribution(user_id: int, db: Session = Depends(get_db)):
    """read challenge category distribution by user id
    
    Args:
        user_id: id of user
        
    Returns:
        result: list of challenge category distribution
        
    Raises:
        HTTPException: user not found
    """
    return challenge_crud.get_challenge_category_distribution(db, user_id)


@router.get("/GetChallengeCard/{challenge_id}")
async def get_challenge_card(challenge_id: int, db:Session = Depends(get_db)):
    """read information need by challenge card by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        challenge card information
    
    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_card_by_challengeID(db, challenge_id)
    return result

@router.get("/GetGroupChallengeMembers/{challenge_id}")
async def get_group_challenge_members(challenge_id: int, db:Session = Depends(get_db)):
    """read group challenge members by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        group challenge members
    
    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.get_group_challenge_members(db, challenge_id)
    return result

# check if user is the challenge owner or not
@router.get("/CheckOwner/{challenge_id}")
async def check_challenge_owner(challenge_id: int, user_id: int, db: Session=Depends(get_db)):
    result = challenge_crud.check_challenge_onwer(challenge_id=challenge_id, user_id=user_id, db=db)
    return result