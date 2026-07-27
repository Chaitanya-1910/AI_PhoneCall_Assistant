from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

class Tenant(BaseModel):
    """
    Base organization/tenant in the multi-tenant architecture.
    """
    tenant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tier: str = "ENTERPRISE"
    settings: Dict[str, Any] = Field(default_factory=dict)
    
class Team(BaseModel):
    """
    A logical grouping within a tenant.
    """
    team_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str

class UserRole(BaseModel):
    """
    RBAC Role within a tenant.
    """
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    permissions: List[str] = Field(default_factory=list)

class TenantUser(BaseModel):
    """
    A dashboard user or agent scoped to a tenant.
    """
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    email: str
    role_id: str
