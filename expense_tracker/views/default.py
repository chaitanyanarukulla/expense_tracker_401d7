from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from expense_tracker.models import Expense
from expense_tracker.security import is_authenticated
from datetime import datetime


@view_config(route_name='home', renderer="expense_tracker:templates/index.jinja2")
def list_expenses(request):
    expenses = request.dbsession.query(Expense).all()
    if not expenses:
        raise HTTPNotFound
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


@view_config(
    route_name='create',
    renderer="expense_tracker:templates/create_expense.jinja2",
    permission='secret'
)
def create_expense(request):
    """Create a new expense and add it to the database."""
    if request.method == "GET":
        return {'title': 'create'}

    if request.method == "POST":
        if not all([field in request.POST for field in ['title', 'amount', 'due_date']]):
            raise HTTPBadRequest
        new_expense = Expense(
            title=request.POST['title'],
            amount=request.POST['amount'],
            due_date=datetime.strptime(request.POST['due_date'], '%Y-%m-%d')
        )
        request.dbsession.add(new_expense)
        return HTTPFound(request.route_url('home'))


@view_config(
    route_name='update',
    renderer="expense_tracker:templates/edit_expense.jinja2",
    permission='secret'
)
def update_expense(request):
    """Create a new expense and add it to the database."""
    expense_id = int(request.matchdict['id'])
    expense = request.dbsession.query(Expense).get(expense_id)
    if not expense:
        raise HTTPNotFound

    if request.method == "GET":
        return {
            'title': 'Edit Expense',
            'expense': expense.to_dict()
        }

    if request.method == "POST":
        expense.title = request.POST['title']
        expense.amount = request.POST['amount']
        expense.due_date = datetime.strptime(request.POST['due_date'], '%Y-%m-%d')
        request.dbsession.add(expense)
        request.dbsession.flush()
        return HTTPFound(request.route_url('detail', id=expense.id))


@view_config(
    route_name='delete',
    permission='secret'
)
def delete_expense(request):
    expense_id = int(request.matchdict['id'])
    expense = request.dbsession.query(Expense).get(expense_id)
    if not expense:
        raise HTTPNotFound

    request.dbsession.delete(expense)
    return HTTPFound(request.route_url('home'))

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


@view_config(
    route_name='login',
    renderer="expense_tracker:templates/login.jinja2",
    permission=NO_PERMISSION_REQUIRED
)
def login(request):
    if request.authenticated_userid:
        return HTTPFound(request.route_url('home'))

    if request.method == "GET":
        return {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # do some verification
        if is_authenticated(username, password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

        return {
            'error': 'Username/password combination was bad.'
        }


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
