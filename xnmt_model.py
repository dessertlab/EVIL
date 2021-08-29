import os
import random

import numpy as np

import dynet_config

dynet_config.set_gpu()
dynet_config.set(mem=2048,random_seed=9)
# 1245884048
import xnmt.tee

from xnmt.modelparts.attenders import MlpAttender
from xnmt.batchers import WordSrcBatcher,InOrderBatcher,Batcher
from xnmt.modelparts.bridges import CopyBridge
from xnmt.modelparts.decoders import AutoRegressiveDecoder
from xnmt.modelparts.embedders import SimpleWordEmbedder,PretrainedSimpleWordEmbedder
from xnmt.eval.tasks import LossEvalTask, AccuracyEvalTask
from xnmt.experiments import Experiment,ExpGlobal
from xnmt.inferences import AutoRegressiveInference
from xnmt.input_readers import PlainTextReader
from xnmt.transducers.recurrent import BiLSTMSeqTransducer, UniLSTMSeqTransducer
from xnmt.modelparts.transforms import AuxNonLinear
from xnmt.modelparts.scorers import Softmax
from xnmt.optimizers import AdamTrainer
from xnmt.param_collections import ParamManager
from xnmt.persistence import save_to_file

from xnmt.train.regimens import SimpleTrainingRegimen
from xnmt.models.translators import DefaultTranslator
from xnmt.vocabs import Vocab
from xnmt.preproc import PreprocVocab,PreprocTokenize,PreprocRunner,SentencepieceTokenizer,VocabFiltererFreq
from xnmt.search_strategies import BeamSearch
from xnmt.length_norm import PolynomialNormalization
from xnmt.persistence import LoadSerialized
from vocab_builder import VocabBuilder


