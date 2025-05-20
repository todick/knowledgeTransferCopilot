import click
import os
import curses
import re
import textwrap
import json
import math
from colours import COLOURS, ALL_COLOURS
from functools import reduce
from datetime import datetime

#region constants and variables
TRANSCRIPT_PATH = ""
DATA_FILE_PATH = ""
STATUS = ""

stdscr = None

TRANSCRIPT = []
ANNOTATIONS = []
UTTERANCES = []
EPISODES = []

UTTERANCE_INDICES = {}

MODE_UTTERANCE = "utterance"
MODE_EPISODE = "episode"
MODE_ATTRIBUTES = "attributes"
MODE_LATEX = "latex"

CURRENT_MODE = MODE_UTTERANCE
CURRENT_ATTRIBUTE_MODE = MODE_UTTERANCE
CURRENT_LINE_EDIT = 0
CURRENT_LINE_VIEW = 7
CURRENT_LINE_VIEW_END = 0
CURRENT_UTTERANCE_INDEX = -1
CURRENT_EPISODE_INDEX = -1

ATTRIBUTE_MENU_FOCUS_ATTRIBUTES = "attributes"
ATTRIBUTE_MENU_FOCUS_VALUES = "values"
ATTRIBUTE_MENU_FOCUS_INT = "int"
ATTRIBUTE_MENU_FOCUS_STR = "str"

OBJECT_TO_EDIT = None
ATTRIBUTE_TO_EDIT = 0
AVAILABLE_ATTRIBUTES = None
ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_ATTRIBUTES
CURRENT_VALUE = 0
CURRENT_INPUT_BUFFER = ""
MULTISELECT = False
CLIPBOARD_UTTERANCE = None
CLIPBOARD_UTTERANCE_ATTRIBUTE = None
CLIPBOARD_EPISODE = None
CLIPBOARD_EPISODE_ATTRIBUTE = None
LATEX_ANNOTATION_INDEX_FST = None
LATEX_ANNOTATION_INDEX_SND = None

SYMBOL_CURRENT_EDIT = "🮥 "
SYMBOL_VIEW_ANNOTATED = "🯂🯃"
SYMBOL_EMPTY = "   "
EDIT_START_COL = 27
UTTERANCE_BRACE_COL = 23
VIEW_END_ROW = 6
MODE_SELECTION_ROW = 2
ATTRIBUTE_VALUE_TEXT_WIDTH = 30
ATTRIBUTE_INT_TEXT_WIDTH = 7
ATTRIBUTE_STR_TEXT_WIDTH = 50

COLOUR_MENU = 4
COLOUR_MENU_SELECTED = 5
COLOUR_MENU_DISABLED = 6
COLOUR_MENU_SELECTED_DISABLED = 7
COLOUR_EPISODE_SELECTED = 8
COLOUR_EPISODE_SELECTED_MULTISELECT = 9
COLOUR_EPISODE_MULTISELECT = 10
COLOUR_RED = 11
COLOUR_GREEN = 12
COLOUR_BLUE = 13
COLOUR_INSTRUCTOR = 14

LATEX_COLOUR_SPEAKER_A = "black"
LATEX_COLOUR_SPEAKER_B = "cyan"
LATEX_COLOUR_SPEAKER_INSTRUCTOR = "green"

SYMBOL_SPEAKER_A = " Ⓐ "
SYMBOL_SPEAKER_B = " Ⓑ "
SYMBOL_SPEAKER_INSTRUCTOR = " 🜲 "

KEY_UP = "↑"
KEY_DOWN = "↓"
KEY_LEFT = "←"
KEY_RIGHT = "→"
KEY_PAGE_UP = "Page ↑"
KEY_PAGE_DOWN = "Page ↓"

KEY_ACTIONS = {}

DICT_ID = "id"
DICT_UTTERANCE = "utterance"
DICT_EPISODE = "episode"
DICT_ANNOTATIONS = "annotations"
DICT_UTTERANCES = "utterances"
DICT_EPISODES = "episodes"
DICT_DEPTH = "depth"

KEY_CODE_MODE_UTTERANCES = "[ u ]"
KEY_CODE_MODE_EPISODES =   "[ e ]"
KEY_CODE_MODE_ATTRIBUTES = "[ t ]"
KEY_CODE_MODE_LATEX =      "[ l ]"
KEY_CODE_MODE_ESCAPE =     "[Del]"
KEY_CODE_MODE_NO_KEY =     " 🮱   "



MAX_INT_INPUT_LENGTH = 4
MAX_STR_INPUT_LENGTH = 47

def EMPTY_UTTERANCE(): 
    r = { DICT_ANNOTATIONS : [], DICT_EPISODES : []}
    for i in ATTRIBUTES_UTTERANCE:
        r[i] = None

    r[ATTRIBUTE_SPEAKER] = ATTRIBUTE_SPEAKER_A
    r[ATTRIBUTE_UNCERTAIN] = "False"
    r[ATTRIBUTE_COPILOT_INTERACTION] = "False"
    r[ATTRIBUTE_REPETITIVE] = "False"
    r[ATTRIBUTE_UNCERTAIN] = "False"
    r[ATTRIBUTE_SCOPE_CHANGE] = "False"
    r[ATTRIBUTE_TERMINATION_ATTEMPT] = "False"
    r[ATTRIBUTE_HASTED_REPLY] = "False"

    return r

def EMPTY_EPISODE(): 
    r = { DICT_DEPTH : 0, DICT_UTTERANCES : []}
    for i in ATTRIBUTES_EPISODE:
        r[i] = None
    return r

def EDIT_START_ROW(): return height() - 4
def VIEW_START_ROW(): return height() - 8

def ATTRIBUTE_VIEW_START_ROW(): return VIEW_START_ROW()

#endregion

#region attribute definitions
ATTRIBUTE_TOPIC_TOOL = "tool"
ATTRIBUTE_TOPIC_PROGRAM = "program"
ATTRIBUTE_TOPIC_BUG = "bug"
ATTRIBUTE_TOPIC_CODE = "code"
ATTRIBUTE_TOPIC_DOMAIN = "domain"
ATTRIBUTE_TOPIC_TECHNIQUE = "technique"
ATTRIBUTES_TOPIC = [ATTRIBUTE_TOPIC_TOOL, ATTRIBUTE_TOPIC_PROGRAM, ATTRIBUTE_TOPIC_BUG, ATTRIBUTE_TOPIC_CODE, ATTRIBUTE_TOPIC_DOMAIN, ATTRIBUTE_TOPIC_TECHNIQUE]

ATTRIBUTE_FINISH_TYPE_ASSIMILATION = "assimilation" 
ATTRIBUTE_FINISH_TYPE_UNNECESSARY = "unnecessary" 
ATTRIBUTE_FINISH_TYPE_LOST_SIGHT = "lost sight" 
ATTRIBUTE_FINISH_TYPE_GAVE_UP = "gave up"
ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS = "trust success"
ATTRIBUTE_FINISH_TYPE_TRUST_FAIL = "trust fail"
ATTRIBUTES_FINISH_TYPE = [ATTRIBUTE_FINISH_TYPE_ASSIMILATION, ATTRIBUTE_FINISH_TYPE_UNNECESSARY, ATTRIBUTE_FINISH_TYPE_LOST_SIGHT, ATTRIBUTE_FINISH_TYPE_GAVE_UP, ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS, ATTRIBUTE_FINISH_TYPE_TRUST_FAIL]

ATTRIBUTE_MEDIUM_VERBALISATION = "verbalisation"
ATTRIBUTE_MEDIUM_TYPING = "typing"
ATTRIBUTE_MEDIUM_BOTH = "typing plus demonstration"
ATTRIBUTE_MEDIUM_EXTERNAL_RESOURCE = "external resource"
ATTRIBUTES_MEDIUM = [ATTRIBUTE_MEDIUM_VERBALISATION, ATTRIBUTE_MEDIUM_TYPING, ATTRIBUTE_MEDIUM_BOTH, ATTRIBUTE_MEDIUM_EXTERNAL_RESOURCE]

ATTRIBUTE_TRIGGER_TYPE_FINDING = "finding"
ATTRIBUTE_TRIGGER_DIRECT_QUESTION = "direct question"
ATTRIBUTE_TRIGGER_KNOWN_FACTS = "stating known facts"
ATTRIBUTE_TRIGGER_SIMPLE_STEP = "simple step"
ATTRIBUTE_TRIGGER_PROPOSITION = "proposition"
ATTRIBUTES_EXPLANATION_TRIGGER_TYPE = [ATTRIBUTE_TRIGGER_TYPE_FINDING, ATTRIBUTE_TRIGGER_DIRECT_QUESTION, ATTRIBUTE_TRIGGER_KNOWN_FACTS, ATTRIBUTE_TRIGGER_SIMPLE_STEP, ATTRIBUTE_TRIGGER_PROPOSITION]

ATTRIBUTE_SPEAKER_A = "speaker A"
ATTRIBUTE_SPEAKER_B = "speaker B"
ATTRIBUTE_SPEAKER_INSTRUCTOR = "instructor"
ATTRIBUTE_SPEAKERS = [ATTRIBUTE_SPEAKER_A, ATTRIBUTE_SPEAKER_B, ATTRIBUTE_SPEAKER_INSTRUCTOR]

ATTRIBUTE_TOPIC = "topic"
ATTRIBUTE_TOPIC_ID = "topic id"
ATTRIBUTE_SCOPE_CHANGE = "scope change"
ATTRIBUTE_MEDIUM = "medium"
ATTRIBUTE_TERMINATION_ATTEMPT = "termination attempt"
ATTRIBUTE_HASTED_REPLY = "hasted reply"
ATTRIBUTE_REPETITIVE = "repetitive"
ATTRIBUTE_UNCERTAIN = "uncertain"
ATTRIBUTE_EXPLANATION_TRIGGER_TYPE = "explanation trigger type"
ATTRIBUTE_FINISH_TYPE = "finish type"
ATTRIBUTE_SPEAKER = "speaker"
ATTRIBUTE_COPILOT_INTERACTION = "copilot interaction"
ATTRIBUTE_NOTES = "notes"

ATTRIBUTES_UTTERANCE = [ATTRIBUTE_SPEAKER, ATTRIBUTE_TOPIC, ATTRIBUTE_TOPIC_ID, ATTRIBUTE_COPILOT_INTERACTION, ATTRIBUTE_SCOPE_CHANGE, ATTRIBUTE_MEDIUM, ATTRIBUTE_TERMINATION_ATTEMPT, ATTRIBUTE_HASTED_REPLY, ATTRIBUTE_REPETITIVE, ATTRIBUTE_UNCERTAIN, ATTRIBUTE_EXPLANATION_TRIGGER_TYPE, ATTRIBUTE_NOTES]
ATTRIBUTES_EPISODE = [ATTRIBUTE_TOPIC, ATTRIBUTE_COPILOT_INTERACTION, ATTRIBUTE_FINISH_TYPE, ATTRIBUTE_NOTES]

INT = "int"
STR = "str"

ATTRIBUTE_TYPE_VALUES = {
    ATTRIBUTE_TOPIC : ATTRIBUTES_TOPIC,
    ATTRIBUTE_TOPIC_ID : INT,
    ATTRIBUTE_SCOPE_CHANGE : ["True", "False"],
    ATTRIBUTE_MEDIUM : ATTRIBUTES_MEDIUM,
    ATTRIBUTE_TERMINATION_ATTEMPT : ["True", "False"],
    ATTRIBUTE_HASTED_REPLY : ["True", "False"],
    ATTRIBUTE_REPETITIVE : ["True", "False"],
    ATTRIBUTE_UNCERTAIN : ["True", "False"],
    ATTRIBUTE_EXPLANATION_TRIGGER_TYPE  : ATTRIBUTES_EXPLANATION_TRIGGER_TYPE,
    ATTRIBUTE_FINISH_TYPE : ATTRIBUTES_FINISH_TYPE,
    ATTRIBUTE_NOTES : STR, 
    ATTRIBUTE_COPILOT_INTERACTION : ["True", "False"],
    ATTRIBUTE_SPEAKER : ATTRIBUTE_SPEAKERS
}

