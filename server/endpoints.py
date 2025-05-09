"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS

import werkzeug.exceptions as wz
from http import HTTPStatus

import data.people as ppl
import data.manuscripts.form as form
import data.manuscripts.form_filler as ff
import data.text as txt
import data.manuscripts.query as qry
import data.manuscripts.fields as flds
import data.roles as rls
import data.account as acc

import security.security as sec

import subprocess

from dotenv import load_dotenv
import os


app = Flask(__name__)
CORS(app)
api = Api(app)

load_dotenv()
ERROR_FILE = os.getenv("ERROR_FILE")

ACCOUNT_EP = '/account'
DATE = '2024-09-24'
DATE_RESP = 'Date'
EDITOR = 'ejc369@nyu.edu'
EDITOR_RESP = 'Editor'
ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
FORM_EP = '/form'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
LOGIN_EP = '/login'
MASTHEAD = 'Masthead'
MESSAGE = 'Message'
PEOPLE_CREATE_FORM = 'People Add Form'
PEOPLE_EP = '/people'
PUBLISHER = 'Palgave'
PUBLISHER_RESP = 'Publisher'
QUERY_EP = '/query'
REGISTER_EP = '/register'
REPO_NAME = 'mmankwgzrz'
REPO_NAME_EP = '/authors'
REPO_NAME_RESP = 'Repository Name'
RETURN = 'return'
ROLES_EP = '/roles'
TEXT_EP = '/text'
TITLE = 'The Journal of API Technology'
TITLE_EP = '/title'
TITLE_RESP = 'Title'
LOG_DIR = '/var/log'
DELETED = 'Deleted'
PEOPLE = 'people'

QUERY_CREATE_FLDS = api.model('CreateQueryEntry', {
    flds.TITLE: fields.String,
    flds.AUTHOR: fields.String,
    flds.AUTHOR_EMAIL: fields.String,
    flds.REFEREES: fields.List(fields.String),
    flds.STATE: fields.String,
    flds.TEXT: fields.String,
})

QUERY_UPDATE_FLDS = api.model('UpdateQueryEntry', {
    flds.TITLE: fields.String,
    flds.AUTHOR: fields.String,
    flds.AUTHOR_EMAIL: fields.String,
    flds.REFEREES: fields.List(fields.String),
    flds.STATE: fields.String,
    flds.TEXT: fields.String,
})

FORM_CREATE_FLDS = api.model('CreateFormEntry', {
    ff.FLD_NM: fields.String,
    ff.QSTN: fields.String,
    ff.PARAM_TYPE: fields.String,
    ff.OPT: fields.Boolean
})

FORM_UPDATE_FLDS = api.model('UpdateFormEntry', {
    ff.FLD_NM: fields.String,
    ff.QSTN: fields.String,
    ff.PARAM_TYPE: fields.String,
    ff.OPT: fields.Boolean
})

PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.List(fields.String),
})

PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.NAME: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.List(fields.String),
})

TEXT_CREATE_FLDS = api.model('CreateTextEntry', {
    txt.KEY: fields.String,
    txt.TITLE: fields.String,
    txt.TEXT: fields.String,
})

TEXT_UPDATE_FLDS = api.model('UpdateTextEntry', {
    txt.TITLE: fields.String,
    txt.TEXT: fields.String,
})

MANU_ACTION_FLDS = api.model('ManuscriptAction', {
    flds.ID: fields.String,
    flds.ACTION: fields.String,
    flds.REFEREES: fields.String,
})

MANU_STATE_FLDS = api.model('ManuscriptState', {
    flds.ID: fields.String,
    flds.STATE: fields.String,
})

LOGIN_FLDS = api.model('Login', {
    acc.EMAIL: fields.String,
    acc.PASSWORD: fields.String,
})

REGISTER_FLDS = api.model('Register', {
    acc.EMAIL: fields.String,
    acc.PASSWORD: fields.String,
})

CHANGE_ACC_PW_FLDS = api.model('ChangeAccountPW', {
    flds.OLD_PASSWORD: fields.String,
    flds.NEW_PASSWORD: fields.String,
})


