# -*- coding: utf-8 -*-
from flask import Blueprint

route_app_management = Blueprint('app_management_page', __name__)
from web.controllers.admin.app_management.AppManagement import *
