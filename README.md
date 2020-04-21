You need to install :

```
pip3 install tensorboardX ray
```

# Commands to try

```
python3 src/main.py -env_config env1.json -model_config base_model.json -out_dir base_experiment
```
*Works as expected* 

```
python3 src/main.py -env_config env2.json -model_config base_model.json -out_dir base_experiment
```
*Doesn't work as expected*
Because env2 has the same name as env1, 
the integrity checker tells you something is wrong

```
python3 src/main.py -env_config env1.json -model_config base_model.json -out_dir base_experiment -model_ext lr_1e6.json
```
*Works as expected*

```
python3 src/main.py -env_config env1.json -model_config base_model.json -out_dir base_experiment -model_ext bad_lr.json
```
*Doesn't work as expected*
The extension file is ill-defined as it doesn't respect the structure of the original model

=============================================
```
python3 src/main.py -env_config env1.json -model_config base_model.json
```
*Works as expected* 

```
python3 src/main.py -env_config env2.json -model_config base_model.json
```
*Works as expected* because we are using storing experiements in default_out, 
which should be used ONLY for dev test ! 
if you don't want this default behavior, you can edit config.py

===============================================

```
python3 src/multiple_run.py -multiple_run_config all_base.json -n_gpus 0 -out_dir all_base -n_seed 4
```

then

```
tensorboard --logdir=. 
```

TADA
