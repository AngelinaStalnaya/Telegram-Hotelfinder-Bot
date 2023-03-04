from typing import List, Dict, TypeVar, Any

from database.common.models import *

T = TypeVar('T')  # any type


def _create_data(model: T, data: List, db=test_database) -> None:  # insert a new record
     db.connect(reuse_if_open=True)
     if model == PriceSort:
          model.create(user_id=data[0], sort=data[1], location_gaia=data[2],
                                location_lat=data[3], location_long=data[4],
                                location_full_name=data[5], check_in=data[6],
                                check_out=data[7])
     elif model == BestPrice:
         model.create(user_id=data[0], sort=data[1], location_gaia=data[2],
                               location_lat=data[3], location_long=data[4],
                               location_full_name=data[5], check_in=data[6],
                               check_out=data[7],  cost_max=data[8],
                               cost_min=data[9], distance_max=data[10])
     elif model == RecordHistory:
         model.create(user_id=data[0], operation=data[1], location=data[2],
                                list_of_hotels=data[3], creation_date=data[4])
     elif model == Hotels:
         model.create(hotel_id=data[0], hotel_name=data[1],
                                address=data[2], distance=data[3],
                                url=data[4], all_photo=data[5])
     elif model == AnswerMaker:
         model.create(user_id=data[0], hotel_id=data[1], cost=data[2],
                                total_cost=data[3], location=data[4], hotel_name=data[5],
                                 distance=data[6], command=data[7], location_name=data[8])
     db.close()


def _create_multiple_data(model: T, data: List[Dict], db=test_database) -> None:
    db.connect(reuse_if_open=True)
    with db.atomic():
        model.insert_many(data).execute()
    db.close()


def _retrieve_all_data(model: T, db=test_database) -> peewee.ModelSelect | bool:  # select & return data
    with db.atomic():
        db.connect(reuse_if_open=True)
        response = model.select().order_by(model.id.desc()).limit(1)
        if response:
            return response
        else:
            return False


def _check_hotel_in_database(model: T, hotel_id: int, db=test_database) -> peewee.ModelSelect | bool:
    db.connect(reuse_if_open=True)
    response = model.select().where(model.hotel_id == hotel_id)
    if response:
        return response
    else:
        return False



def _retrieve_next_hotel(model: T, user_id: int, db=test_database) -> peewee.ModelSelect| bool:
    db.connect(reuse_if_open=True)
    response = model.select(model.hotel_id, model.hotel_name, model.cost, model.total_cost,
                                               model.location, model.distance).where(model.user_id == user_id
                                                and model.success == 0).limit(1)
    if response:
        return response
    else:
        return False


def _retrieve_history_data(model: T, user_id: int, db=test_database) -> tuple [Any, Any]| bool:
    with db.atomic():
        db.connect(reuse_if_open=True)
        response = model.select(model.creation_date,
                             model.operation,
                             model.location,
                              model.list_of_hotels).where(user_id == user_id).order_by(model.creation_date.desc()).limit(10)
        count = model.select(model.operation).where(user_id == user_id).count()
        if response and count:
            return response, count
        else:
            return False


def _retrieve_photo_data(model: T, hotel_id: int, photo_amount: int, db=test_database) -> peewee.ModelSelect | bool:
    with db.atomic():
        db.connect(reuse_if_open=True)
        response = model.select(model.urls).where(model.hotel_id == hotel_id).limit(photo_amount)
        if response:
            return response
        else:
            return False


def _retrieve_hotels_for_history_db(model: T, user_id: int, db=test_database) -> tuple[Any, Any]:
    with db.atomic():
        db.connect(reuse_if_open=True)
        response = model.select(model.command, model.hotel_name,
                             model.location_name, model.user_id).where(user_id == user_id)
        all_hotels = model.select(model.hotel_name).where(user_id == user_id).count()
        if response and all_hotels:
            return response, all_hotels


def _delete_old(model: T, user_id, db=test_database) -> None:  # executing old instances delete
    db.connect(reuse_if_open=True)
    query = model.select().where(model.user_id == user_id).order_by(model.creation_date.desc()).limit(3)
    with db.atomic():
        model.delete().where(model.user_id == user_id and query[-1].creation_date > model.creation_date).execute()
    db.close()


def _delete_answers(model: T, user_id: int, db=test_database) -> None:
    with db.atomic():
        db.connect(reuse_if_open=True)
        model.delete().where(model.user_id == user_id).execute()
    db.close()


def _update(model: T, id_line: int = None, amount: int = None,
                     success: int = None, hotel_id: int = None, db=test_database) -> None:  # executing update of model instance
    db.connect(reuse_if_open=True)
    if model == PriceSort or model == BestPrice:
        model.update({model.results: amount}).where(model.id == id_line).execute()
    elif model == AnswerMaker and success is not None:
        model.update({model.success: success}).where(model.hotel_id == hotel_id).execute()
    elif model == AnswerMaker:
        model.update({model.chosen_photo_amount: amount}). where(model.hotel_id == hotel_id).execute()
    db.close()


class CRUDInterface:

    @staticmethod
    def create(model, data):
        return _create_data(model=model, data=data)

    @staticmethod
    def retrieve_all(model):
        return _retrieve_all_data(model=model)

    @staticmethod
    def retrieve_history(model, user_id):
        return _retrieve_history_data(model=model, user_id=user_id)

    @staticmethod
    def retrieve_hotel(model, user_id):
        return _retrieve_next_hotel(model=model, user_id=user_id)

    @staticmethod
    def check_hotel(model, hotel_id):
        return _check_hotel_in_database(model=model, hotel_id=hotel_id)

    @staticmethod
    def delete_old(model, user_id):
        return _delete_old(model=model, user_id=user_id)

    @staticmethod
    def update(model, id_line=None, amount=None, success=None, hotel_id=None):
        return _update(model=model, id_line=id_line, amount=amount,
                                   success=success, hotel_id=hotel_id)

    @staticmethod
    def create_many(model, data):
        return _create_multiple_data(model=model, data=data)

    @staticmethod
    def retrieve_photo(model, hotel_id, photo_amount):
        return _retrieve_photo_data(model=model, hotel_id=hotel_id, photo_amount=photo_amount)

    @staticmethod
    def retrieve_hotels_for_db(model, user_id):
        return _retrieve_hotels_for_history_db(model=model, user_id=user_id)

    @staticmethod
    def delete_answers(model, user_id):
        return _delete_answers(model=model, user_id=user_id)


if __name__ == "__main__":

    CRUDInterface()
