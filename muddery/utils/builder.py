"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

from muddery.utils import loader
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import create, search, logger


def build_objects(model_name, unique, caller=None):
    """
    Build objects of a model.

    Args:
        model_name: (string) The name of the data model.
        unique: (boolean) If unique, every record in model should has one and only one
                          object in the world.
                          If not unique, a record can has zero or multiple objects.
        caller: (command caller) If provide, running messages will send to the caller.
    """
    ostring = "Building %s." % model_name
    print ostring
    if caller:
        caller.msg(ostring)

    model_obj = get_model(settings.WORLD_DATA_APP, model_name)

    # new objects
    new_obj_names = set(record.key for record in model_obj.objects.all())

    # current objects
    current_objs = loader.search_obj_info_model(model_name)

    # remove objects
    count_remove = 0
    count_update = 0
    count_create = 0
    current_obj_keys = set()

    for obj in current_objs:
        obj_key = loader.get_info_key(obj)

        if unique:
            if obj_key in current_obj_keys:
                # This object is duplcated.
                ostring = "Deleting %s" % obj_key
                print ostring
                if caller:
                    caller.msg(ostring)

                obj.delete()
                count_remove += 1
                continue

            if not obj_key in new_obj_names:
                # This object should be removed
                ostring = "Deleting %s" % obj_key
                print ostring
                if caller:
                    caller.msg(ostring)

                obj.delete()
                count_remove += 1
                continue

        try:
            loader.load_data(obj)
        except Exception, e:
            logger.log_errmsg("%s can not load data:%s" % (obj.dbref, e))

        current_obj_keys.add(obj_key)

    if unique:
        # Create objects.
        for record in model_obj.objects.all():
            if not record.key in current_obj_keys:
                # Create new objects.
                ostring = "Creating %s." % record.key
                print ostring
                if caller:
                    caller.msg(ostring)

                try:
                    obj = create.create_object(record.typeclass, record.name)
                    count_create += 1
                except Exception, e:
                    ostring = "Can not create obj %s: %s" % (record.name, e)
                    logger.log_errmsg(ostring)
                    if caller:
                        caller.msg(ostring)

                try:
                    loader.set_obj_data_info(obj, model_name, record.key)
                except Exception, e:
                    ostring = "Can not set data info to obj %s: %s" % (record.name, e)
                    logger.log_errmsg(ostring)
                    if caller:
                        caller.msg(ostring)

    ostring = "Removed %d object(s). Created %d object(s). Updated %d object(s). Total %d objects.\n"\
              % (count_remove, count_create, count_update, len(model_obj.objects.all()))
    print ostring
    if caller:
        caller.msg(ostring)


def build_details(model_name, caller=None):
    """
    Build details of a model.

    Args:
        model_name: (string) The name of the data model.
        caller: (command caller) If provide, running messages will send to the caller.
    """

    model_detail = get_model(settings.WORLD_DATA_APP, model_name)

    # Remove all details
    objects = search.search_object_attribute(key="details")
    for obj in objects:
        obj.attributes.remove("details")

    # Set details.
    count = 0
    for record in model_detail.objects.all():
        location_objs = loader.search_obj_info_key(record.location)

        # Detail's location.
        for location in location_objs:
            loader.set_obj_detail(location, record.name, record.desc)

            for name in record.name.split(";"):
                loader.set_obj_detail(location, name, record.desc)

            count += 1

    ostring = "Set %d detail(s)." % count
    print ostring
    if caller:
        caller.msg(ostring)


def build_all(caller=None):
    """
    Load csv data and build the world.

    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """

    for room_info in settings.WORLD_ROOMS:
        build_objects(room_info, True, caller)

    for exit_info in settings.WORLD_EXITS:
        build_objects(exit_info, True, caller)

    for object_info in settings.WORLD_OBJECTS:
        build_objects(object_info, True, caller)

    for object_info in settings.PERSONAL_OBJECTS:
        build_objects(object_info, False, caller)

    for detail_info in settings.WORLD_DETAILS:
        build_details(detail_info, caller)