ATTRIBUTE_DEFAULT_VALUES = {
    ATTRIBUTE_MEDIUM : 0,
    ATTRIBUTE_SCOPE_CHANGE : 1,
    ATTRIBUTE_TERMINATION_ATTEMPT : 1,
    ATTRIBUTE_HASTED_REPLY : 1,
    ATTRIBUTE_REPETITIVE : 1,
    ATTRIBUTE_UNCERTAIN : 1,
    ATTRIBUTE_COPILOT_INTERACTION : 1,
    ATTRIBUTE_SPEAKER : 0
}

SPEAKER_SYMBOLS = {
    ATTRIBUTE_SPEAKER_A : SYMBOL_SPEAKER_A,
    ATTRIBUTE_SPEAKER_B : SYMBOL_SPEAKER_B,
    ATTRIBUTE_SPEAKER_INSTRUCTOR : SYMBOL_SPEAKER_INSTRUCTOR
}

SPEAKER_COLOURS = {
    ATTRIBUTE_SPEAKER_A : COLOUR_GREEN,
    ATTRIBUTE_SPEAKER_B : COLOUR_BLUE,
    ATTRIBUTE_SPEAKER_INSTRUCTOR : COLOUR_INSTRUCTOR
}

#endregion

#region small things

def info(text):
    print(text)

def error(text):
    print(text)

def warning(text):
    print(text)

def get_json_name_from_transcript(transcript_path):
    return transcript_path.replace(".txt", "_annotated.json")

def is_timestamp(text):
    return re.match("\d\d:\d\d:\d\d", text)

def height():
    global stdscr
    return stdscr.getmaxyx()[0]

def width():
    global stdscr
    return stdscr.getmaxyx()[1]

def max_utterance_id():
    return max(list(map(lambda u : u[DICT_ID], UTTERANCES)))
    
def max_episode_id():
    return max(list(map(lambda u : u[DICT_ID], EPISODES)))

#endregion

#region screen and control flow

def action(key):
    global CURRENT_LINE_VIEW, CURRENT_LINE_EDIT, stdscr, KEY_ACTIONS, CURRENT_MODE, CURRENT_ATTRIBUTE_MODE, \
        CURRENT_UTTERANCE_INDEX, ATTRIBUTE_MENU_FOCUS, ATTRIBUTE_TO_EDIT, CURRENT_INPUT_BUFFER, CURRENT_VALUE, \
        CURRENT_EPISODE_INDEX, LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND

    # custom input
    if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_INT:
        if key == "KEY_BACKSPACE" and len(CURRENT_INPUT_BUFFER) > 0:
            CURRENT_INPUT_BUFFER = CURRENT_INPUT_BUFFER[:-1]
            return
        elif re.match("\d", key) and len(CURRENT_INPUT_BUFFER) < MAX_INT_INPUT_LENGTH:
            CURRENT_INPUT_BUFFER += key
            return
    
    elif ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_STR:
        if key == "KEY_BACKSPACE" and len(CURRENT_INPUT_BUFFER) > 0:
            CURRENT_INPUT_BUFFER = CURRENT_INPUT_BUFFER[:-1]
            return
        elif re.match("\w|[+,./*-?!=~#';()\[\]\{\}:<> ]", key) and len(key) == 1 and len(CURRENT_INPUT_BUFFER) < MAX_STR_INPUT_LENGTH:
            CURRENT_INPUT_BUFFER += key
            return
    
    # modes
    if CURRENT_MODE != MODE_ATTRIBUTES:
        if key == "u":
            CURRENT_MODE = MODE_UTTERANCE
            return
        elif key == "e":
            CURRENT_MODE = MODE_EPISODE
            return
        elif key == "t":
            CURRENT_ATTRIBUTE_MODE = CURRENT_MODE if CURRENT_MODE != MODE_LATEX else MODE_UTTERANCE
            CURRENT_MODE = MODE_ATTRIBUTES
            ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_ATTRIBUTES
            ATTRIBUTE_TO_EDIT = 0
            CURRENT_VALUE = 0
            return
        elif key == "l":
            CURRENT_MODE = MODE_LATEX
            LATEX_ANNOTATION_INDEX_FST = None
            LATEX_ANNOTATION_INDEX_SND = None
            return
    else:
        if key == "u":
            CURRENT_ATTRIBUTE_MODE = MODE_UTTERANCE
            return
        elif key == "e":
            CURRENT_ATTRIBUTE_MODE = MODE_EPISODE
            return
        elif key == "KEY_DC":
            CURRENT_MODE = CURRENT_ATTRIBUTE_MODE
            return
        elif key == "l":
            CURRENT_MODE = MODE_LATEX
            LATEX_ANNOTATION_INDEX_FST = None
            LATEX_ANNOTATION_INDEX_SND = None
            return
    # view 
    if key == "KEY_UP":
        if CURRENT_LINE_VIEW > 0:
            CURRENT_LINE_VIEW -= 1
        return
    elif key == "KEY_PPAGE":
        if CURRENT_LINE_VIEW > 10:
            CURRENT_LINE_VIEW -= 10
        else:
            CURRENT_LINE_VIEW = 0
        return
    
    elif key == "KEY_DOWN":
        if CURRENT_LINE_VIEW < len(TRANSCRIPT) - 1:
            CURRENT_LINE_VIEW += 1
        return
    
    elif key == "KEY_NPAGE":
        if CURRENT_LINE_VIEW < len(TRANSCRIPT) - 10:
            CURRENT_LINE_VIEW += 10
        else:
            CURRENT_LINE_VIEW = len(TRANSCRIPT) - 1         
        return

    elif key == "o":
        CURRENT_LINE_VIEW = 0
        CURRENT_LINE_EDIT = 0
        set_current_episode(0)
        if len(UTTERANCES) > 0:
            CURRENT_UTTERANCE_INDEX = 0
        return
    elif key == "p":
        CURRENT_LINE_VIEW = len(TRANSCRIPT) - 1
        CURRENT_LINE_EDIT = len(TRANSCRIPT) - 1
        set_current_episode(len(EPISODES) - 1)
        if len(UTTERANCES) > 0:
            CURRENT_UTTERANCE_INDEX = len(UTTERANCES) - 1
        return
    
    for k in KEY_ACTIONS.keys():
        if key == k:
            KEY_ACTIONS[k]()
            return           
    
def draw_mode_controls():
    if CURRENT_MODE != MODE_ATTRIBUTES:
        mode_control_utterances = f" {KEY_CODE_MODE_UTTERANCES if CURRENT_MODE != MODE_UTTERANCE else KEY_CODE_MODE_NO_KEY} {MODE_UTTERANCE} "
        mode_control_episodes = f" {KEY_CODE_MODE_EPISODES if CURRENT_MODE != MODE_EPISODE else KEY_CODE_MODE_NO_KEY} {MODE_EPISODE} "
        mode_control_attributes = f" {KEY_CODE_MODE_ATTRIBUTES} {MODE_ATTRIBUTES} "
        mode_control_latex = f" {KEY_CODE_MODE_LATEX if CURRENT_MODE != MODE_LATEX else KEY_CODE_MODE_NO_KEY} {MODE_LATEX} "
    else:
        mode_control_utterances = f" {KEY_CODE_MODE_ESCAPE if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE else KEY_CODE_MODE_UTTERANCES} {MODE_UTTERANCE} "
        mode_control_episodes = f" {KEY_CODE_MODE_ESCAPE if CURRENT_ATTRIBUTE_MODE == MODE_EPISODE else KEY_CODE_MODE_EPISODES} {MODE_EPISODE} "
        mode_control_attributes = f" {KEY_CODE_MODE_NO_KEY} {MODE_ATTRIBUTES} "
        mode_control_latex = f" {KEY_CODE_MODE_LATEX if CURRENT_MODE != MODE_LATEX else KEY_CODE_MODE_NO_KEY} {MODE_LATEX} "

    pos = [1,
           len(mode_control_utterances) + 1,
           len(mode_control_utterances) + len(mode_control_episodes) + 1,
           len(mode_control_utterances) + len(mode_control_episodes) + len(mode_control_attributes) + 1]
    if CURRENT_MODE == MODE_UTTERANCE:
        stdscr.addstr(MODE_SELECTION_ROW, pos[0], mode_control_utterances, curses.A_REVERSE + curses.color_pair(3))
        stdscr.addstr(MODE_SELECTION_ROW, pos[1], mode_control_episodes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[2], mode_control_attributes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[3], mode_control_latex, curses.A_REVERSE)
    elif CURRENT_MODE == MODE_EPISODE:
        stdscr.addstr(MODE_SELECTION_ROW, pos[0], mode_control_utterances, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[1], mode_control_episodes, curses.A_REVERSE + curses.color_pair(3))
        stdscr.addstr(MODE_SELECTION_ROW, pos[2], mode_control_attributes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[3], mode_control_latex, curses.A_REVERSE)
    elif CURRENT_MODE == MODE_ATTRIBUTES: 
        stdscr.addstr(MODE_SELECTION_ROW, pos[0], mode_control_utterances, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[1], mode_control_episodes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[2], mode_control_attributes, curses.A_REVERSE + curses.color_pair(2))
        stdscr.addstr(MODE_SELECTION_ROW, pos[3], mode_control_latex, curses.A_REVERSE)
        if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
            stdscr.addstr(MODE_SELECTION_ROW, pos[0], mode_control_utterances, curses.A_REVERSE + curses.color_pair(3))
        elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
            stdscr.addstr(MODE_SELECTION_ROW, pos[1], mode_control_episodes, curses.A_REVERSE + curses.color_pair(3))
    elif CURRENT_MODE == MODE_LATEX:
        stdscr.addstr(MODE_SELECTION_ROW, pos[0], mode_control_utterances, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[1], mode_control_episodes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[2], mode_control_attributes, curses.A_REVERSE)
        stdscr.addstr(MODE_SELECTION_ROW, pos[3], mode_control_latex, curses.A_REVERSE + curses.color_pair(3))
        
def draw_horizontal_line(row):
    stdscr.addstr(row, 1, "─" * (width() - 2))

def draw_transcript_line(n, offset, symbol, bold = False):
    timestamp, text = TRANSCRIPT[n]
    lines = textwrap.wrap(text, width() - 30, break_long_words=False)
    last_line = len(lines) - 1

    utterance = None
    prev_utterance = None
    if ANNOTATIONS[n][DICT_UTTERANCE] >= 0:
        utterance = get_utterance(ANNOTATIONS[n][DICT_UTTERANCE])
    if 0 < n < len(ANNOTATIONS) - 1 and ANNOTATIONS[n - 1][DICT_UTTERANCE] >= 0:
        prev_utterance = get_utterance(ANNOTATIONS[n - 1][DICT_UTTERANCE])

    draw_speaker = utterance and (not prev_utterance or prev_utterance[ATTRIBUTE_SPEAKER] != utterance[ATTRIBUTE_SPEAKER])
    if draw_speaker:
        speaker = utterance[ATTRIBUTE_SPEAKER]
        stdscr.addstr(offset, EDIT_START_COL, SPEAKER_SYMBOLS[speaker], curses.color_pair(SPEAKER_COLOURS[speaker]))

    if bold:
        stdscr.addstr(offset - last_line, 2, f"{symbol}", curses.A_BOLD)
    else:
        stdscr.addstr(offset - last_line, 2, f"{symbol}")

    for i in range(len(lines)):
        if bold:
            stdscr.addstr(offset - i, EDIT_START_COL + 4, lines[last_line - i], curses.A_BOLD)
        else:
            stdscr.addstr(offset - i, EDIT_START_COL + 4, lines[last_line - i])

    return len(lines)

def draw_list_of_controls(y, controls):
    x = width() - 1

    for c in range(len(controls) - 1, -1, -1):
        control = controls[c]

        key = control[1:control.index("]")]
        key_print = f"[{key}]"
        description = control[control.index("]") + 2:]

        x -= len(description)
        stdscr.addstr(y, x, description)

        x -= len(key_print) + 1
        stdscr.addstr(y, x, key_print, curses.A_BOLD)

        x -= 3

