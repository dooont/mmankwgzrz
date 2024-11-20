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

app = Flask(__name__)
CORS(app)
api = Api(app)

DATE = '2024-09-24'
DATE_RESP = 'Date'
EDITOR = 'ejc369@nyu.edu'
EDITOR_RESP = 'Editor'
ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'
PEOPLE_EP = '/people'
PUBLISHER = 'Palgave'
PUBLISHER_RESP = 'Publisher'
REPO_NAME = 'mmankwgzrz'
REPO_NAME_EP = '/authors'
REPO_NAME_RESP = 'Repository Name'
RETURN = 'return'
TITLE = 'The Journal of API Technology'
TITLE_EP = '/title'
TITLE_RESP = 'Title'
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
PEOPLE_CREATE_FORM = 'People Add Form'


# This is the endpoint for the hello world
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


# This is the endpoint for the available endpoints
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


# This is the endpoint for the journal title
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


# This is the endpoint for the repository name
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


# This is the endpoint for updating the people
@api.route(f'{PEOPLE_EP}/<email>')
class PeopleUpdate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid data')
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self, email):
        """
        Update a person's details.
        """
        try:
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            roles = request.json.get(ppl.ROLES, [])
            new_email = request.json.get(ppl.EMAIL)

            ret = ppl.update(name, affiliation, email, new_email, roles)
            return {
                MESSAGE: 'Person updated successfully',
                RETURN: ret
            }
        except ValueError as ve:
            raise wz.NotFound(str(ve))
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: {str(err)}')


# This is the endpoint for creating the people
@api.route(f'{PEOPLE_EP}/create/form')
class CreatePeopleForm(Resource):
    """
    Form to add a new person to the journal database.
    """
    def get(self):
        # return {PEOPLE_CREATE_FORM: pfrm.get_add_form()}
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
        if ret is not None:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {email}')


@api.route(f'{PEOPLE_EP}/create')
class PeopleCreate(Resource):
    """
    Add a person to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(PEOPLE_CREATE_FLDS)
    # api.expects indicates that you should expect
    # the PEOPLE_CREATE_FLDS in your payload in swagger
    def put(self):
        """
        Add a person.
        """
        try:
            # name = request.json[ppl.NAME]
            name = request.json.get(ppl.NAME)
            # both above will return the value associated with name
            # but get with parenthesis is safer and takes more time
            affiliation = request.json.get(ppl.AFFILIATION)
            email = request.json.get(ppl.EMAIL)
            role = request.json.get(ppl.ROLES)
            ret = ppl.create(name, affiliation, email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: '
                                   f'{err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }


MASTHEAD = 'Masthead'


# endpoint for Masthed
@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    """
    Get a journal's masthead.
    """
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}
