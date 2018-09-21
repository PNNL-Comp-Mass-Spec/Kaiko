#!/bin/bash
#SBATCH -A deepscience
#SBATCH -N 1
#SBATCH -p dl
#SBATCH --gres=gpu:1
#SBATCH -t 4-0
#SBATCH --mail-type=end
#SBATCH --mail-user joonyong.lee@pnnl.gov
#SBATCH -o DeepNovo_pnnl3/logs/test_kaiko.out
#SBATCH -e DeepNovo_pnnl3/logs/test_kaiko.err
#SBATCH --job-name="test_kaiko"

module purge
module load gcc/4.8.5
module load cuda/8.0.61

source activate deepnovo

# mgf_dir="/pic/scratch/kaiko/"
mgf_dir="/scratch/leej324/${SLURM_JOBID}"
echo $mgf_dir

if [[ -d $mgf_dir ]]; then 
    echo "the directory already exists."
else
    echo "the directory does not exist."
    mkdir -p $mgf_dir
fi

cp -Rp /pic/scratch/kaiko/test_sets $mgf_dir
mgf_dir="/scratch/leej324/${SLURM_JOBID}/test_sets/"

# cp -Rp /pic/scratch/kaiko/deepnovo_mgf3 $mgf_dir
# mgf_dir="/scratch/leej324/${SLURM_JOBID}/deepnovo_mgf3/"

# cp -Rp /pic/scratch/kaiko/Unknown_Biodiversity $mgf_dir
# mgf_dir="/scratch/leej324/${SLURM_JOBID}/Unknown_Biodiversity/"

# cp -Rp /pic/scratch/kaiko/blinded_organisms $mgf_dir
# mgf_dir="/scratch/leej324/${SLURM_JOBID}/blinded_organisms/"

python /people/leej324/DeepNovo_pnnl3/deepnovo_main.py --mgf_dir $mgf_dir --train_dir /pic/scratch/kaiko/pnnl3.model_235_v4_cp_0001 --multi_decode --beam_search --beam_size 5
