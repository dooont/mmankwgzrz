"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS

import werkzeug.exceptions as wz
from http import HTTPStatus

import data.people as ppl

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
TITLE_EP = '/title'
TITLE_RESP = 'Title'
TITLE = 'The Journal of API Technology'
EDITOR_RESP = 'Editor'
EDITOR = 'ejc369@nyu.edu'
DATE_RESP = 'Date'
DATE = '2024-09-24'
REPO_NAME_EP = '/authors'
REPO_NAME_RESP = 'Repository Name'
REPO_NAME = 'mmankwgzrz'
PUBLISHER_RESP = 'Publisher'
PUBLISHER = 'Palgave'
PEOPLE_EP = '/people'
PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
})


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
class JournalTitle(Resource):
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
class printRepoName(Resource):
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


# This is the endpoint for the people
@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles creating, reading, updating
    and deleting the journal people.
    """
    def get(self):
        """
        Retrieve the journal people.
        """
        return ppl.get_people()


@api.route(f'{PEOPLE_EP}/<_id>')
class PeopleDelete(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    def delete(self, _id):
        ret = ppl.delete_person(_id)
        if ret is not None:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {_id}')


# PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
#     pflds.NAME: fields.String,
#     pflds.EMAIL: fields.String,
#     pflds.AFFILIATION: fields.String,
#     EDITOR: fields.String,
# })

PEOPLE_CREATE_FORM = 'People Add Form'