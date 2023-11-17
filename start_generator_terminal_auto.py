import sys
import random
import wexpect


def initial_config(log_setting):
    # Start the program and provide initial log information
    cmd_path, command, log_config = log_setting

    child = wexpect.spawn(cmd_path, ['/c', command])
    for config in log_config:
        child.expect(" ")
        child.sendline(config)
    print("Log initialized")

    return child


def drift_settings_selection(settings):
    drift_setting = {}
    drift_number_max, drift_types, drift_starts, drift_gradual_durations, drift_gradual_after, drift_sudden_lengths, drift_severities = settings
    drift_setting['drift_type'] = random.choice(drift_types)
    drift_setting['drift_start'] = str(round(random.uniform(drift_starts[0], drift_starts[1]), 2))
    drift_setting['drift_gradual_duration'] = str(round(random.randint(drift_gradual_durations[0], drift_gradual_durations[-1]), -1))
    drift_setting['drift_gradual_after'] = str(round(random.randint(drift_gradual_after[0], drift_gradual_after[-1]), -1))
    drift_setting['drift_sudden_length'] = str(round(random.randint(drift_sudden_lengths[0], drift_sudden_lengths[-1]), -1))
    drift_setting['drift_severity'] = str(round(random.uniform(drift_severities[0], drift_severities[1]), 2))

    return drift_setting


def add_first_drift(child, drift_setting):
    if drift_setting['drift_type'] == 'sudden':
        child, configs = first_sudden_drift(child, drift_setting)
    elif drift_setting['drift_type'] == 'gradual':
        child, configs = first_gradual_drift(child, drift_setting)
    else:
        print(f"First drift type {drift_setting['drift_start']} is not allowed. Sudden type is used ")
        child, configs = first_sudden_drift(child, drift_setting)
    return child, configs


def first_sudden_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               drift_setting['drift_sudden_length'],
               drift_setting['drift_start'],
               'random',
               drift_setting['drift_severity']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def first_gradual_drift(child, drift_setting):
    start = round(float(drift_setting['drift_start']), 2)
    gradual_drift_min_length = 0.1
    drift_end = round(start + random.uniform(gradual_drift_min_length, 1-start-gradual_drift_min_length), 2)
    configs = [drift_setting['drift_type'],
               drift_setting['drift_sudden_length'],
               drift_setting['drift_start'],
               str(drift_end),
               'linear',
               'random',
               drift_setting['drift_severity']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_gradual_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               'evolved_version',
               'random',
               drift_setting['drift_severity'],
               'end',
               drift_setting['drift_gradual_duration'],
               drift_setting['drift_gradual_after'],
               'linear']
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_sudden_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               'evolved_version',
               'random',
               drift_setting['drift_severity'],
               'end',
               drift_setting['drift_sudden_length']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_drift(child, drift_setting):
    drift_type = drift_setting['drift_type']

    if drift_type == 'sudden':
        child, configs = add_sudden_drift(child, drift_setting)
    elif drift_type == 'gradual':
        child, configs = add_gradual_drift(child, drift_setting)
    else:
        print(f"Drift type {drift_type} is not allowed. Sudden type is used ")
        child, configs = add_sudden_drift(child, drift_setting)

    return child, configs


def drift_closing_decision(child, drift_number, drift_number_max):
    if drift_number == drift_number_max:
        child.expect("[yes, no]?")
        child.sendline('no')
    else:
        child.expect("[yes, no]?")
        child.sendline('yes')

    return child


def noise_setting_selection(noise_settings):

    noise_setting = {}
    noise, noise_type, noise_starts, noise_ends, noise_proportions, noise_severities = noise_settings
    noise_setting['noise'] = noise
    noise_setting['noise_type'] = noise_type
    noise_start = round(random.uniform(noise_starts[0], noise_starts[1]), 2)
    noise_setting['noise_start'] =str(noise_start)
    noise_setting['noise_end'] =str( round(noise_start + random.uniform(0.1, 1-noise_start-0.1), 2))
    noise_setting['noise_proportion'] =str(round(random.uniform(noise_proportions[0],noise_proportions[-1]), 1))
    noise_setting['noise_severity'] = str(round(random.uniform(noise_severities[0],noise_severities[-1]), 1))

    return noise_setting


def add_noise(child, noise_setting):
    print(f"Noise: {noise_setting['noise']}")
    if noise_setting['noise'] == "yes":
        child.expect("[yes, no]?")
        child.sendline('yes')
        configs = [noise_setting['noise_type'],
                   noise_setting['noise_start'],
                   noise_setting['noise_end'],
                   noise_setting['noise_proportion'],
                   noise_setting['noise_severity']]
        for config in configs:
            child.expect(" ")
            child.sendline(config)
    else:
        child.expect("[yes, no]?")
        child.sendline('no')

    return child


