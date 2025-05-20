import json
import os
from util import log, info, success, warn, error
import constants
import pandas as pd
import re


def read_annotations(in_path, file):
    # parse json into dicts
    content = json.load(open(os.path.join(in_path, file)))
    annotations = content[constants.DICT_ANNOTATIONS]
    utterances = content[constants.DICT_UTTERANCES]
    episodes = content[constants.DICT_EPISODES]

    return annotations, utterances, episodes


def is_copilot_transcript(utterances):
    # determine whether this is a copilot or pair programming transcript
    log("  Determine transcript type")
    copilot_transcript = True
    for utterance in utterances:
        if utterance[constants.ATTRIBUTE_SPEAKER] == constants.ATTRIBUTE_SPEAKER_B:
            copilot_transcript = False
            break
    log(f"    Copilot transcript" if copilot_transcript else "    Pair programming transcript")
    return copilot_transcript


def get_topic_distribution(episodes):
    # count the topics of the episodes and save them in a dict
    log("  Count topic distribution")
    topic_distribution = {}
    for topic in constants.ATTRIBUTES_TOPIC:
        count = 0
        for episode in episodes:
            if episode[constants.ATTRIBUTE_TOPIC] == topic:
                count += 1

        topic_distribution[topic] = count
        log(f"    {topic}: {count}")

    return topic_distribution


def get_finish_type_distribution(episodes):
    log("  Count finish type distribution")
    finish_type_distribution = { constants.ATTRIBUTE_FINISH_TYPE_TRUST : 0 }

    for finish_type in constants.ATTRIBUTES_FINISH_TYPE + [constants.ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS, constants.ATTRIBUTE_FINISH_TYPE_TRUST_FAIL]:
        if finish_type == constants.ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS or finish_type == constants.ATTRIBUTE_FINISH_TYPE_TRUST_FAIL:
            for episode in episodes:
                if episode[constants.ATTRIBUTE_FINISH_TYPE] == finish_type:
                    finish_type_distribution[constants.ATTRIBUTE_FINISH_TYPE_TRUST] += 1
        else:
            count = 0
            for episode in episodes:
                if episode[constants.ATTRIBUTE_FINISH_TYPE] == finish_type:
                    count += 1

            finish_type_distribution[finish_type] = count
            log(f"    {finish_type}: {count}")

    return finish_type_distribution



def aggregate(in_path, out_path):
    # if the output path does not exist, create it
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        log(f"Created output directory '{out_path}'")

    # get all the files in the input directory that contain the word 'annotated' and end on '.json'
    files = [f for f in os.listdir(in_path) if 'annotated' in f and f.endswith('.json')]
    success(f"Found {len(files)} annotation files")

    info("Parse annotation files")
    result = {}
    for file in files:
        log(f"  {file}")
        # read the annotations from the file
        annotations, utterances, episodes = read_annotations(in_path, file)

        copilot = is_copilot_transcript(utterances)
        topic_distribution = get_topic_distribution(episodes)
        finish_type_distribution = get_finish_type_distribution(episodes)
        num_episodes = len(episodes)
        len_episodes = {episode_id: len(episode[constants.DICT_UTTERANCES]) for episode_id, episode in
                        enumerate(episodes)}

        depth = {}
        for episode in episodes:
            episode_id = episode[constants.DICT_ID]
            first_utterance_id = episode[constants.DICT_UTTERANCES][0]
            first_utterance = [u for u in utterances if u[constants.DICT_ID] == first_utterance_id][0]
            depth[episode_id] = first_utterance[constants.DICT_EPISODES].index(
                episode_id) + 1  # +1 because of 0-indexing

        depth_episodes = {episode[constants.DICT_ID]: depth[episode[constants.DICT_ID]] for episode in episodes}

        result[file] = {
            constants.DICT_COPILOT: copilot,
            constants.DICT_TOPIC_DISTRIBUTION: topic_distribution,
            constants.DICT_FINISH_TYPE_DISTRIBUTION: finish_type_distribution,
            constants.DICT_NUM_EPISODES: num_episodes,
            constants.DICT_LEN_EPISODES: len_episodes,
            constants.DICT_DEPTH_EPISODES: depth_episodes
        }

    success("Done")

    info("Write results")
    # write aggregated results over all files
    df_agg = pd.DataFrame()
    df_agg["n"] = [int(re.findall(r'\d\d', file)[0]) for file in files]
    df_agg["file"] = files
    df_agg["copilot"] = [result[file][constants.DICT_COPILOT] for file in files]
    df_agg["num_episodes"] = [result[file][constants.DICT_NUM_EPISODES] for file in files]
    df_agg["max_episode_len"] = [max(result[file][constants.DICT_LEN_EPISODES].values()) for file in files]
    df_agg["max_episode_depth"] = [max(result[file][constants.DICT_DEPTH_EPISODES].values()) for file in files]

    for topic in constants.ATTRIBUTES_TOPIC:
        df_agg[f"topic_{topic}"] = [result[file][constants.DICT_TOPIC_DISTRIBUTION][topic] for file in files]

    for finish_type in constants.ATTRIBUTES_FINISH_TYPE:
        df_agg[f"finish_type_{finish_type.replace(' ', '_')}"] = [result[file][constants.DICT_FINISH_TYPE_DISTRIBUTION][finish_type] for file in files]

    df_agg.to_csv(os.path.join(out_path, "agg.csv"), index=False)

    # write results for each file
    for file in files:
        df = pd.DataFrame()
        df["episode_id"] = list(result[file][constants.DICT_LEN_EPISODES].keys())
        df["episode_len"] = list(result[file][constants.DICT_LEN_EPISODES].values())
        df["episode_depth"] = list(result[file][constants.DICT_DEPTH_EPISODES].values())
        n = int(re.findall('\d\d', file)[0])
        out_name = f"study-{n}.csv"
        df.to_csv(os.path.join(out_path, out_name), index=False)

    success("Done")
