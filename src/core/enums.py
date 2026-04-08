from enum import Enum


class ApiTags(str, Enum):
    """API tags for router documentation."""

    ACCOUNT_MANAGEMENT = "Account Management"
    AUTH = "Accounts"
    PRODUCTS = "Products"
    CATEGORIES = "Categories"
    PERMISSIONS = "Permissions"
    PERMISSION_GROUPS = "Permission Groups"
    ADMIN_ACCOUNT_MANAGEMENT = "Admin Account Management"