class Seq2SeqRunner():
    def __init__(self, vocab_size=4000, model_type='unigram', min_freq=2, layers=1, layer_dim=128, alpha=0.001, epochs=1, src_embedding='SimpleWordEmbedding', dataset = 'annot', trg_embedding = None, parent_model = None, custom_emb_size = 100, dropout = 0.3 ):
        self.vocab_size = vocab_size
        self.model_type = model_type
        self.min_freq = min_freq
        self.layers = layers
        self.layer_dim = layer_dim
        self.alpha = alpha
        self.epochs = epochs
        self.src_embedding = src_embedding # used to choose pre-trained embeddings
        self.dataset = dataset
        self.trg_embedding = trg_embedding
        self.dropout = dropout
        self.train = 'conala-trainnodev'
        self.dev = 'conala-dev'
        self.test = 'conala-test'
        if self.dataset == 'encoder':
            self.train = 'encoder-train'
            self.dev = 'encoder-dev'
            self.test = 'encoder-test'

        elif self.dataset == 'decoder':
            self.train = 'decoder-train'
            self.dev = 'decoder-dev'
            self.test = 'decoder-test'


        
        if self.src_embedding != 'SimpleWordEmbedding' and self.trg_embedding is None:
            raise Exception ("Custom source embedding is set, please make sure to set the target embedding as well")
            
        self.custom_emb_size = custom_emb_size
            
            
        # Parent Model if transfer learning is being used
        self.parent_model  = parent_model
            
            

    def run(self):
        seed=13
        random.seed(seed)
        np.random.seed(seed)
        EXP_DIR = os.path.dirname(__file__)
        EXP = str(self.dataset)
        
        if self.parent_model != None:
            base = os.path.basename(str(self.parent_model))
            file_name = os.path.splitext(base)[0]
            EXP = 'parent_'+ str(file_name)+ '_child_'+ str(self.dataset)
            
        

        model_file = f"{EXP_DIR}/results/{EXP}.mod"
        log_file = f"{EXP_DIR}/results/{EXP}.log"

        xnmt.tee.set_out_file(log_file,exp_name=EXP)
        xnmt.tee.utils.dy.DynetParams().set_mem(1024) #Doesnt work figure out how to set memory
        ParamManager.init_param_col()
        ParamManager.param_col.model_file = model_file
        
        builder = VocabBuilder(f"{EXP_DIR}/conala-corpus/"+self.train + '.json.seq2seq',self.min_freq)
        builder.build()


        pre_runner=PreprocRunner(tasks= [PreprocTokenize(in_files=[f'{EXP_DIR}/conala-corpus/'+self.train+'.snippet',
                                                                   f'{EXP_DIR}/conala-corpus/'+self.train+'.intent',
                                                                   f'{EXP_DIR}/conala-corpus/'+self.dev+'.intent',
                                                                   f'{EXP_DIR}/conala-corpus/'+self.dev+'.snippet',
                                                                   f'{EXP_DIR}/conala-corpus/'+self.test+'.intent',
                                                                   f'{EXP_DIR}/conala-corpus/'+self.test+'.snippet'],
                                                         out_files= [f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet',
                                                                     f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent',
                                                                     f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.intent',
                                                                     f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.snippet',
                                                                     f'{EXP_DIR}/conala-corpus/'+self.test+'.tmspm'+str(self.vocab_size)+'.intent',
                                                                     f'{EXP_DIR}/conala-corpus/'+self.test+'.tmspm'+str(self.vocab_size)+'.snippet'],
                                                         specs= [{'filenum':'all',
                                                                 'tokenizers':[SentencepieceTokenizer(
                                                                    hard_vocab_limit=False,
                                                                    train_files= [f'{EXP_DIR}/conala-corpus/'+self.train+'.intent',
                                                                         f'{EXP_DIR}/conala-corpus/'+self.train+'.snippet'],vocab_size=self.vocab_size,
                                                                 model_type= self.model_type,model_prefix= 'conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.spm')]}])
            ,PreprocVocab(in_files= [f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent',
                                     f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet'],
                          out_files=[f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent.vocab',
                                     f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet.vocab'],
                          specs=[{'filenum':'all','filters':[VocabFiltererFreq(min_freq = self.min_freq)]}])],overwrite=True)

        src_vocab = Vocab(vocab_file=f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent.vocab')
        trg_vocab = Vocab(vocab_file=f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet.vocab')
        #trg_vocab = Vocab(vocab_file=f'{EXP_DIR}/conala-corpus/'+self.train+'.intent.vocab')
        #src_vocab = Vocab(vocab_file=f'{EXP_DIR}/conala-corpus/'+self.train+'.snippet.vocab')
        batcher = Batcher(batch_size=64)

#       inference = AutoRegressiveInference(search_strategy= BeamSearch(beam_size= 5), post_process = 'none',src_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.intent',ref_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.snippet')
        
        #len_norm= PolynomialNormalization(apply_during_search=True),beam_size= 5))#post_process= 'join-piece')
        
        inference = AutoRegressiveInference(search_strategy= BeamSearch(len_norm= PolynomialNormalization(apply_during_search=True),beam_size= 5),post_process= 'join-piece')
    
        layer_dim = self.layer_dim
	
        if self.src_embedding == 'SimpleWordEmbedding':
                  model = DefaultTranslator(
		  src_reader=PlainTextReader(vocab=src_vocab),
		  trg_reader=PlainTextReader(vocab=trg_vocab),
		  src_embedder=SimpleWordEmbedder(emb_dim=layer_dim,vocab= src_vocab),

		  encoder=BiLSTMSeqTransducer(input_dim=layer_dim, hidden_dim=layer_dim, layers=self.layers),
		  attender=MlpAttender(hidden_dim=layer_dim, state_dim=layer_dim, input_dim=layer_dim),
		  trg_embedder=SimpleWordEmbedder(emb_dim=layer_dim, vocab = trg_vocab),

		    decoder=AutoRegressiveDecoder(input_dim=layer_dim,
										 rnn=UniLSTMSeqTransducer(input_dim=layer_dim, hidden_dim=layer_dim,
													  ),
										transform=AuxNonLinear(input_dim=layer_dim, output_dim=layer_dim,
												      aux_input_dim=layer_dim),
									      scorer=Softmax(vocab_size=len(trg_vocab), input_dim=layer_dim),
									    trg_embed_dim=layer_dim,
									    input_feeding= False,
									    bridge=CopyBridge(dec_dim=layer_dim)),
		  inference=inference)

        else:
                  model = DefaultTranslator(
                  src_reader=PlainTextReader(vocab=src_vocab),
                  trg_reader=PlainTextReader(vocab=trg_vocab),
                  src_embedder=PretrainedSimpleWordEmbedder(filename= self.src_embedding,emb_dim=self.custom_emb_size,vocab = src_vocab),

                  encoder=BiLSTMSeqTransducer(input_dim=layer_dim, hidden_dim=layer_dim, layers=self.layers),

                  attender=MlpAttender(hidden_dim=layer_dim, state_dim=layer_dim, input_dim=layer_dim),
                  trg_embedder= PretrainedSimpleWordEmbedder(filename= self.trg_embedding,emb_dim=self.custom_emb_size,vocab = trg_vocab),

                  decoder=AutoRegressiveDecoder(input_dim=layer_dim,
										 rnn=UniLSTMSeqTransducer(input_dim=layer_dim, hidden_dim=layer_dim,
													  ),
										transform=AuxNonLinear(input_dim=layer_dim, output_dim=layer_dim,
												      aux_input_dim=layer_dim),
									      scorer=Softmax(vocab_size=len(trg_vocab), input_dim=layer_dim),
									    trg_embed_dim=layer_dim,
									    input_feeding= False,
									    bridge=CopyBridge(dec_dim=layer_dim)),
		  inference=inference)

		#decoder = AutoRegressiveDecoder(bridge=CopyBridge(),inference=inference))
        if self.parent_model is None:
            train = SimpleTrainingRegimen(
              name=f"{EXP}",
              model=model,
              batcher=WordSrcBatcher(avg_batch_size=64),
              trainer=AdamTrainer(alpha=self.alpha),
              patience= 3,
              lr_decay= 0.5,
              restart_trainer= True,
              run_for_epochs=self.epochs,
              src_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent',
              trg_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet',
              dev_tasks=[LossEvalTask(src_file=f'{EXP_DIR}/conala-corpus/'+ self.dev +'.tmspm'+str(self.vocab_size)+'.intent',
                                     ref_file= f'{EXP_DIR}/conala-corpus/'+ self.dev +'.tmspm'+str(self.vocab_size)+'.snippet',
               #src_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.intent',
               #trg_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.snippet',
               #dev_tasks=[LossEvalTask(src_file=f'{EXP_DIR}/conala-corpus/'+ self.dev +'.intent',
               #                       ref_file= f'{EXP_DIR}/conala-corpus/'+ self.dev +'.snippet', 
                                      model=model,
                                      batcher=WordSrcBatcher(avg_batch_size=64)),
                         AccuracyEvalTask(eval_metrics= 'bleu',
                                          src_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.intent',
                                          #src_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.intent',
                                          ref_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.snippet',
                                          hyp_file= f'{EXP_DIR}/results/{EXP}.dev.hyp',
                                          model = model)])

            evaluate = [AccuracyEvalTask(eval_metrics="bleu",
                                         src_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.tmspm'+str(self.vocab_size)+'.intent',
                                         #src_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.intent',
                                         ref_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.snippet',
                                         hyp_file=f"{EXP_DIR}/results/{EXP}.test.hyp",
                                         inference=inference,
                                         model=model)]

            standard_experiment = Experiment(
              exp_global= ExpGlobal(default_layer_dim= layer_dim, dropout= self.dropout,
                                    log_file= log_file,model_file=model_file),
              name=EXP,
              model=model,
              train=train,
              evaluate=evaluate
            )



        else:
            evaluate = [AccuracyEvalTask(eval_metrics="bleu",
            src_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.tmspm'+str(self.vocab_size)+'.intent',
            #src_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.intent',
            ref_file=f'{EXP_DIR}/conala-corpus/'+self.test+'.snippet',
            hyp_file=f'{EXP_DIR}/results/'+self.dataset+'.test.hyp',
            inference=inference,
            model=model)]

            standard_experiment = Experiment(LoadSerialized(filename = '{EXP_DIR)/'+str(self.parent_model),overwrite=[ExpGlobal(default_layer_dim= layer_dim, dropout= self.dropout,
            log_file= log_file,model_file=model_file),
            ]),
            name=EXP,
            model=model,
            train=SimpleTrainingRegimen( name=f"{EXP}",
            model=model,
            batcher=WordSrcBatcher(avg_batch_size=64),
            trainer=AdamTrainer(alpha=self.alpha),
            patience= 3,
            lr_decay= 0.5,
            restart_trainer= True,
            run_for_epochs=self.epochs,
            src_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.intent',
            trg_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.tmspm'+str(self.vocab_size)+'.snippet',
            dev_tasks=[LossEvalTask(src_file=f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.intent',
            ref_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.snippet',
            #src_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.intent',
            #trg_file= f'{EXP_DIR}/conala-corpus/'+self.train+'.snippet',
            #dev_tasks=[LossEvalTask(src_file=f'{EXP_DIR}/conala-corpus/'+self.dev+'.intent',
            #ref_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.snippet',
            model=model,
            batcher=WordSrcBatcher(avg_batch_size=64)),
            AccuracyEvalTask(eval_metrics= 'bleu',
            src_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.tmspm'+str(self.vocab_size)+'.intent',
            #src_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.intent',                 
            ref_file= f'{EXP_DIR}/conala-corpus/'+self.dev+'.snippet',
            hyp_file= f'{EXP_DIR}/results/'+self.dataset+'.dev.hyp',
            model = model)]),
            evaluate=evaluate
            )


        # run experiment
        standard_experiment(save_fct=lambda: save_to_file(model_file, standard_experiment))
        exit()

            
