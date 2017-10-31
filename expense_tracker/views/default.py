from pyramid.view import view_config
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound


FMT = '%m/%d/%Y'
EXPENSES = [
    {'id': 1, 'title': 'Rent', 'amount': 50000, 'due_date': datetime.strptime('11/1/2017', FMT)},
    {'id': 2, 'title': 'Phone Bill', 'amount': 100, 'due_date': datetime.strptime('11/27/2017', FMT)},
    {'id': 3, 'title': 'Food', 'amount': 600, 'due_date': datetime.strptime('11/2/2017', FMT)},
    {'id': 4, 'title': 'Car', 'amount': 270, 'due_date': datetime.strptime('11/25/2017', FMT)},
    {'id': 5, 'title': 'Internet', 'amount': 100, 'due_date': datetime.strptime('11/12/2017', FMT)},
]


@view_config(route_name='home', renderer="expense_tracker:templates/index.jinja2")
def list_expenses(request):
    return {
        "title": "Expense List",
        "expenses": EXPENSES
    }


@view_config(route_name='detail', renderer="expense_tracker:templates/detail.jinja2")
def expense_detail(request):
    expense_id = int(request.matchdict['id'])
    if expense_id < 0 or expense_id > len(EXPENSES) - 1:
        raise HTTPNotFound
    expense = list(filter(lambda expense: expense['id'] == expense_id, EXPENSES))[0]
    return {
        'title': 'One Expense',
        'expense': expense
    }


@view_config(route_name="api_detail", renderer="json")
def api_detail(request):
    expense_id = int(request.matchdict['id'])
    if expense_id < 0 or expense_id > len(EXPENSES) - 1:
        raise HTTPNotFound
    expense = list(filter(lambda expense: expense['id'] == expense_id, EXPENSES))[0]
    expense['due_date'] = expense['due_date'].strftime(FMT)
    return {
        'title': 'One Expense',
        'expense': expense
    }
