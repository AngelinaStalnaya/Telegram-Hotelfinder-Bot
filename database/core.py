from database.utils.CRUD import CRUDInterface
from database.utils.CRUD import test_database
from database.common.models import RecordHistory, PriceSort, BestPrice, Photo, AnswerMaker, Hotels


test_database.connect()  # establishing the connection to db
test_database.create_tables([PriceSort, BestPrice, RecordHistory, Photo, AnswerMaker, Hotels])  # creation of db-tables

crud = CRUDInterface()




