from database.utils.CRUD import CRUDInterface
from database.utils.CRUD import database
from database.common.models import RecordHistory, PriceSort, BestPrice, Photo, AnswerMaker, Hotels


database.connect()  # establishing the connection to db
database.create_tables([PriceSort, BestPrice, RecordHistory, Photo, AnswerMaker, Hotels])  # creation of db-tables

crud = CRUDInterface()




