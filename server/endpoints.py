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
import data.text as txt
import data.manuscripts.query as qry
import data.manuscripts.fields as flds

app = Flask(__name__)
CORS(app)
api = Api(app)

DATE = '2024-09-24'
DATE_RESP = 'Date'
EDITOR = 'ejc369@nyu.edu'
EDITOR_RESP = 'Editor'
ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
FORM_EP = '/form'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MASTHEAD = 'Masthead'
MESSAGE = 'Message'
PEOPLE_CREATE_FORM = 'People Add Form'
PEOPLE_EP = '/people'
PUBLISHER = 'Palgave'
PUBLISHER_RESP = 'Publisher'
QUERY_EP = '/query'
REPO_NAME = 'mmankwgzrz'
REPO_NAME_EP = '/authors'
REPO_NAME_RESP = 'Repository Name'
RETURN = 'return'
TEXT_EP = '/text'
TITLE = 'The Journal of API Technology'
TITLE_EP = '/title'
TITLE_RESP = 'Title'


QUERY_CREATE_FLDS = api.model('CreateQueryEntry', {
    flds.TITLE: fields.String,
    flds.AUTHOR: fields.String,
    flds.AUTHOR_EMAIL: fields.String,
    flds.REFEREES: fields.List(fields.String),
    flds.STATE: fields.String,
    flds.ACTION: fields.String
})

QUERY_UPDATE_FLDS = api.model('UpdateQueryEntry', {
    flds.TITLE: fields.String,
    flds.AUTHOR: fields.String,
    flds.AUTHOR_EMAIL: fields.String,
    flds.REFEREES: fields.List(fields.String),
    flds.STATE: fields.String,
    flds.ACTION: fields.String
})

FORM_CREATE_FLDS = api.model('CreateFormEntry', {
    'field_name': fields.String,
    'question': fields.String,
    'param_type': fields.String,
    'optional': fields.Boolean
})

FORM_UPDATE_FLDS = api.model('UpdateFormEntry', {
    'field_name': fields.String,
    'question': fields.String,
    'param_type': fields.String,
    'optional': fields.Boolean
})

PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.String,
})

PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.List(fields.String)
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
    flds.TITLE: fields.String,
    flds.REFEREES: fields.String,
    flds.CURR_STATE: fields.String,
    flds.ACTION: fields.String,
})


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
                ppl.ROLES: "list of strings"
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
    def delete(self, email):
        ret = ppl.delete(email)
        if ret > 0:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {email}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self, email):
        """
        Update a person's details.
        """
        try:
            person = ppl.read_one(email)
            if not person:
                raise wz.NotFound(f'Person with email {email} not found.')

            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            roles = request.json.get(ppl.ROLES, [])

            ret = ppl.update(name, affiliation, email, roles)

            return {
                MESSAGE: 'Person updated successfully',
                RETURN: ret
            }
        except ValueError as ve:
            raise wz.NotFound(f'Invalid data provided: {str(ve)}')
        except wz.NotFound:  # Let NotFound exceptions pass through
            raise
        except Exception as err:
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
            role = request.json.get(ppl.ROLES)

            if ppl.exists(email):
                raise wz.NotAcceptable(f'Email {email} is already in use.')

            ret = ppl.create(name, affiliation, email, role)
            return {
                MESSAGE: 'Person added!',
                RETURN: ret,
            }
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: {err=}')


@api.route(f'{PEOPLE_EP}/role/<role>')
class PeopleByRole(Resource):
    def get(self, role):
        """
        Get all people with a specific role.
        """
        all_people = ppl.read()
        people_with_role = [all_people[email] for email in
                            all_people if role in all_people[email][ppl.ROLES]]
        return {"people": people_with_role}


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
        return {"people": people_with_affiliation}


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    """
    Get a journal's masthead.
    """
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


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