def draw_object_info(object, y, x, attributes, clipboard_attribute = None):
    s = f"Id {object[DICT_ID]}   "
    stdscr.addstr(y, x, s)
    x += len(s)

    if DICT_UTTERANCES in object:
        s = f"Len {len(object[DICT_UTTERANCES])}   "
        stdscr.addstr(y, x, s)
        x += len(s)
    if DICT_ANNOTATIONS in object:
        s = f"Len {len(object[DICT_ANNOTATIONS])}   "
        stdscr.addstr(y, x, s)
        x += len(s)

    for attribute in attributes:
        if (attribute != ATTRIBUTE_SPEAKER and
            attribute != ATTRIBUTE_TOPIC and
            attribute != ATTRIBUTE_COPILOT_INTERACTION and
            attribute != ATTRIBUTE_NOTES and
            attribute != ATTRIBUTE_FINISH_TYPE):
            continue

        if x > width() - 2:
            stdscr.addstr(y, width() - 3, "...")
            break

        t = ATTRIBUTE_TYPE_VALUES[attribute]
        v = object[attribute]
        args = []

        if clipboard_attribute and attribute == clipboard_attribute:
            args.append(curses.A_UNDERLINE)
        if not v:
            args.append(curses.color_pair(COLOUR_BLUE))

        if t == INT:
            if v:
                s = str(v)
            else:
                s = attribute
        elif t == STR:
            if v:
                s = v
                if len(v) > 23:
                    s = f"{s[0:20]}..."
            else:
                s = attribute
        elif "True" in t:
            s = attribute
            args.append(curses.color_pair(COLOUR_GREEN) if v == "True" else curses.color_pair(COLOUR_RED))
        else:
            s = attribute if not v else v

        stdscr.addstr(y, x, s, reduce(lambda a, b : a | b, args, 0))
        x += len(s) + 3

def draw_view():
    global CURRENT_MODE, CURRENT_LINE_VIEW_END

    current_utterance = None
    current_utterance_id = -1
    current_episode = None
    current_episode_id = -1

    if len(UTTERANCES) > 0:
        current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]
        current_utterance_id = current_utterance[DICT_ID]
    if len(EPISODES) > 0:
        current_episode = EPISODES[CURRENT_EPISODE_INDEX]
        current_episode_id = current_episode[DICT_ID]

    # Draw lines
    offset = VIEW_START_ROW()

    # Draw utterance braces and episode markings
    n = min(CURRENT_LINE_VIEW, len(TRANSCRIPT) - 1)
    while offset >= VIEW_END_ROW and n >= 0:
        CURRENT_LINE_VIEW_END = n

        # contextual highlight     
        selected = ((CURRENT_MODE == MODE_EPISODE and current_utterance_id == ANNOTATIONS[n][DICT_UTTERANCE]) or 
                    (CURRENT_MODE == MODE_UTTERANCE and current_utterance_id == ANNOTATIONS[n][DICT_UTTERANCE]) or
                    CURRENT_MODE == MODE_ATTRIBUTES and
                        (not MULTISELECT and 
                         (CURRENT_ATTRIBUTE_MODE == MODE_EPISODE and 
                            ANNOTATIONS[n][DICT_UTTERANCE] >= 0 and 
                            current_episode_id in get_utterance(ANNOTATIONS[n][DICT_UTTERANCE])[DICT_EPISODES]) or
                            CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE and
                            (current_utterance_id == ANNOTATIONS[n][DICT_UTTERANCE])))

        # determine whether the current line is selected for a latex export
        if CURRENT_MODE == MODE_LATEX and LATEX_ANNOTATION_INDEX_FST is not None:
            if LATEX_ANNOTATION_INDEX_FST:
                min_latex_selection = min(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND if LATEX_ANNOTATION_INDEX_SND else CURRENT_LINE_EDIT)
                max_latex_selection = max(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND if LATEX_ANNOTATION_INDEX_SND else CURRENT_LINE_EDIT)
                within_latex_selection = min_latex_selection <= n <= max_latex_selection
            else:
                within_latex_selection = False
        else:
            within_latex_selection = False

        in_multi_selection = False
        if CURRENT_MODE == MODE_ATTRIBUTES and MULTISELECT:
            if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
                # check whether the index of the current utterance is in the object to edit list
                in_multi_selection = ANNOTATIONS[n][DICT_UTTERANCE] in [UTTERANCES.index(u) for u in OBJECT_TO_EDIT]
            elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
                # get all episodes the line is part of
                episodes = get_utterance(ANNOTATIONS[n][DICT_UTTERANCE])[DICT_EPISODES]
                # check if any of the episodes is in the object to edit list
                in_multi_selection = reduce(lambda x, y : x or y, list(map(lambda e : get_episode(e) in OBJECT_TO_EDIT, episodes)))

        
        utterance_start = False
        utterance_end = False
        draw_utterance_braces = ANNOTATIONS[n][DICT_UTTERANCE] >= 0
        
        if n == 0 or ANNOTATIONS[n - 1][DICT_UTTERANCE] != ANNOTATIONS[n][DICT_UTTERANCE]: 
            utterance_start = True
        if n == len(ANNOTATIONS) - 1 or ANNOTATIONS[n + 1][DICT_UTTERANCE] != ANNOTATIONS[n][DICT_UTTERANCE]: 
            utterance_end = True

        # draw and highlight transcript lines
        num_lines = draw_transcript_line(n, offset, SYMBOL_EMPTY)

        if CURRENT_MODE != MODE_ATTRIBUTES:
            if CURRENT_MODE == MODE_UTTERANCE:
                if n == CURRENT_LINE_EDIT:
                    draw_transcript_line(n, offset, SYMBOL_CURRENT_EDIT, True)
            if CURRENT_MODE == MODE_EPISODE:
                if current_utterance_id == ANNOTATIONS[n][DICT_UTTERANCE]:
                    draw_transcript_line(n, offset, SYMBOL_EMPTY, True)
            if CURRENT_MODE == MODE_LATEX:
                if within_latex_selection:
                    draw_transcript_line(n, offset, SYMBOL_VIEW_ANNOTATED, True)
                if n == CURRENT_LINE_EDIT:
                    draw_transcript_line(n, offset, SYMBOL_CURRENT_EDIT, True)
        else:
            if selected:
                draw_transcript_line(n, offset, SYMBOL_EMPTY, True)
            if in_multi_selection:
                draw_transcript_line(n, offset, SYMBOL_EMPTY, True)
                if utterance_start and CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
                    draw_transcript_line(n, offset, SYMBOL_VIEW_ANNOTATED, True)

        # utterance braces
        top = {True:"╔", False:"┌"}
        middle = {True:"║", False:"│"}
        bottom = {True:"╚", False:"└"}        
        single = {True:"═", False:"╶"}  

        if draw_utterance_braces:    
            highlight = curses.A_BOLD if selected else curses.A_NORMAL

            if utterance_start:
                stdscr.addstr(offset - num_lines + 1, UTTERANCE_BRACE_COL, top[selected], highlight)
            else:
                stdscr.addstr(offset - num_lines + 1, UTTERANCE_BRACE_COL, middle[selected], highlight)
                stdscr.addstr(offset - num_lines, UTTERANCE_BRACE_COL, middle[selected], highlight)
           
            for i in range(offset - num_lines + 2, offset + 1):
                stdscr.addstr(i, UTTERANCE_BRACE_COL, middle[selected], highlight)

            if utterance_start and utterance_end and num_lines == 1:
                stdscr.addstr(offset - num_lines + 1, UTTERANCE_BRACE_COL, single[selected], highlight)
            elif utterance_end :
                stdscr.addstr(offset, UTTERANCE_BRACE_COL, bottom[selected], highlight)

        # episodes       
        utterance_id = ANNOTATIONS[n][DICT_UTTERANCE]
        episode_ids = []
        if utterance_id > -1:
            utterance =  get_utterance(utterance_id)
            episode_ids = utterance[DICT_EPISODES]

        draw_episode_markings = episode_ids != []
        
        for depth in range(len(episode_ids)):
            episode_id = episode_ids[depth]
            episode = get_episode(episode_id)
            
            # first_utterance = min([UTTERANCES.index(get_utterance(u)) for u in episode[DICT_UTTERANCES]])
            # last_utterance = max([UTTERANCES.index(get_utterance(u)) for u in episode[DICT_UTTERANCES]])
            if not UTTERANCE_INDICES:
                compute_utterance_indices_dict()
            first_utterance = min([UTTERANCE_INDICES[u] for u in episode[DICT_UTTERANCES]])
            last_utterance = max([UTTERANCE_INDICES[u] for u in episode[DICT_UTTERANCES]])

            first_line = min(UTTERANCES[first_utterance][DICT_ANNOTATIONS])
            last_line = max(UTTERANCES[last_utterance][DICT_ANNOTATIONS])

            episode_start = n == first_line 
            episode_end = n == last_line

            episode_select = CURRENT_MODE == MODE_EPISODE or (CURRENT_MODE == MODE_ATTRIBUTES and CURRENT_ATTRIBUTE_MODE == MODE_EPISODE)
            selected = episode_select and current_episode_id == episode_id

            top = {True: "▄", False: ""}
            middle = {True: "█", False: "▒"}
            bottom = {True: "▀", False: ""}
            single = {True: "█", False: "▒"}

            has_copilot_interaction = episode[ATTRIBUTE_COPILOT_INTERACTION]
            if has_copilot_interaction is None:
                has_copilot_interaction = False
            else:
                has_copilot_interaction = True if has_copilot_interaction == "True" else False

            if draw_episode_markings:
                in_multi_selection = (MULTISELECT and CURRENT_MODE == MODE_ATTRIBUTES and CURRENT_ATTRIBUTE_MODE == MODE_EPISODE and 
                                      episode in OBJECT_TO_EDIT)

                highlight = curses.A_NORMAL
                if selected and in_multi_selection:
                    highlight = curses.color_pair(COLOUR_EPISODE_SELECTED_MULTISELECT)
                elif selected:                
                    highlight = curses.color_pair(COLOUR_EPISODE_SELECTED)
                elif in_multi_selection:
                    highlight = curses.color_pair(COLOUR_EPISODE_MULTISELECT)
                
                col_attr = EDIT_START_COL - 20 + depth

                if episode_start:
                    stdscr.addstr(offset - num_lines + 1, col_attr, top[has_copilot_interaction], highlight)
                else:
                    stdscr.addstr(offset - num_lines + 1, col_attr, middle[has_copilot_interaction], highlight)
           
                for i in range(offset - num_lines + 2, offset + 1):
                    stdscr.addstr(i, col_attr, middle[has_copilot_interaction], highlight)

                if episode_start and episode_end and num_lines == 1:
                    stdscr.addstr(offset - num_lines + 1, col_attr, single[has_copilot_interaction], highlight)
                elif episode_end:
                    stdscr.addstr(offset, col_attr, bottom[has_copilot_interaction], highlight)
                elif not episode_end:
                    if offset != offset - num_lines + 1:
                        stdscr.addstr(offset, col_attr, middle[has_copilot_interaction], highlight)
                    stdscr.addstr(offset + 1, col_attr, middle[has_copilot_interaction], highlight)

        offset -= num_lines + 1
        n -= 1

    # Draw controls
    draw_horizontal_line(VIEW_START_ROW() + 2)
    view_controls = ["[o] top", "[p] bottom", f"[{KEY_PAGE_UP}] up fast", f"[{KEY_PAGE_DOWN}] down fast", f"[{KEY_UP}] up", f"[{KEY_DOWN}] down"]
    draw_list_of_controls(VIEW_START_ROW() + 1, view_controls)

    # Draw scroll bar
    space = VIEW_START_ROW() - VIEW_END_ROW
    rel = CURRENT_LINE_VIEW * 1.0 / len(TRANSCRIPT)

    pos = int(space * rel)
    for r in range(VIEW_END_ROW - 1, VIEW_START_ROW() + 1):
        stdscr.addstr(r, width() - 2, "▏ ")

        if VIEW_END_ROW + pos - 1 <= r <= VIEW_END_ROW + pos + 1:
            stdscr.addstr(r, width() - 2, "█")


    # Draw mode specific things
    if CURRENT_MODE == MODE_UTTERANCE:
        if len(UTTERANCES) > 0:
            stdscr.addstr(height() - 5, 1, f"Utterances: {len(UTTERANCES)}")
            stdscr.addstr(height() - 4, 1, f"Selected:")
            draw_object_info(current_utterance, height() - 4, 12, ATTRIBUTES_UTTERANCE)
        else:    
            stdscr.addstr(height() - 4, 1, f"No utterances")

    elif CURRENT_MODE == MODE_EPISODE:
        if len(EPISODES) > 0:
            stdscr.addstr(height() - 5, 1, f"Episodes:   {len(EPISODES)}")
            stdscr.addstr(height() - 4, 1, f"Selected E:")
            draw_object_info(current_episode, height() - 4, 13, ATTRIBUTES_EPISODE)
            if current_utterance:
                stdscr.addstr(height() - 3, 1, f"Selected U:")
                draw_object_info(current_utterance, height() - 3, 13, ATTRIBUTES_UTTERANCE)
        else:    
            stdscr.addstr(height() - 4, 1, f"No episodes")

    elif CURRENT_MODE == MODE_ATTRIBUTES:
        if OBJECT_TO_EDIT == None:
            stdscr.addstr(height() - 4, 1, f"Nothing to edit")
            return

        if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
            if MULTISELECT:
                stdscr.addstr(height() - 5, 1, f"Utterances: {len(UTTERANCES)} │ Multi select: {len(OBJECT_TO_EDIT)} utterance(s)")
            else:
                stdscr.addstr(height() - 5, 1, f"Utterances: {len(UTTERANCES)}")
                stdscr.addstr(height() - 4, 1, f"Selected:")
                draw_object_info(current_utterance, height() - 4, 12, ATTRIBUTES_UTTERANCE)

            if CLIPBOARD_UTTERANCE:
                stdscr.addstr(height() - 3, 1, f"Clipboard:")
                draw_object_info(CLIPBOARD_UTTERANCE, height() - 3, 12, ATTRIBUTES_UTTERANCE, CLIPBOARD_UTTERANCE_ATTRIBUTE)

        elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
            if MULTISELECT:
                stdscr.addstr(height() - 5, 1, f"Episodes: {len(UTTERANCES)} │ Multi select: {len(OBJECT_TO_EDIT)} episode(s)")
            else:         
                stdscr.addstr(height() - 5, 1, f"Episodes:  {len(EPISODES)} │ Utterances: {len(current_episode[DICT_UTTERANCES])}")
                stdscr.addstr(height() - 4, 1, f"Selected:")
                draw_object_info(current_episode, height() - 4, 12, ATTRIBUTES_EPISODE)

            if CLIPBOARD_EPISODE:
                stdscr.addstr(height() - 3, 1, f"Clipboard:")
                draw_object_info(CLIPBOARD_EPISODE, height() - 3, 12, ATTRIBUTES_UTTERANCE, CLIPBOARD_EPISODE_ATTRIBUTE)

        if MULTISELECT and OBJECT_TO_EDIT == []:
            return

        # draw attribute view
        attribute_width = max(list(map(lambda x : len(x), AVAILABLE_ATTRIBUTES))) + 2
        row = ATTRIBUTE_VIEW_START_ROW() - len(AVAILABLE_ATTRIBUTES)
        col_attribute = width() - attribute_width - ATTRIBUTE_VALUE_TEXT_WIDTH - 4
        col_value = col_attribute + attribute_width
        
        selected_row = row

        for i in range(len(AVAILABLE_ATTRIBUTES)):
            attribute = AVAILABLE_ATTRIBUTES[i]            
            
            # for the multi select case
            if MULTISELECT:               
                values = [o[attribute] for o in OBJECT_TO_EDIT]
               
                # check if all values are the same
                if len(set(values)) == 1:
                    value = values[0]
                else:
                    value = "multiple values"    

            # for the single select case
            else:
                value = OBJECT_TO_EDIT[attribute]
                
            colour_selected = COLOUR_MENU_SELECTED if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES else COLOUR_MENU_SELECTED_DISABLED
            colour_not_selected = COLOUR_MENU if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES else COLOUR_MENU_DISABLED
            colour = curses.color_pair(colour_selected if ATTRIBUTE_TO_EDIT == i else colour_not_selected)

            stdscr.addstr(row, col_attribute - 1, " " * (col_value - col_attribute + ATTRIBUTE_VALUE_TEXT_WIDTH + 2), colour)
            stdscr.addstr(row, col_attribute, attribute, colour)
            stdscr.addstr(row, col_value, f"│ {value}", colour)

            if ATTRIBUTE_TO_EDIT == i:
                selected_row = row
            row += 1

        # draw attribute menu for selected attribute
        selected_attribute = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
        possible_values = ATTRIBUTE_TYPE_VALUES[selected_attribute]

        if MULTISELECT:
            values = [o[attribute] for o in OBJECT_TO_EDIT]            
            # check if all values are the same
            if len(set(values)) == 1:
                current_attribute_value = values[0]
            else:
                current_attribute_value = "multiple values"    

        else:
            current_attribute_value = OBJECT_TO_EDIT[selected_attribute] 

        row = selected_row

        if possible_values == INT:
            col = col_attribute - ATTRIBUTE_INT_TEXT_WIDTH - 3
            symbol = SYMBOL_VIEW_ANNOTATED if current_attribute_value is not None else SYMBOL_EMPTY
            colour = curses.color_pair(COLOUR_MENU_SELECTED if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_INT else COLOUR_MENU)
                        
            value = CURRENT_INPUT_BUFFER if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_INT else current_attribute_value

            stdscr.addstr(row, col - 1, " " * (ATTRIBUTE_INT_TEXT_WIDTH + 2), colour)
            stdscr.addstr(row, col, f"{symbol} {value}", colour)

            if len(CURRENT_INPUT_BUFFER) < MAX_INT_INPUT_LENGTH and ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_INT:
                stdscr.addstr(row, col + len(CURRENT_INPUT_BUFFER) + 3, "_", curses.A_BLINK + curses.color_pair(COLOUR_MENU_SELECTED))

        elif possible_values == STR:
            col = col_attribute - ATTRIBUTE_STR_TEXT_WIDTH - 3
            symbol = SYMBOL_VIEW_ANNOTATED if current_attribute_value is not None else SYMBOL_EMPTY
            colour = curses.color_pair(COLOUR_MENU_SELECTED if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_STR else COLOUR_MENU)
                        
            value = CURRENT_INPUT_BUFFER if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_STR else current_attribute_value

            stdscr.addstr(row, col - 1, " " * (ATTRIBUTE_STR_TEXT_WIDTH + 2), colour)
            stdscr.addstr(row, col, f"{symbol} {value}", colour)

            if len(CURRENT_INPUT_BUFFER) < MAX_STR_INPUT_LENGTH and ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_STR:
                stdscr.addstr(row, col + len(CURRENT_INPUT_BUFFER) + 4, "_", curses.A_BLINK + curses.color_pair(COLOUR_MENU_SELECTED))

        else:
            value_width = max(list(map(lambda x : len(x), possible_values))) + 2
            col = col_attribute - value_width - 7

            for i in range(len(possible_values)):                
                value = possible_values[i]
                symbol = SYMBOL_VIEW_ANNOTATED if current_attribute_value == possible_values[i] else SYMBOL_EMPTY
                colour = curses.color_pair(COLOUR_MENU_SELECTED if CURRENT_VALUE == i else COLOUR_MENU)

                if ATTRIBUTE_MENU_FOCUS != ATTRIBUTE_MENU_FOCUS_VALUES:
                    colour = curses.color_pair(COLOUR_MENU_DISABLED)

                stdscr.addstr(row, col, " " * (value_width + 4), colour)
                stdscr.addstr(row, col, f" {symbol} {value}", colour)
                row += 1

