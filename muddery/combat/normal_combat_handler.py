"""
Combat handler.
"""

from django.conf import settings
from muddery.utils import defines
from muddery.utils.builder import delete_object
from muddery.combat.base_combat_handler import BaseCombatHandler


class NormalCombatHandler(BaseCombatHandler):
    """
    This implements the normal combat handler.
    """
    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(NormalCombatHandler, self).start_combat()

        for character in self.characters.values():
            if not character.account:
                # Monsters auto cast skills
                character.start_auto_combat_skill()

    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        for character in self.characters.values():
            # Stop auto cast skills
            character.stop_auto_combat_skill()

        super(NormalCombatHandler, self).at_server_shutdown()

    def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        super(NormalCombatHandler, self).show_combat(character)

        # send messages in order
        character.msg({"combat_commands": character.get_combat_commands()})

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for character in self.characters.values():
            # Stop auto cast skills
            character.stop_auto_combat_skill()

        super(NormalCombatHandler, self).finish()

    def set_combat_results(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        # add exp to winners
        # get total exp
        exp = 0
        for loser in losers:
            exp += loser.provide_exp(loser)

        for character in winners:
            if exp:
                character.add_exp(exp)

            if character.is_typeclass(settings.BASE_PLAYER_CHARACTER_TYPECLASS):
                # get object list
                loots = None
                for loser in losers:
                    obj_list = loser.loot_handler.get_obj_list(character)
                    if obj_list:
                        if not loots:
                            loots = obj_list
                        else:
                            loots.extend(obj_list)

                # give objects to winner
                get_objects = []
                if loots:
                    get_objects = character.receive_objects(loots, mute=True)

                if character.has_account:
                    character.msg({"combat_finish":
                                        {"win": True,
                                         "exp": exp,
                                         "get_objects": get_objects}})

                # call quest handler
                for loser in losers:
                    character.quest_handler.at_objective(defines.OBJECTIVE_KILL, loser.get_data_key())

        # losers are killed.
        for character in losers:
            character.msg({"combat_finish": {"lose": True}})
            character.die(winners)

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        super(NormalCombatHandler, self)._cleanup_character(character)

        if not character.is_typeclass(settings.BASE_PLAYER_CHARACTER_TYPECLASS):
            if character.is_temp:
                # notify its location
                location = character.location
                delete_object(character.dbref)
                if location:
                    for content in location.contents:
                        if content.has_account:
                            content.show_location()
            else:
                if character.is_alive():
                    # Recover all hp.
                    character.db.hp = character.max_hp
