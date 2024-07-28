import os

from firebase_admin import auth
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status


# Set OAuth2 Bearer authentication mode
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2_scheme)):
    """ Verify the token and return the payload """
    try:
        # Simulate the verification of JWT
        # Example payload: payload = {"user_id": "some_user_id"}
        payload = auth.verify_id_token(token)
        return payload
    except auth.InvalidTokenError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex
    except auth.ExpiredTokenError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


def conditional_depends(depends=Depends):
    """ Conditional dependency override """
    def dependency_override():
        # Check if it is a test environment
        if os.environ.get('MODE') == 'test':
            # Test environment, skip actual dependencies
            return lambda: {"user_id": "test_user_id"}
        # Production environment, return actual dependencies
        return depends
    return Depends(dependency_override())
