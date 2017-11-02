import pytest
from pyramid import testing
import transaction
from expense_tracker.models import (
    Expense,
    get_tm_session,
)
from expense_tracker.models.meta import Base
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from faker import Faker
import random

FAKE = Faker()


@pytest.fixture
def configuration(request):
    """Set up a Configurator instance.

    This Configurator instance sets up a pointer to the location of the
        database.
    It also includes the models from your app's model package.
    Finally it tears everything down, including the in-memory SQLite database.

    This configuration will persist for the entire duration of your PyTest run.
    """
    config = testing.setUp(settings={
        'sqlalchemy.url': 'postgres://localhost:5432/test_expenses'
    })
    config.include("expense_tracker.models")
    config.include("expense_tracker.routes")

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a session for interacting with the test database.

    This uses the dbsession_factory on the configurator instance to create a
    new database session. It binds that session to the available engine
    and returns a new session for every call of the dummy_request object.
    """
    SessionFactory = configuration.registry["dbsession_factory"]
    session = SessionFactory()
    engine = session.bind
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Instantiate a fake HTTP Request, complete with a database session.
    This is a function-level fixture, so every new request will have a
    new database session.
    """
    return testing.DummyRequest(dbsession=db_session)


def test_list_expenses_returns_list_of_expenses_in_dict(dummy_request):
    from expense_tracker.views.default import list_expenses
    response = list_expenses(dummy_request)
    assert 'expenses' in response
    assert isinstance(response['expenses'], list)


def test_expense_exists_and_is_in_list(dummy_request):
    from expense_tracker.views.default import list_expenses
    new_expense = Expense(
        title='test expense',
        amount=500,
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(new_expense)
    dummy_request.dbsession.commit()
    response = list_expenses(dummy_request)
    assert new_expense.to_dict() in response['expenses']


def test_detail_view_shows_expense_detail(dummy_request):
    from expense_tracker.views.default import expense_detail
    new_expense = Expense(
        title='test expense',
        amount=500,
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(new_expense)
    dummy_request.dbsession.commit()
    dummy_request.matchdict['id'] = 1
    response = expense_detail(dummy_request)
    assert response['expense'] == new_expense.to_dict()


def test_detail_view_non_existent_expense(dummy_request):
    from expense_tracker.views.default import expense_detail
    new_expense = Expense(
        title='test expense',
        amount=500,
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(new_expense)
    dummy_request.dbsession.commit()
    dummy_request.matchdict['id'] = 2
    with pytest.raises(HTTPNotFound):
        expense_detail(dummy_request)


def test_create_view_makes_new_expense(dummy_request):
    from expense_tracker.views.default import create_expense
    # send a post request to my view with data to make a new expense
    expense_info = {
        "title": "Transportation",
        "amount": 2.75,
        "due_date": '2017-11-02'
    }
    dummy_request.method = "POST"
    dummy_request.POST = expense_info
    create_expense(dummy_request)
    # if expense has been created, it should be in a database query
    expense = dummy_request.dbsession.query(Expense).first()
    assert expense.title == "Transportation"


def test_create_view_on_post_redirects_somewhere(dummy_request):
    from expense_tracker.views.default import create_expense
    # send a post request to my view with data to make a new expense
    expense_info = {
        "title": "Transportation",
        "amount": 2.75,
        "due_date": '2017-11-02'
    }
    dummy_request.method = "POST"
    dummy_request.POST = expense_info
    response = create_expense(dummy_request)
    assert isinstance(response, HTTPFound)


def test_create_view_returns_empty_dict_on_get(dummy_request):
    from expense_tracker.views.default import create_expense
    response = create_expense(dummy_request)
    assert response == {}


def test_create_view_incomplete_data_is_bad_request(dummy_request):
    from expense_tracker.views.default import create_expense
    expense_info = {
        "amount": 2.75,
        "due_date": '2017-11-02'
    }
    dummy_request.method = "POST"
    dummy_request.POST = expense_info
    with pytest.raises(HTTPBadRequest):
        create_expense(dummy_request)


@pytest.fixture(scope="session")
def testapp(request):
    from webtest import TestApp
    from pyramid.config import Configurator

    def main():
        settings = {
            'sqlalchemy.url': 'postgres://localhost:5432/test_expenses'
        }  # points to a database
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('expense_tracker.routes')
        config.include('expense_tracker.models')
        config.scan()
        return config.make_wsgi_app()

    app = main()

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)  # builds the tables

    def tearDown():
        Base.metadata.drop_all(bind=engine) # when tests are done, kill tables in DB

    request.addfinalizer(tearDown)

    return TestApp(app)


@pytest.fixture(scope="session")
def fill_the_db(testapp):
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(EXPENSES)

EXPENSES = []
for i in range(20):
    new_expense = Expense(
        title='potato{}'.format(i),
        amount=random.random() * 1000,
        due_date=FAKE.date_time()
    )
    EXPENSES.append(new_expense)


def test_home_route_has_table(testapp):
    response = testapp.get("/")
    assert len(response.html.find_all('table')) == 1
    assert len(response.html.find_all('tr')) == 1


def test_home_route_with_expenses_has_rows(testapp, fill_the_db):
    response = testapp.get("/")
    assert len(response.html.find_all('tr')) == 21


def test_detail_route_with_expenses_shows_expense_detail(testapp, fill_the_db):
    response = testapp.get("/expenses/3")
    assert 'potato2' in response.ubody


def test_create_view_successful_post_redirects_home(testapp):
    expense_info = {
        "title": "Transportation",
        "amount": 2.75,
        "due_date": '2017-11-02'
    }
    response = testapp.post("/expenses/new-expense", expense_info)
    assert response.location == 'http://localhost/'


def test_create_view_successful_post_actually_shows_home_page(testapp):
    expense_info = {
        "title": "Booze",
        "amount": 88.50,
        "due_date": '2017-11-02'
    }
    response = testapp.post("/expenses/new-expense", expense_info)
    next_page = response.follow()
    assert "Booze" in next_page.ubody
