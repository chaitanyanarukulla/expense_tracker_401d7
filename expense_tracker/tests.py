from pyramid.testing import DummyRequest
import pytest


def test_list_expenses_returns_list_of_expenses_in_dict():
    from expense_tracker.views.default import list_expenses
    req = DummyRequest()
    response = list_expenses(req)
    assert 'expenses' in response
    assert isinstance(response['expenses'], list)


@pytest.fixture
def testapp():
    from webtest import TestApp
    from pyramid.config import Configurator

    def main():
        config = Configurator()
        config.include('pyramid_jinja2')
        config.include('.routes')
        config.scan()
        return config.make_wsgi_app()

    app = main()
    return TestApp(app)


def test_home_route_has_table(testapp):
    from expense_tracker.views.default import EXPENSES
    response = testapp.get("/")
    assert len(EXPENSES) == len(response.html.find_all('tr')) - 1
