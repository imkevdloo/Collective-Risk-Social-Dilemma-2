import random

from otree.api import *
from otree.models import player
import itertools


doc = """
Test CRSD
"""


class Constants(BaseConstants):
    name_in_url = 'test_crsd'
    players_per_group = None
    num_rounds = 10
    regrowth_rate = 8
    withdrawal_decisions = [0, 1, 2, 3, 4]
    treatments = ['MECO', 'SECO']
    MECO_p = 0.625
    SECO_p = 0.5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.CharField()
    withdrawal_player = models.IntegerField(label="How many trees would you like to withdraw?")
    p2 = models.IntegerField(min=0, max=4)
    p3 = models.IntegerField(min=0, max=4)
    p4 = models.IntegerField(min=0, max=4)
    group_withdrawal = models.IntegerField(min=0, max=16)
    forest = models.IntegerField(min=20, max=20, label="Please indicate of how many trees the forest consists.")
    eco_status = models.StringField()
    sold_products = models.IntegerField(min=0, max=40)  # Equal to cumulative withdrawal_player of all rounds
    profit_round = models.FloatField()  # profit of only that round
    profit_total = models.FloatField()  # profit in total for player


# FUNCTIONS
def set_group_withdrawal(player):
    participant = player.participant
    participant.withdrawal_player = participant.withdrawal_player
    player.p2 = random.choice(Constants.withdrawal_decisions)
    player.p3 = random.choice(Constants.withdrawal_decisions)
    player.p4 = random.choice(Constants.withdrawal_decisions)
    participant.group_withdrawal = player.p2 + player.p3 + player.p4 + participant.withdrawal_player
    return participant.group_withdrawal


def set_forest(player):
    participant = player.participant
    participant.forest = participant.forest - participant.group_withdrawal + Constants.regrowth_rate
    return participant.forest


def set_eco_status(player):
    participant = player.participant
    if participant.treatment == 'MECO' or participant.treatment == 'SECO':
        if participant.eco_status == "Eco-label status: Yes!":
            if participant.withdrawal_player <= 2:
                participant.eco_status = "Eco-label status: Yes!"
                print("Yes")
            else:
                participant.eco_status = "Eco-label status: No!"
                print("No")
        else:
            participant.eco_status = "Eco-label status: No!"
    else:
        participant.eco_status = ""
    return participant.eco_status


def set_sold_products(player):
    participant = player.participant
    participant.sold_products = participant.sold_products + participant.withdrawal_player
    return participant.sold_products


def set_profit_round(player):
    participant = player.participant
    if participant.treatment == 'MECO' and participant.eco_status == "Eco-label status: Yes!":
        participant.profit_round = participant.withdrawal_player * Constants.MECO_p
    else:
        participant.profit_round = participant.withdrawal_player * Constants.SECO_p
    return participant.profit_round


def set_profit_total(player):
    participant = player.participant
    participant.profit_total = participant.profit_total + participant.profit_round
    return participant.profit_total


# PAGES
class Decision(Page):
    form_model = 'player'
    form_fields = ['withdrawal_player']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['withdrawal_player'] not in Constants.withdrawal_decisions:
            return 'Please fill in either 0, 1, 2, 3 or 4'

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.withdrawal_player = player.withdrawal_player
        participant.group_withdrawal = set_group_withdrawal(player)
        participant.forest = set_forest(player)
        participant.eco_status = set_eco_status(player)
        participant.sold_products = set_sold_products(player)
        participant.profit_round = set_profit_round(player)
        participant.profit_total = set_profit_total(player)


class GameOver(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest <= 0

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.round_number = player.round_number


class Results(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0

class EndGame(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 10 or player.participant.forest <= 0

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.round_number = player.round_number


page_sequence = [Decision, GameOver, Results, EndGame]
