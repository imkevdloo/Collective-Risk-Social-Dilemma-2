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
        [1, 'I consent, I would like to participate'], [2, 'I do not consent, I do not wish to participate']
        ],
        widget=widgets.RadioSelect,
    )
    treatment = models.StringField()
    forest = models.IntegerField(label="How many trees are there in the forest at the start of the game?")
    check_threshold = models.IntegerField(label="The game ends when the forest reaches ... trees.")
    sold_products = models.IntegerField(min=0, max=40)
    profit_total = models.FloatField()
    eco_status = models.StringField()


def creating_session(subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            participant = player.participant
            participant.treatment = random.choice(Constants.treatments)
            print(participant.treatment)


# PAGES
class Welcome(Page):
    form_model = 'player'
    form_fields = ['consent']


class InstructionsMECO(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'MECO'


class InstructionsSECO(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'SECO'


class InstructionsControl(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.treatment == 'Control'


class Check(Page):
    form_model = 'player'
    form_fields = ['forest', 'check_threshold']

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['forest'] != 20 or values['check_threshold'] != 0:
            return 'One or more of your answers are not correct. Please try again!'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.sold_products = 0
        player.profit_total = 0
        player.eco_status = "Eco-label status: Yes!"
        participant = player.participant
        participant.forest = player.forest
        participant.sold_products = player.sold_products
        participant.profit_total = player.profit_total
        participant.eco_status = player.eco_status


class ReadyToStart(Page):
    pass


page_sequence = [Welcome, InstructionsMECO, InstructionsSECO, InstructionsControl, Check, ReadyToStart]