def edit_entry():
    global CURRENT_LINE_EDIT, CURRENT_MODE, SYMBOL_CURRENT_EDIT, ANNOTATIONS, CURRENT_LINE_EDIT, KEY_ACTIONS, \
        CURRENT_UTTERANCE_INDEX, CURRENT_EPISODE_DEPTH, OBJECT_TO_EDIT, ATTRIBUTE_TO_EDIT, AVAILABLE_ATTRIBUTES, \
        CURRENT_VALUE, LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND
    
    KEY_ACTIONS = {"q" : quit, "f" : save }
        
    controls = []

    if CURRENT_MODE == MODE_UTTERANCE:
        current_annotation = ANNOTATIONS[CURRENT_LINE_EDIT]
        current_utterance = None
        if CURRENT_UTTERANCE_INDEX != -1:
            current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]
        
        # As soon as we know the mode, we can display controls
        previous_annotation_exists = CURRENT_LINE_EDIT != 0
        next_annotation_exists = CURRENT_LINE_EDIT != len(ANNOTATIONS) - 1

        KEY_ACTIONS["k"] = fill_with_empty_utterances
        controls.append("[k] fill")

        if not has_empty_utterance():
            KEY_ACTIONS["n"] = new_utterance                                
            controls.append("[n] new")

        if len(UTTERANCES) > 0:            
            controls.append("[x] delete")
            KEY_ACTIONS["x"] = delete_current_utterance
            
            if len(current_utterance[DICT_ANNOTATIONS]) > 0:
                controls.append("[j] jump")
                KEY_ACTIONS["j"] = jump_to_utterance_annotations

            if current_annotation[DICT_UTTERANCE] != current_utterance[DICT_ID]:
                if (CURRENT_LINE_EDIT == 0 or CURRENT_LINE_EDIT == len(ANNOTATIONS) - 1 or
                    len(current_utterance[DICT_ANNOTATIONS]) == 0 or
                    ANNOTATIONS[CURRENT_LINE_EDIT - 1][DICT_UTTERANCE] == current_utterance[DICT_ID] or 
                    ANNOTATIONS[CURRENT_LINE_EDIT + 1][DICT_UTTERANCE] == current_utterance[DICT_ID]):
                    controls.append("[a] add line")
                    KEY_ACTIONS["a"] = add_to_utterance
            else:
                controls.append(f"[r] remove line")
                KEY_ACTIONS["r"] = remove_from_current_utterance


            if CURRENT_UTTERANCE_INDEX > 0:
                controls.append(f"[{KEY_LEFT}] previous")
                KEY_ACTIONS["KEY_LEFT"] = previous_utterance
            if CURRENT_UTTERANCE_INDEX < len(UTTERANCES) - 1:
                controls.append(f"[{KEY_RIGHT}] next")
                KEY_ACTIONS["KEY_RIGHT"] = next_utterance

        if previous_annotation_exists:
            controls.append("[-] up")
            KEY_ACTIONS["-"] = previous_annotation
        if next_annotation_exists:
            controls.append("[+] down")
            KEY_ACTIONS["+"] = next_annotation

    elif CURRENT_MODE == MODE_EPISODE:
        current_utterance = None
        current_episode = None

        if CURRENT_UTTERANCE_INDEX != -1:
            current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]
        if CURRENT_EPISODE_INDEX != -1:
            current_episode = EPISODES[CURRENT_EPISODE_INDEX]

        # As soon as we know the mode, we can display controls
        if current_utterance is not None:
            previous_annotation_exists = UTTERANCES.index(current_utterance) > 0
            next_annotation_exists = UTTERANCES.index(current_utterance) < len(UTTERANCES) - 1
            
            if not has_empty_episode():
                KEY_ACTIONS["n"] = new_episode                                
                controls.append("[n] new")
            
            if len(EPISODES) > 0:
                allow_delete = True
                allow_remove = True
                episodes = set()
                for u in current_episode[DICT_UTTERANCES]:
                    for e in get_utterance(u)[DICT_EPISODES]:
                        episodes.add(e)

                # for e in episodes:
                #     if get_episode(e)[DICT_DEPTH] > current_episode[DICT_DEPTH]:
                #         allow_delete = False
                #         break

                for e in current_utterance[DICT_EPISODES]:
                    if get_episode(e)[DICT_DEPTH] > current_episode[DICT_DEPTH]:
                        allow_remove = False
                        break
                
                if allow_delete:
                    controls.append("[x] delete")
                    KEY_ACTIONS["x"] = delete_current_episode
                
                if len(current_episode[DICT_UTTERANCES]) > 0:
                    controls.append("[j] jump")
                    KEY_ACTIONS["j"] = jump_to_episode_first_utterance

                current_utterance_depth = get_episode_depth(current_utterance[DICT_ID])
                if current_utterance[DICT_ID] not in current_episode[DICT_UTTERANCES]:
                    if ((current_episode[DICT_DEPTH] == 0) or
                        (current_episode[DICT_DEPTH] > 0 and current_utterance_depth == current_episode[DICT_DEPTH] - 1)):
                        if (len(current_episode[DICT_UTTERANCES]) == 0 or
                            UTTERANCES[CURRENT_UTTERANCE_INDEX - 1][DICT_ID] in current_episode[DICT_UTTERANCES] or 
                            (CURRENT_UTTERANCE_INDEX < len(UTTERANCES) - 1 and UTTERANCES[CURRENT_UTTERANCE_INDEX + 1][DICT_ID] in current_episode[DICT_UTTERANCES])):            
                            controls.append("[a] add utterance")
                            KEY_ACTIONS["a"] = add_current_to_current_episode
                else:
                    if allow_remove:
                        controls.append(f"[r] remove utterance")
                        KEY_ACTIONS["r"] = remove_current_from_current_episode

                if CURRENT_EPISODE_INDEX > 0:
                    controls.append(f"[{KEY_LEFT}] previous")
                    KEY_ACTIONS["KEY_LEFT"] = previous_episode
                if CURRENT_EPISODE_INDEX < len(EPISODES) - 1:
                    controls.append(f"[{KEY_RIGHT}] next")
                    KEY_ACTIONS["KEY_RIGHT"] = next_episode

            if CURRENT_UTTERANCE_INDEX > 0:
                controls.append("[-] previous")
                KEY_ACTIONS["-"] = previous_utterance
            if CURRENT_UTTERANCE_INDEX < len(UTTERANCES) - 1:
                controls.append("[+] next")
                KEY_ACTIONS["+"] = next_utterance

    elif CURRENT_MODE == MODE_ATTRIBUTES:
        OBJECT_TO_EDIT = OBJECT_TO_EDIT if MULTISELECT else None
        AVAILABLE_ATTRIBUTES = None

        # first determine whether multiselect is enabled
        if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
            if MULTISELECT:
                controls.append(f"[m] single select")
            else:
                controls.append(f"[m] multi select")
            KEY_ACTIONS["m"] = toggle_multiselect
        
        # determine what is to edit and add controls for navigating 
        # first for multi select mode
        if MULTISELECT:
            if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
                if len(UTTERANCES) > 0:
                    if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
                        if CURRENT_UTTERANCE_INDEX > 0:
                            controls.append(f"[-] previous")
                            KEY_ACTIONS["-"] = previous_utterance
                        if CURRENT_UTTERANCE_INDEX < len(UTTERANCES) - 1:
                            controls.append(f"[+] next")
                            KEY_ACTIONS["+"] = next_utterance

                    if UTTERANCES[CURRENT_UTTERANCE_INDEX] in OBJECT_TO_EDIT:
                        controls.append(f"[n] remove from selection")
                        KEY_ACTIONS["n"] = remove_from_multi_selection
                    else:
                        controls.append(f"[n] add to selection")
                        KEY_ACTIONS["n"] = add_to_multi_selection

                    AVAILABLE_ATTRIBUTES = ATTRIBUTES_UTTERANCE

            elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
                if len(EPISODES) > 0:
                    if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
                        if CURRENT_EPISODE_INDEX > 0:
                            controls.append(f"[-] previous")
                            KEY_ACTIONS["-"] = previous_episode
                        if CURRENT_EPISODE_INDEX < len(EPISODES) - 1:
                            controls.append(f"[+] next")
                            KEY_ACTIONS["+"] = next_episode
                    
                    if EPISODES[CURRENT_EPISODE_INDEX] in OBJECT_TO_EDIT:
                        controls.append(f"[n] remove from selection")
                        KEY_ACTIONS["n"] = remove_from_multi_selection
                    else:
                        controls.append(f"[n] add to selection")
                        KEY_ACTIONS["n"] = add_to_multi_selection

                    AVAILABLE_ATTRIBUTES = ATTRIBUTES_EPISODE

        # now for single select mode which is default
        else:
            if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
                if len(UTTERANCES) > 0:
                    if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
                        if CURRENT_UTTERANCE_INDEX > 0:
                            controls.append(f"[-] previous")
                            KEY_ACTIONS["-"] = previous_utterance
                        if CURRENT_UTTERANCE_INDEX < len(UTTERANCES) - 1:
                            controls.append(f"[+] next")
                            KEY_ACTIONS["+"] = next_utterance

                        controls.append(f"[c] copy")
                        KEY_ACTIONS["c"] = copy_utterance
                        controls.append(f"[y] copy {CLIPBOARD_UTTERANCE_ATTRIBUTE}")
                        KEY_ACTIONS["y"] = copy_utterance_attribute

                        if CLIPBOARD_UTTERANCE:
                            controls.append(f"[v] paste")
                            KEY_ACTIONS["v"] = paste_utterance
                        if CLIPBOARD_UTTERANCE_ATTRIBUTE:
                            controls.append(f"[b] paste {CLIPBOARD_UTTERANCE_ATTRIBUTE}")
                            KEY_ACTIONS["b"] = paste_utterance_attribute

                    OBJECT_TO_EDIT = UTTERANCES[CURRENT_UTTERANCE_INDEX]
                    AVAILABLE_ATTRIBUTES = ATTRIBUTES_UTTERANCE              

            elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
                if len(EPISODES) > 0:
                    if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
                        if CURRENT_EPISODE_INDEX > 0:
                            controls.append(f"[-] previous")
                            KEY_ACTIONS["-"] = previous_episode
                        if CURRENT_EPISODE_INDEX < len(EPISODES) - 1:
                            controls.append(f"[+] next")
                            KEY_ACTIONS["+"] = next_episode

                        controls.append(f"[c] copy")
                        KEY_ACTIONS["c"] = copy_episode
                        controls.append(f"[y] copy {CLIPBOARD_EPISODE_ATTRIBUTE}")
                        KEY_ACTIONS["y"] = copy_episode_attribute

                        if CLIPBOARD_EPISODE:
                            controls.append(f"[v] paste")
                            KEY_ACTIONS["v"] = paste_episode
                        if CLIPBOARD_EPISODE_ATTRIBUTE:
                            controls.append(f"[b] paste {CLIPBOARD_EPISODE_ATTRIBUTE}")
                            KEY_ACTIONS["b"] = paste_episode_attribute

                    OBJECT_TO_EDIT = EPISODES[CURRENT_EPISODE_INDEX]
                    AVAILABLE_ATTRIBUTES = ATTRIBUTES_EPISODE

        # if there is no object to edit, go back to the other mode
        # we cannot say "not OBJECT_TO_EDIT" because, in the multi select mode, OBJECT_TO_EDIT is a list that can be empty
        if OBJECT_TO_EDIT is None:
            CURRENT_MODE = CURRENT_ATTRIBUTE_MODE
            return
        
        # if necessary, reset the selected value to 0
        if type(AVAILABLE_ATTRIBUTES) == list:
            # if necessary, reset the selected attribute to 0
            if ATTRIBUTE_TO_EDIT not in range(len(AVAILABLE_ATTRIBUTES)):
                ATTRIBUTE_TO_EDIT = 0

            if CURRENT_VALUE not in range(len(ATTRIBUTE_TYPE_VALUES[AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]])):
                CURRENT_VALUE = 0    

        selected_attribute = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
        possible_values = ATTRIBUTE_TYPE_VALUES[selected_attribute]

        # add controls for menu navigation depending on which menu we are in (selecting attributes or values)
        if ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_ATTRIBUTES:
            controls.append(f"[w] previous attribute")
            KEY_ACTIONS["w"] = previous_attribute
            controls.append(f"[s] next attribute")
            KEY_ACTIONS["s"] = next_attribute

            controls.append(f"[a] edit")
            KEY_ACTIONS["a"] = value_menu
            controls.append(f"[x] clear")
            KEY_ACTIONS["x"] = clear_attribute_value

        elif ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_VALUES:            
            controls.append(f"[w] previous value")
            KEY_ACTIONS["w"] = previous_value
            controls.append(f"[s] next value")
            KEY_ACTIONS["s"] = next_value

            controls.append(f"[Home] apply")
            KEY_ACTIONS["KEY_HOME"] = apply_attribute_value

            controls.append(f"[x] clear")
            KEY_ACTIONS["x"] = clear_attribute_value

            controls.append(f"[d] back")
            KEY_ACTIONS["d"] = attribute_menu

        elif ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_INT:
            controls.append(f"[Backspace] delete")
            controls.append(f"[0-9] enter number")

            controls.append(f"[Home] apply")
            KEY_ACTIONS["KEY_HOME"] = apply_attribute_value

            controls.append(f"[x] clear")
            KEY_ACTIONS["x"] = clear_attribute_value
            
            controls.append(f"[d] back")
            KEY_ACTIONS["d"] = attribute_menu
        
        elif ATTRIBUTE_MENU_FOCUS == ATTRIBUTE_MENU_FOCUS_STR:
            controls.append(f"[Backspace] delete")
            controls.append(f"[...] enter text")

            controls.append(f"[Home] apply")
            KEY_ACTIONS["KEY_HOME"] = apply_attribute_value

    elif CURRENT_MODE == MODE_LATEX:
        current_annotation = ANNOTATIONS[CURRENT_LINE_EDIT]

        # As soon as we know the mode, we can display controls
        previous_annotation_exists = CURRENT_LINE_EDIT != 0
        next_annotation_exists = CURRENT_LINE_EDIT != len(ANNOTATIONS) - 1

        if previous_annotation_exists:
            controls.append("[-] up")
            KEY_ACTIONS["-"] = previous_annotation
        if next_annotation_exists:
            controls.append("[+] down")
            KEY_ACTIONS["+"] = next_annotation

        if not LATEX_ANNOTATION_INDEX_FST and not LATEX_ANNOTATION_INDEX_SND:
            KEY_ACTIONS["a"] = set_first_annotation_index
            controls.append("[a] set start")
        elif LATEX_ANNOTATION_INDEX_FST and not LATEX_ANNOTATION_INDEX_SND:
            KEY_ACTIONS["a"] = set_second_annotation_index
            controls.append("[a] set end")
        elif LATEX_ANNOTATION_INDEX_FST and LATEX_ANNOTATION_INDEX_SND:
            KEY_ACTIONS["a"] = set_first_annotation_index
            controls.append("[a] reset start")
            KEY_ACTIONS["KEY_HOME"] = export_latex
            controls.append(f"[Home] export to latex")

    controls.append("[f] save")
    controls.append("[q] quit")

    draw_list_of_controls(height() - 2, controls)

