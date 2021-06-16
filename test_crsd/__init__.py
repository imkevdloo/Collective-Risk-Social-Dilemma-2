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
    removal_decisions = [0, 1, 2, 3, 4]
    treatments = ['MECO', 'SECO', 'Control']
    MECO_p = 0.625
    SECO_p = 0.5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.CharField()
    tree_removal_player = models.IntegerField(label="How many trees would you like to withdraw?")
    p2 = models.IntegerField(min=0, max=4)
    p3 = models.IntegerField(min=0, max=4)
    p4 = models.IntegerField(min=0, max=4)
    group_withdrawal = models.IntegerField(min=0, max=16)
    total_group_withdrawal = models.IntegerField()
    forest = models.IntegerField(min=20, max=20, label="Please indicate of how many trees the forest consists.")
    eco_status = models.StringField()
    sold_products = models.IntegerField(min=0, max=40)  # Equal to cumulative tree_removal_player of all rounds
    profit_round = models.FloatField()  # profit of only that round
    profit_total = models.FloatField()  # profit in total for player
    sustainable_production = models.LongStringField()
    sButtonClick = models.StringField(label="")
    sTimeClick = models.StringField(label="")
    game_over = models.IntegerField(min=0, max=1)


# FUNCTIONS
def set_group_withdrawal(player):
    participant = player.participant
    participant.tree_removal_player = participant.tree_removal_player
    player.p2 = 4  # random.choice(Constants.removal_decisions) # always sustainable (0, 1, 2)
    player.p3 = 4  # random.choice(Constants.removal_decisions) # always selfish (3, 4)
    player.p4 = 4  # random.choice(Constants.removal_decisions) # group_withdrawal > 10 --> 3 or 4,
    participant.group_withdrawal = player.p2 + player.p3 + player.p4 + participant.tree_removal_player
    return participant.group_withdrawal


def set_forest(player):
    participant = player.participant
    participant.forest = participant.forest - participant.group_withdrawal + Constants.regrowth_rate
    return participant.forest


def set_eco_status(player):
    participant = player.participant
    if participant.treatment == 'MECO' or participant.treatment == 'SECO':
        if participant.eco_status == "Yes":
            if participant.tree_removal_player <= 2:
                participant.eco_status = "Yes"
            else:
                participant.eco_status = "No"
        else:
            participant.eco_status = "No"
    else:
        participant.eco_status = " "
    return participant.eco_status


def set_sold_products(player):
    participant = player.participant
    participant.sold_products = participant.sold_products + participant.tree_removal_player
    return participant.sold_products


def set_profit_round(player):
    participant = player.participant
    if participant.treatment == 'MECO' and participant.eco_status == "Yes":
        participant.profit_round = participant.tree_removal_player * Constants.MECO_p
    else:
        participant.profit_round = participant.tree_removal_player * Constants.SECO_p
    return participant.profit_round


def set_profit_total(player):
    participant = player.participant
    participant.profit_total = participant.profit_total + participant.profit_round
    return participant.profit_total


def set_sustainable_production(player):
    participant = player.participant
    if participant.eco_status == "Yes":
        participant.sustainable_production = "Your production is sustainable."
        print(participant.sustainable_production)
    else:
        participant.sustainable_production = "Your production is not sustainable."
        print(participant.sustainable_production)
    return participant.sustainable_production


def set_total_group_withdrawal(player):
    participant = player.participant
    participant.total_group_withdrawal = participant.total_group_withdrawal + participant.group_withdrawal
    return participant.total_group_withdrawal


# PAGES
class DecisionEco(Page):
    form_model = 'player'
    form_fields = ['tree_removal_player', 'sButtonClick', 'sTimeClick']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0 and (participant.treatment == 'MECO' or participant.treatment == 'SECO')

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['tree_removal_player'] not in Constants.removal_decisions:
            return 'Please fill in either 0, 1, 2, 3 or 4'

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.tree_removal_player = player.tree_removal_player
        participant.group_withdrawal = set_group_withdrawal(player)
        participant.forest = set_forest(player)
        participant.total_group_withdrawal = set_total_group_withdrawal(player)
        participant.eco_status = set_eco_status(player)
        participant.sold_products = set_sold_products(player)
        participant.profit_round = set_profit_round(player)
        participant.profit_total = set_profit_total(player)
        participant.sButtonClick = player.sButtonClick
        participant.sTimeClick = player.sTimeClick
        participant.game_over = 0


class DecisionControl(Page):
    form_model = 'player'
    form_fields = ['tree_removal_player', 'sButtonClick', 'sTimeClick']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0 and participant.treatment == 'Control'

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['tree_removal_player'] not in Constants.removal_decisions:
            return 'Please fill in either 0, 1, 2, 3 or 4'

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.tree_removal_player = player.tree_removal_player
        participant.group_withdrawal = set_group_withdrawal(player)
        participant.forest = set_forest(player)
        participant.total_group_withdrawal = set_total_group_withdrawal(player)
        participant.eco_status = set_eco_status(player)
        participant.sold_products = set_sold_products(player)
        participant.profit_round = set_profit_round(player)
        participant.profit_total = set_profit_total(player)
        participant.sustainable_production = set_sustainable_production(player)
        participant.sButtonClick = player.sButtonClick
        participant.sTimeClick = player.sTimeClick
        participant.game_over = 0


class GameOver(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest <= 0 and participant.game_over == 0

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.round_number = player.round_number
        player.participant.game_over = 1


class Results(Page):
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0


class EndGame(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 10 or player.participant.forest <= 0


page_sequence = [DecisionEco, DecisionControl, GameOver, Results, EndGame]
