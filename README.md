# EVIL: Exploiting Software via Natural Language

This repository contains the dataset and the code related to the paper **EVIL: Exploiting Software via Natural Language** accepted for publication at the 32nd International Symposium on Software Reliability Engineering (ISSRE 2021) conference. 
*EVIL* is an approach to automatically generate software exploits in assembly/Python language from descriptions in natural language. 
The approach leverages Neural Machine Translation (NMT) techniques and a dataset that we developed for this work. 

This repository contains:
1. A substantive **dataset** containing exploits collected from shellcode databases, and their descriptions in the English language. The dataset includes both assembly code (i.e, shellcodes and decoders) and Python code (i.e., encoders). Such data is valuable to support research in machine translation for security-oriented applications since the techniques are data-driven. 
2. The code to reproduce the **experiments** described the paper.
3. The **appendix** of the paper containing additional information on the test set.


## Dataset
To automatically generate Python and assembly programs used for security exploits, we curated a large dataset for feeding NMT techniques. A sample in the dataset consists of a snippet of code from these exploits and their corresponding description in the English language.
We collected exploits from publicly available databases ([*exploitdb*](https://www.exploit-db.com/), [*shellstorm*](http://shell-storm.org/shellcode/)), public repositories (e.g., GitHub), and programming guidelines. In particular, we focused on exploits targeting Linux, the most common OS for security-critical network services, running on IA-32 (i.e., the 32-bit version of the x86 Intel Architecture). The dataset is stored in the folder *EVIL/datasets* and consists of two parts: 
1. **Encoders**: a Python dataset, which contains Python code used by exploits to encode the shellcode;
2. **Decoders**: an assembly dataset, which includes shellcode and decoders to revert the encoding.

Both datasets are already slipt in train, dev and test set. ``encoder-*.in`` represents the natural language intents and ``encoder-*.out`` represents the corresponding code snippets. 
Please, find the detailed information of the dataset on the paper. 


## Experiments
Before setting up our project we'd like to make sure you have some prerequisite installations and setups.
This section is written based on our setup experience on *Red Hat's Linux 7.5*. Please run on a Linux OS. It is strongly recommended to run with **at least one GPU**.

### Step 1: Python Setup
 * Ensure you have Anaconda3 installed, if not install **Python 3.7** from [*Anaconda*](https://www.anaconda.com/download/)

#### Recommended GPU Set up
* If you are using an HPC cluster run the following command to enable **Python 3.7 with CUDA**: `module load cuda/9.2  anaconda3/5.0.1-cuda92`
* If you are using a local machine and have anaconda set up already run the following command `conda env create -f evil_env_gpu.yml` Upon completion activate it using `conda activate evil_env`. The move to the Install Natural Language tools section.


### Step 2: Dependencies Setup
* It is recommended you use a virtual environment for the dependency set up (**Conda environment**). If you do not  wish to do so, then simply run ``pip3 install -r requirements.txt``.

#### Setting up a Conda environment
* Import our saved conda environment using the command: ``conda env create -f evil_env.yml`` and activate it using ``source activate evil_env`` or ``conda activate evil_env``

* Alternatively, you can create an anaconda Python 3.7 virtual environment using the command ``conda create -n yourenvname python=3.7 anaconda``.  Activate the environment by typing ``source activate yourenvname``

* Run ``pip3 install -r requirements.txt`` to install the dependencies

#### Install Natural Language tools
* Install nltk tokenizers and corpora ``python -m nltk.downloader``, then click on install all

* Install the spacy language model by using the following command ``python -m spacy download en_core_web_lg``
   

### Step 3: Replicating Results
This  section briefly describes how to replicate the experiment mentioned in the paper. Before running any of the bash commands ensure that you conda environment is **activated**.
To Launch the finetuning and evalulation processes the basic command template is as follows: <br>
``bash Launch.sh [DEVICE] [DATASET] [PREPROCESSING]``<br>

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
* From the EVIL home directory, run ``bash Launch.sh 0 [DATASET] [PREPROCESSING]``

#### Running on an HPC with a SLURM scheduler
* Navigate to ``EVIL/model/fine_tune.slurm`` and add in your GPU queue name under the TODO comment.
* From the EVIL home directory, run ``bash Launch.sh 1 [DATASET] [PREPROCESSING]``
* When the job is complete, from the EVIL home directory, run ``bash evaluate.sh``

#### Running on an HPC with a TORQUE scheduler
* Navigate to ``EVIL/model/fine_tune.pbs`` and add in your GPU queue name under the TODO comment.
* From the EVIL home directory, run ``bash Launch.sh 2 [DATASET] [PREPROCESSING]``
* When the job is complete, from the EVIL home directory, run ``bash evaluate.sh``

#### Final Results
The final evaluation results would appear on your console if you are running on your local machine and in the specified logging output directory if a job was submitted.
The predicted output will be generated in the subdirectory ``model/eval/[encoder/decoder]_test_output.json``.

## Appendix
The folder *EVIL/appendix* contains detailed information on the 20 encoders and decoders used in the test set.
It includes the source URL, the number of total lines (n_t) of the programs, and the number of syntactically correct (n_syn) and semantically correct (n_sem) lines generated by our approach, for both the encoders in Python and decoders in Assembly. 
In total, the test set for the Python programs contains 375 unique pairs of Python code snippets (not including prints) along with their natural description. The test set for assembly contains 305 unique pairs of code snippets (95 are multi-line snippets) and natural language intents.

 
### Notes
* Run ``bash utils/test_split.sh`` for details on the different preprocessing options
* If you chose to submit a job, the logs will be stored in ``model/job_logs/``, named with the job id.
* Run ``bash utils/test_split.sh [DATASET] 0`` for raw corpus token counts



## TODO
- [x] Add in preprocessing options for both encoder and decoder datasets in the ``preproc`` folder
- [x] Edit `Launch.sh` to account for dataset and preproccessing selections
- [ ] Edit `eval_prep.py` to account for dataset selection.
- [x] Update the README
- [x] CodeBERT download and set up
- [x] Dataset loading and preprocessing shell script written
- [x] Environment set up
- [ ] Upload finetuned models to Huggingface
- [ ] Write a Google Colab notebook to demo Python encoder generation and assembly decoder generation
- [ ] Implement encoder and decoder datasets in Huggingface
- [ ] Make a demo space on HuggingFace
