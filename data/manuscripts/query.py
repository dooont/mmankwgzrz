import data.manuscripts.fields as flds
import data.people as ppl
import data.roles as rls
import data.db_connect as dbc

from bson import ObjectId, errors


MANU_COLLECT = 'manuscripts'

# States Codes
AUTHOR_REVIEW = 'AU_RVW'
AUTHOR_REVISION = 'AU_REV'
COPY_EDIT = 'CED'
EDITOR_REVIEW = 'ED_RVW'
FORMATTING = 'FMT'
PUBLISHED = 'PUB'
REFEREE_REVIEW = 'REF_RVW'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
WITHDRAWN = 'WDN'

VALID_STATES = {
    AUTHOR_REVIEW: 'Author Review',
    AUTHOR_REVISION: 'Author Revision',
    COPY_EDIT: 'Copy Edit',
    EDITOR_REVIEW: 'Editor Review',
    FORMATTING: 'Formatting',
    PUBLISHED: 'Published',
    REFEREE_REVIEW: 'Referee Review',
    REJECTED: 'Rejected',
    SUBMITTED: 'Submitted',
    WITHDRAWN: 'Withdrawn',
}

# States of when the role can choose action on manuscript
EDITOR_CHOOSE_ACTION = [SUBMITTED, REFEREE_REVIEW, EDITOR_REVIEW, COPY_EDIT, FORMATTING]

ROLE_CHOOSE_ACTION = {
    rls.ED_CODE: EDITOR_CHOOSE_ACTION,
    rls.CE_CODE: EDITOR_CHOOSE_ACTION,
    rls.ME_CODE: EDITOR_CHOOSE_ACTION,
    rls.AUTHOR_CODE: [AUTHOR_REVISION, AUTHOR_REVIEW],
    rls.RE_CODE: [REFEREE_REVIEW]
}

# Action Codes
ACTION_ACCEPT = 'ACC'
ACTION_ACCEPT_WITH_REV = 'AWR'
ACTION_ASSIGN_REF = 'ARF'
ACTION_DELETE_REF = 'DRF'
ACTION_DONE = 'DON'
ACTION_REJECT = 'REJ'
ACTION_SUBMIT_REVIEW = 'SBR'
ACTION_WITHDRAW = 'WDN'

ACTION_NAMES = {
    ACTION_ACCEPT: 'Accept',
    ACTION_ACCEPT_WITH_REV: 'Accept with Revisions',
    ACTION_ASSIGN_REF: 'Assign Referee',
    ACTION_DELETE_REF: 'Delete Referee',
    ACTION_DONE: 'Done',
    ACTION_REJECT: 'Reject',
    ACTION_SUBMIT_REVIEW: 'Submit Review',
    ACTION_WITHDRAW: 'Withdraw',
}

TEST_STATE = SUBMITTED
TEST_ACTION = ACTION_ACCEPT

SAMPLE_MANU = {
    flds.TITLE: 'Sample Manuscript',
    flds.AUTHOR: 'Andy Ng',
    flds.AUTHOR_EMAIL: 'an3299@Nyu.edu',
    flds.REFEREES: [],
    flds.STATE: SUBMITTED,
    flds.TEXT: "Text",
    flds.ABSTRACT: 'Abstract',
}

FUNC = 'f'


def get_states() -> dict:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


def get_actions() -> dict:
    return ACTION_NAMES


def is_valid_action(action: str) -> bool:
    return action in ACTION_NAMES


def create_manuscript(title: str, author: str, author_email: str, referee: str, state: str, text: str, abstract: str) -> str:
    if not ppl.exists(author_email):
        raise ValueError('Author does not exist')

    # Add author role when you submit manuscript
    author_info = ppl.read_one(author_email)
    roles = author_info.get(ppl.ROLES, [])
    if rls.AUTHOR_CODE not in roles:
        updated_roles = roles + [rls.AUTHOR_CODE]
        ppl.update(author_info[ppl.NAME], author_info[ppl.AFFILIATION], author_email, updated_roles)

    if not is_valid_state(state):
        raise ValueError(f'Invalid state: {state}')
    
    referees = [referee] if referee else []
    manuscript = {
        flds.TITLE: title,
        flds.AUTHOR: author,
        flds.AUTHOR_EMAIL: author_email, 
        flds.REFEREES: referees,
        flds.STATE: state,
        flds.TEXT: text,
        flds.ABSTRACT: abstract,
    }
    
    result = dbc.create(MANU_COLLECT, manuscript)
    inserted_doc = dbc.read_one(MANU_COLLECT, {flds.ID: result.inserted_id})
    return str(inserted_doc[flds.ID])


