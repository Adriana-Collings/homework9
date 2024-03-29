import ParameterClassesTreat as P
import MarkovModelTreat as MarkovCls
import SupportMarkovModelHW as SupportMarkov
import scr.SamplePathClasses as PathCls
import scr.FigureSupport as Figs
import InputDataTreat as Data

# create a cohort
cohort = MarkovCls.Cohort(
    id=1,
    therapy=P.Therapies.NONE)

# simulate the cohort
simOutputs = cohort.simulate()

print('Number of strokes', simOutputs.get_if_developed_stroke())

# graph survival curve
PathCls.graph_sample_path(
    sample_path=simOutputs.get_survival_curve(),
    title='Survival curve',
    x_label='Simulation time step',
    y_label='Number of alive patients'
    )

# graph histogram of survival times
Figs.graph_histogram(
    data=simOutputs.get_survival_times(),
    title='Survival times of patients with Stroke',
    x_label='Survival time (years)',
    y_label='Counts',
    bin_width=1
)

# print the outcomes of this simulated cohort
SupportMarkov.print_outcomes(simOutputs, 'No treatment:')






