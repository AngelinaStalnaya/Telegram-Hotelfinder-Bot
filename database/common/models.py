from datetime import datetime
import peewee

test_database = peewee.SqliteDatabase('final_testings.db', autoconnect=True)  # creation of an instance of db, connection to the SQLite db


def make_table_name(model_class):  # function to proper naming of functions as "name_tbl"
    model_name = model_class.__name__
    return model_name.lower() + '_tbl'


class BaseModel(peewee.Model):  # base model creation (establishes the DB connection for all inherit models)

    class Meta:

        database = test_database
        legacy_table_names = False
        table_function = make_table_name


class PriceSort(BaseModel):  # creation of db-table for structuring data for site_api requests

    id = peewee.AutoField()
    user_id = peewee.IntegerField()
    sort = peewee.TextField()
    location_gaia = peewee.TextField()
    location_lat = peewee.TextField()
    location_long = peewee.TextField()
    location_full_name = peewee.TextField()
    check_in = peewee.DateField()
    check_out = peewee.DateField()
    creation_data = peewee.DateTimeField(default=datetime.now())
    results = peewee.IntegerField(default=0)


class BestPrice(PriceSort):

    cost_max = peewee.IntegerField()
    cost_min = peewee.IntegerField()
    distance_max = peewee.IntegerField()


class RecordHistory(BaseModel):  # creation of db-table for user's records history

    id = peewee.AutoField()
    user_id = peewee.IntegerField()
    creation_date = peewee.DateTimeField()
    operation = peewee.TextField()
    location = peewee.TextField()
    list_of_hotels = peewee.TextField()


class Photo(BaseModel):
    id = peewee.AutoField()
    hotel_address = peewee.TextField()
    hotel_name = peewee.TextField()
    hotel_id = peewee.IntegerField()
    urls = peewee.TextField()


class AnswerMaker(BaseModel):

    id = peewee.AutoField()
    command = peewee.TextField()
    user_id = peewee.IntegerField()
    hotel_id = peewee.IntegerField()
    hotel_name = peewee.TextField()
    distance = peewee.TextField()
    cost = peewee.TextField()
    total_cost = peewee.TextField()
    chosen_photo_amount = peewee.IntegerField(default=0)
    success = peewee.IntegerField(default=0)
    location = peewee.TextField()
    location_name = peewee.TextField()


class Hotels(BaseModel):
    id = peewee.AutoField()
    hotel_id = peewee.IntegerField()
    hotel_name = peewee.TextField()
    address = peewee.TextField()
    distance = peewee.TextField()
    url = peewee.TextField()
    all_photo = peewee.IntegerField()