def update(id: str, title: str, author: str, author_email: str, referee: str, state: str, text: str, abstract: str) -> str:
    """ 
    Updates an existing manuscripts information in the db. 
    If manuscript doesn't exist then a ValueError is raised.
    """
    if not exists(id):
        raise ValueError(f'Can not update non-existent manuscript: {id=}')
    
    if referee: 
        if not ppl.is_valid_email(author_email):
            raise ValueError(f'Email is invalid: {referee=}')
    
    if not ppl.exists(author_email):
        raise ValueError(f'Author doesnt exist: {author_email=}')
    
    if not is_valid_state(state):
        raise ValueError(f'Invalid state: {state=}')
    
    manuscript = { 
            flds.TITLE: title,
            flds.AUTHOR: author,
            flds.AUTHOR_EMAIL: author_email,
            flds.REFEREES: referee,
            flds.STATE: state,
            flds.TEXT: text,
            flds.ABSTRACT: abstract,
        }
    
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise ValueError(f"Invalid ObjectId: {id}")

    dbc.update(MANU_COLLECT, {flds.ID: object_id}, manuscript)
    return id


def get_manuscripts() -> dict[str, dict]:
    """
    Retrieves all manuscripts from the database.
    Returns a dictionary of dictionaries:
    {id: each manuscript represented by a dictionary}
    """
    manuscripts = dbc.read_dict(MANU_COLLECT, flds.ID, no_id=False)
    return manuscripts


def get_one_manu(id: str) -> dict:
    """
    Retrieves a manuscript from the database, by taking in an email.
    """
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise ValueError(f"Invalid ObjectId: {id}")
    
    manuscript = dbc.read_one(MANU_COLLECT, {flds.ID: object_id})
    return manuscript


def delete(id: str) -> int:
    """ 
    Deletes a selected manusciprt from the database.
    """
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise ValueError(f"Invalid ObjectId: {id}")
    
    return dbc.delete(MANU_COLLECT, {flds.ID: object_id})


def exists(id: str) -> bool:
    """
    Checks if a manuscript with the given title exists in the database.
    """
    try:
        manuscript = get_one_manu(id)
        return manuscript is not None
    except ValueError:
        return False


def assign_ref(manu: dict, ref: str) -> str:
    if ref in manu[flds.REFEREES]:
        raise ValueError(f'Referee already in manuscript: {ref}')
    manu[flds.REFEREES].append(ref)
    return REFEREE_REVIEW


def delete_ref(manu: dict, ref: str) -> str:
    if ref not in manu[flds.REFEREES]:
        raise ValueError(f'Referee not in manuscript: {ref}')
    manu[flds.REFEREES].remove(ref)
    if manu[flds.REFEREES]:
        return REFEREE_REVIEW
    return SUBMITTED


def get_active_manuscripts(user_email):
    """
    Returns active manuscripts visible to the given user.
    """
    active_manuscripts = []
    manuscripts = get_manuscripts()
    user_info = ppl.read_one(user_email)
    user_roles = user_info.get(ppl.ROLES, [])

    for manu in manuscripts.values():
        manu_state = manu[flds.STATE]

        # Skip withdrawn/published/rejected
        if manu_state in (WITHDRAWN, PUBLISHED, REJECTED):
            continue

        # Editors see all active manuscripts
        if any(role in rls.MH_ROLES for role in user_roles):
            active_manuscripts.append(manu)
            continue

        # Authors or referees see only their own
        is_author = user_email == manu[flds.AUTHOR_EMAIL]
        is_referee = user_email in manu[flds.REFEREES]
        if is_author or is_referee:
            active_manuscripts.append(manu)
    
    # Sort manuscripts by state
    state_order = [
        SUBMITTED, REFEREE_REVIEW, AUTHOR_REVISION, EDITOR_REVIEW, COPY_EDIT, AUTHOR_REVIEW, FORMATTING 
    ]

    active_manuscripts.sort(key=lambda m: state_order.index(m[flds.STATE]))

    return active_manuscripts


COMMON_ACTIONS = {
    ACTION_WITHDRAW: {
        FUNC: lambda **kwargs: WITHDRAWN,
    },
}

