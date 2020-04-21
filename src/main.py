from logging_helper import SweetLogger
from config import load_config

import ray
import random

@ray.remote(num_gpus=0)
def start_experiment(model_config, env_config, out_dir, seed, model_ext, local_test):

    # =================== CONFIGURATION==================
    # ===================================================
    full_config, expe_path = load_config(model_config_file=model_config,
                                         model_ext_file=model_ext,
                                         env_config_file=env_config,
                                         out_dir=out_dir,
                                         seed=seed)
    if local_test:
        # Override GPU context, switch to CPU on local machine
        device = 'cpu' # I'm poor i don't own a gpu

    # =================== LOGGING =======================
    # ===================================================

    # SweetLogger is a tensorboardXWriter with additionnal tool to help dealing with lists

    # dump_step_every is usually located in the model, but where ever suits you
    # It indicates how frequently you want to log you tensboardX, see SweetLogger for more details
    tf_logger = SweetLogger(dump_step=full_config["dump_log_every"], path_to_log=expe_path)

    # =================== DEFINE ENVIRONMENT ===================
    # ==========================================================
    max_iter = full_config["n_env_iter"]


    # =================== DEFINE MODEL ========================
    # =========================================================
    basic_learning_rate = full_config["algo_params"]["learning_rate"]


    # =================== TRAIN HERE ==========================
    # =========================================================

    print("Starting learning")
    for current_iter in range(max_iter):

        done = False
        n_iteration_this_episode = 0

        while not done:
            reward = random.random()
            n_iteration_this_episode += 1

            tf_logger.log("train/reward", reward, operation=['mean', 'max', 'min'])
            tf_logger.log("train/lr", basic_learning_rate)

            # You have to do this at every step, most of the time, it doesn't do anything but it's dealt within SweetLogger
            tf_logger.dump(current_iter)

            if reward > 0.9:
                done = True
                basic_learning_rate *= 0.9999

    print("End of learning")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser('Log Parser arguments!')

    parser.add_argument("-env_config", type=str)
    parser.add_argument("-model_config", type=str)
    parser.add_argument("-model_ext", type=str)
    parser.add_argument("-out_dir", type=str, default="default_out", help="Directory all results")
    parser.add_argument("-seed", type=int, default=42, help="Random seed used")
    parser.add_argument("-local_test", type=bool, default=False, help="If env is run on my PC or a headless server")

    args = parser.parse_args()


    start_experiment._function(env_config=args.env_config,
                               model_config=args.model_config,
                               model_ext=args.model_ext,
                               out_dir=args.out_dir,
                               seed=args.seed,
                               local_test=args.local_test
                               )