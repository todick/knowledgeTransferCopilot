from constants import *

import math
import click
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import spearmanr, mannwhitneyu

PLOT_FOLDER = '../../plots/'

def read_and_separate_data():
    global df_rq_copilot, df_rq_pp, df_rq_total
    df_rq_total = pd.read_csv('../../results/agg/agg.csv')

    # get data for copilot and pp separately
    df_rq_copilot = df_rq_total[df_rq_total[DICT_COPILOT]]
    df_rq_pp = df_rq_total[~ df_rq_total[DICT_COPILOT]]

    # add a column to the total df called "Group" based on the "Copilot" column
    df_rq_total['Group'] = df_rq_total[DICT_COPILOT].apply(lambda x: DICT_COPILOT_PRETTY if x else DICT_PP_PRETTY)


def read_single_files():
    global df_single_copilot, df_single_pp, df_single_total

    data = pd.read_csv('../../results/agg/agg.csv')

    result = {}
    result_copilot = {}
    result_pp = {}

    # loop over all n and read the corresponding file
    for _, row in data.iterrows():
        n = row['n']
        file_name = f'study-{n}.csv'
        file_path = f'../../results/agg/{file_name}'
        file_data = pd.read_csv(file_path)
        result[n] = file_data

        if row[DICT_COPILOT]:
            result_copilot[n] = file_data
        else:
            result_pp[n] = file_data

    df_single_copilot, df_single_pp, df_single_total = result_copilot, result_pp, result


@click.group()
def cli():
    global df_questionnaire_pp, df_questionnaire_copilot, df_questionnaire_total, colour_palette, colour_pp, colour_copilot, column_names, colour_palette_reversed
    
    df_questionnaire_pp = pd.read_csv('../../results/questionnaire_pp.csv')
    df_questionnaire_copilot = pd.read_csv('../../results/questionnaire_copilot.csv')
    df_questionnaire_total = pd.concat([df_questionnaire_copilot, df_questionnaire_pp], ignore_index=True)

    colour_palette = sns.color_palette("colorblind")[:2]
    colour_pp = colour_palette[0]
    colour_copilot = colour_palette[1]
    colour_palette_reversed = [colour_copilot, colour_pp]

    column_names = [
        "Programming Experience (Relative)",
        "Programming Experience (Absolute)",
        "Python Experience",
        "GitHub Copilot Experience",
        "Pair Programming Experience",
    ]

    read_and_separate_data()
    read_single_files()


@cli.command()
def questionnaire_stats():
    corr_experience_rel_abs = spearmanr(df_questionnaire_total["Programming Experience (Relative)"],
                                        df_questionnaire_total["Programming Experience (Absolute)"])
    
    corr_experience_rel_python = spearmanr(df_questionnaire_total["Programming Experience (Relative)"], 
                                           df_questionnaire_total["Python Experience"])
    
    corr_python_age = spearmanr(df_questionnaire_total["Programming Experience (Absolute)"], 
                                df_questionnaire_total["Age"])

    mwu_relative_xp = mannwhitneyu(df_questionnaire_pp["Programming Experience (Relative)"],
                                   df_questionnaire_copilot["Programming Experience (Relative)"])
    
    mwu_absolute_xp = mannwhitneyu(df_questionnaire_pp["Programming Experience (Absolute)"],
                                   df_questionnaire_copilot["Programming Experience (Absolute)"])

    mwu_python_xp = mannwhitneyu(df_questionnaire_pp["Python Experience"],
                                 df_questionnaire_copilot["Python Experience"])
    
    mwu_copilot_xp = mannwhitneyu(df_questionnaire_pp["GitHub Copilot Experience"],
                                  df_questionnaire_copilot["GitHub Copilot Experience"])
    
    mwu_pp_xp = mannwhitneyu(df_questionnaire_pp["Pair Programming Experience"],
                             df_questionnaire_copilot["Pair Programming Experience"])

    def z(u):
        n1 = len(df_questionnaire_pp)
        n2 = len(df_questionnaire_copilot)
        c = u - n1 * n2 * 0.5 
        d = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

        return c / d

    z_scores = [z(t[0]) for t in [mwu_relative_xp, mwu_absolute_xp, mwu_python_xp, mwu_copilot_xp, mwu_pp_xp]]

    print(f"""
Corr. Rel. <-> Abs. XP:         {corr_experience_rel_abs}
Corr. Rel. <-> Python XP:       {corr_experience_rel_python}
Corr. Age  <-> Python XP:       {corr_python_age}

MWU Rel. XP:                    {mwu_relative_xp}  z: {z_scores[0]}
MWU Abs. XP:                    {mwu_absolute_xp}  z: {z_scores[1]}
MWU Python XP:                  {mwu_python_xp}   z: {z_scores[2]}
MWU Copilot XP:                 {mwu_copilot_xp}  z: {z_scores[3]}
MWU PP XP:                      {mwu_pp_xp}   z: {z_scores[4]}
          """)

@cli.command()
def csv_episodes():   
    df_rq_copilot.to_csv(f'{PLOT_FOLDER}/data/copilot_episodes.csv', index=False)
    df_rq_pp.to_csv(f'{PLOT_FOLDER}/data/pp_episodes.csv', index=False)

