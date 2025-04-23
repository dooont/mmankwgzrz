"""
This module is for security access control based on roles.
"""

import data.people as ppl

# Action Constants
CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'

# Feature Constants
TEXT = 'text'

# Role Constants
CONSULTING_EDITOR = 'CE'
EDITOR = 'ED'
MANAGING_EDITOR = 'ME'

# Field Constants
FEATURE = 'feature'
ACTION = 'action'
USER_EMAIL = 'user_email'

# Permission rules: define which roles can do what on which feature
PERMISSION_RULES = {
    TEXT: {
        UPDATE: [CONSULTING_EDITOR, EDITOR, MANAGING_EDITOR],
    },
}


def is_permitted(feature: str, action: str, user_email: str) -> bool:
    """
    Checks if a user is allowed to perform the specified action on a feature.
    Looks up the required roles and checks if the user has any of them.
    """
    # If the feature/action is not protected, disallow by default
    if feature not in PERMISSION_RULES:
        return False
    if action not in PERMISSION_RULES[feature]:
        return False

    required_roles = PERMISSION_RULES[feature][action]
    user = ppl.read_one(user_email)
    if not user:
        return False

    for role in required_roles:
        if ppl.has_role(user, role):
            return True
    return False
