import os
import sys
from src import configurations as config
from src.drifts.drift_complex import add_recurring_drift, add_incremental_drift
from src.drifts.drift_simple import add_simple_drift
from src.data_classes.class_drift import DriftInfo
from src.data_classes.class_noise import NoiseInfo
from src.data_classes.class_collection import Collection
from src.controllers.process_tree_controller import generate_tree_from_file, generate_specific_trees
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from src.data_classes.class_input import get_parameters
import time
from pm4py.objects.process_tree import semantics
from src.noise_controller_new import insert_noise
from src.utilities import select_random, InfoTypes, DriftTypes, add_duration_to_log, add_unique_trace_ids

from src.data_classes.class_input import InputParameters

def generate_logs(par:InputParameters, file_path_to_own_models=None):
    """
    Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files
    :param par(InputParameters): is a class storing the parameter used to generate the logs
    :param file_path_to_own_models(str): file path to own process model, if desired to be used
    :return: collection of event logs with drifts saved in out_folder
    """

    # CREATE DIR TO STORE GENERATED LOGS
    out_folder = creat_output_folder(config.DEFAULT_OUTPUT_DIR, par.Folder_name)
    # MAIN LOOP
    number_of_logs = select_random(par.Number_event_logs)
    print('Generating', number_of_logs, 'logs in', out_folder)
    collection = Collection()
    for log_id in range(1, number_of_logs + 1):
        try:
            # SELECT PARAMETERS FOR THE CURRENT LOG
            log_name = "log_" + str(log_id) + '_' + str(int(time.time())) + ".xes"
            tree_initial = generate_initial_tree(par.Process_tree_complexity, file_path_to_own_models)
            num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
            event_log = semantics.generate_log(tree_initial, num_traces)
            drift_n = select_random(par.Number_drifts_per_log, option='uniform_int')
            for drift_id in range(1, drift_n + 1):
                # Set drift info instance
                # TODO: integrate
                drift_instance = DriftInfo()
                drift_instance.set_log_id(log_name)
                drift_instance.set_drift_id(drift_id)
                drift_instance.set_process_perspective('control-flow')
                drift_type = select_random(par.Drift_types, option='random')
                drift_instance.set_drift_type(drift_type)
                drift_instance.add_process_tree(tree_initial)
                # GENERATE LOG WITH A CERTAIN DRIFT TYPE
                if drift_type == DriftTypes.sudden.value:
                    event_log, drift_instance = add_simple_drift(event_log, drift_instance, par, drift_type)
                elif drift_type == DriftTypes.gradual.value:
                    event_log, drift_instance = add_simple_drift(event_log, drift_instance, par, drift_type)
                elif drift_type == DriftTypes.recurring.value:
                    event_log, drift_instance = add_recurring_drift(event_log, drift_instance, par)
                elif drift_type == DriftTypes.incremental.value:
                    event_log, drift_instance = add_incremental_drift(event_log, drift_instance, par)
                else:
                    UserWarning(f'Specified "drift_type" {drift_type} in the parameter file does not exist')

                collection.add_drift(drift_instance)


            # ADD TIME PERSPECTIVE TO EVENT LOG
            add_duration_to_log(event_log, par)
            # ADD UNIQUE TRACE IDs
            add_unique_trace_ids(event_log)

            # ADD NOISE and CREATE NOISE INFO INSTANCE
            # TODO: integrate the noise related lines below
            noise = select_random(par.Noise, option='random')
            if noise:
                noisy_trace_prob = select_random(par.Noisy_trace_prob, option='uniform_step')
                noisy_event_prob = select_random(par.Noisy_event_prob, option='uniform_step')
                noise_instance = NoiseInfo(log_name, noisy_trace_prob, noisy_event_prob)
                event_log = insert_noise(event_log, noise_instance.noisy_trace_prob, noise_instance.noisy_event_prob, par.Task_exp_duration_sec)
                collection.add_noise(noise_instance)
                event_log.attributes[InfoTypes.noise_info.value] = noise_instance.noise_info_to_dict()

            collection.convert_change_trace_index_into_timestamp(event_log, log_name)
            event_log = collection.add_drift_info_to_log(event_log, log_name)

            # EXPORT GENERATED LOG
            xes_exporter.apply(event_log, os.path.join(out_folder, log_name))

        except:
            print(f"There is an error in {log_name}!!!")
            continue

    collection.export_drift_and_noise_info_to_flat_file_csv(path=out_folder)
    print('Finished generating collection of', number_of_logs, 'logs in', out_folder)


def generate_initial_tree(complexity_options_list: list, file_path_to_own_models:str)->dict:
    """
    #TODO: write what this function does
    :param complexity_options_list:
    :param file_path_to_own_models:
    :return:
    """
    complexity = select_random(complexity_options_list, option='random')
    if file_path_to_own_models is None:
        generated_process_tree = generate_specific_trees(complexity)
    else:
        generated_process_tree = generate_tree_from_file(file_path_to_own_models)
    return generated_process_tree


def creat_output_folder(path: str = config.DEFAULT_OUTPUT_DIR, folder_name: str = config.PARAMETER_NAME):
    out_folder = os.path.join(path, folder_name + '_' + str(int(time.time())))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    return out_folder


def main(par):
    if len(sys.argv) == 1:
        generate_logs(par)
    elif len(sys.argv) == 2:
        generate_logs(par, sys.argv[1])



if __name__ == '__main__':
    par = get_parameters(config.PARAMETER_NAME)
    # n_noise = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # n_drifts = [1, 2, 3, 4, 5]
    #multiple_collection_generator(par, n_drifts=n_drifts, n_noise=n_noise)
    #multiple_collection_generator(par)
    main(par)
    #experiments_multiple_collection_generator(par, complexities=['middle', 'complex'])
    sys.exit()

