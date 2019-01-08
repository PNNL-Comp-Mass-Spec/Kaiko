# Kaiko
Kaiko is a deep learning-based *de novo* peptide sequencing tool. The codebase is based on [DeepNovo](https://github.com/nh2tran/DeepNovo).

## Installation and Requirements
Kaiko is a deep learning program, and as such requires significant computational resources to train. Computational infrastructures for GPU-based deep learning are often very different from each other. In our [publication](https://www.biorxiv.org/content/early/2018/09/27/428334) describing Kaiko, we use a super computer that is able to remotely execute python scripts and Jupyter notebooks on the GPU cluster.

To install Kaiko for training purposes, clone this GitHub repository and ensure that you have the software packages and versions (Python: 2.7, TensorFlow: 1.2).

Running the pre-trained version of Kaiko to annotate MS/MS spectra does not require a GPU based computer. Install Kaiko by cloning this GitHub repository and ensure that you have the software packages and versions (Python: 2.7, TensorFlow: 1.2).

## Data format
Kaiko uses .mgf file format as in the DeepNovo codebase. DeepNovo allows a single mgf file for a training, whereas Kaiko can use the multiple mgf files for a training run. It allows Kaiko scalable to train more than 1 million spectra. Please refer to [tool/mgf_for_kaiko.ipynb](tool/mgf_for_kaiko.ipynb) to convert mzML files to mgf files compatible with Kaiko. Unlike the typical mgf format, the known sequence for each spectrum should be placed in mgf files as like `SEQ=[Peptide Sequence]`. It also allows the pickle format. For this, see [tool/mgf2binary/mgf2pickle.ipynb](tool/mgf2binary/mgf2pickle.ipynb).

## How to Use
Kaiko can be run in two modes. The first mode is called training where the goal is to develop a new neural network model for annotating spectra. It takes a very long time to train a large neural network with the requisite training data. If you use the GPU node configuration mentioned in our paper and the small 300K training set, we anticipate that it will take 1 hour per epoch. If you were to train on the large dataset of 5M spectra, we anticipate that it will take 12 hours per epoch. The final model in our paper was trained for 60 epochs, and therefore took about one month of a GPU node for training. Hyper-parameter optimization of this large model takes dramatically more time as it performs full training rounds on a sweep of parameters.

The second mode of use for Kaiko is testing where the goal is to evaluate a model on unseen data. This is the mode that most end-users will access to annotate their spectra. This mode is much faster. Although we typically run it on our GPU cluster, it does not require such resources.

### Demo dataset

We have included in the repository a single test_query.mgf file which includes a single MS/MS spectrum for testing. For a more comprehensive testing, there are 300K peptide-spectrum pairs in 18 mgf files for 5 different species. To download this extended set, execute the following script:

```
cd mgf_input
sh ./get_test_mgf.sh
```

Also, set the `--lastindex` as 17 and edit the following line in src/deepnovo_debug.py as below.

```
valid_index = [16, 17]
```

### Pre-trained Model

To acquire the pre-trained model and knapsack data, execute the script:

```
cd model
sh ./get_data.sh
```

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

### Inference on your own data

To run inference on your own data, put mgf files in the $mgf_dir. For the SEQ field, enter UNKNOWN (e.g. SEQ=UNKNOWN). This will produce inference output in the $decode_path (default is ./decode_path) where there is
one corresponding output file per input file in $mgf_dir. For example, if there is an input file called test_query.mgf in the mgf_dir, then the output file will be test_query_out.txt.


This is an example command:

```
python kaiko_main.py --mgf_dir $mgf_dir --train_dir $train_dir --multi_decode --decode_path $decode_path --beam_search --beam_size 5
```

The output inference txt file will be a tab separated file with headers. The columns that matter are:

1. scan - represents the value you put into the SCANS= field in the MGF input file
2. output_score - output de novo score
3. output_seq - de novo sequence for the MS/MS spectrum


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

### For Testing with Docker

We have additionally wrapped kaiko to run within docker. Docker currently only supports inference and not training. To build the docker:

```
sh ./build_docker.sh
```

To run the docker

```
sh ./run_docker.sh
```

This will drop you into a command line within the docker image. We mount in mgf_input, model, and the source code. To perform inference on the input data (that is in mgf_input), execute

```
sh ./test_docker.sh
```

## License
[BSD License](LICENSE.txt).
