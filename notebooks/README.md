# EVIL: Exploiting Software via Natural Language

## Notebooks (WIP)

This folder contains a Google Colab notebook that you can run on a GPU runtime instance to run our finetuned best performing models (CodeBERT) on both the encoder and decoder datasets.








#### Final Results
The final evaluation results would appear on your console if you are running on your local machine and in the specified logging output directory if a job was submitted.
The predicted output will be generated in the subdirectory ``model/eval/assembly_test_output.json``.
 
### Notes
* The dataset directory is in ``datasets/assembly``. ``assembly-*.in`` represents the intents and ``assembly-*.out`` represents the corresponding snippets. 
* Run ``bash utils/test_split.sh`` for details on the different preprocessing options
* If you chose to submit a job, the logs will be stored in ``model/job_logs/``, named with the job id.
* Run ``bash utils/test_split.sh 0`` for raw corpus token counts