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
    age = models.IntegerField(label="Please enter your age:", min=18, max=100)
    gender = models.IntegerField(
        choices=[
        [1, 'Female'],
        [2, 'Male'],
        [3, 'Non-binary'],
        [4, 'Prefer not to say'],
        [5, 'Other']
        ],
        label="Please select your gender:",
        )
    nationality = models.StringField(label="Please enter your nationality:")
    education = models.IntegerField(
        choices=[
        [1, 'Primary school'],
        [2, 'High school or equivalent'],
        [3, 'Bachelor degree'],
        [4, 'Master degree'],
        [5, 'Other']
        ],
        label="What is the highest level of education that you have completed?:",
        )
    occupation = models.IntegerField(
        choices=[
        [1, 'Student'],
        [2, 'Working'],
        [3, 'Other'],
        ],
        label="What is your main occupation?:",
        )
    deforestation_knowledge = models.IntegerField(
        choices=[
        [1, 'Very high'],
        [2, 'Above average'],
        [3, 'Average'],
        [4, 'Below average'],
        [5, 'Very low']
        ],
        label="My knowledge about deforestation and the environment is:",
        widget=widgets.RadioSelect
        )
    environment_importance = models.IntegerField(
        choices=[
        [1, 'Very important'],
        [2, 'Important'],
        [3, 'Moderately important'],
        [4, 'Slightly important'],
        [5, 'Not important']
        ],
        label="I find the environment:",
        widget=widgets.RadioSelect
        )
    tree_certificate = models.StringField(
        label="If you would like to receive a certificate of the trees that we planted, please fill in your e-mail address:", blank=True)
    profit_certificate = models.StringField(
        label="If you would like to have a chance to receive your profit, please fill in your e-mail address:", blank=True)



# PAGES
class EndGameControl(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 'Control' #and (player.round_number == 10 or player.participant.forest <= 0)


class EndGameEco(Page):
    @staticmethod
    def is_displayed(player):
        return (player.participant.treatment == 'MECO' or player.participant.treatment == 'SECO') #and (player.round_number == 10 or player.participant.forest <= 0)


class Survey(Page):
    form_model = 'player'
    form_fields = ['age', 'nationality', 'gender', 'education', 'occupation',
                   'deforestation_knowledge', 'environment_importance', 'tree_certificate', 'profit_certificate']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.age = player.age
        player.nationality = player.nationality
        player.gender = player.gender
        player.education = player.education
        player.occupation = player.occupation
        player.deforestation_knowledge = player.deforestation_knowledge
        player.environment_importance = player.environment_importance



class Thankyou(Page):
    pass


page_sequence = [EndGameControl, EndGameEco, Survey, Thankyou]