def main():

    drift_setting_dict = {}
    child = initial_config(LOG_SETTING)


    drift_number_max = random.randint(drift_numbers[0], drift_numbers[-1])
    for drift_number in range(1, drift_number_max + 1):
        drift_setting = drift_settings_selection(SETTINGS)
        if drift_number == 1:
            child, configs = add_first_drift(child, drift_setting)
        else:
            child, configs = add_drift(child, drift_setting)
        drift_setting_dict[str(drift_number)] = configs
        print(f"Drift {drift_number} added: {drift_setting['drift_type']}")
        child = drift_closing_decision(child, drift_number, drift_number_max)

    noise_setting = noise_setting_selection(NOISE_SETTINGS)
    drift_setting_dict['noise_setting'] = noise_setting
    child = add_noise(child, noise_setting)

    child.expect(wexpect.EOF)
    console = child.before
    #discprint(console)
    log_name = console[-31:]
    #child.terminate()

    #print(console)
    #child.kill()

    config_dict = {log_name[2:-2]: drift_setting_dict}
    return config_dict


if __name__ == "__main__":
    number_of_logs = 55

    cmd_path = 'C:\windows\system32\cmd.exe'
    command = 'python start_generator_terminal.py'
    log_config = ['random', 'one_model', 'no', 'complex']
    LOG_SETTING = [cmd_path, command, log_config]

    drift_numbers = [4, 5]
    drift_types = ['sudden', 'gradual']
    drift_starts = [0.2, 0.8]
    drift_gradual_durations = [100, 1000]
    drift_gradual_after = [500, 2000]
    drift_sudden_lengths = [1000, 2000]
    drift_severities = [0.2, 0.8]
    SETTINGS = [drift_numbers,
                drift_types,
                drift_starts,
                drift_gradual_durations,
                drift_gradual_after,
                drift_sudden_lengths,
                drift_severities]

    noise = 'no'
    noise_type = 'changed_model'
    noise_starts = [0.1, 0.9]
    noise_ends = [0.1, 0.9]
    noise_proportions = [0.1, 0.5]
    noise_severities = [0.1, 0.5]
    NOISE_SETTINGS = [noise, noise_type, noise_starts, noise_ends, noise_proportions, noise_severities]

    USED_PARAMETERS = {}
    for i in range(1, number_of_logs+1):
        print(f"Start of log generation: {i} out of {number_of_logs}")
        USED_PARAMETERS |= main()
        print(f"End of log generation: {i}", "\n")


    sys.exit()



# import wexpect
#
#
# def initial_config(cmd_path, command, log_config):
#     # Start the program and provide initial log information
#     child = wexpect.spawn(cmd_path, ['/c', command])
#     for config in log_config:
#         child.expect(" ")
#         child.sendline(config)
#     print("Log initialized with ", log_config)
#
#     return child
#
#
# def main():
#     child = initial_config(cmd_path, command, log_config)
#
#     print("drift 1")
#     child.expect(" ")
#     child.sendline('sudden')
#     child.expect(" ")
#     child.sendline('2000')
#     child.expect(" ")
#     child.sendline('0.5')
#     child.expect(" ")
#     child.sendline('random')
#     child.expect(" ")
#     child.sendline('0.3')
#
#     child.expect("[yes, no]?")
#     child.sendline('yes')
#
#     print("drift 2")
#     child.expect(" ")
#     child.sendline('gradual')
#     child.expect(" ")
#     child.sendline('evolved_version')
#     child.expect(" ")
#     child.sendline('random')
#     child.expect(" ")
#     child.sendline('0.5')
#     child.expect("[end, into]?")
#     child.sendline('end')
#     child.expect(" ")
#     child.sendline('500')
#     child.expect(" ")
#     child.sendline('1000')
#     child.expect(" ")
#     child.sendline('linear')
#
#     child.expect("[yes, no]?")
#     child.sendline('yes')
#
#     print("drift 3")
#     child.expect(" ")
#     child.sendline('sudden')
#     child.expect(" ")
#     child.sendline('evolved_version')
#     child.expect(" ")
#     child.sendline('random')
#     child.expect(" ")
#     child.sendline('0.3')
#     child.expect("[end, into]?")
#     child.sendline('end')
#     child.expect(" ")
#     child.sendline('2000')
#
#     child.expect("[yes, no]?")
#     child.sendline('yes')
#
#     print("drift 4")
#     child.expect(" ")
#     child.sendline('gradual')
#     child.expect(" ")
#     child.sendline('evolved_version')
#     child.expect(" ")
#     child.sendline('random')
#     child.expect(" ")
#     child.sendline('0.5')
#     child.expect("[end, into]?")
#     child.sendline('end')
#     child.expect(" ")
#     child.sendline('500')
#     child.expect(" ")
#     child.sendline('1000')
#     child.expect(" ")
#     child.sendline('linear')
#
#     child.expect("[yes, no]?")
#     child.sendline('yes')
#
#     print("drift 5")
#     child.expect(" ")
#     child.sendline('sudden')
#     child.expect(" ")
#     child.sendline('evolved_version')
#     child.expect(" ")
#     child.sendline('random')
#     child.expect(" ")
#     child.sendline('0.3')
#     child.expect("[end, into]?")
#     child.sendline('end')
#     child.expect(" ")
#     child.sendline('2000')
#
#     child.expect("[yes, no]?")
#     child.sendline('no')
#
#     child.expect("[yes, no]?")
#     child.sendline('no')
#
#     child.expect(wexpect.EOF)
#     print(child.before)
#
#
# if __name__ == "__main__":
#     cmd_path = 'C:\windows\system32\cmd.exe'
#     command = 'python start_generator_terminal.py'
#     log_config = ['random', 'one_model', 'no', 'middle']
#
#     drift_number_max = 5
#     drift_types = ['sudden', 'gradual']
#     drift_starts = [0.2, 0.8]
#     drift_gradual_durations = [100, 1000]
#     drift_gradual_after = [500, 2000]
#     drift_sudden_lengths = [1000, 2000]
#
#     SETTINGS = [drift_number_max,
#                 drift_types,
#                 drift_starts,
#                 drift_gradual_durations,
#                 drift_gradual_after,
#                 drift_sudden_lengths]
#
#     main()