@api.route(f'{QUERY_EP}/<title>')
class QueryEntry(Resource):
    """
    This class handles read, update, and delete for a single
    manuscript in the manuscript db collection.
    """
    def get(self, title):
        """
        Retrieve a single manuscript.
        """
        manuscript = qry.get_one_manu(title)
        if manuscript:
            return manuscript
        else:
            raise wz.NotFound(f'No such manuscript: {title}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.expect(QUERY_UPDATE_FLDS)
    def put(self, title):
        """
        Update a manuscript.
        """
        try:
            if not qry.exists(title):
                raise wz.NotFound(f'No such manuscript: {title}')

            author = request.json.get(flds.AUTHOR)
            author_email = request.json.get(flds.AUTHOR_EMAIL)
            referees = request.json.get(flds.REFEREES)
            state = request.json.get(flds.STATE)
            action = request.json.get(flds.ACTION)

            ret = qry.update(title, author, author_email, referees,
                             state, action)

            return {
                MESSAGE: 'Manuscript updated successfully',
                RETURN: ret
            }
        except ValueError as ve:
            raise wz.NotFound(f'Invalid data provided: {str(ve)}')
        except Exception as exp:
            raise wz.NotAcceptable(f'Could not update manuscript: {str(exp)}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript.')
    def delete(self, title):
        """
        Delete a manuscript.
        """
        deleted_count = qry.delete(title)
        if deleted_count == 0:
            raise wz.NotFound(f'No such manuscript: {title}')
        return {'Deleted': deleted_count}


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
            action = request.json.get(flds.ACTION)

            if qry.exists(title):
                raise wz.NotAcceptable(f'Title {title} is already in use.')

            new_manuscript = qry.create_manuscript(title, author, author_email,
                                                   referees, state, action)
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
            title = request.json.get(flds.TITLE)
            manu = qry.get_one_manu(title)
            ref = request.json.get(flds.REFEREES)
            curr_state = request.json.get(flds.CURR_STATE)
            action = request.json.get(flds.ACTION)
            new_state = qry.handle_action(curr_state, action,
                                          manu=manu, ref=ref)

            qry.update(manu[flds.TITLE], manu[flds.AUTHOR],
                       manu[flds.AUTHOR_EMAIL],
                       manu[flds.REFEREES], new_state, manu[flds.ACTION])

        except Exception as err:
            raise wz.NotAcceptable(f'Bad input: {err=}')
        return {
            MESSAGE: 'Action received!',
            RETURN: new_state,
        }


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
        field = next((fld for fld in fields if fld[form.FLD_NM]
                      == field_name), None)
        if field:
            return field
        else:
            raise wz.NotFound(f'No such field: {field_name}')

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such field.')
    def delete(self, field_name):
        fields = form.get_form()
        field = next((fld for fld in fields if fld[form.FLD_NM]
                      == field_name), None)
        if field:
            fields.remove(field)
            return {'Deleted': field}
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
                question=request.json.get('question'),
                param_type=request.json.get('param_type'),
                optional=request.json.get('optional')
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
            field_name = request.json.get('field_name')
            question = request.json.get('question')
            param_type = request.json.get('param_type')
            optional = request.json.get('optional')

            fields = form.get_form()
            if any(fld[form.FLD_NM] == field_name for fld in fields):
                raise wz.NotAcceptable(f'{field_name} is already used.')

            new_field = {
                form.FLD_NM: field_name,
                'question': question,
                'param_type': param_type,
                'optional': optional
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
            return {'texts': texts}
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
            key = request.json.get('key')
            title = request.json.get('title')
            text = request.json.get('text')

            if txt.read_one(key):
                raise wz.NotAcceptable(f"Key '{key}' already exists.")

            new_text = txt.create(key, title, text)

            return {'Message': 'Text entry added!', 'Text Entry': new_text}
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
            return {'Message': f'{deleted_count} text entry deleted.'}
        except Exception as err:
            raise wz.NotFound(f'Could not delete text entry: {str(err)}')

    @api.expect(TEXT_UPDATE_FLDS)
    def put(self, key):
        """
        Update a text entry.
        """
        try:
            title = request.json.get('title')
            text = request.json.get('text')

            updated_text = txt.update(key, title=title, text=text)

            return {'Message': 'Text entry updated!',
                    'Updated Entry': updated_text}
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update text entry: {str(err)}')
