# Kaiko
Kaiko is a deep learning-based *de novo* peptide sequencing tool. The codebase is based on [DeepNovo](https://github.com/nh2tran/DeepNovo).

## Data format
Kaiko uses .mgf file format as in the DeepNovo codebase. DeepNovo allows a single mgf file for a training, whereas Kaiko can use the multiple mgf files for a training run. It allows Kaiko scalable to train more than 1 million spectra. Please refer to [tool/mgf_for_kaiko.ipynb](tool/mgf_for_kaiko.ipynb) to convert mzML files to mgf files compatible with Kaiko. Unlike the typical mgf format, the known sequence for each spectrum should be placed in mgf files as like `SEQ=[Peptide Sequence]`. It also allows the pickle format. For this, see [tool/mgf2binary/mgf2pickle.ipynb](tool/mgf2binary/mgf2pickle.ipynb).

## How to Use
### For training
```
python kaiko_main.py --mgf_dir $mgf_dir --train_dir $train_dir --multi_train --learning_rate 0.0001 --epoch_stop 100 --lastindex $lastindex --data_format mgf
```

| Parameter       |  Description|
| ------------- | ------------- |
| --multi_train | please use this option when you have training datasets with many mgf files. |
| --mgf_dir | a directory of target mgf files. `mgf_list.log` should be in the folder, which contains a list of mgf filenames in a column `mgf_file`. |
| --train_dir | a directory for output models |
| --learning_rate | a learning rate |
| --epoch_stop | a number of epochs |
| --lastindex | a last index of the mgf files in `mgf_list.log` to use in training |
| --data_format | a data format (pickle or mgf) |

### For testing
```
python kaiko_main.py --mgf_dir $mgf_dir --train_dir $train_dir --multi_decode --beam_search --beam_size 5
```
| Parameter       |  Description|
| ------------- | ------------- |
| --multi_decode | please use this option when you have many mgf files for test datasets. |
| --mgf_dir | a directory of target mgf files. |
| --train_dir | a directory for a pre-trained model to use in testing |
| --beam_search | use the beam search for decoding |
| --beam_size | a size for the beam search |
| --topk | use if you want to save the top k in beam search for each spectrum |

### For hyper-parameter optimization
We use the [SigOpt](https://sigopt.com/) to optimize the hyperparameters. Note that to train Kaiko for more than 1M spectra, it takes so much time. Also, note that optimal hyper-parameters for a small subset are likely not to fit for a large training set. To use this you need to sign in sigopt and set up an experiment. For more details, please refer to (this APIs)[https://app.sigopt.com/docs/overview/python].
```
python kaiko_main.py --mgf_dir $mgf_dir --train_dir $train_dir --sigopt --api_token $api_token --experiment_id $experiment_id --epoch_stop $epoch_stop
```
| Parameter       |  Description|
| ------------- | ------------- |
| --sigopt | use this option when you do search hyperparameters. |
| --mgf_dir | a directory of target mgf files. |
| --train_dir | a directory to store best models |
| --api_token | the api token for your sigopt account |
| --experiment_id | the experiment id for your experiment |
| --epoch_stop | a number of epochs for each trial |

