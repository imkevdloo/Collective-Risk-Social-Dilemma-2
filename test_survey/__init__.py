from otree.api import *


doc = """
Concluding survey of the experiment
"""


class Constants(BaseConstants):
    name_in_url = 'test_survey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField()
    gender = models.StringField()



# PAGES
class Survey(Page):
    pass


class Thankyou(Page):
    pass


page_sequence = [Survey, Thankyou]
