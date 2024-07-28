# pylint: disable=unused-argument

from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import CRUD.blocked_user_list as block_crud
import CRUD.challenge as challenge_crud
import schemas
from auth_dependencies import conditional_depends, verify_token
from database import get_db

load_dotenv()

router = APIRouter()

TIMEZONE_MAPPING = {
    "Sydney": ["Australia/Sydney", "Australia/Melbourne"],
    "Perth": ["Australia/Perth"],
    "Brisbane": ["Australia/Brisbane"],
    "Beijing": ["Asia/Shanghai"],
}


@router.post("/CreateChallenge/", response_model=schemas.ChallengeRead,
             status_code=status.HTTP_201_CREATED)
async def create_challenge_route(
        challenge: schemas.ChallengeCreate, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Create challenge """
    return challenge_crud.create_challenge(db=db, challenge=challenge)


@router.get("/GetChallenge/{challenge_id}", response_model=schemas.ChallengeRead)
async def get_challenge_route(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read challenge by id

    Args:
        challenge_id: id of challenge

    Returns:
        challenge

    Raises:
        HTTPException: challenge not found
    """
    challenge = challenge_crud.get_challenge(db=db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge


@router.get("/GetChallengeByUserIdAndChallengeId/{user_id}/{challenge_id}",
            response_model=schemas.ChallengeRead)
async def get_challenge_by_user_and_challenge_route(
        user_id: int, challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read challenge by challenge id and user id

    Args:
        user_id: id of user
        challenge_id: id of challenge

    Returns:
        challenge

    Raises:
        HTTPException: challenge not found
    """
    challenge = challenge_crud.get_challenge_by_user_id_and_challenge_id(
        db=db, user_id=user_id, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge


@router.post("/test/update_breaking_days/{timezone}")
def test_update_breaking_days(timezone: str, db: Session = Depends(get_db)):
    """ Update breaking days for all challenges in the database based on the timezone provided """

    # Attempt to get the list of timezones from the mapping
    timezones = TIMEZONE_MAPPING.get(timezone)

    # If the timezone is not found, use "UTC" as default
    if not timezones:
        full_timezone_str = "UTC"
    else:
        # If the timezone is found and it is a list, use the first entry
        full_timezone_str = timezones

    challenge_crud.update_breaking_days_for_specific_challenges(
        db, full_timezone_str)
    return {"message": f"Breaking days updated successfully for timezone {timezone}"}


@router.get("/GetUserChallenges/{user_id}",
            response_model=List[List[schemas.ChallengeWithBreakingDays]])
async def get_user_challenges_route(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read all challenges of one user by user id

    Args:
        user_id: id of user

    Returns:
        list of active challenges and finished challenges

    Raises:
        HTTPException: user not found
    """
    active_challenges = challenge_crud.get_active_challenges_by_user_id(
        db, user_id)
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(
        db, user_id)
    return [active_challenges, finished_challenges]


@router.get("/GetUserLastChallenges{user_id}", response_model=schemas.ChallengeRead)
async def get_user_last_challenge(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read last challenge of one user by user id

    Args:
        user_id: id of user

    Returns:
        last_challenge: last challenge

    Raises:
        HTTPException: user not found
    """
    last_challenges = challenge_crud.get_last_challenge_by_user_id(db, user_id)
    return last_challenges


@router.get("/GetUserActiveChallenges/{user_id}",
            response_model=List[schemas.ChallengeWithBreakingDays])
async def get_user_active_challenges_route(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read active challenges list of one user by user id

    Args:
        user_id: id of user

    Returns:
        active_challenges: list of active challenges

    Raises:
        HTTPException: user not found
    """
    active_challenges = challenge_crud.get_active_challenges_by_user_id(
        db, user_id)
    return active_challenges


@router.get("/GetChallengesWithCourseID/{course_id}", response_model=List[schemas.ChallengeRead])
async def get_challenge_course_id(
        course_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read challenges list by course id

    Args:
        course_id: id of course

    Returns:
        challenges_with_course_id: list of challenges

    Raises:
        HTTPException: Course not found
    """
    course_id_related_challenges = challenge_crud.get_challenges_by_course_id(
        db, course_id)
    return course_id_related_challenges


@router.get("/GetUserFinishedChallenges/{user_id}",
            response_model=List[schemas.ChallengeWithBreakingDays])
async def get_user_finished_challenges_route(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read finished challenges list of one user by user id

    Args:
        user_id: id of user

    Returns:
        finished_challenges: list of finished challenges

    Raises:
        HTTPException: user not found
    """
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(
        db, user_id)
    return finished_challenges


@router.get("/GetAllChallenges/{user_id}", response_model=list[schemas.ChallengeRead])
async def get_challenges_route(user_id: int, db: Session = Depends(get_db),
                               current_user: dict = conditional_depends(depends=verify_token)):
    """ Read all challenges of one user by user id """
    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=user_id)

    return challenge_crud.get_challenges(db=db, blocked_user_list=blocked_user_list)


@router.get("/GetBreakingDaysLeftByUserIdAndChallengeId/{user_id}/{challenge_id}",
            response_model=schemas.GroupChallengeMembersRead)
async def get_challenge_breaking_days_left(
        user_id: int, challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read challenge breaking days left by user id and challenge id

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


@router.put("/UpdateChallenge/{challenge_id}",
            response_model=schemas.ChallengeRead)
async def update_challenge_route(
        challenge_id: int, challenge: schemas.ChallengeCreate, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Update challenge by challenge id """
    updated_challenge = challenge_crud.update_challenge(
        db=db, challenge_id=challenge_id, challenge=challenge)
    if updated_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return updated_challenge


@router.delete("/DeleteChallenge/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge_route(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Delete challenge by challenge id """
    if not challenge_crud.delete_challenge(db=db, challenge_id=challenge_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Challenge deleted successfully"})


@router.delete("/DeleteUserAccount/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Delete user account by user id """
    if not challenge_crud.delete_user_account(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "User Account deleted successfully"})


@router.delete("/DeleteGroupChallengeMember/{challenge_id}/{user_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_challenge_member_route(
        challenge_id: int, user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Delete group challenge member by challenge id and user id

    Args:
        challenge_id: id of challenge
        user_id: id of user

    Raises:
        Challenge not found or member not found
    """
    if not challenge_crud.delete_group_challenge_member(
            db=db, challenge_id=challenge_id, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Challenge or member not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Challenge member deleted successfully"})


@router.get("/SetInvitationCodeByChallengeID/{challenge_id}")
async def generate_invitation_code(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Generate invitation code by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        invitation code
    """
    result = challenge_crud.generate_invitation_code(
        db=db, challenge_id=challenge_id)
    return result


@router.get("/GetChallengeInfoByInvitationCode/{unique_token}")
async def get_challenge_info_by_invitation_code(
        unique_token: str, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Get challenge information by invitation code """
    result = challenge_crud.get_challenge_info_by_code(
        db=db, unique_token=unique_token)
    return result


@router.post("/JoinGroupChallengeByInvite/{user_id}/{token}")
async def invitation(
        token: str, user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Join group challenge by invitation code """
    result = challenge_crud.join_group_challenge_by_token_and_user_id(
        db=db, unique_token=token, user_id=user_id)
    return result


@router.get("/GetDiscoverChallenges/")
async def get_discover_challenges(
        db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read discover challenges """
    discover_challenges = challenge_crud.get_discover_challenges(db)
    return discover_challenges


@router.get("/GetChallengeDetailsPartA/{challenge_id}")
async def get_challenge_details_first_half(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read first half information need by challenge details page by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        result: first half information need by challenge details page

    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_details_page_first_half_by_challenge_ID(
        db, challenge_id)
    return result


@router.get("/GetChallengeDetailsPartB/{challenge_id}")
async def get_challenge_details_second_half(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read second half information need by challenge details page by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        result: first half information need by challenge details page

    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_details_page_second_half_by_challenge_ID(
        db, challenge_id)
    return result


@router.get("/getChallengeCategoryDistribution/{user_id}")
def get_challenge_category_distribution(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read challenge category distribution by user id

    Args:
        user_id: id of user

    Returns:
        result: list of challenge category distribution

    Raises:
        HTTPException: user not found
    """
    return challenge_crud.get_challenge_category_distribution(db, user_id)


@router.get("/GetChallengeCard/{challenge_id}")
async def get_challenge_card(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read information need by challenge card by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        challenge card information

    Raises:
        HTTPException: challenge not found
    """
    result = challenge_crud.challenge_card_by_challengeID(db, challenge_id)
    return result


@router.get("/GetGroupChallengeMembers/{challenge_id}/{user_id}")
async def get_group_challenge_members(
        challenge_id: int, user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read group challenge members by challenge_id

    Args:
        challenge_id: id of challenge

    Returns:
        group challenge members

    Raises:
        HTTPException: challenge not found
    """
    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=user_id)

    result = challenge_crud.get_group_challenge_members(
        db, challenge_id, blocked_user_list=blocked_user_list)

    return result


@router.get("/CheckOwner/{challenge_id}")
async def check_challenge_owner(
        challenge_id: int, user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Check if the user is the owner of the challenge """
    result = challenge_crud.check_challenge_owner(
        challenge_id=challenge_id, user_id=user_id, db=db)
    return result


@router.get("/GetUserChallengesWithToken_Testing/{user_id}",
            response_model=List[List[schemas.ChallengeWithBreakingDays]])
async def get_user_challenges_route_with_token(user_id: int, db: Session = Depends(get_db)):
    """ Read all challenges of one user by user id

    Args:
        user_id: id of user

    Returns:
        list of active challenges and finished challenges

    Raises:
        HTTPException: user not found
    """
    active_challenges = challenge_crud.get_active_challenges_by_user_id(
        db, user_id)
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(
        db, user_id)
    return [active_challenges, finished_challenges]
