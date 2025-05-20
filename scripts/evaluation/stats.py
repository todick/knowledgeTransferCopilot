import pandas as pd
import numpy as np
import constants
from scipy.stats import ttest_ind, chi2_contingency, mannwhitneyu

def read_and_separate_data(in_path):
    data = pd.read_csv(in_path + '/agg.csv')

    # get data for copilot and pp separately
    data_copilot = data[data[constants.DICT_COPILOT]]
    data_pp = data[~ data[constants.DICT_COPILOT]]

    return data_copilot, data_pp, data


def read_single_files(in_path):
    data = pd.read_csv(in_path + '/agg.csv')

    result = {}
    result_copilot = {}
    result_pp = {}

    # loop over all n and read the corresponding file
    for _, row in data.iterrows():
        n = row['n']
        file_name = f'study-{n}.csv'
        file_path = in_path + '/' + file_name
        file_data = pd.read_csv(file_path)
        result[n] = file_data

        if row[constants.DICT_COPILOT]:
            result_copilot[n] = file_data
        else:
            result_pp[n] = file_data

    return result, result_copilot, result_pp


def eval_episode_frequency(in_path, out_path):
    data_copilot, data_pp, data = read_and_separate_data(in_path)

    # get the mean of the number of episodes for each model
    mean_copilot = data_copilot[constants.DICT_NUM_EPISODES].mean()
    mean_pp = data_pp[constants.DICT_NUM_EPISODES].mean()
    mean_total = data[constants.DICT_NUM_EPISODES].mean()

    # count the episodes per group
    count_copilot = data_copilot[constants.DICT_NUM_EPISODES].sum()
    count_pp = data_pp[constants.DICT_NUM_EPISODES].sum()

    # get the quantiles
    quantiles_copilot = data_copilot[constants.DICT_NUM_EPISODES].quantile([0.25, 0.5, 0.75])
    quantiles_pp = data_pp[constants.DICT_NUM_EPISODES].quantile([0.25, 0.5, 0.75])

    # put those three values into a df and write it to a csv
    df = pd.DataFrame()
    df[constants.DICT_COPILOT] = [True, False]
    df[constants.DICT_MEAN] = [mean_copilot, mean_pp]

    df[constants.DICT_25_QUANTILE] = [quantiles_copilot[0.25], quantiles_pp[0.25]]
    df[constants.DICT_MEDIAN] = [quantiles_copilot[0.5], quantiles_pp[0.5]]
    df[constants.DICT_75_QUANTILE] = [quantiles_copilot[0.75], quantiles_pp[0.75]]

    df.to_csv(out_path + '/episode_frequency.csv', index=False)
    ttest_count = ttest_ind(data_copilot[constants.DICT_NUM_EPISODES], data_pp[constants.DICT_NUM_EPISODES], equal_var=False)
    mwu_count = mannwhitneyu(data_copilot[constants.DICT_NUM_EPISODES], data_pp[constants.DICT_NUM_EPISODES])

    print("Episode count [Copilot, PP]")
    print(count_copilot, count_pp)
    print("Welch's t-test for episode count - Copilot vs. Pair Programming")
    print(ttest_count)

