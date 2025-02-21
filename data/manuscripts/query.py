import data.manuscripts.fields as flds
import data.people as ppl
import data.db_connect as dbc


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

VALID_STATES = [
    AUTHOR_REVIEW,
    AUTHOR_REVISION,
    COPY_EDIT,
    EDITOR_REVIEW,
    FORMATTING,
    PUBLISHED,
    REFEREE_REVIEW,
    REJECTED,
    SUBMITTED,
    WITHDRAWN,
]

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
    flds.ID : '1',
    flds.TITLE: 'Sample Manuscript',
    flds.AUTHOR: 'Andy Ng',
    flds.AUTHOR_EMAIL: 'an3299@Nyu.edu',
    flds.REFEREES: [],
    flds.STATE: SUBMITTED,
    flds.ACTION: ACTIONS['ASSIGN_REF'],
}

FUNC = 'f'


def get_states() -> list[str]:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def create_manuscript(id: str, title: str, author: str, author_email: str, referee: str, state: str) -> str:
    if exists(id):
        raise ValueError('ID already exists use another one')

    if not ppl.exists(author_email):
        raise ValueError('Author does not exist')

    if not is_valid_state(state):
        raise ValueError(f'Invalid state: {state}')
    
    referees = [referee] if referee else []
    manuscript = {
                    flds.ID: id,
                    flds.TITLE: title,
                    flds.AUTHOR: author,
                    flds.AUTHOR_EMAIL: author_email, 
                    flds.REFEREES: referees,
                    flds.STATE: state,
                }
    
    # print(manuscript)
    dbc.create(MANU_COLLECT, manuscript)
    return id
    

def update(id : str, title: str, author: str, author_email: str, referee: str, state: str) -> str:
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
    
    # if not is_valid_action(action):          
    #     raise ValueError(f'Invalid action: {action=}')
    
    manuscript = { 
            flds.ID: id,
            flds.TITLE: title,
            flds.AUTHOR: author,
            flds.AUTHOR_EMAIL: author_email,
            flds.REFEREES: referee,
            flds.STATE: state
        }
    
    # print(manuscript)
    dbc.update(MANU_COLLECT, {flds.ID: id}, manuscript)
    return id


def get_manuscripts() -> dict[str, dict]:
    """
    Retrieves all manuscripts from the database.
    Returns a dictionary of {title, each manuscript represented by a dictionary}
    """
    manuscripts = dbc.read_dict(MANU_COLLECT, flds.ID)
    print(f'Manuscripts retrieved: {manuscripts}')
    return manuscripts


def get_one_manu(id : str) -> dict:
    """
    Retrieves a manuscript from the database, by taking in an email.
    """
    manuscript = dbc.read_one(MANU_COLLECT, {flds.ID: id})
    print(f'Manuscript retrieved: {manuscript}')
    return manuscript


def delete(id : str) -> int:
    """ 
    Deletes a selected manusciprt from the database.
    """
    print(f'{flds.ID=}: {id=}')
    return dbc.delete(MANU_COLLECT, {flds.ID: id})

def exists(id: str) -> bool:
    """
    Checks if a manuscript with the given title exists in the database.
    """
    return get_one_manu(id) is not None


def assign_ref(manu: dict, ref: str, extra=None) -> str:
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
    print(handle_action(SUBMITTED, ACTIONS['ASSIGN_REF'], manu=SAMPLE_MANU))


if __name__ == '__main__':
    main()
