import random
import itertools

from otree.api import *

doc = """
Welcome page with consent form and instructions.
"""


class Constants(BaseConstants):
    name_in_url = 'test_instructions'
    players_per_group = None
    num_rounds = 1
    treatments = ['MECO', 'SECO', 'Control']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.IntegerField(
        choices=[
            [1, 'I consent, I would like to participate.']
        ], widget = widgets.RadioSelect)
    treatment = models.StringField()
    forest = models.IntegerField(label="How many trees are there in the forest at the start of the game?")
    check_threshold = models.IntegerField(label="The game ends after 10 rounds or when the forest has ... trees left.")
    check_profit_Control = models.FloatField(label="If you have removed a total of 16 trees at the end of the game,"
                                                   " what will your total profit be?")
    check_profit_MECO = models.FloatField(label="You have removed 1 tree in round 1, 4 trees in round 2, and 1 tree in round 3. "
                                                "How many points did you earn at the end of round 3?")
    check_profit_SECO = models.FloatField(label="You have removed 1 tree in round 1, 4 trees in round 2, and 1 tree in round 3. "
                                                "How many points did you earn at the end of round 3?")
    trees_player_total = models.IntegerField(min=0, max=40)
    trees_group_total = models.IntegerField()
    points_group_total = models.FloatField()
    points_player_total = models.FloatField()
    eco_status = models.StringField()


def creating_session(subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            participant = player.participant
            participant.treatment = random.choice(Constants.treatments)
            print(participant.treatment)
    return participant.treatment


# PAGES
class Welcome(Page):
    form_model = 'player'
    form_fields = ['consent']


class InstructionsMECO(Page):
    form_model = 'player'
    form_fields = ['forest', 'check_threshold', 'check_profit_MECO']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'MECO'

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['forest'] != 20 or values['check_threshold'] != 0 or values['check_profit_MECO'] != 3.25:
            return 'One or more of your answers are not correct. Please try again!'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.trees_player_total = 0
        player.points_player_total = 0
        player.eco_status = "Yes"
        participant = player.participant
        participant.forest = player.forest
        participant.trees_group_total = 0
        participant.points_group_total = 0
        participant.trees_player_total = player.trees_player_total
        participant.points_player_total = player.points_player_total
        participant.eco_status = player.eco_status


class InstructionsSECO(Page):
    form_model = 'player'
    form_fields = ['forest', 'check_threshold', 'check_profit_SECO']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'SECO'

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['forest'] != 20 or values['check_threshold'] != 0 or values['check_profit_SECO'] != 6:
            return 'One or more of your answers are not correct. Please try again!'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.trees_player_total = 0
        player.points_player_total = 0
        player.eco_status = "Yes"
        participant = player.participant
        participant.forest = player.forest
        participant.trees_group_total = 0
        participant.points_group_total = 0
        participant.trees_player_total = player.trees_player_total
        participant.points_player_total = player.points_player_total
        participant.eco_status = player.eco_status


class InstructionsControl(Page):
    form_model = 'player'
    form_fields = ['forest', 'check_threshold', 'check_profit_Control']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'Control'

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['forest'] != 20 or values['check_threshold'] != 0  or values['check_profit_Control'] != 8:
            return 'One or more of your answers are not correct. Please try again!'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.trees_player_total = 0
        player.points_player_total = 0
        player.eco_status = "Yes"
        participant = player.participant
        participant.forest = player.forest
        participant.trees_group_total = 0
        participant.points_group_total = 0
        participant.trees_player_total = player.trees_player_total
        participant.points_player_total = player.points_player_total
        participant.eco_status = player.eco_status


class ReadyToStart(Page):
    pass


page_sequence = [Welcome, InstructionsMECO, InstructionsSECO, InstructionsControl, ReadyToStart]
