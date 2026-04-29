"""
This file extends the original demo by adding more complete API endpoints
for people and manuscripts. It includes CRUD operations, request validation,
and integration with the data layer. It also introduces structured input
models for Swagger and basic authorization checks for certain actions.
adding new endpoints people.
count which count the total number of people right now.
get roles which allows user to search how many people and their names
in certain role.
"""
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS

import werkzeug.exceptions as wz

import data.manuscripts as manu
import data.people as ppl
import data.roles as rls

import security.security as sec
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
MANU_EP = '/manuscripts'
PEOPLE_EP = '/people'
PUBLISHER = 'Palgave'
PUBLISHER_RESP = 'Publisher'
ROLES_EP = '/roles'
RETURN = 'return'
TITLE = 'The Journal of API Technology'
TITLE_EP = '/title'
TITLE_RESP = 'Title'


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
            PUBLISHER_RESP: PUBLISHER,
        }


@api.route(ROLES_EP)
class Roles(Resource):
    """
    This class handles reading person roles.
    """

    def get(self):
        """
        Retrieve the journal person roles.
        """
        return rls.read()


@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """

    def get(self):
        """
        Retrieve the journal people.
        """
        return ppl.read()


EDITOR = 'editor'


@api.route(f'{PEOPLE_EP}/<email>/<user_id>')
class Person(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """

    def get(self, email, user_id):
        """
        Retrieve a journal person.
        """
        person = ppl.read_one(email)
        if person:
            return person
        else:
            raise wz.NotFound(f'No such record: {email}')

    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    def delete(self, email, user_id):
        kwargs = {sec.LOGIN_KEY: 'any key for now'}
        if not sec.is_permitted(sec.PEOPLE, sec.DELETE, user_id,
                                **kwargs):
            raise wz.Forbidden('This user does not have '
                               + 'authorization for this action.')
        ret = ppl.delete(email)
        if ret is not None:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {email}')


PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.List(fields.String(), description='A list of roles')
})


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
            roles = request.json.get(ppl.ROLES)
            ret = ppl.create(name, affiliation, email, roles)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: '
                                   f'{err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }


@api.route(f'{PEOPLE_EP}/update')
class PeopleUpdate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(PEOPLE_CREATE_FLDS)
    def put(self):
        try:
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            email = request.json.get(ppl.EMAIL)
            roles = request.json.get(ppl.ROLES)
            ret = ppl.update(name, affiliation, email, roles)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: {err=}')
        return {
            MESSAGE: 'Person updated!',
            RETURN: ret,
        }


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


@api.route(MANU_EP)
class Manuscripts(Resource):
    def get(self):

        return manu.read()


MANU_ACTION_FLDS = api.model('ManuscriptAction', {
    manu.MANU_ID: fields.String,
    manu.CURR_STATE: fields.String,
    manu.ACTION: fields.String,
    manu.REFEREE: fields.String,
})


@api.route(f'{MANU_EP}/receive_action')
class ReceiveAction(Resource):

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(MANU_ACTION_FLDS)
    def put(self):
        try:
            print(request.json)
            manu_id = request.json.get(manu.MANU_ID)
            curr_state = request.json.get(manu.CURR_STATE)
            action = request.json.get(manu.ACTION)
            kwargs = {}
            kwargs[manu.REFEREE] = request.json.get(manu.REFEREE)
            ret = manu.handle_action(manu_id, curr_state, action, **kwargs)
        except Exception as err:
            raise wz.NotAcceptable(f'Bad action: ' f'{err=}')
        return {
            MESSAGE: 'Action received!',
            RETURN: ret,
        }


@api.route(f'{MANU_EP}/<string:manu_id>')
class Manuscript(Resource):

    def get(self, manu_id):
        manu_rec = manu.read_one(manu_id)
        if not manu_rec:
            raise wz.NotFound("No such manuscript.")
        return manu_rec


MANU_CREATE_FLDS = api.model('AddNewManuscript', {
    manu.TITLE: fields.String,
    manu.AUTHOR: fields.String,
})


@api.route(f'{MANU_EP}/create')
class ManuscriptCreate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(MANU_CREATE_FLDS)
    def post(self):

        try:
            title = request.json.get(manu.TITLE)
            author = request.json.get(manu.AUTHOR)
            ret = manu.create(title, author)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add manuscript: {err=}')
        return {
            MESSAGE: 'Manuscript added!',
            RETURN: ret,
        }


@api.route(f'{MANU_EP}/delete/<string:manu_id>')
class ManuscriptDelete(Resource):
    """
    Delete a manuscript.
    """

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript')
    def delete(self, manu_id):
        ret = manu.delete(manu_id)
        if ret == 0:
            raise wz.NotFound('No such manuscript.')
        return {
            MESSAGE: 'Manuscript deleted!',
            RETURN: manu_id,
        }


MANU_UPDATE_FLDS = api.model('UpdateManuscript', {
    'manu_id': fields.String,
    'new_state': fields.String,
})


@api.route(f'{MANU_EP}/update')
class ManuscriptUpdate(Resource):
    """
    Update manuscript state.
    """

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(MANU_UPDATE_FLDS)
    def put(self):
        try:
            manu_id = request.json.get('manu_id')
            new_state = request.json.get('new_state')

            ret = manu.update(manu_id, new_state)

            if ret == 0:
                raise wz.NotFound('No such manuscript.')

            return {
                MESSAGE: 'Manuscript updated!',
                RETURN: manu_id,
            }

        except Exception as err:
            raise wz.NotAcceptable(f'Could not update manuscript: {err}')


@api.route(f'{PEOPLE_EP}/count')
class PeopleCount(Resource):
    """
    Return total number of people in the journal db.
    """

    def get(self):
        return {'count': ppl.count()}


@api.route('/people/by-role/<string:role>')
class PeopleByRole(Resource):
    def get(self, role):
        """
        Retrieve all people who have the given role.
        """
        all_people = ppl.read()
        results = []

        for person in all_people.values():
            person_roles = person.get('roles', [])
            if role in person_roles:
                results.append(person)

        return {
            "role": role,
            "count": len(results),
            "people": results
        }
