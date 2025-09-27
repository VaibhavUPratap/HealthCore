"""
Routes package initializer.
Exposes blueprints for easy registration in app/__init__.py
"""

from .auth_routes import auth_bp
from .data_routes import data_bp

__all__ = ["auth_bp", "data_bp"]
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
import os
import logging
import time