#endregion

#region attributes

def add_to_multi_selection():
    if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
        OBJECT_TO_EDIT.append(UTTERANCES[CURRENT_UTTERANCE_INDEX])
    elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
        OBJECT_TO_EDIT.append(EPISODES[CURRENT_EPISODE_INDEX])

def remove_from_multi_selection():
    if CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
        OBJECT_TO_EDIT.remove(UTTERANCES[CURRENT_UTTERANCE_INDEX])
    elif CURRENT_ATTRIBUTE_MODE == MODE_EPISODE:
        OBJECT_TO_EDIT.remove(EPISODES[CURRENT_EPISODE_INDEX])

def toggle_multiselect():
    global MULTISELECT, OBJECT_TO_EDIT
    MULTISELECT = not MULTISELECT
    OBJECT_TO_EDIT = [] if MULTISELECT else None

def next_attribute():
    global ATTRIBUTE_TO_EDIT
    ATTRIBUTE_TO_EDIT += 1
    if ATTRIBUTE_TO_EDIT > len(AVAILABLE_ATTRIBUTES) - 1:
        ATTRIBUTE_TO_EDIT = 0

def previous_attribute():
    global ATTRIBUTE_TO_EDIT
    ATTRIBUTE_TO_EDIT -= 1
    if ATTRIBUTE_TO_EDIT < 0:
        ATTRIBUTE_TO_EDIT = len(AVAILABLE_ATTRIBUTES) - 1

def next_value():
    global CURRENT_VALUE
    CURRENT_VALUE += 1
    if CURRENT_VALUE > len(ATTRIBUTE_TYPE_VALUES[AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]]) - 1:
        CURRENT_VALUE = 0

def previous_value():
    global CURRENT_VALUE
    CURRENT_VALUE -= 1
    if CURRENT_VALUE < 0:
        CURRENT_VALUE = len(ATTRIBUTE_TYPE_VALUES[AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]]) - 1

