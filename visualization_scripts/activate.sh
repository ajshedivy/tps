#!/usr/bin/env/bash

#conda init bash
echo "----------------------------starting script----------------------------"
eval "$(conda shell.bash hook)"
conda activate py2cyto_env

#echo "check enviornment"
if [ $? -ne 0 ]; then
	echo "-creating py2cyto environment"
	conda env create -f minimal_env.yml
	conda activate py2cyto_env
fi
echo "-environment activated"


python run.py $1 $2
echo "-end script"
