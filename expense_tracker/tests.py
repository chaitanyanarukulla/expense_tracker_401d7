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


def test_list_view_returns_dict(dummy_request):
    from expense_tracker.views.default import list_expenses
    expense = Expense(
        title="Harry potter reference",
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(expense)
    dummy_request.dbsession.commit()
    response = list_expenses(dummy_request)
    assert isinstance(response, dict)


def tests_home_route_is_200_ok(dummy_request):
    from expense_tracker.views.default import list_expenses
    expense = Expense(
        title="Harry potter reference",
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(expense)
    dummy_request.dbsession.commit()
    response = list_expenses(dummy_request)
    assert response['title'] == 'Expense List'


def test_expense_is_added_to_db(db_session):
    first_len = len(db_session.query(Expense).all())
    expense = Expense(
        title="Harry potter reference",
        amount=5
    )
    db_session.add(expense)
    db_session.commit()
    assert len(db_session.query(Expense).all()) == first_len + 1


def test_created_expense_in_db_is_dict(dummy_request):
    from expense_tracker.views.default import list_expenses
    expense = Expense(
        title="Harry potter reference",
        amount=5,
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(expense)
    dummy_request.dbsession.commit()
    response = list_expenses(dummy_request)
    assert isinstance(response, dict)


def test_detail_view_non_existent_expense(dummy_request):
    from expense_tracker.views.default import expense_detail
    expense = Expense(
        title="Harry potter reference",
        amount=5,
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(expense)
    dummy_request.dbsession.commit()
    dummy_request.matchdict['id'] = 2000
    with pytest.raises(HTTPNotFound):
        expense_detail(dummy_request)


def test_create_view_still_works(dummy_request):
    from expense_tracker.views.default import create_expense
    response = create_expense(dummy_request)
    assert response['title'] == 'create'


def test_list_view_return_expense_instance_with_incomplete_info(dummy_request):
    from expense_tracker.views.default import list_expenses
    expense = Expense(
        title="Harry potter reference",
        due_date=datetime.now()
    )
    dummy_request.dbsession.add(expense)
    dummy_request.dbsession.commit()
    request = dummy_request
    response = list_expenses(request)
    assert 'amount' not in response


def test_list_view_http_not_found(dummy_request):
    from expense_tracker.views.default import list_expenses
    with pytest.raises(HTTPNotFound):
        list_expenses(dummy_request)


def test_update_view_still_works(dummy_request):
    from expense_tracker.views.default import update_expense
    updated_entry = {
        'title': 'flerg',
        'amount': 5,
        'due_date': datetime.now()
    }
    dummy_request.method = "POST"
    dummy_request.POST = updated_entry
    dummy_request.matchdict[1]
    response = update_expense(dummy_request)
    assert response['title'] == 'Edit Expense'


def test_create_view_adds_entry_on_post_request(dummy_request, db_session):
    from expense_tracker.views.default import create_expense
    entry = {
        'title': 'flerg',
        'amount': 5,
        'due_date': '2017-11-8'
    }
    dummy_request.method = "POST"
    dummy_request.POST = entry
    create_expense(dummy_request)
    query = db_session.query(Expense)
    assert query.get(1).title == "flerg"


def test_request_method_is_httpfound(dummy_request):
    from expense_tracker.views.default import create_expense
    dummy_request.method = "POST"
    dummy_request.POST = {
        'title': 'flerg',
        'amount': 5,
        'due_date': '2017-11-8'
    }
    response = create_expense(dummy_request)
    assert isinstance(response, HTTPFound)


def test_update_view_updates_entry_via_website(dummy_request):
    from expense_tracker.views.default import update_expense
    entry = {
        'title': 'flerg',
        'amount': 5,
        'due_date': '2017-11-8'
    }
    dummy_request.method = "POST"
    dummy_request.POST = entry
    dummy_request.matchdict['id'] = 1
    update_expense(dummy_request)
    entry = dummy_request.dbsession.query(Expense).get(1)
    assert entry.title == 'flerg' and entry.amount == 5

# def test_list_expenses_returns_list_of_expenses_in_dict(dummy_request):
#     from expense_tracker.views.default import list_expenses
#     response = list_expenses(dummy_request)
#     assert 'expenses' in response
#     assert isinstance(response['expenses'], list)


# def test_expense_exists_and_is_in_list(dummy_request):
#     from expense_tracker.views.default import list_expenses
#     new_expense = Expense(
#         title='test expense',
#         amount=500,
#         due_date=datetime.now()
#     )
#     dummy_request.dbsession.add(new_expense)
#     dummy_request.dbsession.commit()
#     response = list_expenses(dummy_request)
#     assert new_expense.to_dict() in response['expenses']


# def test_detail_view_shows_expense_detail(dummy_request):
#     from expense_tracker.views.default import expense_detail
#     new_expense = Expense(
#         title='test expense',
#         amount=500,
#         due_date=datetime.now()
#     )
#     dummy_request.dbsession.add(new_expense)
#     dummy_request.dbsession.commit()
#     dummy_request.matchdict['id'] = 1
#     response = expense_detail(dummy_request)
#     assert response['expense'] == new_expense.to_dict()


# def test_detail_view_non_existent_expense(dummy_request):
#     from expense_tracker.views.default import expense_detail
#     new_expense = Expense(
#         title='test expense',
#         amount=500,
#         due_date=datetime.now()
#     )
#     dummy_request.dbsession.add(new_expense)
#     dummy_request.dbsession.commit()
#     dummy_request.matchdict['id'] = 2
#     with pytest.raises(HTTPNotFound):
#         expense_detail(dummy_request)


# def test_create_view_makes_new_expense(dummy_request):
#     from expense_tracker.views.default import create_expense
#     # send a post request to my view with data to make a new expense
#     expense_info = {
#         "title": "Transportation",
#         "amount": 2.75,
#         "due_date": '2017-11-02'
#     }
#     dummy_request.method = "POST"
#     dummy_request.POST = expense_info
#     create_expense(dummy_request)
#     # if expense has been created, it should be in a database query
#     expense = dummy_request.dbsession.query(Expense).first()
#     assert expense.title == "Transportation"


# def test_create_view_on_post_redirects_somewhere(dummy_request):
#     from expense_tracker.views.default import create_expense
#     # send a post request to my view with data to make a new expense
#     expense_info = {
#         "title": "Transportation",
#         "amount": 2.75,
#         "due_date": '2017-11-02'
#     }
#     dummy_request.method = "POST"
#     dummy_request.POST = expense_info
#     response = create_expense(dummy_request)
#     assert isinstance(response, HTTPFound)


# def test_create_view_returns_empty_dict_on_get(dummy_request):
#     from expense_tracker.views.default import create_expense
#     response = create_expense(dummy_request)
#     assert response == {}


# def test_create_view_incomplete_data_is_bad_request(dummy_request):
#     from expense_tracker.views.default import create_expense
#     expense_info = {
#         "amount": 2.75,
#         "due_date": '2017-11-02'
#     }
#     dummy_request.method = "POST"
#     dummy_request.POST = expense_info
#     with pytest.raises(HTTPBadRequest):
#         create_expense(dummy_request)



# @pytest.fixture(scope="session")
# def testapp(request):
#     from webtest import TestApp
#     from pyramid.config import Configurator

#     def main():
#         settings = {
#             'sqlalchemy.url': 'postgres://localhost:5432/test_expenses'
#         }  # points to a database
#         config = Configurator(settings=settings)
#         config.include('pyramid_jinja2')
#         config.include('expense_tracker.routes')
#         config.include('expense_tracker.models')
#         config.scan()
#         return config.make_wsgi_app()

#     app = main()

#     SessionFactory = app.registry["dbsession_factory"]
#     engine = SessionFactory().bind
#     Base.metadata.create_all(bind=engine)  # builds the tables

#     def tearDown():
#         Base.metadata.drop_all(bind=engine) # when tests are done, kill tables in DB

#     request.addfinalizer(tearDown)

#     return TestApp(app)


# @pytest.fixture(scope="session")
# def fill_the_db(testapp):
#     SessionFactory = testapp.app.registry["dbsession_factory"]
#     with transaction.manager:
#         dbsession = get_tm_session(SessionFactory, transaction.manager)
#         dbsession.add_all(EXPENSES)

# EXPENSES = []
# for i in range(20):
#     new_expense = Expense(
#         title='potato{}'.format(i),
#         amount=random.random() * 1000,
#         due_date=FAKE.date_time()
#     )
#     EXPENSES.append(new_expense)


# def test_home_route_has_table(testapp):
#     response = testapp.get("/")
#     assert len(response.html.find_all('table')) == 1
#     assert len(response.html.find_all('tr')) == 1


# def test_home_route_with_expenses_has_rows(testapp, fill_the_db):
#     response = testapp.get("/")
#     assert len(response.html.find_all('tr')) == 21


# def test_detail_route_with_expenses_shows_expense_detail(testapp, fill_the_db):
#     response = testapp.get("/expenses/3")
#     assert 'potato2' in response.ubody


# def test_create_view_successful_post_redirects_home(testapp):
#     expense_info = {
#         "title": "Transportation",
#         "amount": 2.75,
#         "due_date": '2017-11-02'
#     }
#     response = testapp.post("/expenses/new-expense", expense_info)
#     assert response.location == 'http://localhost/'


# def test_create_view_successful_post_actually_shows_home_page(testapp):
#     expense_info = {
#         "title": "Booze",
#         "amount": 88.50,
#         "due_date": '2017-11-02'
#     }
#     response = testapp.post("/expenses/new-expense", expense_info)
#     next_page = response.follow()
#     assert "Booze" in next_page.ubody