def value_menu():
    global ATTRIBUTE_MENU_FOCUS, CURRENT_VALUE, CURRENT_INPUT_BUFFER

    selected_attribute = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
    possible_values = ATTRIBUTE_TYPE_VALUES[selected_attribute]

    if MULTISELECT:
        values = [o[selected_attribute] for o in OBJECT_TO_EDIT]            
        # check if all values are the same
        if len(set(values)) == 1:
            current_attribute_value = values[0]
        else:
            current_attribute_value = None
    else:
        current_attribute_value = OBJECT_TO_EDIT[selected_attribute] 

    if possible_values == INT:
        if current_attribute_value == None:
            CURRENT_INPUT_BUFFER = ""
        else:
            CURRENT_INPUT_BUFFER = str(current_attribute_value)

        ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_INT

    elif possible_values == STR:
        if current_attribute_value == None:
            CURRENT_INPUT_BUFFER = ""
        else:
            CURRENT_INPUT_BUFFER = current_attribute_value

        ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_STR        

    else:
        ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_VALUES

        if current_attribute_value != None:
            CURRENT_VALUE = possible_values.index(current_attribute_value)
        else: 
            CURRENT_VALUE = 0
    
def attribute_menu(): 
    global ATTRIBUTE_MENU_FOCUS, CURRENT_INPUT_BUFFER
    ATTRIBUTE_MENU_FOCUS = ATTRIBUTE_MENU_FOCUS_ATTRIBUTES
    CURRENT_INPUT_BUFFER = ""
    
def clear_attribute_value():
    global CURRENT_INPUT_BUFFER
    selected_attribute = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
    
    if MULTISELECT: 
        for o in OBJECT_TO_EDIT:
            o[selected_attribute] = None
    else:
        OBJECT_TO_EDIT[selected_attribute] = None

    CURRENT_INPUT_BUFFER = ""

    if selected_attribute == ATTRIBUTE_COPILOT_INTERACTION and CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
        # get all episodes that could be affected by a change of the copilot interaction flag
        if MULTISELECT:
            episodes = set()
            for u in OBJECT_TO_EDIT:
                for e in u[DICT_EPISODES]:
                    episodes.add(e)
            episodes = list(episodes)
        else:
            episodes = OBJECT_TO_EDIT[DICT_EPISODES]
        
        # update these episodes
        for episode_id in episodes:
            episode = get_episode(episode_id)
            utterance_ids = episode[DICT_UTTERANCES]
            utterances = list(map(lambda u : get_utterance(u), utterance_ids))
            has_copilot_interaction = reduce(lambda a, b: a or b, list(map(lambda u : True if u[ATTRIBUTE_COPILOT_INTERACTION] == "True" else False, utterances)), False)

            episode[ATTRIBUTE_COPILOT_INTERACTION] = str(has_copilot_interaction)

def apply_attribute_value():
    global STATUS

    selected_attribute = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
    possible_values = ATTRIBUTE_TYPE_VALUES[selected_attribute]

    STATUS = f"Unsaved changes, attribute of {CURRENT_ATTRIBUTE_MODE} modified"

    if possible_values == INT:
        value = None
        if CURRENT_INPUT_BUFFER != "":
            value = int(CURRENT_INPUT_BUFFER)

        if MULTISELECT: 
            for o in OBJECT_TO_EDIT:
                o[selected_attribute] = value
        else:
            OBJECT_TO_EDIT[selected_attribute] = value

        attribute_menu()

    elif possible_values == STR:
        value = None
        if CURRENT_INPUT_BUFFER != "":
            value = CURRENT_INPUT_BUFFER

        if MULTISELECT: 
            for o in OBJECT_TO_EDIT:
                o[selected_attribute] = value
        else:
            OBJECT_TO_EDIT[selected_attribute] = value

        attribute_menu()

    else:
        if MULTISELECT: 
            for o in OBJECT_TO_EDIT:
                o[selected_attribute] = possible_values[CURRENT_VALUE]
        else:
            OBJECT_TO_EDIT[selected_attribute] = possible_values[CURRENT_VALUE]

        if selected_attribute == ATTRIBUTE_COPILOT_INTERACTION and CURRENT_ATTRIBUTE_MODE == MODE_UTTERANCE:
            # get all episodes that could be affected by a change of the copilot interaction flag
            if MULTISELECT:
                episodes = set()
                for u in OBJECT_TO_EDIT:
                    for e in u[DICT_EPISODES]:
                        episodes.add(e)
                episodes = list(episodes)
            else:
                episodes = OBJECT_TO_EDIT[DICT_EPISODES]
            
            # update these episodes
            for episode_id in episodes:
                episode = get_episode(episode_id)
                utterance_ids = episode[DICT_UTTERANCES]
                utterances = list(map(lambda u : get_utterance(u), utterance_ids))
                has_copilot_interaction = reduce(lambda a, b: a or b, list(map(lambda u : True if u[ATTRIBUTE_COPILOT_INTERACTION] == "True" else False, utterances)), False)

                episode[ATTRIBUTE_COPILOT_INTERACTION] = str(has_copilot_interaction)
            
        attribute_menu()

#endregion

#region episodes

def copy_episode():
    global CLIPBOARD_EPISODE, STATUS
    CLIPBOARD_EPISODE = EPISODES[CURRENT_EPISODE_INDEX]
    STATUS = "Unsaved changes, episode copied"

def copy_episode_attribute():
    global STATUS, CLIPBOARD_EPISODE_ATTRIBUTE
    copy_episode()
    CLIPBOARD_EPISODE_ATTRIBUTE = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
    STATUS = "Unsaved changes, episode value copied"

def paste_episode():
    global CLIPBOARD_EPISODE, STATUS

    if MULTISELECT:
        for o in OBJECT_TO_EDIT:
            for attribute in ATTRIBUTES_EPISODE:
                o[attribute] = CLIPBOARD_EPISODE[attribute]
    else:
        for attribute in ATTRIBUTES_EPISODE:
            OBJECT_TO_EDIT[attribute] = CLIPBOARD_EPISODE[attribute]
    STATUS = "Unsaved changes, episode pasted"

def paste_episode_attribute():
    global CLIPBOARD_EPISODE, STATUS
    if MULTISELECT:
        for o in OBJECT_TO_EDIT:
            o[CLIPBOARD_EPISODE_ATTRIBUTE] = CLIPBOARD_EPISODE[CLIPBOARD_EPISODE_ATTRIBUTE]
    else:
        OBJECT_TO_EDIT[CLIPBOARD_EPISODE_ATTRIBUTE] = CLIPBOARD_EPISODE[CLIPBOARD_EPISODE_ATTRIBUTE]
    STATUS = "Unsaved changes, episode value pasted"

def get_episode_depth(utterance_id):
    return len(get_utterance(utterance_id)[DICT_EPISODES])

def sort_episodes():
    global EPISODES
    for episode in EPISODES:
        episode[DICT_UTTERANCES].sort()
    EPISODES.sort(key=lambda e : math.inf if len(e[DICT_UTTERANCES]) == 0 else UTTERANCES.index(get_utterance(e[DICT_UTTERANCES][0])))

def has_empty_episode():
    for episode in EPISODES:
        if len(episode[DICT_UTTERANCES]) == 0:
            return True
    
    return False

def jump_to_episode_first_utterance():
    global CURRENT_LINE_VIEW, CURRENT_LINE_EDIT
    utterance = get_utterance(EPISODES[CURRENT_EPISODE_INDEX][DICT_UTTERANCES][0])
    CURRENT_LINE_VIEW = utterance[DICT_ANNOTATIONS][-1]
    CURRENT_LINE_EDIT = utterance[DICT_ANNOTATIONS][0]

def get_episode(id):
    r = list(filter(lambda u : u[DICT_ID] == id, EPISODES))
    if len(r) == 1:
        return r[0]
    else:
        raise KeyError(f"Not exactly one episode with id {id}")


def new_episode():
    global EPISODES, CURRENT_EPISODE_INDEX, STATUS

    episode = EMPTY_EPISODE()
    if len(EPISODES) == 0:
        episode[DICT_ID] = 0
    else:
        episode[DICT_ID] = max_episode_id() + 1

    EPISODES.append(episode)
    
    sort_utterances()
    CURRENT_EPISODE_INDEX = len(EPISODES) - 1

    STATUS = "Unsaved changes, new episode"
    sort_episodes()


def delete_episode(episode_id):
    global EPISODES, CURRENT_EPISODE_INDEX, STATUS
    episode = get_episode(episode_id)

    for u in episode[DICT_UTTERANCES]:
        get_utterance(u)[DICT_EPISODES].remove(episode_id)

    EPISODES.remove(episode)
    
    sort_episodes()
    
    if len(EPISODES) == 0:
        CURRENT_EPISODE_INDEX = -1
    if CURRENT_EPISODE_INDEX == len(EPISODES):
        CURRENT_EPISODE_INDEX -= 1

    STATUS = "Unsaved changes, episode deleted"


def delete_current_episode():
    delete_episode(EPISODES[CURRENT_EPISODE_INDEX][DICT_ID])


def add_to_episode(utterance_id, episode_id):
    global STATUS, CURRENT_EPISODE_INDEX

    utterance = get_utterance(utterance_id)
    episode = get_episode(episode_id)
    
    utterance[DICT_EPISODES].append(episode[DICT_ID])
    episode[DICT_UTTERANCES].append(utterance[DICT_ID])

    if episode[DICT_DEPTH] == 0:
        episode[DICT_DEPTH] = len(utterance[DICT_EPISODES])

    utterance_ids = episode[DICT_UTTERANCES]
    utterances = list(map(lambda u : get_utterance(u), utterance_ids))
    has_copilot_interaction = reduce(lambda a, b: a or b, list(map(lambda u : True if u[ATTRIBUTE_COPILOT_INTERACTION] == "True" else False, utterances)), False)

    episode[ATTRIBUTE_COPILOT_INTERACTION] = str(has_copilot_interaction)

    STATUS = "Unsaved changes, episode modified"

    sort_episodes()
    CURRENT_EPISODE_INDEX = EPISODES.index(episode)
    
def add_current_to_episode(episode_id):
    add_to_episode(UTTERANCES[CURRENT_UTTERANCE_INDEX][DICT_ID], episode_id)

def add_current_to_current_episode():
    add_current_to_episode(EPISODES[CURRENT_EPISODE_INDEX][DICT_ID])


def remove_utterance_from_episode(episode_id, utterance_id):
    global EPISODES, STATUS, CURRENT_EPISODE_INDEX
    current_episode = get_episode(episode_id)
    current_utterance = get_utterance(utterance_id)

    current_episode[DICT_UTTERANCES].remove(utterance_id)
    current_utterance[DICT_EPISODES].remove(episode_id)

    STATUS = "Unsaved changes, episode modified"

    if len(current_episode[DICT_UTTERANCES]) == 0:
        delete_episode(episode_id)     
        return True

    utterance_ids = current_episode[DICT_UTTERANCES]
    utterances = list(map(lambda u : get_utterance(u), utterance_ids))
    has_copilot_interaction = reduce(lambda a, b: a or b, list(map(lambda u : True if u[ATTRIBUTE_COPILOT_INTERACTION] == "True" else False, utterances)), False)

    current_episode[ATTRIBUTE_COPILOT_INTERACTION] = str(has_copilot_interaction)

    sort_episodes()

    CURRENT_EPISODE_INDEX = EPISODES.index(current_episode)

    return False 

def remove_current_from_episode(episode_id):
    current_episode = get_episode(episode_id)
    if remove_utterance_from_episode(episode_id, UTTERANCES[CURRENT_UTTERANCE_INDEX][DICT_ID]):
        return

    index_to_delete = 1

    current_episode[DICT_UTTERANCES].sort()
    for i in range(1, len(current_episode[DICT_UTTERANCES])):
        predecessor = UTTERANCES.index(get_utterance(current_episode[DICT_UTTERANCES][i - 1]))
        utterance = UTTERANCES.index(get_utterance(current_episode[DICT_UTTERANCES][i]))
        if utterance - predecessor == 1:
            index_to_delete = i + 1
        else:
            break

    for i in range(len(current_episode[DICT_UTTERANCES]) - index_to_delete):
        utterance_id = current_episode[DICT_UTTERANCES][index_to_delete]
        remove_utterance_from_episode(episode_id, utterance_id)

    sort_episodes()
    
