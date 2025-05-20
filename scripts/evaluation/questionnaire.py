import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, ttest_1samp
import matplotlib.pyplot as plt

from constants import *


def read_data(in_path):
    return pd.read_csv(in_path + '/questionnaire_result.csv')


def questionnaire(in_path, out_path):
    data = read_data(in_path)

    data_copilot = data[data["Group"] == "copilot"]
    data_pp = data[data["Group"] == "pp"]
    data_copilot.to_csv(out_path + '/questionnaire_copilot.csv', index=False)
    data_pp.to_csv(out_path + '/questionnaire_pp.csv', index=False)

    mean = data.mean(numeric_only=True)
    language_count = data.groupby('Mother Tongue').count()["Age"]
    study_programme_count = data.groupby('Study Programme').count()["Age"]
    mean.to_csv(out_path + '/questionnaire_mean.csv', header=False)
    language_count.to_csv(out_path + '/questionnaire_language_count.csv', header=False)
    study_programme_count.to_csv(out_path + '/questionnaire_study_programme_count.csv', header=False)

    mean_copilot = data_copilot.mean(numeric_only=True)
    mean_pp = data_pp.mean(numeric_only=True)
    mean_copilot.to_csv(out_path + '/questionnaire_mean_copilot.csv', header=False)
    mean_pp.to_csv(out_path + '/questionnaire_mean_pp.csv', header=False)

    corr_experience_rel_abs = spearmanr(data["Programming Experience (Relative)"],
                                        data["Programming Experience (Absolute)"])
    corr_experience_rel_python = spearmanr(data["Programming Experience (Relative)"], data["Python Experience"])
    corr_python_age = spearmanr(data["Programming Experience (Absolute)"], data["Age"])

    corr_means_rel_total_copilot = ttest_1samp(data_copilot["Programming Experience (Relative)"],
                                               mean["Programming Experience (Relative)"])
    corr_means_abs_total_copilot = ttest_1samp(data_copilot["Programming Experience (Absolute)"],
                                               mean["Programming Experience (Absolute)"])
    corr_means_rel_total_pp = ttest_1samp(data_pp["Programming Experience (Relative)"],
                                          mean["Programming Experience (Relative)"])
    corr_means_abs_total_pp = ttest_1samp(data_pp["Programming Experience (Absolute)"],
                                          mean["Programming Experience (Absolute)"])

    corr_means_cp_total_copilot = ttest_1samp(data_copilot["GitHub Copilot Experience"],
                                          mean["GitHub Copilot Experience"])
    corr_means_cp_total_pp = ttest_1samp(data_pp["GitHub Copilot Experience"],
                                          mean["GitHub Copilot Experience"])

    corr_means_pp_total_copilot = ttest_1samp(data_copilot["Pair Programming Experience"],
                                          mean["Pair Programming Experience"])
    corr_means_pp_total_pp = ttest_1samp(data_pp["Pair Programming Experience"],
                                          mean["Pair Programming Experience"])

    print(f"""
        Corr. Rel. Exp. <-> Abs. Exp.: {corr_experience_rel_abs}
        Corr. Rel. Exp. <-> Python Exp.: {corr_experience_rel_python}

""")
