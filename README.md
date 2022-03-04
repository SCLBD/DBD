# DBD
This a Pytorch implementation of our paper "[Backdoor Defense via Decoupling the Training
Process](https://openreview.net/pdf?id=TySnJ-0RdKI)".

**Table of Contents:**
- [DBD](#dbd)
  - [Setup](#setup)
    - [Environments](#environments)
    - [Datasets](#datasets)
    - [Log and checkpoint directories](#log-and-checkpoint-directories)
  - [Usage](#usage)
    - [No Defense](#no-defense)
    - [DBD](#dbd-1)
  - [Pretrained Models](#pretrained-models)
    - [Test](#test)
    - [Results](#results)
- [License](#license)
- [Citation](#citation)

## Setup
### Environments
We recommend conda as the package manager to setup the environment used in our experiments. Create
the environment `dbd` from the [environment.yml](./environment.yml) file and activate it:
```
conda env create -f environment.yml && conda activate dbd
```
### Datasets
Download CIFAR-10 dataset from its [official
website](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz) and extract it to `dataset_dir`
specified in the [YAML configuration files](./config).

**Note:** Make sure `dataset_dir` contains the sub-string `cifar`.

### Log and checkpoint directories
Create `saved_dir` and `storage_dir` specified in the [YAML configuration
files](./config) to save logs and checkpoints respectively:
```
mkdir saved_data && mkdir storage
``` 

## Usage
We give examples to compare the standard supervised training (No Defense) and DBD on CIFAR-10
dataset under BadNets attack with ResNet-18. Other settings can also be found in the [YAML
configuration files](./config). Please have an overview before running the codes.

### No Defense
Run the following script to train a backdoored model:
```
python supervise.py --config config/supervise/badnets/cifar10_resnet18/example.yaml \
                    --resume False \
                    --gpu 0
```

### DBD
1. Self-Supervised Learning

    Run the following script to train a purified feature extractor:
    ```
    python simclr.py --config config/defense/simclr/badnets/cifar10_resnet18/example.yaml \
                     --resume False \
                     --gpu 0
    ```
2. Semi-Supervised Fine-tuning

    Run the following script to finetune a clean model:
    ```
    python mixmatch_finetune.py --config config/defense/mixmatch_finetune/badnets/cifar10_resnet18/example.yaml \
                                --resume False \
                                --gpu 0
    ```

## Pretrained Models
We provide pretrained models [here](./checkpoint).

### Test
Run the following script to test No Defense under BadNets attack:
```
python test.py --config config/supervise/badnets/cifar10_resnet18/example.yaml \
               --ckpt-dir checkpoint/supervise/badnets/cifar10_resnet18/example \
               --resume latest_model.pt \
               --gpu 0
```
Run the following script to test DBD under BadNets attack:
```
python test.py --config config/supervise/badnets/cifar10_resnet18/example.yaml \
               --ckpt-dir checkpoint/defense/mixmatch_finetune/badnets/cifar10_resnet18/example \
               --resume latest_model.pt \
               --gpu 0
```
Run the following script to test No Defense under Blended attack:
```
python test.py --config config/supervise/blend/cifar10_resnet18/example.yaml \
               --ckpt-dir checkpoint/supervise/blend/cifar10_resnet18/example \
               --resume latest_model.pt \
               --gpu 0
```
Run the following script to test DBD under Blended attack:
```
python test.py --config config/supervise/blend/cifar10_resnet18/example.yaml \
               --ckpt-dir checkpoint/defense/mixmatch_finetune/blend/cifar10_resnet18/example \
               --resume latest_model.pt \
               --gpu 0
```

### Results
|   Method   | BadNets BA (%) | BadNets ASR (%) | Blended BA (%) | Blended ASR (%) |
|:----------:|:--------------:|:---------------:|:--------------:|:---------------:|
| No Defense |     95.13      |       100       |     94.26      |      98.15      |
|    DBD     |     92.50      |      0.88       |     92.60      |      0.31       |

# License
Our codes is released under [GNU General Public License v3.0](./LICENSE).

# Citation
If our work or this repo is useful for your research, please cite our paper as follows:
```
@inproceedings{huang2022backdoor,
  title={Backdoor Defense via Decoupling the Training Process},
  author={Kunzhe Huang, Yiming Li, Baoyuan Wu, Zhan Qin and Kui Ren},
  booktitle={ICLR},
  year={2022}
}
```