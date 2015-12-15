"""
AttributeHandler handles a character's custom attributes.
"""

from muddery.utils.localized_strings_handler import LS
from django.conf import settings
from evennia.utils import logger


class AttributeHandler(object):
    """
    Handles a character's custom attributes.
    """
    def __init__(self, owner):
        """
        Initialize handler.
        """
        self.owner = owner
        self.attributes = owner.db.attributes


    def set(self, key, value=None):
        """
        Set an attribute.
        """
        self.attributes[key] = value


    def get(self, key, default=None):
        """
        Get an attribute. If the key does not exist, returns default.
        """
        if not key in self.attributes:
            return default

        return self.attributes[key]


    def remove(self, key):
        """
        Remove an attribute
        """
        if not key in self.attributes:
            return

        del self.attributes[key]


    def has(self, key):
        """
        Does this attribute exist.
        """
        return key in self.attributes


    def is_value(self, key, value):
        """
        Does this attribute match the value.
        """
        if not key in self.attributes:
            return False

        return self.attributes[key] == value
