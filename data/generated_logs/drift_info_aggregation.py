import os
from pm4py.objects.log.importer.xes import importer as xes_importer
import sys
import pandas as pd
import re


def load_event_log_names():
    list_of_files = {}
    absolute_path = os.path.dirname(__file__)

    for dir_path, dir_names, filenames in os.walk(absolute_path):
        for filename in filenames:
            if filename.endswith('.xes') and filename[:len('terminal_log_')] == 'terminal_log_':
                list_of_files[filename] = os.sep.join([dir_path])

    if not list_of_files:
        raise ValueError("Event logs genereated via a terminal mode are not found")

    return list_of_files


def load_event_log(file_path, file_name):
    # Save the log name to a global variable
    event_log = None
    if file_name.endswith('.xes'):
        variant = xes_importer.Variants.ITERPARSE
        parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
        event_log = xes_importer.apply(os.path.join(file_path, file_name), variant=variant, parameters=parameters)
    else:
        raise ValueError("Issue with loading an event log")

    return event_log


def save_dict_to_csv(all_logs_drift_info):
    flat_file = []
    for key, value in all_logs_drift_info.items():
        for key2, value2 in value.items():
            for key3, value3 in value2.items():
                row = [key, key2[:-1], key3, value3]
                flat_file.append(row)

    flat_file_df = pd.DataFrame(flat_file, columns=['log', 'drift', 'attribute', 'value'])
    flat_file_df.to_csv('drift_info_flat_file.csv', index=False)

    return flat_file_df


def main(file_path, file_name, max_number_of_drifts):

    log = load_event_log(file_path, file_name)
    log_drifts = {}

    for i in range(1, max_number_of_drifts):
        try:
            log_drift_id = f'drift info {i}:'
            drift_info = log.attributes[log_drift_id]
            drift_info_dict = {}
            drift_info = drift_info.replace("; ", ";")
            for row in drift_info.split(';'):
                infos = row.split(': ', 1)
                if infos[1].find("(") == -1:
                    drift_info_dict[infos[0]] = infos[1]
                else:
                    drift_info_dict[infos[0]] = re.sub("[\(\[].*?[\)\]]", "", infos[1])[:-1]

            log_drifts[log_drift_id] = drift_info_dict
        except:
            break

    return log_drifts


def transform_flat_file(all_logs_drift_info_df):

    output = []
    temp = all_logs_drift_info_df.loc[all_logs_drift_info_df.attribute == 'drift type'].copy()
    del temp["attribute"]
    temp.rename(columns={'value': 'drift_type'}, inplace=True)
    all_logs_drift_info_df_ext = pd.merge(all_logs_drift_info_df, temp, on=['log', 'drift'], how='left', )

    for index, row in all_logs_drift_info_df_ext.iterrows():
        if row.drift_type == "gradual" and row.attribute == "drift start timestamp":
            values = [row.log, row.value, "gradual_start"]
            output.append(values)
        elif row.drift_type == "gradual" and row.attribute == "drift end timestamp":
            values = [row.log, row.value, "gradual_end"]
            output.append(values)
        elif row.drift_type == "sudden" and row.attribute == "drift start timestamp":
            values = [row.log, row.value, "sudden"]
            output.append(values)
        else:
            pass

    output_df = pd.DataFrame(output, columns=['log_name', 'change_moment', 'Note'])
    output_df.to_csv('drift_info_aggregated.csv', index=False)

    return None


if __name__ == "__main__":
    max_number_of_drifts = 5

    all_logs_drift_info = {}
    list_of_event_logs = load_event_log_names()
    for file_name, file_path in list_of_event_logs.items():
        print("\n", '=' * 80, "\n", f"Log in progress: '{file_name}'")
        all_logs_drift_info[file_name] = main(file_path, file_name, max_number_of_drifts)


    all_logs_drift_info_df = save_dict_to_csv(all_logs_drift_info)
    transform_flat_file(all_logs_drift_info_df)

    sys.exit()
