import os

from src.log_generators.event_logs_one_model import generate_logs_with_model
#from src.log_generators import generate_logs_with_models
from src.controllers.input_controller import input_start, input_parameters, generate_tree_out_of_file, input_comp, \
    input_start_second, input_no_yes
from src.controllers.process_tree_controller import generate_tree, generate_specific_trees
import time
from src import configurations as config

def main():
    out_folder = config.DEFAULT_OUTPUT_DIR + '/terminal_logs'
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    out_file = os.path.join(out_folder, 'log_' + str(int(time.time())) + '.xes')
    print("--- GENERAL INPUT ---")
    print('The tool offers different paths to generate event logs with drifts.\n'
          '\t - import models: one or two own models can be imported,\n '
          '\t   whereby the BPMN models and Petri nets need to be block-structured.\n'
          '\t - randomly generated models: one or two process trees can be generated randomly.\n'
          'When using one model, it can evolve randomly or in a controlled manner.\n'
          'When using two models, the second model is/should be the already evolved version of the first model.\n'
          'Several event logs can be generated with one run of the application, and the parameters can be changed for each event log.\n\n'
          'Press ENTER for an interaction to set a default value.\n'
          'Press CTRL+C to interrupt the tool\'s execution.\n'
          )

    two_one_rand = input_start(
        'Import models or use randomly generated models [import, random]: ')
    if two_one_rand == 'import':
        imp = input_start_second(
            "Evolution of one imported model or use of two imported models [one_model, two_models]: ")
        if imp == 'one_model':
            tree_one = generate_tree_out_of_file(
                "File path of the model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'data/example_models/bpmn/model_00.bpmn'): ")
            generate_logs_with_model(tree_one, out_file)
        elif imp == 'two_models':
            tree_one = generate_tree_out_of_file(
                "File path of the first model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'data/example_models/bpmn/model_00.bpmn'): ")
            tree_two = generate_tree_out_of_file(
                "File path of the second model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'data/example_models/bpmn/model_01.bpmn'): ")
            generate_logs_with_models(tree_one, tree_two, False, out_file)
    elif two_one_rand == 'random':
        imp = input_start_second(
            "Evolution of one randomly generated model or use of two randomly generated models [one_model, two_models]: ")
        if imp == 'one_model':
            default = input_no_yes(
                "Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]? ")
            if default == 'yes':
                parameters = input_parameters()
                tree_ran = generate_tree(parameters)
            else:
                str_clp = input_comp(
                    "Complexity of the process tree to be generated [simple, middle, complex]: ")
                tree_ran = generate_specific_trees(str_clp)
            generate_logs_with_model(tree_ran, out_file)
        elif imp == 'two_models':
            default = input_no_yes(
                "Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]? ")
            parameters = {}
            if default == 'yes':
                parameters = input_parameters()
                tree_ran_one = generate_tree(parameters)
                tree_ran_two = generate_tree(parameters)
            else:
                str_clp = input_comp("Complexity of the process trees to be generated [simple, middle, complex]: ")
                tree_ran_one = generate_specific_trees(str_clp)
                tree_ran_two = generate_specific_trees(str_clp)
            generate_logs_with_models(tree_ran_one, tree_ran_two, True, out_file, parameters)


if __name__ == '__main__':
    main()
