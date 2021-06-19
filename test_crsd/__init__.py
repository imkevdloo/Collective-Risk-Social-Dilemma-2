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
    sustainable_decisions = [0, 1, 2]
    not_sustainable_decisions = [3, 4]
    treatments = ['MECO', 'SECO', 'Control']
    MECO_p = 1.25


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.CharField()
    trees_player_round = models.IntegerField(label="How many trees would you like to cut down?") # Number of trees cut down in that round of player
    eco_status = models.StringField() # Whether trees_player_round satisfies sustainability/eco-label standards
    trees_player_total = models.IntegerField(min=0, max=40)  # Total accumulated number of trees cut down of player
    trees_p2 = models.IntegerField(min=0, max=4) # Trees cut down p2 (always sustainable)
    trees_p3 = models.IntegerField(min=0, max=4) # Trees cut down p3 (depends on rest of group)
    trees_p4 = models.IntegerField(min=0, max=4) # Trees cut down p4 (always selfish)
    trees_group_round = models.IntegerField(min=0, max=16) # Number of trees cut down in round n of group in total
    trees_group_total = models.IntegerField() # Total accumulated number of trees cut down of group
    forest = models.IntegerField(min=20, max=20, label="Please indicate of how many trees the forest consists.")
    points_player_round = models.FloatField()  # Points of player in round n
    points_player_total = models.FloatField()  # Total accumulated points of player 
    points_group_round = models.FloatField() # Total points of group for round n
    points_group_total = models.FloatField() # Total accumulated points of group
    profit_player_total = models.FloatField()
    game_over = models.IntegerField(min=0, max=1)
    sButtonClick = models.StringField(label="")
    sTimeClick = models.StringField(label="")


# FUNCTIONS
def set_trees_group_round(player):
    participant = player.participant
    participant.trees_player_round = participant.trees_player_round
    participant.trees_p2 = random.choice(Constants.sustainable_decisions) # always sustainable (0, 1, 2)
    participant.trees_p4 = random.choice(Constants.not_sustainable_decisions) # always selfish (3, 4)
    if (participant.trees_p2 + participant.trees_p4 + participant.trees_player_round) > 10:
        participant.trees_p3 = random.choice(Constants.not_sustainable_decisions) # not sustainable if rest of group trees > 10
    else:
        participant.trees_p3 = random.choice(Constants.sustainable_decisions) # sustainable if rest of group trees < 10
    participant.trees_group_round = participant.trees_p2 + participant.trees_p3 + participant.trees_p4 + participant.trees_player_round
    return participant.trees_group_round


def set_trees_group_total(player):
    participant = player.participant
    participant.trees_group_total = participant.trees_group_total + participant.trees_group_round
    return participant.trees_group_total


def set_forest(player):
    participant = player.participant
    participant.forest = participant.forest - participant.trees_group_round + Constants.regrowth_rate
    if participant.forest < 0:
        participant.forest = 0
    return participant.forest


def set_eco_status(player):
    participant = player.participant
    if participant.treatment == 'MECO' or participant.treatment == 'SECO':
        if participant.eco_status == "Yes":
            if participant.trees_player_round <= 2:
                participant.eco_status = "Yes"
            else:
                participant.eco_status = "No"
        else:
            participant.eco_status = "No"
    else:
        participant.eco_status = " "
    return participant.eco_status


def set_trees_player_total(player):
    participant = player.participant
    participant.trees_player_total = participant.trees_player_total + participant.trees_player_round
    return participant.trees_player_total


def set_points_player_round(player):
    participant = player.participant
    if participant.treatment == 'MECO' and participant.eco_status == "Yes":
        participant.points_player_round = participant.trees_player_round * Constants.MECO_p
    else:
        participant.points_player_round = participant.trees_player_round
    return participant.points_player_round


def set_points_player_total(player):
    participant = player.participant
    participant.points_player_total = participant.points_player_total + participant.points_player_round
    return participant.points_player_total


def set_points_group_round(player):
    participant = player.participant
    if participant.treatment == 'MECO' and participant.trees_p3 <= 2:
        participant.points_group_round = (participant.trees_p2 * Constants.MECO_p) + (participant.trees_p3 * Constants.MECO_p) + participant.trees_p4 + participant.points_player_round
    else:
        participant.points_group_round = participant.trees_group_round
    return participant.points_group_round


def set_points_group_total(player):
    participant = player.participant
    participant.points_group_total = participant.points_group_total + participant.points_group_round
    return participant.points_group_total


def set_profit(player):
    participant = player.participant
    participant.profit_player_total = participant.points_player_total * 0.5
    return participant.profit_player_total


# PAGES
class DecisionControl(Page):
    form_model = 'player'
    form_fields = ['trees_player_round', 'sButtonClick', 'sTimeClick']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0 and participant.treatment == 'Control'

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['trees_player_round'] not in Constants.removal_decisions:
            return 'Please fill in either 0, 1, 2, 3 or 4'

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        player.treatment = participant.treatment
        participant.trees_player_round = player.trees_player_round
        player.trees_group_round = set_trees_group_round(player)
        player.forest = set_forest(player)
        player.trees_group_total = set_trees_group_total(player)
        player.eco_status = set_eco_status(player)
        player.trees_player_total = set_trees_player_total(player)
        player.points_player_round = set_points_player_round(player)
        player.points_player_total = set_points_player_total(player)
        player.points_group_round = set_points_group_round(player)
        player.points_group_total = set_points_group_total(player)
        player.profit_player_total = set_profit(player)
        player.game_over = 0
        participant.sButtonClick = player.sButtonClick
        participant.sTimeClick = player.sTimeClick


class DecisionEco(Page):
    form_model = 'player'
    form_fields = ['trees_player_round', 'sButtonClick', 'sTimeClick']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.forest > 0 and (participant.treatment == 'MECO' or participant.treatment == 'SECO')

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['trees_player_round'] not in Constants.removal_decisions:
            return 'Please fill in either 0, 1, 2, 3 or 4'

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.trees_player_round = player.trees_player_round
        player.trees_group_round = set_trees_group_round(player)
        player.forest = set_forest(player)
        player.trees_group_total = set_trees_group_total(player)
        player.eco_status = set_eco_status(player)
        player.trees_player_total = set_trees_player_total(player)
        player.points_player_round = set_points_player_round(player)
        player.points_player_total = set_points_player_total(player)
        player.points_group_round = set_points_group_round(player)
        player.points_group_total = set_points_group_total(player)
        player.profit_player_total = set_profit(player)
        player.game_over = 0
        participant.sButtonClick = player.sButtonClick
        participant.sTimeClick = player.sTimeClick


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


page_sequence = [DecisionEco, DecisionControl, GameOver, Results]
