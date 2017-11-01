from sqlalchemy import (
    Column,
    Unicode,
    Float,
    DateTime,
    Integer
)

from .meta import Base
from datetime import datetime


class Expense(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    amount = Column(Float(precision=2))
    due_date = Column(DateTime)
    creation_date = Column(DateTime)

    def __init__(self, *args, **kwargs):
        """Modify the init method to do more things."""
        super(Expense, self).__init__(*args, **kwargs)
        self.creation_date = datetime.now()

    def to_dict(self):
        """Take all model attributes and render them as a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'due_date': self.due_date.strftime('%m/%d/%Y'),
            'creation_date': self.creation_date.strftime('%m/%d/%Y')
        }

# model1 = MyModel() <-- a model instance

# Index('my_index', MyModel.name, unique=True, mysql_length=255)
