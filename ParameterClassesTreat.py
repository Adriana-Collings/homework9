from enum import Enum
import numpy as np
import scipy.stats as stat
import math as math
import InputDataTreat as Data
import scr.MarkovClasses as MarkovCls
import scr.RandomVariantGenerators as Random
import scr.ProbDistParEst as Est


class HealthStats(Enum):
    """ health states of patients with HIV """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    DEATH = 3


class Therapies(Enum):
    """ mono vs. combination therapy """
    NONE = 0
    ANTICOAG = 1


class ParametersFixed():
    def __init__(self, therapy):

        # selected therapy
        self._therapy = therapy

        # simulation time step
        self._delta_t = Data.DELTA_T

        # initial health state
        self._initialHealthState = HealthStats.WELL

        # transition probability matrix of the selected therapy
        self._prob_matrix = []
        # treatment relative risk
        self._treatmentRR = 0

        # calculate transition probabilities between states
        self._prob_matrix = Data.TRANS_MATRIX  # calculate_prob_matrix()

        # update the transition probability matrix if therapy is being used
        #if self._therapy == Therapies.ANTICOAG:
         #   self._prob_matrix_treatment = Data.TREATMENT_TRANS_MATRIX
            # treatment relative risk
            #self._treatmentRR = Data.ANTICOAG_RR
            # calculate transition probability matrix for the combination therapy
           # self._prob_matrix = calculate_prob_matrix_anticoag(
            #    matrix_none=self._prob_matrix, anticoag_rr=Data.ANTICOAG_RR)

    def get_initial_health_state(self):
        return self._initialHealthState

    def get_delta_t(self):
        return self._delta_t

    def get_transition_prob(self, state):
        return self._prob_matrix[state.value]

    #def get_transition_prob_treatment(self, state):
    #    return self._prob_matrix_treatment[state.value]


def calculate_prob_matrix():
    """ :returns transition probability matrix"""

    #  create an empty matrix populated with zeros
    prob_matrix = []
    for s in HealthStats:
        prob_matrix.append([0]*len(HealthStats))

    #  for all health states
    for s in HealthStats:
        # if current health state is death (the patient will stay there forever)
        if s == HealthStats.DEATH:
            #  probability of staying in this state is 1
            prob_matrix[s.value][s.value] = 1
        else:
            sum_counts = sum(Data.TRANS_MATRIX[s.value])
            #  calculate the transition probabilities out of this state
            for j in range(s.value, HealthStats.DEATH.value+1):
                prob_matrix[s.value][j] = Data.TRANS_MATRIX[s.value][j] / sum_counts
    return prob_matrix


def calculate_prob_matrix_anticoag(matrix_none, anticoag_rr):
    """
    :param matrix_none: (list of lists) transition probability matrix under no therapy
    :param anticoag_rr: relative risk of the treatment
    :returns (list of lists) transition probability matrix under combination therapy """
    matrix_treat = []
    for s in HealthStats:
        matrix_treat.append([0]*len(HealthStats))

    #  populate the combo matrix
    #  first non-diagonal elements
    for s in HealthStats:
        for next_s in range(s.value+1, len(HealthStats)):
            matrix_treat[s.value][next_s] = anticoag_rr * matrix_none[s.value][next_s]

    #  diagonal elements are calculated to make sure the sum of each row is 1
    for s in HealthStats:
        if s != HealthStats.DEATH:
            matrix_treat[s.value][s.value] = 1 - sum(matrix_treat[s.value][s.value+1:])  # colon gives you everything
            # on right side of first provided index
    return matrix_treat
