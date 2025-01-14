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
        # 分割路径
        parts = path.split('/')
        normalized_parts = []
        
        # 获取路径结构
        path_structure = {
            'opportunity': 'opportunity_id',  # 添加特定路径的参数映射
            'opportunities': 'id',
            'communities': 'id',
            'ershoufangs': 'id',
            'deal-records': 'id'
        }
        
        for part in parts:
            # 如果部分是纯数字，替换为对应的参数名
            if part.isdigit():
                # 查找前一个部分来确定参数名
                prev_part = normalized_parts[-1].split('/')[-1] if normalized_parts else ''
                param_name = path_structure.get(prev_part, 'id')
                normalized_parts.append('{' + param_name + '}')
            else:
                normalized_parts.append(part)
        
        # 重新组合路径
        return '/'.join(normalized_parts)

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
            
        # 检查每个角色的权限
        for role in roles:
            apis = await role.apis.all()
            for api in apis:
                # 检查方法和路径是否匹配
                if api.method == method and api.path == normalized_path:
                    return
  
        # 如果没有找到匹配的权限，抛出异常
        raise HTTPException(
            status_code=403,
            detail={
                'code': 403,
                'message': f'Permission denied method:{method} path:{path}',
                'error': {
                    'type': 'permission_denied',
                    'message': '没有访问权限'
                }
            }
        )


DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
