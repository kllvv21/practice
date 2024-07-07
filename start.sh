#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate myenv
python main.py.py
read -p "Press any key to continue..."