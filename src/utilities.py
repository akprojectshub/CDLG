import datetime
import random
from enum import Enum
from random import uniform, randint
from datetime import timedelta, datetime
import src.configurations as config
import numpy
from pm4py.util.xes_constants import DEFAULT_TRANSITION_KEY
import re
from src.data_classes.class_input import get_parameters


def select_random(data: list, option: str = 'random') -> any:
    if len(data) == 1:
        data_selected = data[0]
    elif len(data) == 2 and option == 'uniform':
        data_selected = uniform(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_int':
        data_selected = randint(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_step':
        data_selected = round(uniform(data[0], data[1]), 1)
    elif option == 'random':
        data_selected = random.choice(data)
    else:
        data_selected = None
        Warning(f"Check function 'select_random' call: {data, option, data_selected}")

    if isinstance(data, float):
        data_selected = round(data_selected, 2)

    return data_selected


class InfoTypes(Enum):
    drift_info = "drift:info"
    noise_info = "noise:info"


class DriftTypes(Enum):
    sudden = 'sudden'
    gradual = 'gradual'
    recurring = 'recurring'
    incremental = 'incremental'


class ChangeTypes(Enum):
    sudden = 'sudden'
    gradual = 'gradual'


class TraceAttributes(Enum):
    concept_name = "concept:name"
    timestamp = "time:timestamp"
    model_version = "model_version:id"


def add_duration_to_log(log, par=None):

    if par is None:
        par = get_parameters(config.PARAMETER_NAME)

    log_start_timestamp_list = [datetime.strptime(v, '%Y/%m/%d %H:%M:%S') for v in config.FIRST_TIMESTAMP.split(',')]
    log_start_timestamp = select_random(log_start_timestamp_list, option='random')
    trace_exp_arrival_sec = select_random(par.Trace_exp_arrival_sec, option='uniform_int')
    task_exp_duration_sec = select_random(par.Task_exp_duration_sec, option='uniform_int')

    # Main loop over all traces and events
    for index_trace, trace in enumerate(log):
        if len(trace) > 0:
            if index_trace == 0:
                # First trace
                for index_event, event in enumerate(trace):
                    if index_event == 0:
                        # Define the timestamp of the first trace and first event
                        log[index_trace][index_event][TraceAttributes.timestamp.value] = log_start_timestamp
                    else:
                        # Define the timestamp of all other events in the first
                        task_duration = numpy.random.exponential(task_exp_duration_sec)
                        value = trace[index_event - 1][TraceAttributes.timestamp.value]
                        event[TraceAttributes.timestamp.value] = value + timedelta(seconds=task_duration)
            else:
                # All other traces
                for index_event, event in enumerate(trace):
                    if index_event == 0:
                        # The timestamp of the first event depends on the start timestamp of the previous trace + exp. timedelta
                        trace_arrival = numpy.random.exponential(trace_exp_arrival_sec)
                        value = log[index_trace - 1][index_event][TraceAttributes.timestamp.value]
                        event[TraceAttributes.timestamp.value] = value + timedelta(seconds=trace_arrival)
                    else:
                        # The timestamp of the next event depends on the previous timestamp + exp. timedelta
                        task_duration = numpy.random.exponential(task_exp_duration_sec)
                        value = trace[index_event - 1][TraceAttributes.timestamp.value]
                        event[TraceAttributes.timestamp.value] = value + timedelta(seconds=task_duration)
                        # print(f"Event log length: {len(log)}")
                        # print(log)
                        # print(f"Trace: {trace}, trace length: {len(trace)}")
                        # print(f"Index: {index_event}, and event: {event}")
                        # ValueError("Error")

    add_event_lifecycle(log)

    return None


def add_event_lifecycle(log):
    for trace in log:
        for event in trace:
            event[DEFAULT_TRANSITION_KEY] = 'complete'
    return None


def add_unique_trace_ids(log):
    trace_id = 1
    for trace in log:
        trace.attributes[TraceAttributes.concept_name.value] = str(trace_id)
        trace_id += 1
    return None


def extract_list_from_string(string_of_list: str):
    return [int(int_val_str) for int_val_str in re.findall(r'\d+', string_of_list)]


def remove_duplicates(strings:list):
    seen = set()
    result = []
    for string in strings:
        if string not in seen:
            seen.add(string)
            result.append(string)
    return result

class Log_attr_params():
    drift_info = "drift:info"
    children = "children"
    change_info = "change_info"
    change_type = "change_type"
    process_tree_before = "process_tree_before"
    process_tree_after = "process_tree_after"
    activities_deleted = "activities_deleted"
    activities_added = "activities_added"
    activities_moved = "activities_moved"
    drift_type = "drift_type"
    process_perspective = "process_perspective"
    change_trace_index = "change_trace_index"