@api.route('/log/error')
class ErrorLog(Resource):
    """
    Returns the last few lines of the server error log.
    """
    def get(self):
        filepath = f'{LOG_DIR}/{ERROR_FILE}'
        result = subprocess.run(f'tail {filepath}', shell=True,
                                stdout=subprocess.PIPE, text=True)
        return {'error_log': result.stdout.strip()}


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(TITLE_EP)
class GetJournalTitle(Resource):
    """
    This class handles creating, reading, updating
    and deleting the journal title.
    """
    def get(self):
        """
        Retrieve the journal title.
        """
        return {
            TITLE_RESP: TITLE,
            EDITOR_RESP: EDITOR,
            DATE_RESP: DATE,
            PUBLISHER_RESP: PUBLISHER
        }


@api.route(REPO_NAME_EP)
class GetRepoName(Resource):
    """
    This class is focused around printing the name of the repository
    for the assignment
    """
    def get(self):
        """
        Print the name of the repository
        """
        return {
            REPO_NAME_RESP: REPO_NAME
        }


@api.route(f'{LOGIN_EP}')
class Login(Resource):
    """
    Logs a user given email and password.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Invalid request')
    @api.expect(LOGIN_FLDS)
    def post(self):
        """
        Logs user in with email and password.
        """
        email = request.json.get(acc.EMAIL)
        password = request.json.get(acc.PASSWORD)

        if not email or not password:
            raise wz.BadRequest('Both email and password are required.')

        try:
            acc.login(email, password)
            return {
                MESSAGE: 'Login success!',
            }, HTTPStatus.OK
        except ValueError as err:
            raise wz.BadRequest(f'{str(err)}')


@api.route(f'{REGISTER_EP}')
class Register(Resource):
    """
    Register a user given email and password.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Invalid request')
    @api.expect(REGISTER_FLDS)
    def post(self):
        """
        Register user with email and password.
        """
        email = request.json.get(acc.EMAIL)
        password = request.json.get(acc.PASSWORD)

        if not email or not password:
            raise wz.BadRequest('Both email and password are required.')

        try:
            email = acc.register(email, password)
            return {
                MESSAGE: f'Sign up success for {email}!',
            }, HTTPStatus.OK
        except ValueError as err:
            raise wz.BadRequest(f'{str(err)}')


@api.route(f'{ACCOUNT_EP}/<email>')
class Account(Resource):
    """
    Delete user account given email.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such account.')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Missing or invalid '
                  'Authorization header. Please log back in.')
    def delete(self, email):
        """
        Deletes the user account.
        """
        # extract Bearer email
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise wz.Unauthorized('Missing or invalid Authorization header. '
                                  'Please log back in.')
        bearer_email = auth_header.split(' ')[1].strip()
        if not bearer_email:
            raise wz.Unauthorized('Missing email in Authorization header. '
                                  'Please log back in.')
        # check if Bearer email matches the email in the route
        if bearer_email != email:
            # if not, check if Bearer email belongs to an editor
            requester = ppl.read_one(bearer_email)
            if not requester:
                raise wz.NotFound(f"""Email not found:
                                      {bearer_email}""")
            roles = requester.get(flds.ROLES, [])
            if not any(role in rls.MH_ROLES for role in roles):
                raise wz.Unauthorized(
                    """You are unauthorized to modify another user.""")

        try:
            acc.delete(email)
            # delete from people collection too
            ppl.delete(email)
            return {
                MESSAGE: f'Successfully deleted account: {email}',
            }, HTTPStatus.OK
        except ValueError as err:
            raise wz.BadRequest(f'Could not delete account: {str(err)}')


@api.route(f'{ACCOUNT_EP}/password')
class AccountPassword(Resource):
    """
    Changes the user's password
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Invalid request')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Missing or invalid '
                  'Authorization header. Please log back in.')
    @api.expect(CHANGE_ACC_PW_FLDS)
    def post(self):
        """
        Updates the user's password.
        """
        # extract Bearer email
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise wz.Unauthorized('Missing or invalid Authorization header. '
                                  'Please log back in.')
        bearer_email = auth_header.split(' ')[1].strip()
        if not bearer_email:
            raise wz.Unauthorized('Missing email in Authorization header. '
                                  'Please log back in.')

        # first confirm the old password is correct
        if not acc.check_password(request.json.get(flds.OLD_PASSWORD),
                                  acc.get_password(bearer_email)):
            raise wz.Unauthorized('Your old password is incorrect.')
        try:
            # check that new password is valid
            acc.is_valid_password(request.json.get(flds.NEW_PASSWORD))
            # change the password
            if acc.change_password(request.json.get(flds.NEW_PASSWORD),
                                   bearer_email):
                return {MESSAGE: "Successfully updated password."}
            raise wz.NotFound("Email not found.")
        except ValueError as e:
            # rethrow the error
            raise wz.BadRequest(str(e))


