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


def get_states() -> list[str]:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# Actions
ACTIONS = {
    'ACCEPT': 'ACC',
    'ACCEPT_WITH_REV': 'AWR',
    'ASSIGN_REF': 'ARF',
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


FUNC = 'f'

STATE_TABLE = {
    AUTHOR_REVIEW: {
        ACTIONS['DONE']: {
            FUNC: lambda x: FORMATTING,
        }
    },
    AUTHOR_REVISION: {
        ACTIONS['DONE']: {
            FUNC: lambda x: EDITOR_REVIEW,
        }
    },
    COPY_EDIT: {
        ACTIONS['DONE']: {
            FUNC: lambda x: AUTHOR_REVIEW,
        }
    },
    EDITOR_REVIEW: {
        ACTIONS['ACCEPT']: {
            FUNC: lambda x: COPY_EDIT,
        }
    },
    FORMATTING: {
        ACTIONS['DONE']: {
            FUNC: lambda x: PUBLISHED,
        }
    },
    PUBLISHED: {
        ACTIONS['DONE']: {
            FUNC: lambda x: PUBLISHED,
        },
    },
    REFEREE_REVIEW: {
        ACTIONS['ACCEPT']: {
            FUNC: lambda x: COPY_EDIT,
        },
        ACTIONS['REJECT']: {
            FUNC: lambda x: REJECTED,
        },
        ACTIONS['ACCEPT_WITH_REV']: {
            FUNC: lambda x: AUTHOR_REVISION,
        }
    }, 
    REJECTED: {
        ACTIONS['DONE']: {
            FUNC: lambda x: REJECTED,
        }    
    },
    SUBMITTED: {
        ACTIONS['ASSIGN_REF']: {
            FUNC: lambda x: REFEREE_REVIEW,
        },
        ACTIONS['REJECT']: {
            FUNC: lambda x: REJECTED,
        }
    },
    WITHDRAWN: {
        ACTIONS['WITHDRAW']: {
            FUNC: lambda x: WITHDRAWN,
        }
    },
}


def get_valid_actions_by_state(state: str) -> list:
    return list(STATE_TABLE[state].keys())
                

def handle_action(curr_state, action) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Invalid state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'Invalid action: {action}')

    return STATE_TABLE[curr_state][action][FUNC](x=curr_state)
    
    


def main():
    print(handle_action(SUBMITTED, ACTIONS['ASSIGN_REF']))


if __name__ == '__main__':
    main()
