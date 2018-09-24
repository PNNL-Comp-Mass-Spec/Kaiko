#!/bin/bash
#SBATCH -A deepscience
#SBATCH -N 1
#SBATCH -p fat
#SBATCH --gres=gpu:1
#SBATCH -t 4-0
#SBATCH --mail-type=end
#SBATCH --mail-user joonyong.lee@pnnl.gov
#SBATCH -o kaiko/logs/pnnl3_235_v4_cp_00001_6.out
#SBATCH -e kaiko/logs/pnnl3_235_v4_cp_00001_6.err
#SBATCH --job-name="pnnl3_235_v4_cp_00001_6"

module purge
module load gcc/4.8.5
module load cuda/8.0.61

source activate deepnovo

mgf_dir="/scratch/leej324/${SLURM_JOBID}"
echo $mgf_dir

if [[ -d $mgf_dir ]]; then 
    echo "the directory already exists."
else
    echo "the directory does not exist."
    mkdir -p $mgf_dir
fi

# cp -Rp /pic/scratch/kaiko/kaiko_mgf3 $mgf_dir
# mgf_dir="/scratch/leej324/${SLURM_JOBID}/kaiko_mgf3/"
cp -Rp /pic/scratch/kaiko/cpickle $mgf_dir
mgf_dir="/scratch/leej324/${SLURM_JOBID}/cpickle/"

api_token="ORPEZZOXIWKLKQOHLJQFSUUWCPYTPLMNGKKTDKPFWCKZRGQL"
experiment_id=45068
epoch_stop=3
lastindex=234

# python /people/leej324/kaiko/kaiko_main.py --mgf_dir $mgf_dir --train_dir /pic/scratch/kaiko/pnnl3.model_sigopt --sigopt --api_token $api_token --experiment_id $experiment_id --epoch_stop $epoch_stop
python /people/leej324/kaiko/kaiko_main.py --mgf_dir $mgf_dir --train_dir /pic/scratch/kaiko/pnnl3.model_235_v4_cp_0001 --multi_train --learning_rate 0.00001 --epoch_stop 100 --lastindex $lastindex --data_format pickle