@api.route('/permissions')
class Permissions(Resource):
    """
    Check if a user has permission to perform a specific action on a feature.
    """
    @api.doc(params={
        sec.FEATURE: 'The feature to access (e.g. "text")',
        sec.ACTION: 'The action to perform (e.g. "update")',
        sec.USER_EMAIL: 'The email of the user'
    })
    @api.response(HTTPStatus.OK, 'Permission check result')
    @api.response(HTTPStatus.BAD_REQUEST, 'Missing or invalid parameters')
    def get(self):
        """
        Check if the user has permission to perform an action on a feature.
        """
        feature = request.args.get(sec.FEATURE)
        action = request.args.get(sec.ACTION)
        user_email = request.args.get(sec.USER_EMAIL)

        if not feature or not action or not user_email:
            raise wz.BadRequest("Missing required query parameters: " +
                                "feature, action, user email")

        allowed = sec.is_permitted(feature, action, user_email)

        return {"permitted": allowed}


@api.route('/query/can_choose_action')
class CanChooseAction(Resource):
    """
    Determine if the given user can choose an action for a manuscript.
    """
    @api.doc(params={
        flds.MANU_ID: 'The ID of the manuscript',
        flds.USER_EMAIL: 'The email of the user'
    })
    @api.response(HTTPStatus.OK, 'Permission check result')
    @api.response(HTTPStatus.BAD_REQUEST, 'Missing or invalid parameters')
    def get(self):
        manu_id = request.args.get(flds.MANU_ID)
        user_email = request.args.get(flds.USER_EMAIL)

        if not manu_id or not user_email:
            raise wz.BadRequest(
                "Missing required query parameters: manu_id, user_email")

        try:
            permitted = qry.can_choose_action(manu_id, user_email)
            return permitted
        except Exception as e:
            raise wz.BadRequest(f"Error checking action permissions: {str(e)}")


@api.route('/query/can_move_action')
class CanMoveAction(Resource):
    """
    Determine if the given user can use the MOVE action for a manuscript
    """
    @api.doc(params={
        flds.MANU_ID: 'The ID of the manuscript',
        flds.USER_EMAIL: 'Email of the user'
    })
    @api.response(HTTPStatus.OK, 'Permission granted')
    @api.response(HTTPStatus.BAD_REQUEST, 'Missing or invalid params')
    def get(self):
        manu_id = request.args.get(flds.MANU_ID)
        user_email = request.args.get(flds.USER_EMAIL)

        if not manu_id or not user_email:
            raise wz.NotFound(
                "Missing manuscript or user"
            )
        try:
            permitted = qry.can_move_action(manu_id, user_email)
            return permitted
        except Exception as e:
            raise wz.BadRequest(f"Error checking move permission: {str(e)}")


@api.route(f'{PEOPLE_EP}/create/form')
class CreatePeopleForm(Resource):
    """
    Form to add a new person to the journal database.
    """
    def get(self):
        return {
            PEOPLE_CREATE_FORM: {
                ppl.NAME: "string",
                ppl.EMAIL: "string",
                ppl.AFFILIATION: "string",
                ppl.ROLES: "list of strings",
            }
        }


