"""
Upgrade custom's game dir to the latest version.
"""

import os, ast, json
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.server.upgrader import utils
from muddery.server.upgrader.base_upgrader import BaseUpgrader
from django.apps import apps


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.0.0 (include this version)
    from_min_version = (0, 3, 4)

    # from max version 0.3.3 (not include this version)
    from_max_version = (0, 3, 5)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        os.chdir(game_dir)

        # add models
        file_path = os.path.join(game_dir, "worlddata", "models.py")
        utils.file_append(file_path, ["\n",
                                      "class action_room_interval(BaseModels.action_room_interval):\n",
                                      "    pass\n",
                                      "\n",
                                      "\n",
                                      "class action_message(BaseModels.action_message):\n",
                                      "    pass\n",
                                      "\n",
                                      "\n",
                                      "class action_get_objects(BaseModels.action_get_objects):\n",
                                      "    pass\n",
                                      "\n"
                                      ])

        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations", "worlddata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "worlddata"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)



    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
