import gdown
import os
url = 'https://drive.google.com/uc?id=1Rw60M7A1h4L_nHfeLRhi7Z8H3EHvuHRG'
os.chdir(os.path.realpath('model/pretrained_models'))

files = os.listdir(os.path.curdir)
if 'config.json' in files and 'pytorch_model.bin' in files:
    print('Found properly installed Pretrained models!')
else:
    output = 'codebert.zip'

    gdown.cached_download(url, output, postprocess=gdown.extractall, quiet = False)
    print('Pretrained CodeBERT model properly installed!')