@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles reading journal people.
    """
    def get(self):
        """
        Retrieve the journal people.
        """
        return ppl.read()


@api.route(f'{PEOPLE_EP}/<email>')
class Person(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """
    def get(self, email):
        """
        Retrieve a journal person.
        """
        person = ppl.read_one(email)
        if person:
            return person
        else:
            raise wz.NotFound(f'No such record: {email}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Authorization header missing')
    def delete(self, email):
        # extract Bearer email
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise wz.NotFound('Missing or invalid Authorization header')
        bearer_email = auth_header.split(' ')[1].strip()
        if not bearer_email:
            raise wz.Unauthorized('No email found in Bearer token.')

        # check if Bearer email matches the email in the route
        if bearer_email != email:
            # if not, check if Bearer email belongs to an editor
            requester = ppl.read_one(bearer_email)
            if not requester:
                raise wz.NotFound(f"""Requester email not found:
                                      {bearer_email}""")
            roles = requester.get('roles', [])
            if not any(role in roles for role in (
                    rls.ED_CODE, rls.ME_CODE, rls.CE_CODE)):
                raise wz.Unauthorized("""You are unauthorized to modify
                                      another user""")
        ret = ppl.delete(email)
        if ret > 0:
            return {DELETED: ret}
        else:
            raise wz.NotFound(f'No such person: {email}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Authorization header missing')
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self, email):
        """
        Update a person's details.
        """
        # extract Bearer email
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise wz.Unauthorized('You must log in to perform this action.')
        bearer_email = auth_header.split(' ')[1].strip()
        if not bearer_email:
            raise wz.Unauthorized('You must log in to perform this action.')
        # check if Bearer email matches the email in the route
        if bearer_email != email:
            # if not, check if Bearer email belongs to an editor
            requester = ppl.read_one(bearer_email)
            if not requester:
                raise wz.NotFound(f"""Requester email not found:
                                      {bearer_email}""")
            roles = requester.get('roles', [])
            if not any(role in roles for role in (
                    rls.ED_CODE, rls.ME_CODE, rls.CE_CODE)):
                raise wz.Unauthorized("""You are unauthorized to modify
                                      another user""")

        try:
            person = ppl.read_one(email)
            if not person:
                raise wz.NotFound(f'Person email not found: {email}')

            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            roles = request.json.get(ppl.ROLES, [])

            ret = ppl.update(name, affiliation, email, roles)

            return {
                MESSAGE: 'Person updated successfully',
                RETURN: ret
            }
        except ValueError as err:
            raise wz.NotAcceptable(f'Could not update person: {str(err)}')


