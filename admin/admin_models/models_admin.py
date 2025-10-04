from sqladmin import ModelView

from models.gis_models import *


class PointAdmin(ModelView, model=Point):
    column_list = [Point.id, Point.latitude, Point.longitude]


class RouteAdmin(ModelView, model=Route):
    column_list = [Route.id, Route.created_datetime]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]


class OrganizationCategoryAdmin(ModelView, model=OrganizationCategory):
    column_list = [OrganizationCategory.id, OrganizationCategory.name]


class ImageAdmin(ModelView, model=Image):
    column_list = [Image.id, Image.filepath]


class OrganizationAdmin(ModelView, model=Organization):
    column_list = [Organization.id, Organization.name]


class EventAdmin(ModelView, model=Event):
    column_list = [Event.id, Event.address, Event.worker]


class EventCategoryAdmin(ModelView, model=EventCategory):
    column_list = [EventCategory.id, EventCategory.name]