STATE_TABLE = {
    AUTHOR_REVIEW: {
        ACTION_DONE: {
            FUNC: lambda **kwargs: FORMATTING,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REVISION: {
        ACTION_DONE: {
            FUNC: lambda **kwargs: EDITOR_REVIEW,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        ACTION_DONE: {
            FUNC: lambda **kwargs: AUTHOR_REVIEW,
        },
        **COMMON_ACTIONS,
    },
    EDITOR_REVIEW: {
        ACTION_ACCEPT: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        **COMMON_ACTIONS,
    },
    FORMATTING: {
        ACTION_DONE: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
        **COMMON_ACTIONS,
    },
    PUBLISHED: {},
    REFEREE_REVIEW: {
        ACTION_ACCEPT: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        ACTION_REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        ACTION_ACCEPT_WITH_REV: {
            FUNC: lambda **kwargs: AUTHOR_REVISION,
        },
        ACTION_ASSIGN_REF: {
            FUNC: assign_ref,
        },
        ACTION_DELETE_REF: {
            FUNC: delete_ref,
        },
        ACTION_SUBMIT_REVIEW: {
            FUNC: lambda **kwargs: REFEREE_REVIEW,
        },
        **COMMON_ACTIONS,
    }, 
    REJECTED: {},
    SUBMITTED: {
        ACTION_ASSIGN_REF: {
            FUNC: assign_ref,
        },
        ACTION_REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {},
}

                
def handle_action(curr_state, action, **kwargs) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Invalid state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'Invalid action: {action}')

    return STATE_TABLE[curr_state][action][FUNC](**kwargs)


def can_choose_action(manu_id: str, user_email: str) -> bool:
    manu = get_one_manu(manu_id)
    manu_author = manu[flds.AUTHOR_EMAIL]
    manu_referees = manu[flds.REFEREES]
    manu_state = manu[flds.STATE]
    user_info = ppl.read_one(user_email)
    user_roles = user_info.get(ppl.ROLES, [])

    # Author logic
    if user_email == manu_author:
        if ACTION_WITHDRAW in STATE_TABLE.get(manu_state, {}):
            return True
        if manu_state in ROLE_CHOOSE_ACTION.get(rls.AUTHOR_CODE, []):
            return True

    # Referee logic
    if rls.RE_CODE in user_roles and user_email in manu_referees:
        if manu_state in ROLE_CHOOSE_ACTION.get(rls.RE_CODE, []):
            return True

    # Editor logic
    if user_email != manu_author:
        for editor_role in rls.MH_ROLES:
            if editor_role in user_roles:
                if manu_state in ROLE_CHOOSE_ACTION.get(editor_role, []):
                    return True

    return False


def can_move_action(manu_id, user_email) -> bool:
    manu = get_one_manu(manu_id)
    manu_author = manu[flds.AUTHOR_EMAIL]
    # manu_referees = manu[flds.REFEREES]
    manu_state = manu[flds.STATE]
    user_info = ppl.read_one(user_email)
    user_roles = user_info.get(ppl.ROLES, [])

    #Editor logic ONLY
    if user_email != manu_author:
        for editor_role in rls.MH_ROLES:
            if editor_role in user_roles:
                if manu_state in VALID_STATES:
                    return True
                
    return False


EDITOR_ROLE_ACTIONS = {
    SUBMITTED: [ACTION_ASSIGN_REF, ACTION_REJECT],
    REFEREE_REVIEW: [
        ACTION_ASSIGN_REF,
        ACTION_DELETE_REF,
        ACTION_ACCEPT,
        ACTION_ACCEPT_WITH_REV,
        ACTION_REJECT,
    ],
    EDITOR_REVIEW: [ACTION_ACCEPT],
    COPY_EDIT: [ACTION_DONE],
    FORMATTING: [ACTION_DONE],

}

ROLE_STATE_ACTIONS = {
    rls.AUTHOR_CODE: {
        AUTHOR_REVIEW: [ACTION_DONE],
        AUTHOR_REVISION: [ACTION_DONE],
    },
    rls.RE_CODE: {
        REFEREE_REVIEW: [ACTION_SUBMIT_REVIEW],
    },
    rls.ED_CODE: EDITOR_ROLE_ACTIONS,
    rls.ME_CODE: EDITOR_ROLE_ACTIONS,
    rls.CE_CODE: EDITOR_ROLE_ACTIONS,
}


def get_valid_actions(manu_id: str, user_email: str) -> list[str]:
    """
    Returns the list of valid actions the user can perform on the manuscript.
    """
    if not can_choose_action(manu_id, user_email):
        return []

    manu = get_one_manu(manu_id)
    manu_state = manu[flds.STATE]

    user_info = ppl.read_one(user_email)
    if not user_info:
        raise ValueError(f"No such user: {user_email}")
    user_roles = user_info.get(ppl.ROLES, [])

    result = []
    is_author = user_email == manu[flds.AUTHOR_EMAIL]
    is_referee = user_email in manu[flds.REFEREES]
    next_actions = STATE_TABLE.get(manu_state, {}).keys()

    for role in user_roles:
        # Skip editor actions on your own manuscript
        if is_author and role in rls.MH_ROLES:
            continue

        # Allow referee actions only if you're actually assigned
        if role == rls.RE_CODE and not is_referee:
            continue

        state_actions = ROLE_STATE_ACTIONS.get(role, {})
        allowed = state_actions.get(manu_state, [])

        for action in allowed:
            if action in next_actions and action not in result:
                result.append(action)

    # Author can always withdraw
    if is_author and ACTION_WITHDRAW in next_actions and ACTION_WITHDRAW not in result:
        result.append(ACTION_WITHDRAW)

    return result

def get_valid_states(manu_id: str, user_emai: str) ->list[str]:
    """
    Returns list of approriate states the editor can move the manuscript to.
    """
    if not can_move_action(manu_id, user_emai):
        return []
    
    manu = get_one_manu(manu_id)
    manu_state = manu[flds.STATE]

    states = []
    for state in VALID_STATES:
        if state != manu_state and state not in states:
            if state != WITHDRAWN:
                states.append(state)

    return states
    
   
def main():
    print(handle_action(SUBMITTED, ACTION_ASSIGN_REF, manu=SAMPLE_MANU, ref='kw3000@nyu.edu'))


if __name__ == '__main__':
    main()