def remove_current_from_current_episode():
    global CURRENT_EPISODE_INDEX
    current_episode = EPISODES[CURRENT_EPISODE_INDEX]
    remove_current_from_episode(current_episode[DICT_ID])
    
    if len(EPISODES) > 0:
        current_episode = EPISODES[CURRENT_EPISODE_INDEX]
    else:
        CURRENT_EPISODE_INDEX = -1

def set_current_episode(index, show_at_top = False):
    global CURRENT_EPISODE_INDEX, CURRENT_LINE_EDIT, CURRENT_LINE_VIEW

    if 0 <= index <= len(EPISODES) - 1:
        CURRENT_EPISODE_INDEX = index
    else:
        return

    episode = EPISODES[CURRENT_EPISODE_INDEX]
    utterances = episode[DICT_UTTERANCES]

    if len(utterances) == 0:
        return

    utterance_id = min(utterances)
    annotations = get_utterance(utterance_id)[DICT_ANNOTATIONS]

    if show_at_top:
        CURRENT_LINE_EDIT = annotations[0]
        if annotations[0] not in range(CURRENT_LINE_VIEW_END, CURRENT_LINE_VIEW):
            CURRENT_LINE_VIEW = annotations[0] + len(annotations) + 2
    else:
        CURRENT_LINE_EDIT = annotations[0]
        if annotations[-1] not in range(CURRENT_LINE_VIEW_END, CURRENT_LINE_VIEW):
            CURRENT_LINE_VIEW = annotations[0] + len(annotations) + 2

def next_episode():
    set_current_episode(CURRENT_EPISODE_INDEX + 1)

def previous_episode():
    set_current_episode(CURRENT_EPISODE_INDEX - 1)


#endregion

#region utterances

def fill_with_empty_utterances():
    global UTTERANCES, ANNOTATIONS, CURRENT_LINE_EDIT, STATUS, CURRENT_LINE_VIEW
    count = 0

    old_view = CURRENT_LINE_VIEW
    old_edit = CURRENT_LINE_EDIT

    for i in range(len(ANNOTATIONS)):
        if ANNOTATIONS[i][DICT_UTTERANCE] == -1:
            CURRENT_LINE_EDIT = i
            CURRENT_LINE_VIEW = i
            new_utterance()
            count += 1

    CURRENT_LINE_VIEW = old_view
    CURRENT_LINE_EDIT = old_edit

    if count == 0:
        STATUS = "No new utterances added"
    elif count == 1:
        STATUS = "Added 1 new utterance"
    else:
        STATUS = f"Added {count} new utterances"

def compute_utterance_indices_dict():
    global UTTERANCE_INDICES
    UTTERANCE_INDICES = { UTTERANCES[i][DICT_ID] : i for i in range(len(UTTERANCES))}

def copy_utterance():
    global CLIPBOARD_UTTERANCE, STATUS
    CLIPBOARD_UTTERANCE = UTTERANCES[CURRENT_UTTERANCE_INDEX]
    STATUS = "Unsaved changes, utterance values copied"

def copy_utterance_attribute():
    global STATUS, CLIPBOARD_UTTERANCE_ATTRIBUTE
    copy_utterance()
    CLIPBOARD_UTTERANCE_ATTRIBUTE = AVAILABLE_ATTRIBUTES[ATTRIBUTE_TO_EDIT]
    STATUS = "Unsaved changes, utterance value copied"

def paste_utterance():
    global STATUS
    if MULTISELECT:
        for o in OBJECT_TO_EDIT:
            for attribute in ATTRIBUTES_UTTERANCE:
                o[attribute] = CLIPBOARD_UTTERANCE[attribute]
    else:
        for attribute in ATTRIBUTES_UTTERANCE:
            OBJECT_TO_EDIT[attribute] = CLIPBOARD_UTTERANCE[attribute]
    STATUS = "Unsaved changes, utterance values pasted"

def paste_utterance_attribute():
    global STATUS

    if MULTISELECT:
        for o in OBJECT_TO_EDIT:
            o[CLIPBOARD_UTTERANCE_ATTRIBUTE] = CLIPBOARD_UTTERANCE[CLIPBOARD_UTTERANCE_ATTRIBUTE]
    else:
        OBJECT_TO_EDIT[CLIPBOARD_UTTERANCE_ATTRIBUTE] = CLIPBOARD_UTTERANCE[CLIPBOARD_UTTERANCE_ATTRIBUTE]

    STATUS = "Unsaved changes, utterance value pasted"

def sort_utterances():
    global UTTERANCES
    UTTERANCES.sort(key=lambda u : math.inf if len(u[DICT_ANNOTATIONS]) == 0 else u[DICT_ANNOTATIONS][0])
    compute_utterance_indices_dict()

def jump_to_utterance_annotations():
    global CURRENT_LINE_VIEW, CURRENT_LINE_EDIT
    utterance = get_utterance(CURRENT_UTTERANCE_INDEX)
    CURRENT_LINE_VIEW = utterance[DICT_ANNOTATIONS][-1]
    CURRENT_LINE_EDIT = utterance[DICT_ANNOTATIONS][0]

def new_utterance():
    global UTTERANCES, CURRENT_UTTERANCE_INDEX, STATUS

    utterance = EMPTY_UTTERANCE()
    if len(UTTERANCES) == 0:
        utterance[DICT_ID] = 0
    else:
        utterance[DICT_ID] = max_utterance_id() + 1

    UTTERANCES.append(utterance)
    
    sort_utterances()
    CURRENT_UTTERANCE_INDEX = len(UTTERANCES) - 1

    add_to_utterance()

def delete_utterance(id):
    global UTTERANCES, CURRENT_UTTERANCE_INDEX, STATUS
    utterance = get_utterance(id)

    for a in utterance[DICT_ANNOTATIONS]:
        ANNOTATIONS[a][DICT_UTTERANCE] = -1

    UTTERANCES.remove(utterance)
    
    sort_utterances()
    
    if len(UTTERANCES) == 0:
        CURRENT_UTTERANCE_INDEX = -1
    if CURRENT_UTTERANCE_INDEX == len(UTTERANCES):
        CURRENT_UTTERANCE_INDEX -= 1

    for episode in EPISODES:
        if id in episode[DICT_UTTERANCES]:
            episode[DICT_UTTERANCES].remove(id)

    STATUS = "Unsaved changes, utterance deleted"

def delete_current_utterance():
    delete_utterance(UTTERANCES[CURRENT_UTTERANCE_INDEX][DICT_ID])

def add_to_utterance():
    global CURRENT_UTTERANCE_INDEX, UTTERANCES, STATUS
    if ANNOTATIONS[CURRENT_LINE_EDIT][DICT_UTTERANCE] != -1:
        remove_from_utterance(ANNOTATIONS[CURRENT_LINE_EDIT][DICT_UTTERANCE])

    current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]

    current_utterance[DICT_ANNOTATIONS].append(CURRENT_LINE_EDIT)
    ANNOTATIONS[CURRENT_LINE_EDIT][DICT_UTTERANCE] = current_utterance[DICT_ID]

    sort_utterances()
    CURRENT_UTTERANCE_INDEX = UTTERANCES.index(current_utterance)

    STATUS = "Unsaved changes, utterance modified"

def remove_line_from_utterance(id, line):
    global CURRENT_UTTERANCE_INDEX, UTTERANCES, STATUS
    current_utterance = get_utterance(id)

    current_utterance[DICT_ANNOTATIONS].remove(line)
    ANNOTATIONS[line][DICT_UTTERANCE] = -1
    
    STATUS = "Unsaved changes, utterance modified"

    if len(current_utterance[DICT_ANNOTATIONS]) == 0:
        delete_utterance(id)     
        return True

    return False 

def remove_from_utterance(id):
    current_utterance = get_utterance(id)
    if remove_line_from_utterance(id, CURRENT_LINE_EDIT):
        return

    index_to_delete = 1

    for i in range(1, len(current_utterance[DICT_ANNOTATIONS])):
        predecessor = current_utterance[DICT_ANNOTATIONS][i - 1]
        line = current_utterance[DICT_ANNOTATIONS][i]

        if line - predecessor == 1:
            index_to_delete = i + 1
        else:
            break

    for i in range(len(current_utterance[DICT_ANNOTATIONS]) - index_to_delete):
        line = current_utterance[DICT_ANNOTATIONS][index_to_delete]
        remove_line_from_utterance(id, line)

    sort_utterances()
    
def remove_from_current_utterance():
    global CURRENT_UTTERANCE_INDEX
    current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]
    remove_from_utterance(current_utterance[DICT_ID])
    if len(UTTERANCES) > 0:
        current_utterance = UTTERANCES[CURRENT_UTTERANCE_INDEX]
        CURRENT_UTTERANCE_INDEX = UTTERANCES.index(current_utterance)
    else:
        CURRENT_UTTERANCE_INDEX = -1

def get_utterance(id):
    global UTTERANCE_INDICES
    # r = list(filter(lambda u : u[DICT_ID] == id, UTTERANCES))
    # if len(r) == 1:
    #     return r[0]
    # else:
    #     raise KeyError(f"Not exactly one utterance with id {id}")
    if not UTTERANCE_INDICES:
        compute_utterance_indices_dict()
    if id not in UTTERANCE_INDICES:
        raise KeyError(f"Not exactly one utterance with id {id}")
    return UTTERANCES[UTTERANCE_INDICES[id]]

def has_empty_utterance():
    for utterance in UTTERANCES:
        if len(utterance[DICT_ANNOTATIONS]) == 0:
            return True
    
    return False

def next_utterance():
    global CURRENT_UTTERANCE_INDEX, CURRENT_LINE_EDIT, CURRENT_LINE_VIEW
    CURRENT_UTTERANCE_INDEX += 1

    annotations = UTTERANCES[CURRENT_UTTERANCE_INDEX][DICT_ANNOTATIONS]

    if len(annotations) > 0:
        CURRENT_LINE_EDIT = annotations[0]
        if annotations[-1] not in range(CURRENT_LINE_VIEW_END, CURRENT_LINE_VIEW):
            CURRENT_LINE_VIEW = annotations[-1] + len(annotations)

def previous_utterance():
    global CURRENT_UTTERANCE_INDEX, CURRENT_LINE_EDIT, CURRENT_LINE_VIEW
    CURRENT_UTTERANCE_INDEX -= 1

    annotations = UTTERANCES[CURRENT_UTTERANCE_INDEX][DICT_ANNOTATIONS]

    if len(annotations) > 0:
        CURRENT_LINE_EDIT = annotations[0]
        if annotations[0] not in range(CURRENT_LINE_VIEW_END, CURRENT_LINE_VIEW):
            CURRENT_LINE_VIEW -= len(annotations)

#endregion

#region annotations

def previous_annotation():
    global CURRENT_LINE_EDIT, CURRENT_LINE_VIEW
    CURRENT_LINE_EDIT -= 1
    if CURRENT_LINE_EDIT < CURRENT_LINE_VIEW_END + 2:
        CURRENT_LINE_VIEW -= 1  

def next_annotation(): 
    global CURRENT_LINE_EDIT, CURRENT_LINE_VIEW
    CURRENT_LINE_EDIT += 1
    if CURRENT_LINE_EDIT > CURRENT_LINE_VIEW:
        CURRENT_LINE_VIEW += 1  

#endregion

#endregion

#region latex

def set_first_annotation_index():
    global LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND
    LATEX_ANNOTATION_INDEX_FST = CURRENT_LINE_EDIT
    LATEX_ANNOTATION_INDEX_SND = None

def set_second_annotation_index():
    global LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND
    LATEX_ANNOTATION_INDEX_SND = CURRENT_LINE_EDIT

    min_element = min(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND)
    max_element = max(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND)
    LATEX_ANNOTATION_INDEX_FST = min_element
    LATEX_ANNOTATION_INDEX_SND = max_element