@api.route(f'{PEOPLE_EP}/create')
class PeopleCreate(Resource):
    """
    Add a person to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(PEOPLE_CREATE_FLDS)
    def put(self):
        """
        Add a person.
        """
        try:
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            email = request.json.get(ppl.EMAIL)
            roles = request.json.get(ppl.ROLES, [])

            if ppl.exists(email):
                raise wz.NotAcceptable(f'Email is already in use: {email}')

            ret = ppl.create(name, affiliation, email, roles)
            return {
                MESSAGE: 'Person added!',
                RETURN: ret,
            }
        except ValueError as err:
            raise wz.NotAcceptable(f'Could not add person: {str(err)}')


@api.route(f'{PEOPLE_EP}/role/<role>')
class PeopleByRole(Resource):
    def get(self, role):
        """
        Get all people with a specific role.
        """
        all_people = ppl.read()
        people_with_role = [all_people[email] for email in
                            all_people if role in all_people[email][ppl.ROLES]]
        return {PEOPLE: people_with_role}


@api.route(f'{PEOPLE_EP}/affiliation/<affiliation>')
class PeopleByAffiliation(Resource):
    def get(self, affiliation):
        """
        Get all people from a specific affiliation.
        """
        all_people = ppl.read()
        people_with_affiliation = [all_people[email] for email in all_people
                                   if all_people[email][ppl.AFFILIATION]
                                   == affiliation]
        return {PEOPLE: people_with_affiliation}


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    """
    Get a journal's masthead.
    """
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


@api.route(ROLES_EP)
class Role(Resource):
    """
    This class handles reading journal people roles.
    """
    def get(self):
        """
        Retrieve the journal people roles.
        """
        return rls.get_roles()


@api.route(QUERY_EP)
class Query(Resource):
    """
    This class handles reading all the manuscripts.
    """
    def get(self):
        """
        Retrieve the all the manuscripts.
        """
        return qry.get_manuscripts()


@api.route(f'{QUERY_EP}/<id>')
class QueryEntry(Resource):
    """
    This class handles read, update, and delete for a single
    manuscript in the manuscript db collection.
    """
    def get(self, id):
        """
        Retrieve a single manuscript.
        """
        try:
            manuscript = qry.get_one_manu(id)
        except ValueError:
            raise wz.BadRequest(f"Invalid ObjectId: {id}")
        else:
            if manuscript:
                return manuscript
            else:
                raise wz.NotFound(f'No such manuscript: {id}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.expect(QUERY_UPDATE_FLDS)
    def put(self, id):
        """
        Update a manuscript.
        """
        title = request.json.get(flds.TITLE)
        author = request.json.get(flds.AUTHOR)
        author_email = request.json.get(flds.AUTHOR_EMAIL)
        referees = request.json.get(flds.REFEREES)
        state = request.json.get(flds.STATE)
        text = request.json.get(flds.TEXT)
        abstract = request.json.get(flds.ABSTRACT)

        if not qry.exists(id):
            raise wz.NotFound(f'No such manuscript with id: {id}')

        if not qry.is_valid_state(state):
            raise wz.BadRequest(f'Invalid manuscript state: {state}')

        updated_manu = qry.update(
            id, title, author, author_email, referees, state, text,
            abstract)

        return {
            MESSAGE: 'Manuscript updated successfully',
            RETURN: updated_manu
        }

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript.')
    def delete(self, id):
        """
        Delete a manuscript.
        """
        try:
            deleted_count = qry.delete(id)
        except ValueError:
            raise wz.BadRequest(f"Invalid ObjectId: {id}")
        else:
            if deleted_count == 0:
                raise wz.NotFound(f'No such manuscript: {id}')
            return {DELETED: deleted_count}


@api.route(f'{QUERY_EP}/create')
class QueryCreate(Resource):
    """
    This class handles creating a manuscript and adding
    to the manuscript database collection.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(QUERY_CREATE_FLDS)
    def put(self):
        """
        Create a manuscript and add to the databse.
        """
        try:
            title = request.json.get(flds.TITLE)
            author = request.json.get(flds.AUTHOR)
            author_email = request.json.get(flds.AUTHOR_EMAIL)
            referees = request.json.get(flds.REFEREES)
            state = request.json.get(flds.STATE)
            text = request.json.get(flds.TEXT)
            abstract = request.json.get(flds.TEXT)

            new_manuscript = qry.create_manuscript(title, author,
                                                   author_email, referees,
                                                   state, text, abstract)
            return {
                MESSAGE: 'Manuscript added!',
                RETURN: new_manuscript
            }

        except Exception as err:
            raise wz.NotAcceptable(f'Could not add manuscript: {err=}')