def eval_episode_length_depth(in_path, out_path):
    _, single_data_copilot, single_data_pp = read_single_files(in_path)

    lens_copilot, depths_copilot = [], []
    lens_pp, depths_pp = [], []

    for df in single_data_copilot:
        lens_copilot += [l for l in single_data_copilot[df][constants.DICT_LEN_EPISODES]]
        depths_copilot += [l for l in single_data_copilot[df][constants.DICT_DEPTH_EPISODES]]

    for df in single_data_pp:
        lens_pp += [l for l in single_data_pp[df][constants.DICT_LEN_EPISODES]]
        depths_pp += [l for l in single_data_pp[df][constants.DICT_DEPTH_EPISODES]]

    df = pd.DataFrame()
    df[constants.DICT_MEAN_LEN_COPILOT] = [np.mean(lens_copilot)]
    df[constants.DICT_MEAN_DEPTH_COPILOT] = [np.mean(depths_copilot)]
    df[constants.DICT_MEAN_LEN_PP] = [np.mean(lens_pp)]
    df[constants.DICT_MEAN_DEPTH_PP] = [np.mean(depths_pp)]
    df[constants.DICT_MEDIAN_LEN_COPILOT] = [np.median(lens_copilot)]
    df[constants.DICT_MEDIAN_DEPTH_COPILOT] = [np.median(depths_copilot)]
    df[constants.DICT_MEDIAN_LEN_PP] = [np.median(lens_pp)]
    df[constants.DICT_MEDIAN_DEPTH_PP] = [np.median(depths_pp)]
    df.to_csv(out_path + '/episode_length_depth.csv', index=False)

    result_len = mannwhitneyu(lens_pp, lens_copilot)
    result_depth = mannwhitneyu(depths_copilot, depths_pp)
    print("Mann Whitney U episode len - Copilot vs. Pair Programming")
    print(result_len)
    print("Mann Whitney U episode depth - Copilot vs. Pair Programming")
    print(result_depth)

def eval_topics(in_path, out_path):
    data_copilot, data_pp, _ = read_and_separate_data(in_path)

    topics = constants.ATTRIBUTES_TOPIC
    obs = []
    values = {}

    for topic in topics:
        copilot_sum = data_copilot[f"topic_{topic}"].sum()
        pp_sum = data_pp[f"topic_{topic}"].sum()
        obs.append([copilot_sum, pp_sum])
        values[topic] = [copilot_sum, pp_sum]

    obs = np.array(obs)
    chi_squared_topics = chi2_contingency(obs)

    print("Chi Squared Test for topics - Copilot vs. Pair Programming")
    print(f"{chi_squared_topics}\n")

    for topic in topics:
        obs_topic = np.array([obs.sum(axis=0) - values[topic], values[topic]]).transpose()
        chi_squared_topic = chi2_contingency(obs_topic)
        print(f"Chi squared test for topic {topic}")
        print(f"{chi_squared_topic}\n")

def eval_finish_types(in_path, out_path):
    data_copilot, data_pp, _ = read_and_separate_data(in_path)

    finish_types = constants.ATTRIBUTES_FINISH_TYPE
    obs = []
    values = {}

    for finish_type in finish_types:
        copilot_sum = data_copilot[f"finish_type_{finish_type.replace(' ', '_')}"].sum()
        pp_sum = data_pp[f"finish_type_{finish_type.replace(' ', '_')}"].sum()            
        obs.append([copilot_sum, pp_sum])
        values[finish_type] = [copilot_sum, pp_sum]

    obs = np.array(obs)
    chi_squared_finish_types = chi2_contingency(obs)
    print("Chi squared test for finish types - Copilot vs. Pair Programming")
    print(f"{chi_squared_finish_types}\n")

    for finish_type in finish_types:
        obs_finish_type = np.array([obs.sum(axis=0) - values[finish_type], values[finish_type]]).transpose()
        chi_squared_finish_type = chi2_contingency(obs_finish_type)
        print(f"Chi squared test for finish type {finish_type}")
        print(f"{chi_squared_finish_type}\n")

    values_success = [values[finish_type] for finish_type in constants.ATTRIBUTES_FINISH_TYPE_SUCCESS]
    values_fail = [values[finish_type] for finish_type in constants.ATTRIBUTES_FINISH_TYPE_FAIL]
    obs_success = np.array(values_success).sum(axis=0)
    obs_fail = np.array(values_fail).sum(axis=0)
    obs_combined = np.array([obs_success, obs_fail]).transpose()
    print("Chi squared test for successful vs. unsuccessful finish")
    print(f"{chi2_contingency(obs_combined)}\n")