@cli.command()
def export_plot_data():   
    global df_single_copilot, df_single_pp
    len_copilot, depth_copilot = [], []
    len_pp, depth_pp = [], []

    for df in df_single_copilot:
        len_copilot.extend(list(df_single_copilot[df][DICT_LEN_EPISODES]))
        depth_copilot.extend(list(df_single_copilot[df][DICT_DEPTH_EPISODES]))

    for df in df_single_pp:
        len_pp.extend(list(df_single_pp[df][DICT_LEN_EPISODES]))
        depth_pp.extend(list(df_single_pp[df][DICT_DEPTH_EPISODES]))

    # Export binned episode lengths 
    bin_edges = np.linspace(1, 181, 19)  # 20 bins between 0 and 180
    bin_centers = [int((bin_edges[i] + bin_edges[i + 1]) / 2) for i in range(len(bin_edges) - 1)]
    copilot_binned, _ = np.histogram(len_copilot, bins=bin_edges)
    pp_binned, _ = np.histogram(len_pp, bins=bin_edges)

    df_lengths = pd.DataFrame({
        "EpisodeLength": bin_centers,
        "Copilot": copilot_binned,
        "PairProgramming": pp_binned,
    })
    df_lengths.to_csv(f'{PLOT_FOLDER}/data/episode_length.csv', index=False)
    
    # Export episode depths
    copilot_binned, _ = np.histogram(depth_copilot, 3)
    pp_binned, _ = np.histogram(depth_pp, 3)
    df_depths = pd.DataFrame({
        "EpisodeDepth": [1,2,3],
        "Copilot": copilot_binned,
        "PairProgramming": pp_binned,
    })
    df_depths.to_csv(f'{PLOT_FOLDER}/data/episode_depth.csv', index=False)

    # Export binned episode count
    bin_edges = np.linspace(1, 61, 7)  # 6 bins between 0 and 60
    bin_centers = [int((bin_edges[i] + bin_edges[i + 1]) / 2) for i in range(len(bin_edges) - 1)]

    copilot_binned, _ = np.histogram(df_rq_copilot[DICT_NUM_EPISODES], bins=bin_edges)
    pp_binned, _ = np.histogram(df_rq_pp[DICT_NUM_EPISODES], bins=bin_edges)
    df_counts = pd.DataFrame({
        "Episodes": bin_centers,
        "Copilot": copilot_binned,
        "PairProgramming": pp_binned,
    })
    df_counts.to_csv(f'{PLOT_FOLDER}/data/number_episodes.csv', index=False)

    # Export topic types relative
    topics = ATTRIBUTES_TOPIC
    values_copilot = []
    values_pp = []
    
    for topic in topics:
        values_copilot.append(df_rq_copilot[f"topic_{topic}"].sum())
        values_pp.append(df_rq_pp[f"topic_{topic}"].sum())
    topics_capitalised = [f"{topic[0].upper()}{topic[1:]}" for topic in topics]

    num_episodes_copilot = df_rq_copilot[DICT_NUM_EPISODES].sum()
    num_episodes_pp = df_rq_pp[DICT_NUM_EPISODES].sum()

    values_copilot_rel = [value / num_episodes_copilot * 100 for value in values_copilot]
    values_pp_rel = [value / num_episodes_pp * 100 for value in values_pp]

    df = pd.DataFrame({
        'Topic': topics_capitalised,
        'Copilot': values_copilot_rel,
        'PairProgramming': values_pp_rel,
    })
    df.to_csv(f'{PLOT_FOLDER}/data/topic_types.csv', index=False, float_format='%.1f')

    # Export finish types relative
    finish_types = ATTRIBUTES_FINISH_TYPE
    values_copilot = []
    values_pp = []
    for finish_type in finish_types:
        values_copilot.append(df_rq_copilot[f"finish_type_{finish_type.replace(' ', '_')}"].sum())
        values_pp.append(df_rq_pp[f"finish_type_{finish_type.replace(' ', '_')}"].sum())
    finish_types_capitalised = [finish_type.title() for finish_type in finish_types]

    num_episodes_copilot = df_rq_copilot[DICT_NUM_EPISODES].sum()
    num_episodes_pp = df_rq_pp[DICT_NUM_EPISODES].sum()

    total_copilot = 0
    for i in range(len(df_rq_copilot)):
        for finish_type in finish_types:
            total_copilot += df_rq_copilot.iloc[i][f"finish_type_{finish_type.replace(' ', '_')}"]

    total_pp = 0
    for i in range(len(df_rq_pp)):
        for finish_type in finish_types:
            total_pp += df_rq_pp.iloc[i][f"finish_type_{finish_type.replace(' ', '_')}"]

    values_copilot_rel = [value / total_copilot * 100.0 for value in values_copilot]
    values_pp_rel = [value / total_pp * 100.0 for value in values_pp]

    df = pd.DataFrame({
        'FinishType': finish_types_capitalised,
        'Copilot': values_copilot_rel,
        'PairProgramming': values_pp_rel,
    })
    df.to_csv(f'{PLOT_FOLDER}/data/finish_types.csv', index=False, float_format='%.1f')

if __name__ == '__main__':
    cli()


