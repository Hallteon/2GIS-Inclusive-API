from sqladmin import ModelView
from models.gis_models import *


class PointAdmin(ModelView, model=Point):
    column_list = [Point.id, Point.latitude, Point.longitude]


class RouteAdmin(ModelView, model=Route):
    column_list = [Route.id, Route.created_datetime]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]


# class TrafficFineAdmin(ModelView, model=TrafficFine):
#     column_list = [TrafficFine.id, TrafficFine.fines_collected_sum, TrafficFine.fines_imposed_sum]