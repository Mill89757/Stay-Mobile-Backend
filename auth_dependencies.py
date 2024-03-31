from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from firebase_setup import firebase_app
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import os

# 设置OAuth2的Bearer类型认证模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print(token)
        # 这里是模拟验证JWT的逻辑
        payload = {"user_id": "some_user_id"}  # 示例载荷
        print(payload)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"},
        )

def conditional_depends(depends=Depends):
    def dependency_override():
        # 检查是否为测试环境
        if os.environ.get('MODE') == 'test':
            # 测试环境下，跳过实际的依赖项
            return lambda: {"user_id": "test_user_id"}
        else:
            # 生产环境下，返回实际的依赖项
            return depends
    return Depends(dependency_override())