# print('progress 0')
#
# child.expect("Import models or use randomly generated models [import, random]: ")
# child.sendline('random')
# child.expect("Evolution of one randomly generated model or use of two randomly generated models [one_model, two_models]:")
# child.sendline('one_model')
# child.expect("Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]?")
# child.sendline('no')
# child.expect("Complexity of the process tree to be generated [simple, middle, complex]:")
# child.sendline('middle')
#
# print('progress 1')
# child.expect("Type of concept drift [sudden, gradual, recurring, incremental]:")
# child.sendline('sudden')
# child.expect("Number of traces in the event log (x >= 100):")
# child.sendline('2000')
# child.expect("Starting point of the drift (0 < x < 1):")
# child.sendline('0.5')
# child.expect("Controlled or random evolution of the process tree version [controlled, random]:")
# child.sendline('random')
# child.expect("Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):")
# child.sendline('0.3')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
# child.sendline('yes')
#
# print('progress 2')
#
# child.expect("Type of 2. concept drift in the event log [sudden, gradual, recurring, incremental]:")
# child.sendline('gradual')
# child.expect("Process model version for the evolution of the additional gradual drift [initial_version, evolved_version]:")
# child.sendline('revolved_version')
# child.expect("Controlled or random evolution of the process tree version [controlled, random]:")
# child.sendline('random')
# child.expect("Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):")
# child.sendline('0.5')
# child.expect("Adding the additional gradual drift at the end of the log or into the log [end, into]?")
# child.sendline('end')
# child.expect("Number of additional traces of the gradual drift to be added at the end of the event log (int):")
# child.sendline('500')
# child.expect("Number of additional traces of the new model to be added after the drift occurred (int):")
# child.sendline('1000')
# child.expect("Method for distributing the traces during the gradual drift [linear, exponential]:")
# child.sendline('linear')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
# child.sendline('yes')
#
# print('progress 3')
#
#
# child.expect("Type of 3. concept drift in the event log [sudden, gradual, recurring, incremental]:")
# child.sendline('sudden')
# child.expect("Process model version for the evolution of the additional sudden drift [initial_version, evolved_version]:")
# child.sendline('evolved_version')
# child.expect("Controlled or random evolution of the process tree version [controlled, random]:")
# child.sendline('random')
# child.expect("Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):")
# child.sendline('0.3')
# child.expect("Adding the additional sudden drift at the end of the log or into the log [end, into]?")
# child.sendline('end')
# child.expect("Number of additional traces from the new model to be added at the end of the event log (int):")
# child.sendline('500')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
# child.sendline('yes')
#
# print('progress 4')
# child.expect("Type of 4. concept drift in the event log [sudden, gradual, recurring, incremental]:")
# child.sendline('gradual')
# child.expect("Process model version for the evolution of the additional gradual drift [initial_version, evolved_version]:")
# child.sendline('revolved_version')
# child.expect("Controlled or random evolution of the process tree version [controlled, random]:")
# child.sendline('random')
# child.expect("Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):")
# child.sendline('0.5')
# child.expect("Adding the additional gradual drift at the end of the log or into the log [end, into]?")
# child.sendline('end')
# child.expect("Number of additional traces of the gradual drift to be added at the end of the event log (int):")
# child.sendline('500')
# child.expect("Number of additional traces of the new model to be added after the drift occurred (int):")
# child.sendline('1000')
# child.expect("Method for distributing the traces during the gradual drift [linear, exponential]:")
# child.sendline('linear')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
# child.sendline('yes')
#
# print('progress 5')
# child.expect("Type of 5. concept drift in the event log [sudden, gradual, recurring, incremental]:")
# child.sendline('sudden')
# child.expect("Process model version for the evolution of the additional sudden drift [initial_version, evolved_version]:")
# child.sendline('evolved_version')
# child.expect("Controlled or random evolution of the process tree version [controlled, random]:")
# child.sendline('random')
# child.expect("Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):")
# child.sendline('0.3')
# child.expect("Adding the additional sudden drift at the end of the log or into the log [end, into]?")
# child.sendline('end')
# child.expect("Number of additional traces from the new model to be added at the end of the event log (int):")
# child.sendline('500')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
# child.sendline('no')
# child.expect("Do you want to add an additional drift to the event log [yes, no]?")
#
# child.expect("Do you want to add noise to the event log [yes, no]?")
# child.sendline('no')
#
# print('done')
#
#
# # Import models or use randomly generated models [import, random]:
# random
# # Evolution of one randomly generated model or use of two randomly generated models [one_model, two_models]:
# one_model
# # Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]?
# no
# # Complexity of the process tree to be generated [simple, middle, complex]:
# middle
#
# # Type of concept drift [sudden, gradual, recurring, incremental]:
# sudden
# # Number of traces in the event log (x >= 100):
# 2000
# # Starting point of the drift (0 < x < 1):
# 0.5
# # Controlled or random evolution of the process tree version [controlled, random]:
# random
# # Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):
# 0.3
#
# # Do you want to add an additional drift to the event log [yes, no]?
# yes
#
# # Type of 2. concept drift in the event log [sudden, gradual, recurring, incremental]:
# gradual
# # Process model version for the evolution of the additional gradual drift [initial_version, evolved_version]:
# evolved_version
# # Controlled or random evolution of the process tree version [controlled, random]:
# random
# # Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):
# 0.5
# # Adding the additional gradual drift at the end of the log or into the log [end, into]?
# end
# # Number of additional traces of the gradual drift to be added at the end of the event log (int):
# 500
# # Number of additional traces of the new model to be added after the drift occurred (int):
# 1000
# # Method for distributing the traces during the gradual drift [linear, exponential]:
# linear
# # Do you want to add an additional drift to the event log [yes, no]?
# yes
#
# # Type of 3. concept drift in the event log [sudden, gradual, recurring, incremental]:
# sudden
# # Process model version for the evolution of the additional sudden drift [initial_version, evolved_version]:
# evolved_version
# # Controlled or random evolution of the process tree version [controlled, random]:
# random
# # Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):
# 0.3
# # Adding the additional sudden drift at the end of the log or into the log [end, into]?
# end
# # Number of additional traces from the new model to be added at the end of the event log (int):
# 500
# # Do you want to add an additional drift to the event log [yes, no]?
# yes
#
# # Type of 4. concept drift in the event log [sudden, gradual, recurring, incremental]:
# gradual
# # Process model version for the evolution of the additional gradual drift [initial_version, evolved_version]:
# evolved_version
# # Controlled or random evolution of the process tree version [controlled, random]:
# random
# # Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):
# 0.5
# # Adding the additional gradual drift at the end of the log or into the log [end, into]?
# end
# # Number of additional traces of the gradual drift to be added at the end of the event log (int):
# 5000
# # Number of additional traces of the new model to be added after the drift occurred (int):
# 500
# # Method for distributing the traces during the gradual drift [linear, exponential]:
# linear
# # Do you want to add an additional drift to the event log [yes, no]?
# yes
#
# # Type of 5. concept drift in the event log [sudden, gradual, recurring, incremental]:
# sudden
# # Process model version for the evolution of the additional sudden drift [initial_version, evolved_version]:
# evolved_version
# # Controlled or random evolution of the process tree version [controlled, random]:
# random
# # Proportion of the activities in the process tree to be affected by random evolution (0 < x < 1):
# 0.3
# # Adding the additional sudden drift at the end of the log or into the log [end, into]?
# end
# # Number of additional traces from the new model to be added at the end of the event log (int):
# 500
# # Do you want to add an additional drift to the event log [yes, no]?
# no
#
# # Do you want to add noise to the event log [yes, no]?
# no