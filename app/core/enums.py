import enum

class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"

class AuditAction(str, enum.Enum):
    CREATED_USER = "created_user"
    UPDATED_USER = "updated_user"
    DELETED_USER = "deleted_user"
    CREATED_ORG = "created_org"
    UPDATED_ORG = "updated_org"
    DELETED_ORG = "deleted_org"