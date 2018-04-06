import InputDataHW as Settings
import scr.FormatFunctions as F


#def new_outcomes(patient, therapy_name):

#    survival_patient_mean_CI_text = F.format_estimate_interval(
#        estimate=patient.get_sumStat_survival_times().get_mean,  # no mean?
#        interval=patient.get_sumStat_survival_times().get_t_CI(alpha=Settings.ALPHA),
#        deci=2)
#    print(therapy_name)
#    print(" Estimate of patient survival time and {:.{prec}%} confidence interval:".format(1 - Settings.ALPHA, prec=0),
#          survival_patient_mean_CI_text)


def print_outcomes(simOutput, therapy_name):
    """ prints the outcomes of a simulated cohort
    :param simOutput: output of a simulated cohort
    :param therapy_name: the name of the selected therapy
    """
    # mean and confidence interval text of patient survival time
    survival_mean_CI_text = F.format_estimate_interval(
        estimate=simOutput.get_sumStat_survival_times().get_mean(),
        interval=simOutput.get_sumStat_survival_times().get_t_CI(alpha=Settings.ALPHA),
        deci=2)

    # mean and confidence interval text of time to stroke
    time_to_death_CI_text = F.format_estimate_interval(
        estimate=simOutput.get_sumStat_time_to_stroke().get_mean(),
        interval=simOutput.get_sumStat_time_to_stroke().get_t_CI(alpha=Settings.ALPHA),
        deci=2)

    # print outcomes
    print(therapy_name)
    print("  Estimate of mean survival time and {:.{prec}%} confidence interval:".format(1 - Settings.ALPHA, prec=0),
          survival_mean_CI_text)
    print("  Estimate of mean time to stroke and {:.{prec}%} confidence interval:".format(1 - Settings.ALPHA, prec=0),
          time_to_death_CI_text)
    print("")


