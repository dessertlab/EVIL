from xnmt_model import Seq2SeqRunner
import os
import shutil
import zipfile
import sys

"""

Seq2Seq Params:

    vocab_size=4000 --> vocab size for embeddings 
    model_type='unigram' --> unigram, bpe
    min_freq=2 --> min freq to include vocab token in embedding
    layers=1 --> num of layers in lstm
    layer_dim=128 --> dimension
    alpha=0.001 --> learning rate
    epochs=1 --> epochs 
    src_embedding='SimpleWordEmbedding' --> if not set uses simpleword embedding by xnmt, can use a pre-trained embedding if replaced with file name.vec
    dataset = 'annot' --> dataset type see options below
    trg_embedding = None --> target embedding if using a pre-trained embedding (pre-trained embedding of snippets)
    parent_model = None --> parent model if using transfer learning, include directory and file name.mod of parent model (def: saved_models/ conala_annot_best.mod)
    custom_emb_size = 100 --> custom embedding size if using a pre-trained embedding
    
    dataset options:

        encoder
        decoder
        

"""


#Add your options here and update the loop in Launch.sh
dataset = str(sys.argv[1])
xnmt_options = [
Seq2SeqRunner(model_type='bpe',epochs= 200, layer_dim= 512, alpha= 0.001,min_freq= 1,dataset = dataset, vocab_size = 20000)



]

xnmt = xnmt_options[0]

xnmt_select = 0
if xnmt_select < len(xnmt_options):
    print("Setting XNMT Seq2Seq Options")
    xnmt = xnmt_options[xnmt_select]
else:
    print("Failed to set XNMT Options...., using default")

xnmt.run()
