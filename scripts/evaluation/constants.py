TEXT_SPACE_ABS = 2
TEXT_SPACE_REL = 0.01

# dict keys for the evaluation
DICT_COPILOT = "copilot"
DICT_COPILOT_PRETTY = "GitHub Copilot"
DICT_PP_PRETTY = "Pair Programming"
DICT_TOPIC_DISTRIBUTION = "topic_distribution"
DICT_FINISH_TYPE_DISTRIBUTION = "finish_type_distribution"
DICT_NUM_EPISODES = "num_episodes"
DICT_LEN_EPISODES = "episode_len"
DICT_DEPTH_EPISODES = "episode_depth"

DICT_MEAN = "mean"
DICT_MEDIAN = "median"
DICT_25_QUANTILE = "25_quantile"
DICT_75_QUANTILE = "75_quantile"

DICT_MEAN_LEN_COPILOT = "mean_len_copilot"
DICT_MEAN_DEPTH_COPILOT = "mean_depth_copilot"
DICT_MEAN_LEN_PP = "mean_len_pp"
DICT_MEAN_DEPTH_PP = "mean_depth_pp"
DICT_MEDIAN_LEN_COPILOT = "median_len_copilot"
DICT_MEDIAN_DEPTH_COPILOT = "median_depth_copilot"
DICT_MEDIAN_LEN_PP = "median_len_pp"
DICT_MEDIAN_DEPTH_PP = "median_depth_pp"

# json keys for the annotations
DICT_ID = "id"
DICT_UTTERANCE = "utterance"
DICT_EPISODE = "episode"
DICT_ANNOTATIONS = "annotations"
DICT_UTTERANCES = "utterances"
DICT_EPISODES = "episodes"
DICT_DEPTH = "depth"

ATTRIBUTE_TOPIC_TOOL = "tool"
ATTRIBUTE_TOPIC_PROGRAM = "program"
ATTRIBUTE_TOPIC_BUG = "bug"
ATTRIBUTE_TOPIC_CODE = "code"
ATTRIBUTE_TOPIC_DOMAIN = "domain"
ATTRIBUTE_TOPIC_TECHNIQUE = "technique"
ATTRIBUTES_TOPIC = [ATTRIBUTE_TOPIC_TOOL, ATTRIBUTE_TOPIC_PROGRAM, ATTRIBUTE_TOPIC_BUG, ATTRIBUTE_TOPIC_CODE,
                    ATTRIBUTE_TOPIC_DOMAIN, ATTRIBUTE_TOPIC_TECHNIQUE]

ATTRIBUTE_FINISH_TYPE_ASSIMILATION = "assimilation"
ATTRIBUTE_FINISH_TYPE_UNNECESSARY = "unnecessary"
ATTRIBUTE_FINISH_TYPE_LOST_SIGHT = "lost sight"
ATTRIBUTE_FINISH_TYPE_GAVE_UP = "gave up"
ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS = "trust success"
ATTRIBUTE_FINISH_TYPE_TRUST_FAIL = "trust fail"
ATTRIBUTE_FINISH_TYPE_TRUST = "trust"
ATTRIBUTES_FINISH_TYPE = [ATTRIBUTE_FINISH_TYPE_ASSIMILATION, ATTRIBUTE_FINISH_TYPE_TRUST,
                          ATTRIBUTE_FINISH_TYPE_UNNECESSARY, ATTRIBUTE_FINISH_TYPE_LOST_SIGHT,
                          ATTRIBUTE_FINISH_TYPE_GAVE_UP]
ATTRIBUTES_FINISH_TYPE_SUCCESS = [ATTRIBUTE_FINISH_TYPE_ASSIMILATION, ATTRIBUTE_FINISH_TYPE_TRUST]
ATTRIBUTES_FINISH_TYPE_FAIL = [ATTRIBUTE_FINISH_TYPE_UNNECESSARY, ATTRIBUTE_FINISH_TYPE_LOST_SIGHT,
                               ATTRIBUTE_FINISH_TYPE_GAVE_UP]

ATTRIBUTE_SPEAKER_A = "speaker A"
ATTRIBUTE_SPEAKER_B = "speaker B"
ATTRIBUTE_SPEAKER_INSTRUCTOR = "instructor"
ATTRIBUTE_SPEAKERS = [ATTRIBUTE_SPEAKER_A, ATTRIBUTE_SPEAKER_B, ATTRIBUTE_SPEAKER_INSTRUCTOR]

ATTRIBUTE_TOPIC = "topic"
ATTRIBUTE_FINISH_TYPE = "finish type"
ATTRIBUTE_SPEAKER = "speaker"
ATTRIBUTE_COPILOT_INTERACTION = "copilot interaction"
ATTRIBUTE_NOTES = "notes"

ATTRIBUTES_UTTERANCE = [ATTRIBUTE_SPEAKER, ATTRIBUTE_TOPIC,  ATTRIBUTE_COPILOT_INTERACTION, ATTRIBUTE_NOTES]
ATTRIBUTES_EPISODE = [ATTRIBUTE_TOPIC, ATTRIBUTE_COPILOT_INTERACTION, ATTRIBUTE_FINISH_TYPE, ATTRIBUTE_NOTES]

INT = "int"
STR = "str"

ATTRIBUTE_TYPE_VALUES = {
    ATTRIBUTE_TOPIC: ATTRIBUTES_TOPIC,    
    ATTRIBUTE_FINISH_TYPE: ATTRIBUTES_FINISH_TYPE,
    ATTRIBUTE_NOTES: STR,
    ATTRIBUTE_COPILOT_INTERACTION: ["True", "False"],
    ATTRIBUTE_SPEAKER: ATTRIBUTE_SPEAKERS
}

ATTRIBUTE_DEFAULT_VALUES = {
    ATTRIBUTE_COPILOT_INTERACTION: 1,
    ATTRIBUTE_SPEAKER: 0
}
