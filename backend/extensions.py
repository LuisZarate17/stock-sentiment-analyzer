"""
Shared Flask extensions — instantiated here, initialized in create_app().
"""
from flask_caching import Cache

cache = Cache()