def export_latex():
    global STATUS

    colours = ["blue", "red", "green", "magenta", "cyan", "green"]
    latex = ""

    # first, generate the nodes with the text lines
    n = LATEX_ANNOTATION_INDEX_SND - LATEX_ANNOTATION_INDEX_FST + 1
    latex += "% nodes\n"
    for i in range(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND + 1):
        id = n - (i - LATEX_ANNOTATION_INDEX_FST) - 1

        utterance_id = ANNOTATIONS[i][DICT_UTTERANCE]
        utterance = get_utterance(utterance_id)
        speaker = utterance[ATTRIBUTE_SPEAKER]
        colour = LATEX_COLOUR_SPEAKER_A
        if speaker == ATTRIBUTE_SPEAKER_B:
            colour = LATEX_COLOUR_SPEAKER_B
        elif speaker == ATTRIBUTE_SPEAKER_INSTRUCTOR:
            colour = LATEX_COLOUR_SPEAKER_INSTRUCTOR

        latex += f"\\node[anchor=west, {colour}, font=\sffamily] at (0.15,{id}) {{\\footnotesize {TRANSCRIPT[i][1]}}};\n"

    # then, draw utterance braces
    latex += "\n% utterance braces\n"
    for i in range(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND + 1):
        id = n - (i - LATEX_ANNOTATION_INDEX_FST) - 1
        utterance_id = ANNOTATIONS[i][DICT_UTTERANCE]
        utterance = get_utterance(utterance_id)
        speaker = utterance[ATTRIBUTE_SPEAKER]

        utterance_start = False
        utterance_end = False

        if i == LATEX_ANNOTATION_INDEX_FST or ANNOTATIONS[i - 1][DICT_UTTERANCE] != utterance_id:
            utterance_start = True
        if i == LATEX_ANNOTATION_INDEX_SND or ANNOTATIONS[i + 1][DICT_UTTERANCE] != utterance_id:
            utterance_end = True


        colour = LATEX_COLOUR_SPEAKER_A
        if speaker == ATTRIBUTE_SPEAKER_B:
            colour = LATEX_COLOUR_SPEAKER_B
        elif speaker == ATTRIBUTE_SPEAKER_INSTRUCTOR:
            colour = LATEX_COLOUR_SPEAKER_INSTRUCTOR

        if utterance_start and utterance_end:
            # draw a special symbol
            latex += f"\draw[{colour}, thick] (0,{id}) -- (-0.15,{id});\n"
        elif utterance_start or utterance_end:
            latex += f"\draw[{colour}, thick] (0,{id}) -- (-0.15,{id});\n"

            if not utterance_end:
                latex += f"\\draw[{colour}, thick] (-0.15,{id}) -- (-0.15,{id - 1});\n"

    # at last, draw bars for episodes
    latex += "\n% episode markings\n"

    for episode in EPISODES:
        utterance_ids = episode[DICT_UTTERANCES]
        utterances = list(map(lambda u : get_utterance(u), utterance_ids))

        # get the first and last annotation of the episode
        annotations = []
        for utterance in utterances:
            annotations += utterance[DICT_ANNOTATIONS]
        annotations.sort()

        annotations_inside = [a for a in annotations if LATEX_ANNOTATION_INDEX_FST <= a <= LATEX_ANNOTATION_INDEX_SND]

        if len(annotations_inside) == 0:
            continue

        episode_start = n - (annotations_inside[0] - LATEX_ANNOTATION_INDEX_FST) - 1
        episode_end = n - (annotations_inside[-1] - LATEX_ANNOTATION_INDEX_FST) - 1
        depth = utterances[0][DICT_EPISODES].index(episode[DICT_ID])

        episode_start_inside = annotations[0] in range(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND + 1)
        episode_end_inside = annotations[-1] in range(LATEX_ANNOTATION_INDEX_FST, LATEX_ANNOTATION_INDEX_SND + 1)

        d = -1.5 + depth * 0.17
        start_str = f"({d + (0.2 if episode_start_inside else 0):.2f},{episode_start - (0.17 if episode_start_inside else 0):.2f})"
        end_str = f"({d + (0.2 if episode_end_inside else 0):.2f},{episode_end + (0.17 if episode_end_inside else 0):.2f})"

        latex += f"\\draw[line width=5, color={colours[depth]}]\n"
        latex += f"{start_str} --\n"
        latex += f"({d:.2f},{episode_start - 0.3:.2f}) --\n"
        latex += f"({d:.2f},{episode_end + 0.3:.2f}) --\n"
        latex +=  f"{end_str};\n"

        if episode_start_inside:
            if episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_ASSIMILATION:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {end_str} {{\\footnotesize \\faCheck}};\n"
            elif (episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_TRUST_FAIL or
                  episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_TRUST_SUCCESS):
                latex += f"\\node[anchor=west, color={colours[depth]}] at {end_str} {{\\footnotesize \\faCircleO}};\n"
            elif (episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_UNNECESSARY or
                  episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_GAVE_UP or
                  episode[ATTRIBUTE_FINISH_TYPE] == ATTRIBUTE_FINISH_TYPE_LOST_SIGHT):
                latex += f"\\node[anchor=west, color={colours[depth]}] at {end_str}{{\\footnotesize \\faTimes}};\n"

        if episode_end_inside:
            if episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_TOOL:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faWrench}};\n"
            elif episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_PROGRAM:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faLaptop}};\n"
            elif episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_BUG:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faBug}};\n"
            elif episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_CODE:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faCode}};\n"
            elif episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_DOMAIN:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faPaperclip}};\n"
            elif episode[ATTRIBUTE_TOPIC] == ATTRIBUTE_TOPIC_TECHNIQUE:
                latex += f"\\node[anchor=west, color={colours[depth]}] at {start_str} {{\\footnotesize \\faComments}};\n"

    latex = f"""
%\\documentclass{{article}}
%\\usepackage{{tikz}}
%\\usepackage{{fontawesome}}
%\\usepackage{{contour}}
%\\begin{{document}}
    \\begin{{tikzpicture}}[x=1cm,y=0.5cm]
{latex}
    \\end{{tikzpicture}}
%\\end{{document}}
"""

    filename = f"{TRANSCRIPT_PATH.replace('.txt', f'_{LATEX_ANNOTATION_INDEX_FST}-{LATEX_ANNOTATION_INDEX_SND}.tex')}".replace("final", "exports")
    STATUS = f"Exported to '{filename}'"
    with open(filename, "w") as f:
        f.write(latex)

#endregion

#region management

def quit():
    current_selected = 0   

    while True:
        stdscr.clear()
        stdscr.addstr(1, 1, f"EDIT   {TRANSCRIPT_PATH}")
        stdscr.addstr(height() - 6, 1, f" What do you want to do?")
        if current_selected == 0:
            stdscr.addstr(height() - 4, 2, f" back ", curses.color_pair(2) + curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6, f" save and quit ", curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6 + 15, f" quit without saving ", curses.A_REVERSE)
        elif current_selected == 1:
            stdscr.addstr(height() - 4, 2, f" back ", curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6, f" save and quit ", curses.color_pair(2) + curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6 + 15, f" quit without saving ", curses.A_REVERSE)
        elif current_selected == 2:
            stdscr.addstr(height() - 4, 2, f" back ", curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6, f" save and quit ", curses.A_REVERSE)
            stdscr.addstr(height() - 4, 2 + 6 + 15, f" quit without saving ", curses.color_pair(1) + curses.A_REVERSE)

        controls = [f"[{KEY_LEFT}] previous", f"[{KEY_RIGHT}] next", f"[Home] select"]
        controls = " │ ".join(controls)
        stdscr.addstr(height() - 2, width() - len(controls) - 1, controls)

        key = stdscr.getkey()

        if key == "KEY_LEFT":
            current_selected -= 1
            if current_selected < 0:
                current_selected = 2
        elif key == "KEY_RIGHT":
            current_selected += 1
            if current_selected > 2:
                current_selected = 0
        elif key == "KEY_HOME":
            if current_selected == 0:
                return
            elif current_selected == 1:
                save()
                exit(0)
            elif current_selected == 2:
                exit()
        
def edit_mode():
    global TRANSCRIPT_PATH, DATA_FILE_PATH, stdscr

    while True:
        stdscr.clear()
        stdscr.addstr(1, width() - len(STATUS) - 2, STATUS)
        stdscr.addstr(1, 1, f"EDIT   {TRANSCRIPT_PATH.split('/')[-1]}")

        edit_entry()
        draw_view()    
        draw_mode_controls()

        stdscr.refresh()
        
        action(stdscr.getkey())

def init_edit_mode():
    global stdscr

    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(True)
    stdscr.clear()

    for i in range(0, 28):
        colour = ALL_COLOURS[COLOURS[i]]
        curses.init_color(i, *colour) 

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(COLOUR_MENU, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOUR_MENU_SELECTED, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(COLOUR_MENU_DISABLED, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOUR_MENU_SELECTED_DISABLED, curses.COLOR_WHITE, 30)
    curses.init_pair(COLOUR_EPISODE_SELECTED, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_EPISODE_SELECTED_MULTISELECT, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_EPISODE_MULTISELECT, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_RED, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(COLOUR_INSTRUCTOR, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

def parse(fill_values_if_none = False):
    global TRANSCRIPT, TRANSCRIPT_PATH, DATA_FILE_PATH, ANNOTATIONS, UTTERANCES, EPISODES, CURRENT_UTTERANCE_INDEX, CURRENT_EPISODE_INDEX

    with open(TRANSCRIPT_PATH, "r") as f:
        transcript = f.readlines()
    
    for i in range(len(transcript)):
        line = transcript[i].replace("\n", "")
        # if is_timestamp(line) and i + 1 < len(transcript):
        #     next_line = transcript[i + 1].replace("\n", "")
        #     TRANSCRIPT.append((line, next_line))
        
        # Whisper does not provide timestamps
        TRANSCRIPT.append(("", line))

    if os.path.exists(DATA_FILE_PATH):
        info(f"Found annotated data.")
        with open(DATA_FILE_PATH, "r") as f:
            d = json.load(f)
            ANNOTATIONS = d[DICT_ANNOTATIONS]
            UTTERANCES = d[DICT_UTTERANCES]
            EPISODES = d[DICT_EPISODES]

        for utterance in UTTERANCES:
            for attribute in ATTRIBUTES_UTTERANCE:
                if attribute not in utterance.keys():
                    utterance[attribute] = None
            if fill_values_if_none:
                fill_attributes = [ATTRIBUTE_SPEAKER, ATTRIBUTE_SCOPE_CHANGE, ATTRIBUTE_COPILOT_INTERACTION, ATTRIBUTE_HASTED_REPLY, ATTRIBUTE_REPETITIVE, ATTRIBUTE_UNCERTAIN, ATTRIBUTE_TERMINATION_ATTEMPT, ATTRIBUTE_MEDIUM]
                for attribute in fill_attributes:
                    if utterance[attribute] == None:
                        utterance[attribute] = ATTRIBUTE_TYPE_VALUES[attribute][ATTRIBUTE_DEFAULT_VALUES[attribute]]

        for episode in EPISODES:
            for attribute in ATTRIBUTES_EPISODE:
                if attribute not in episode.keys():
                    episode[attribute] = None
    else:
        info(f"Did not find any annotated data.")
        ANNOTATIONS = [{DICT_UTTERANCE : -1} for _ in range(len(TRANSCRIPT))]

    if len(UTTERANCES) > 0:
        CURRENT_UTTERANCE_INDEX = 0
    if len(EPISODES) > 0:
        CURRENT_EPISODE_INDEX = 0

def read():
    global TRANSCRIPT, TRANSCRIPT_PATH, DATA_FILE_PATH

    parse(True)

    init_edit_mode()
    edit_mode()

def end_edit_mode():
    global stdscr
    try:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.curs_set(True)
        curses.endwin()
    except:
        pass

def save():
    global STATUS
    with open(DATA_FILE_PATH, "w") as f:
        d = {DICT_EPISODES : EPISODES, DICT_UTTERANCES : UTTERANCES, DICT_ANNOTATIONS : ANNOTATIONS}
        f.write(json.dumps(d, indent=4))

    STATUS = f"Saved at {datetime.now().strftime('%d.%m.%y, %H:%M:%S')}"

#endregion

@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def main(path):   
    global TRANSCRIPT_PATH, DATA_FILE_PATH, stdscr
    TRANSCRIPT_PATH = path
    DATA_FILE_PATH = get_json_name_from_transcript(path)

    read()


if __name__ == '__main__':   
    try: 
        main()
    finally:
        end_edit_mode()

   