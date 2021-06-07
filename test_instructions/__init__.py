import random
import itertools

from otree.api import *

c = Currency

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
        choices=[[1, 'I consent, I would like to participate'], [2, 'I do not consent, I do not wish to participate']],
        widget=widgets.RadioSelect,
        label="By choosing to consent below, you acknowledge that you have read and agree to the information provided "
              "above. You hereby acknowledge that you are at least 18 years old, your participation in the study is "
              "voluntary and you are aware that you may choose to terminate your participation at any time for any "
              "reason without any consequences.")

    treatment = models.StringField()
    forest = models.IntegerField(label="As a check, how many trees are there in the forest at the start of the game?")
    sold_products = models.IntegerField(min=0, max=40)
    profit_total = models.FloatField()


def creating_session(subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            participant = player.participant
            participant.treatment = random.choice(Constants.treatments)


# PAGES
class Welcome(Page):
    form_model = 'player'
    form_fields = 'consent'


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
    class InstructionsSECO(Page):
        @staticmethod
        def is_displayed(player):
            participant = player.participant
            return participant.treatment == 'Control'


class Check(Page):
    form_model = 'player'
    form_fields = ['forest']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.sold_products = 0
        player.profit_total = 0
        participant = player.participant
        participant.forest = player.forest
        participant.sold_products = player.sold_products
        participant.profit_total = player.profit_total


page_sequence = [Welcome, InstructionsMECO, InstructionsSECO, InstructionsControl, Check]
