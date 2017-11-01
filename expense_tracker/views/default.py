from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from expense_tracker.models import Expense


@view_config(route_name='home', renderer="expense_tracker:templates/index.jinja2")
def list_expenses(request):
    expenses = request.dbsession.query(Expense).all()
    expenses = [expense.to_dict() for expense in expenses]
    return {
        "title": "Expense List",
        "expenses": expenses
    }


@view_config(route_name='detail', renderer="expense_tracker:templates/detail.jinja2")
def expense_detail(request):
    expense_id = int(request.matchdict['id'])
    expense = request.dbsession.query(Expense).get(expense_id)
    if expense:
        return {
            'title': 'One Expense',
            'expense': expense.to_dict()
        }
    raise HTTPNotFound


# @view_config(route_name="api_detail", renderer="json")
# def api_detail(request):
#     expense_id = int(request.matchdict['id'])
#     if expense_id < 0 or expense_id > len(EXPENSES) - 1:
#         raise HTTPNotFound
#     expense = list(filter(lambda expense: expense['id'] == expense_id, EXPENSES))[0]
#     expense['due_date'] = expense['due_date'].strftime(FMT)
#     return {
#         'title': 'One Expense',
#         'expense': expense
#     }
