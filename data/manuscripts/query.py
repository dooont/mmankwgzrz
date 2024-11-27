# State Contants
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
TEST_STATE = SUBMITTED

VALID_STATES = [
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
]


def get_states() -> list[str]:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# actions:
ACTIONS = {
    'ACCEPT': 'ACC',
    'ASSIGN_REF': 'ARF',
    'DONE': 'DON',
    'REJECT': 'REJ',
}

# for testing:
TEST_ACTION = ACTIONS['ACCEPT']

VALID_ACTIONS = list(ACTIONS.values())


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def handle_action(curr_state, action) -> str:
    if not is_valid_state(curr_state):
        raise ValueError(f'Invalid state: {curr_state}')
    if not is_valid_action(action):
        raise ValueError(f'Invalid action: {action}')
    new_state = curr_state
    if curr_state == SUBMITTED:
        if action == ACTIONS['ACCEPT']:
            new_state = IN_REF_REV
        elif action == ACTIONS['REJECT']:
            new_state = REJECTED
    elif curr_state == IN_REF_REV:
        if action == ACTIONS['DONE']:
            new_state = COPY_EDIT
        elif action == ACTIONS['REJECT']:
            new_state = REJECTED
    return new_state