@api.route(f'{QUERY_EP}/handle_action')
class HandleAction(Resource):
    """
    Handle query action and receive the next state for a manuscript.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(MANU_ACTION_FLDS)
    def put(self):
        """
        Handle query action and receive the next state for a manuscript.
        """
        try:
            id = request.json.get(flds.ID)
            manu = qry.get_one_manu(id)
            curr_state = manu[flds.STATE]
            action = request.json.get(flds.ACTION)
            ref = request.json.get(flds.REFEREES)
            new_state = qry.handle_action(curr_state, action,
                                          manu=manu, ref=ref)

            qry.update(manu[flds.ID], manu[flds.TITLE], manu[flds.AUTHOR],
                       manu[flds.AUTHOR_EMAIL],
                       manu[flds.REFEREES], new_state, manu[flds.TEXT],
                       manu[flds.ABSTRACT])

        except Exception as err:
            raise wz.NotAcceptable(f'Bad input: {err=}')
        return {
            MESSAGE: 'Action received!',
            RETURN: new_state,
        }


@api.route(f'{QUERY_EP}/handle_state')
class HandleState(Resource):
    """
    Switch Manuscript state.
    """
    @api.response(HTTPStatus.OK, 'Sucess')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Couldn't switch state!")
    @api.expect(MANU_STATE_FLDS)
    def put(self):
        """
        Handle state switch for the editor's move ability.
        """
        try:
            id = request.json.get(flds.ID)
            new_state = request.json.get(flds.STATE)
            manu = qry.get_one_manu(id)
            qry.update(manu[flds.ID], manu[flds.TITLE], manu[flds.AUTHOR],
                       manu[flds.AUTHOR_EMAIL], manu[flds.REFEREES], new_state,
                       manu[flds.TEXT], manu[flds.ABSTRACT])
        except Exception as e:
            raise wz.NotAcceptable(f'Bad input: {e=}')
        return {
            MESSAGE: 'State updated!',
            RETURN: new_state,
        }


@api.route(f'{QUERY_EP}/active/<email>')
class QueryActive(Resource):
    """
    Retrieve active manuscripts for a user.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User not found.')
    def get(self, email):
        """
        Returns manuscripts based on user role and relation.
        """
        if not ppl.exists(email):
            raise wz.NotFound(f"No such user: {email}")

        try:
            active_manuscripts = qry.get_active_manuscripts(email)
        except Exception as err:
            raise wz.NotAcceptable(
                f"Error retrieving active manuscripts: {err}"
                )

        return active_manuscripts


@api.route(f'{QUERY_EP}/states')
class State(Resource):
    """
    This class handles reading manuscript states.
    """
    def get(self):
        """
        Retrieve the manuscript states.
        """
        return qry.get_states()


@api.route(f'{QUERY_EP}/actions')
class Action(Resource):
    """
    This class handles reading manuscript actions.
    """
    def get(self):
        """
        Retrieve the manuscript actions.
        """
        return qry.get_actions()


@api.route(f'{QUERY_EP}/valid_actions')
class ValidActions(Resource):
    @api.doc(params={
        flds.USER_EMAIL: 'The email of the user requesting actions',
        flds.MANU_ID: 'The ID of the manuscript'
    })
    def get(self):
        user_email = request.args.get(flds.USER_EMAIL)
        manu_id = request.args.get(flds.MANU_ID)

        if not user_email or not manu_id:
            raise wz.BadRequest("Missing user_email or manu_id")

        try:
            actions = qry.get_valid_actions(manu_id, user_email)
            return actions
        except ValueError as e:
            raise wz.BadRequest(str(e))


@api.route(f'{QUERY_EP}/valid_states')
class ValidStates(Resource):
    @api.doc(params={
        flds.USER_EMAIL: 'The email of the user with move state ability',
        flds.MANU_ID: 'The ID of manuscript'
    })
    def get(self):
        user_email = request.args.get(flds.USER_EMAIL)
        manu_id = request.args.get(flds.MANU_ID)

        if not user_email or not manu_id:
            raise wz.BadRequest("Missing user_email or manu_id")

        try:
            states = qry.get_valid_states(manu_id, user_email)
            return states
        except ValueError as e:
            raise wz.BadRequest(str(e))


@api.route(FORM_EP)
class Form(Resource):
    """
    This class handles reading the form.
    """
    def get(self):
        """
        Retrieve the form.
        """
        return form.get_form()


