import json
import os

from copy import deepcopy
from random import shuffle, randint

DEFAULT_OUT = "default_out"

EXPE_DEFAULT_CONFIG = {
    "model_ext": '',
    "seed": 42,
    "out_dir": DEFAULT_OUT,
    "local_test" : False
}

def override_config_recurs(config, config_extension):
    for key, value in config_extension.items():
        if type(value) is dict:
            config[key] = override_config_recurs(config[key], config_extension[key])
        else:
            assert key in config, "Warning, key defined in extension but not original : new key is {}".format(key)

            # Don't override names, change add name extension to the original
            if key == "name":
                config["name"] = config["name"] + "_" + value
            else:
                config[key] = value

    return config

def load_single_config(config_path):
    return json.load(open(config_path, "r"))

def check_json_intregrity(config_file_path, config_dict):

    config_file = open(config_file_path, 'r')

    content = config_file.read()
    if content:
        config_dict_loaded = json.loads(content)
    else:
        return

    # if config_dict_loaded != config_dict:
    #     print("Warning, config on disk and specified by params are different")
    assert config_dict_loaded == config_dict, \
        """
        Error in config file handling, config_file on disk and this one must be the same !"
        config_dict :        {}
        ========
        config_dict_loaded : {}

        """.format(config_dict, config_dict_loaded)


def load_config(env_config_file, model_config_file, seed,
                out_dir,
                env_ext_file=None,
                model_ext_file=None
                ):
    """
    Everything is centered around config file and extension
    The basic file create a json
    The extension overrides few parameters

    Security checklist :
    - If you create an extend a model, checking that the overriden parameters exist in original model,
         because it usually indicate a fail in the extension fail (bad naming or wrong place in the hierarchy)
    - If you create an expe with the same environment name => Check that the new env == old one
    - If you create an expe with the same model name (+ ext) => Check that the new model == old one

    :param env_config_file: json name, don't need to specify full path, the function looks in     config/env
    :param model_config_file: json name, don't need to specify full path, the function looks in   config/model
    :param seed: you have to select a random seed
    :param out_dir: Where you environment and subdirectory will be located
    :param model_ext_file: json name, don't need to specify full path, the function looks in   config/model_ext
    :return: full_config, path_to_expe
                                       full_config_contains model (overriden if ext) and env
                                       path_to_expe is the full path to your experiement
                                               The structure is :      out_dir/env_name/model+ext_name/seed/
    """
    # === Loading Env config, extension and check integrity =====
    # ===========================================================
    if type(env_config_file) is str:
        env_config = load_single_config(os.path.join("config", "env", env_config_file))
    else:
        assert type(env_config_file) is dict, \
            "Can be dict or str, but not something else, is {}\n{}".format(type(env_config_file), env_config_file)
        env_config = env_config_file

    # Override env file if specified
    if env_ext_file:
        env_ext_config = load_single_config(os.path.join("config", "env_ext", env_ext_file))
        env_config = override_config_recurs(env_config, env_ext_config)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # create env_file if necessary
    env_name = env_config["name"]
    env_path = os.path.join(out_dir, env_name)

    if not os.path.exists(env_path):
        os.mkdir(env_path)

    env_config_path = os.path.join(env_path, "env_config.json")
    if not os.path.exists(env_config_path):
        config_file = open(env_config_path, 'w')
        json.dump(obj=env_config, fp=config_file, indent='    ', separators=(',',':'))
    else:
        # default_out is the test setting, to avoid integrity checking and manually deleting
        if DEFAULT_OUT not in env_path:
            check_json_intregrity(config_file_path=env_config_path,
                                  config_dict=env_config)

    # === Loading MODEL config, extension and check integrity =====
    # ===========================================================
    if type(model_config_file) is str:
        model_config = load_single_config(os.path.join("config", "model", model_config_file))
    else:
        assert type(model_config_file) is dict, "Problem, should be dict is {}\n{}".format(type(model_config_file),
                                                                                           model_config_file)
        model_config = model_config_file

    # Override model file if specified
    # Can be a dict of parameters or a str indicating the path to the extension
    if model_ext_file:
        if type(model_ext_file) is str:
            model_ext_config = load_single_config(os.path.join("config", "model_ext", model_ext_file))
        else:
            assert type(model_ext_file) is dict, "Not a dict problem, type : {}".format(type(model_ext_file))
            model_ext_config = model_ext_file

        model_config = override_config_recurs(model_config, model_ext_config)
    else:
        model_ext_config = {"name": ''}

    # create model_file if necessary
    model_name = model_config["name"]
    model_path = os.path.join(env_path, model_name)

    if not os.path.exists(model_path):
        os.mkdir(model_path)

    model_config_path = os.path.join(model_path, "model_full_config.json")
    if not os.path.exists(model_config_path):
        config_file = open(model_config_path, 'w')
        json.dump(obj=model_config, fp=config_file, indent='    ', separators=(',',':'))

        # Dump the extension file too, easier to visualize quickly
        model_ext_config_path = os.path.join(model_path, "model_ext_config.json")
        model_ext_config_file = open(model_ext_config_path, 'w')
        json.dump(obj=model_ext_config, fp=model_ext_config_file, indent='    ', separators=(',',':'))

    else:
        # Ignore DEFAULT_OUT directory, just for testing, no need to check json everytime
        if DEFAULT_OUT not in model_path:
            check_json_intregrity(config_file_path=model_config_path,
                                  config_dict=model_config)

    # Merge env and model config into one dict
    full_config = {**model_config, **env_config}
    full_config["model_name"] = model_config["name"]
    full_config["env_name"] = env_config["name"]
    del full_config["name"]

    # set seed
    full_config["seed"] = seed
    set_seed(seed)
    path_to_expe = os.path.join(model_path, str(seed))

    if not os.path.exists(path_to_expe):
        os.mkdir(path_to_expe)

    print(full_config["model_name"])
    print(full_config["env_name"])
    return full_config, path_to_expe


def read_multiple_config_file(config_path):
    json_config = json.load(open(os.path.join("config/multiple_run_config", config_path), "r"))
    assert type(json_config) == list, "Should be a list"

    all_expe_to_run = []

    for config in json_config:
        expe_config = deepcopy(EXPE_DEFAULT_CONFIG)
        expe_config.update(config)
        all_expe_to_run.append(expe_config)

    return all_expe_to_run

def extend_multiple_seed(all_expe_to_run, number_of_seed=2):
    extended_expe_list = []
    for expe in all_expe_to_run:
        for n_seed in range(number_of_seed):
            new_expe = deepcopy(expe)
            new_expe["seed"] = n_seed
            extended_expe_list.append(new_expe)

    return extended_expe_list

# =====================
# OTHER RANDOM FUNCTION
# =====================
def set_seed(seed):
    import torch
    import random
    import numpy as np

    if seed >= 0:
        print('Using seed {}'.format(seed))
        np.random.seed(seed)
        torch.manual_seed(seed)
        random.seed(seed)
    else:
        raise NotImplementedError("Cannot set negative seed")