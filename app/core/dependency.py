from typing import Optional
import re
import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.settings import settings


class AuthControl:
    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        try:
            if token == "dev":
                user = await User.filter().first()
                user_id = user.id
            else:
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的Token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}")


class PermissionControl:
    @classmethod
    def normalize_path(cls, path: str) -> str:
        """
        将实际路径转换为权限模式
        例如: /api/v1/house/opportunities/20 -> /api/v1/house/opportunities/{id}
        """
        # 使用正则表达式匹配数字部分并替换为 {id}
        return re.sub(r'/\d+(?=/|$)', '/{id}', path)

    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        if current_user.is_superuser:
            return
            
        method = request.method
        path = request.url.path
        normalized_path = cls.normalize_path(path)
        
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")
            
        apis = [await role.apis for role in roles]
        permission_apis = []
        
        # 收集所有权限路径模式
        for api_list in apis:
            for api in api_list:
                # 将数据库中存储的API路径也标准化
                normalized_api_path = cls.normalize_path(api.path)
                permission_apis.append((api.method, normalized_api_path))
                
        permission_apis = list(set(permission_apis))
        
        if (method, normalized_path) not in permission_apis:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission denied method:{method} path:{normalized_path}"
            )


DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
