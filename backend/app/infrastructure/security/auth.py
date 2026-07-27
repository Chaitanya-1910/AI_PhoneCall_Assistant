import time
from typing import Dict, Any, Optional
from jose import jwt, JWTError

class SecurityManager:
    """
    Handles JWT generation, validation, and Role Based Access Control (RBAC).
    """
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def create_access_token(self, subject: str, role: str, expires_delta_sec: int = 3600) -> str:
        to_encode = {
            "sub": subject,
            "role": role,
            "exp": time.time() + expires_delta_sec
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
            
    def require_role(self, token: str, required_role: str) -> bool:
        payload = self.verify_token(token)
        if not payload:
            return False
        return payload.get("role") == required_role
