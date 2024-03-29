import scr.SamplePathClasses as PathCls
import scr.StatisticalClasses as StatCls
import scr.RandomVariantGenerators as rndClasses
import scr.EconEvalClasses as EconCls
import ParameterClassesTreat as P
import InputDataTreat as Data

# patient class simulates patient, patient monitor follows patient, cohort simulates a cohort,
#  cohort outcome extracts info from simulation and returns it back


class Patient:  # when you store in self then all the things in that class have access to it
    def __init__(self, id, parameters):
        """ initiates a patient
        :param id: ID of the patient
        :param parameters: parameter object
        """

        self._id = id
        # random number generator
        self._rng = None
        # parameters
        self._param = parameters
        # state monitor
        self._stateMonitor = PatientStateMonitor(parameters)
        # simulate time step
        self._delta_t = parameters.get_delta_t()  # length of time step!

    def simulate(self, sim_length):
        """ simulate the patient over the specified simulation length """
        # random number generator for this patient
        self._rng = rndClasses.RNG(self._id)  # from now on use random number generator from support library

        k = 0  # current time step

        # while the patient is alive and simulation length is not yet reached
        while self._stateMonitor.get_if_alive() and k*self._delta_t < sim_length:
            # find transition probabilities of future state
            trans_prob = self._param.get_transition_prob(self._stateMonitor.get_current_state())
            # create an empirical distribution
            empirical_dist = rndClasses.Empirical(trans_prob)
            # sample from the empirical distribution to get a new state
            # (return an intger from {0, 1, 2, ...}
            new_state_index = empirical_dist.sample(self._rng) # pass RNG

            # update health state
            self._stateMonitor.update(k, P.HealthStats(new_state_index))

            # increment time step
            k += 1

    def get_survival_time(self):
        """ returns the patient's survival time"""
        return self._stateMonitor.get_survival_time()

    def get_time_to_stroke(self):
        """ returns the patient's time to stroke """
        return self._stateMonitor.get_time_to_stroke()

    def get_if_developed_stroke(self):
        return self._stateMonitor.get_if_developed_stroke()


class PatientStateMonitor:
    """ to update patient outcomes (years survived, cost, etc.) throughout the simulation """
    def __init__(self, parameters):
        """
        :param parameters: patient parameters
        """
        # current health state
        self._currentState = parameters.get_initial_health_state()
        self._delta_t = parameters.get_delta_t()
        self._survivalTime = 0
        self._timeToStroke = 0
        self._ifDevelopedStroke = False
        self._strokecount = 0

    def update(self, k, next_state):
        """
        :param k: current time step
        :param next_state: next state
        """
        # updates state of patient
        # if the patient has died, do nothing
        if not self.get_if_alive():
            return

        # update survival time
        if next_state is P.HealthStats.DEATH:
            self._survivalTime = (k+0.5) * self._delta_t  # k is number of steps its been, delta t is length of time
            # step, the 0.5 is a half cycle correction

        # update time until stroke
        if self._currentState != P.HealthStats.STROKE and next_state == P.HealthStats.STROKE:
            self._ifDevelopedStroke = True
            self._timeToStroke = (k+0.5) * self._delta_t

        self._currentState = next_state

    def get_if_alive(self):
        result = True
        if self._currentState == P.HealthStats.DEATH:
            result = False
        return result

    def get_current_state(self):
        return self._currentState

    def get_survival_time(self):
        """ returns the patient survival time """
        # return survival time only if the patient has died
        if not self.get_if_alive():
            return self._survivalTime
        else:
            return None

    def get_time_to_stroke(self):
        """ returns the patient's time to stroke"""
        # return time to stroke  only if the patient has developed stroke
        if self._ifDevelopedStroke:
            return self._timeToStroke
        else:
            return None

    def get_if_developed_stroke(self):
        if self._currentState == P.HealthStats.STROKE:
            self._strokecount += 1
        return self._strokecount

class Cohort:
    def __init__(self, id, therapy):
        """ create a cohort of patients
        :param id: an integer to specify the seed of the random number generator
        """
        self._initial_pop_size = Data.POP_SIZE
        self._patients = []      # list of patients
        self._strokecount = 0

        # populate the cohort
        for i in range(self._initial_pop_size):
            # create a new patient (use id * pop_size + i as patient id)
            patient = Patient(id * self._initial_pop_size + i, P.ParametersFixed(therapy))
            # add the patient to the cohort
            self._patients.append(patient)

    def simulate(self):
        """ simulate the cohort of patients over the specified number of time-steps
        :returns outputs from simulating this cohort
        """

        # simulate all patients
        for patient in self._patients:
            patient.simulate(Data.SIM_LENGTH)

        # return the cohort outputs
        return CohortOutputs(self)

    def get_initial_pop_size(self):
        return self._initial_pop_size

    def get_patients(self):
        return self._patients



class CohortOutputs:
    def __init__(self, simulated_cohort):
        """ extracts outputs from a simulated cohort
        :param simulated_cohort: a cohort after being simulated
        """

        self._survivalTimes = []        # patients' survival times
        self._times_to_Stroke = []        # patients' times to stroke
        self._count_strokes = []

        # survival curve
        self._survivalCurve = \
            PathCls.SamplePathBatchUpdate('Population size over time', id, simulated_cohort.get_initial_pop_size())

        # find patients' survival times
        for patient in simulated_cohort.get_patients():

            # get the patient survival time
            survival_time = patient.get_survival_time()
            if not (survival_time is None):
                self._survivalTimes.append(survival_time)           # store the survival time of this patient
                self._survivalCurve.record(survival_time, -1)       # update the survival curve

            # get the patient's time to stroke
            time_to_stroke = patient.get_time_to_stroke()
            if not (time_to_stroke is None):
                self._times_to_Stroke.append(time_to_stroke)

            count_strokes = patient.get_if_developed_stroke()
            if not (time_to_stroke is None):
                self._count_strokes.append(count_strokes)


        # summary statistics
        self._sumStat_survivalTime = StatCls.SummaryStat('Patient survival time', self._survivalTimes)
        self._sumState_timeToStroke = StatCls.SummaryStat('Time until stroke', self._times_to_Stroke)

    def get_if_developed_stroke(self):
        return len(self._count_strokes)

    def get_survival_times(self):
        return self._survivalTimes

    def get_times_to_stroke(self):
        return self._times_to_Stroke

    def get_sumStat_survival_times(self):
        return self._sumStat_survivalTime

    def get_sumStat_time_to_stroke(self):
        return self._sumState_timeToStroke

    def get_survival_curve(self):
        return self._survivalCurve
