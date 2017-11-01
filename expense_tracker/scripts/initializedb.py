import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import Expense
from datetime import datetime


FMT = '%m/%d/%Y'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


EXPENSES = [
    {'id': 1, 'title': 'Rent', 'amount': 50000, 'due_date': datetime.strptime('11/1/2017', FMT)},
    {'id': 2, 'title': 'Phone Bill', 'amount': 100, 'due_date': datetime.strptime('11/27/2017', FMT)},
    {'id': 3, 'title': 'Food', 'amount': 600, 'due_date': datetime.strptime('11/2/2017', FMT)},
    {'id': 4, 'title': 'Car', 'amount': 270, 'due_date': datetime.strptime('11/25/2017', FMT)},
    {'id': 5, 'title': 'Internet', 'amount': 100, 'due_date': datetime.strptime('11/12/2017', FMT)},
]


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    # Point to your environment's database URL before the engine is created
    settings['sqlalchemy.url'] = os.environ['DATABASE_URL']

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)  # drop all existing tables from this database
    Base.metadata.create_all(engine)  # make new tables based on whatever inherits from the Base class

    # ---- NOTHING BELOW THIS POINT IS NECESSARY UNLESS YOU WANT TO START WITH A NEW MODEL INSTANCE -----
    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        all_expenses = []
        for expense in EXPENSES:
            all_expenses.append(
                Expense(
                    title=expense['title'],
                    amount=expense['amount'],
                    due_date=expense['due_date']
                )
            )
        dbsession.add_all(all_expenses)
