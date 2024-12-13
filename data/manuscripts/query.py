# from manuscripts import fields as flds (this give you errors when deploying)
import data.manuscripts.fields as flds
#the other import breaks matthew and andy's builds

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

TEST_STATE = SUBMITTED

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

SAMPLE_MANU = {
    flds.TITLE: 'Sample Manuscript',
    flds.AUTHOR: 'Andy Ng',
    flds.REFEREES: [],
}

def get_states() -> list[str]:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


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

# for testing:
TEST_ACTION = ACTIONS['ACCEPT']

VALID_ACTIONS = list(ACTIONS.values())


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def assign_ref(manu: dict, ref: str, extra=None) -> str:
    print(extra)
    manu[flds.REFEREES].append(ref)
    return REFEREE_REVIEW


def delete_ref(manu: dict, ref: str) -> str:
    if len(manu[flds.REFEREES]) > 0:
        manu[flds.REFEREES].remove(ref)
    if len(manu[flds.REFEREES]) > 0:
        return REFEREE_REVIEW
    else:
        return SUBMITTED


FUNC = 'f'

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


def get_valid_actions_by_state(state: str) -> list:
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