@api.route(f'{FORM_EP}/<field_name>')
class FormField(Resource):
    """
    This class handles CRUD for form fields.
    """
    def get(self, field_name):
        """
        Retrieve a form field.
        """
        fields = form.get_form()
        field = next((fld for fld in fields if fld[ff.FLD_NM]
                      == field_name), None)
        if field:
            return field
        else:
            raise wz.NotFound(f'No such field: {field_name}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such field.')
    def delete(self, field_name):
        fields = form.get_form()
        field = next((fld for fld in fields if fld[ff.FLD_NM]
                      == field_name), None)
        if field:
            fields.remove(field)
            return {DELETED: field}
        else:
            raise wz.NotFound(f'No such field: {field_name}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Field not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.expect(FORM_UPDATE_FLDS)
    def put(self, field_name):
        """
        Update a form field.
        """
        try:
            updated_field = form.update_form_field(
                field_name,
                question=request.json.get(ff.QSTN),
                param_type=request.json.get(ff.PARAM_TYPE),
                optional=request.json.get(ff.OPT)
            )
            return {
                MESSAGE: 'Field updated successfully',
                RETURN: updated_field
            }, HTTPStatus.OK
        except ValueError as ve:
            raise wz.NotFound(str(ve))
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update field: {str(err)}')


@api.route(f'{FORM_EP}/create')
class FormCreate(Resource):
    """
    Add a field to the form.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(FORM_CREATE_FLDS)
    def put(self):
        """
        Add a form field.
        """
        try:
            field_name = request.json.get(ff.FLD_NM)
            question = request.json.get(ff.QSTN)
            param_type = request.json.get(ff.PARAM_TYPE)
            optional = request.json.get(ff.OPT)

            fields = form.get_form()
            if any(fld[form.FLD_NM] == field_name for fld in fields):
                raise wz.NotAcceptable(f'{field_name} is already used.')

            new_field = {
                ff.FLD_NM: field_name,
                ff.QSTN: question,
                ff.PARAM_TYPE: param_type,
                ff.OPT: optional
            }
            fields.append(new_field)
            return {
                MESSAGE: 'Field added!',
                RETURN: new_field,
            }
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add field: {str(err)}')


@api.route(TEXT_EP)
class Texts(Resource):
    """
    This class handles retrieving all text entries.
    """
    def get(self):
        """
        Retrieve all text entries.
        """
        try:
            texts = txt.read()
            print(texts)
            return texts
        except Exception as err:
            raise wz.NotFound(f'Could not retrieve text entries: {str(err)}')


@api.route(f'{TEXT_EP}/create')
class CreateText(Resource):
    """
    This class handles creating a new text entry.
    """
    @api.expect(TEXT_CREATE_FLDS)
    def put(self):
        """
        Add a new text entry.
        """
        try:
            key = request.json.get(txt.KEY)
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)

            if txt.read_one(key):
                raise wz.NotAcceptable(f"Key '{key}' already exists.")

            new_text = txt.create(key, title, text)

            return {MESSAGE: 'Text entry added!', 'Text Entry': new_text}
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add text entry: {str(err)}')


@api.route(f'{TEXT_EP}/<key>')
class Text(Resource):
    """
    This class handles operations on a single text entry by key: getting,
    deleting, and updating.
    """
    def get(self, key):
        """
        Retrieve a single text entry by key.
        """
        try:
            text_entry = txt.read_one(key)
            if not text_entry:
                raise wz.NotFound(f'No text entry found for key: {key}')
            return text_entry
        except Exception as err:
            raise wz.NotFound(f'Could not retrieve text entry: {str(err)}')

    def delete(self, key):
        """
        Delete a text entry by key.
        """
        try:
            deleted_count = txt.delete(key)
            if deleted_count == 0:
                raise wz.NotFound(f'No text entry found for key: {key}')
            return {MESSAGE: f'{deleted_count} text entry deleted.'}
        except Exception as err:
            raise wz.NotFound(f'Could not delete text entry: {str(err)}')

    @api.expect(TEXT_UPDATE_FLDS)
    def put(self, key):
        """
        Update a text entry.
        """
        try:
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)

            updated_text = txt.update(key, title=title, text=text)

            return {MESSAGE: 'Text entry updated!',
                    'Updated Entry': updated_text}
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update text entry: {str(err)}')
