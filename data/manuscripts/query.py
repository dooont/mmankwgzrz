import data.manuscripts.fields as flds
import data.people as ppl
import data.db_connect as dbc

from bson import ObjectId, errors


MANU_COLLECT = 'manuscripts'

# States
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

TEST_STATE = SUBMITTED

# Actions
ACTIONS = {
    'ACCEPT': 'ACC',
    'ACCEPT_WITH_REV': 'AWR',
    'ASSIGN_REF': 'ARF',
    'DELETE_REF': 'DRF',
    'DONE': 'DON',
    'REJECT': 'REJ',
    'WITHDRAW': 'WDN',
}

VALID_ACTIONS = list(ACTIONS.values())

TEST_ACTION = ACTIONS['ACCEPT']

SAMPLE_MANU = {
    flds.TITLE: 'Sample Manuscript',
    flds.AUTHOR: 'Andy Ng',
    flds.AUTHOR_EMAIL: 'an3299@Nyu.edu',
    flds.REFEREES: [],
    flds.STATE: SUBMITTED,
    flds.ACTION: ACTIONS['ASSIGN_REF'],
}

FUNC = 'f'


def get_states() -> dict:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


def get_actions() -> list[str]:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def create_manuscript(title: str, author: str, author_email: str, referee: str, state: str) -> str:
    if not ppl.exists(author_email):
        raise ValueError('Author does not exist')

    if not is_valid_state(state):
        raise ValueError(f'Invalid state: {state}')
    
    referees = [referee] if referee else []
    manuscript = {
                    flds.TITLE: title,
                    flds.AUTHOR: author,
                    flds.AUTHOR_EMAIL: author_email, 
                    flds.REFEREES: referees,
                    flds.STATE: state,
                }
    
    result = dbc.create(MANU_COLLECT, manuscript)
    inserted_doc = dbc.read_one(MANU_COLLECT, {flds.ID: result.inserted_id})
    return str(inserted_doc[flds.ID])
    

def update(id: str, title: str, author: str, author_email: str, referee: str, state: str) -> str:
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
            flds.STATE: state
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
    Returns a dictionary of {title, each manuscript represented by a dictionary}
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
    return REFEREE_REVIEW


COMMON_ACTIONS = {
    ACTIONS['WITHDRAW']: {
        FUNC: lambda **kwargs: WITHDRAWN,
    },
}

STATE_TABLE = {
    AUTHOR_REVIEW: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: FORMATTING,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REVISION: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: EDITOR_REVIEW,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: AUTHOR_REVIEW,
        },
        **COMMON_ACTIONS,
    },
    EDITOR_REVIEW: {
        ACTIONS['ACCEPT']: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        **COMMON_ACTIONS,
    },
    FORMATTING: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
        **COMMON_ACTIONS,
    },
    PUBLISHED: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
        **COMMON_ACTIONS,
    },
    REFEREE_REVIEW: {
        ACTIONS['ACCEPT']: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        ACTIONS['REJECT']: {
            FUNC: lambda **kwargs: REJECTED,
        },
        ACTIONS['ACCEPT_WITH_REV']: {
            FUNC: lambda **kwargs: AUTHOR_REVISION,
        },
        ACTIONS['ASSIGN_REF']: {
            FUNC: assign_ref,
        },
        ACTIONS['DELETE_REF']: {
            FUNC: delete_ref,
        },
        **COMMON_ACTIONS,
    }, 
    REJECTED: {
        ACTIONS['DONE']: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    SUBMITTED: {
        ACTIONS['ASSIGN_REF']: {
            FUNC: assign_ref,
        },
        ACTIONS['REJECT']: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {
        **COMMON_ACTIONS,
    },
}


def get_valid_actions_by_state(state: str) -> list[str]:
    return list(STATE_TABLE[state].keys())
                

def handle_action(curr_state, action, **kwargs) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Invalid state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'Invalid action: {action}')

    return STATE_TABLE[curr_state][action][FUNC](**kwargs)
    
   
def main():
    print(handle_action(SUBMITTED, ACTIONS['ASSIGN_REF'], manu=SAMPLE_MANU, ref='kw3000@nyu.edu'))


if __name__ == '__main__':
    main()
