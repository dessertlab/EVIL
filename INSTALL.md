# Experiments Replication
This section is written based on our setup experience on *Red Hat's Linux 7.5* and *CentOS Linux release 7.5.1804*. Please run on a Linux OS. It is strongly recommended to run with **at least one GPU**.

Before setting up our project we'd like to make sure you have some prerequisite installations and setups.



## Step 1: Python Setup
Ensure you have Anaconda3 installed, if not install **Python 3.7** from [*Anaconda*](https://www.anaconda.com) with the following steps:
* Install the list of dependencies described [here](https://docs.anaconda.com/anaconda/install/linux/)
* Download the installer [here](https://repo.anaconda.com/archive/). For example, you can use the `wget` command: `wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh`, then type `chmod +x Anaconda3-2021.05-Linux-x86_64.sh` and run `bash Anaconda3-2021.05-Linux-x86_64.sh` to complete the installation.
* You may need to add *anaconda directory* to the PATH environment variable (e.g., `export PATH="/path_to_anaconda/anaconda/bin:$PATH"`).

### Recommended GPU Set up
* If you are using an HPC cluster run the following command to enable **Python 3.7 with CUDA**: `module load cuda/9.2  anaconda3/5.0.1-cuda92`
* If you are using a local machine and have anaconda set up already run the following command `conda env create -f evil_env_gpu.yml` Upon completion activate it using `conda activate evil_env`. The move to the Install Natural Language tools section. 


## Step 2: Dependencies Setup
* Move to the EVIL main directory
* It is recommended you use a virtual environment for the dependency set up (**Conda environment**). If you do not  wish to do so, then simply run ``pip3 install -r requirements.txt``.

### Setting up a Conda environment
* Import our saved conda environment using the command: ``conda env create -f evil_env.yml`` and activate it using ``source activate evil_env`` or ``conda activate evil_env``

* Alternatively, you can create an anaconda Python 3.7 virtual environment using the command ``conda create -n yourenvname python=3.7 anaconda``.  Activate the environment by typing ``source activate yourenvname``.

* Run ``pip3 install -r requirements.txt`` to install the dependencies.

### Install Natural Language tools
* Install nltk tokenizers and corpora ``python -m nltk.downloader``, then type `d` (Download), and type `all` in Identifier. Type `q` at the end of the installation.

* Install the spacy language model by using the following command ``python -m spacy download en_core_web_lg``
   

## Step 3: Running Experiments
This section briefly describes how to replicate the experiment mentioned in the paper. If you are using an anaconda environment, please ensure that you conda environment is **activated** before running any of the bash commands below.

### CodeBERT
To Launch the finetuning and evaluation processes of CodeBERT the basic command template is as follows: <br>
``bash CodeBERT_Launch.sh [DEVICE] [DATASET] [PREPROCESSING]``<br>

**Device Options**:

0. Local machine
1. HPC with a SLURM scheduler
2. HPC with a TORQUE scheduler

**Dataset Options:** 
1.  Python Encoder Dataset
2.  Assembly Decoder Dataset

**Preprocessing Options:**

0. Raw corpus counts
1. Preprocessing without the Intent Parser (IP)
2. Preprocessing with the Intent Parser (IP)

#### Running on a local machine
* From the EVIL home directory, run ``bash CodeBERT_Launch.sh 0 [DATASET] [PREPROCESSING]``

#### Running on an HPC with a SLURM scheduler
* Navigate to ``EVIL/model/fine_tune.slurm`` and add in your GPU queue name under the TODO comment.
* From the EVIL home directory, run ``bash CodeBERT_Launch.sh 1 [DATASET] [PREPROCESSING]``
* When the job is complete, from the EVIL home directory, run ``bash evaluate.sh``

#### Running on an HPC with a TORQUE scheduler
* Navigate to ``EVIL/model/fine_tune.pbs`` and add in your GPU queue name under the TODO comment.
* From the EVIL home directory, run ``bash CodeBERT_Launch.sh 2 [DATASET] [PREPROCESSING]``
* When the job is complete, from the EVIL home directory, run ``bash evaluate.sh``

#### Final Results
The final evaluation results would appear on your console if you are running on your local machine and in the specified logging output directory if a job was submitted.
The predicted output will be generated in the subdirectory ``model/eval/[encoder/decoder]_test_output.json``.


### Seq2Seq 
To launch the training and evaluation of the Seq2Seq model mentioned in the paper also ensure the conda environment is active. The basic command template is as follows: <br>
``bash Seq2Seq_Launch.sh [DATASET] [PREPROCESSING]``<br>
The dataset and preprocessing options are the same as that of CodeBERT.

#### Final Results
The final evaluation results would appear on your console if you are running on your local machine and in the specified logging output directory `seq2seq/logs`
The predicted output will be generated in the subdirectory ``seq2seq/archive/id-[timestamp]/answer_[encoder/decoder].txt``.


 
## Notes
* Run ``bash utils/test_split.sh`` for details on the different preprocessing options
* If you chose to submit a job, the logs will be stored in ``model/job_logs/``, named with the job id.
* Run ``bash utils/test_split.sh [DATASET] 0`` for raw corpus token counts

