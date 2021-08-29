import json
import collections
import os
class VocabBuilder ():

    def __init__ (self,seq2seq, min_freq):
        
        self.seq2seq = seq2seq
        self.min_freq = min_freq
        
    def build(self):

        with open(self.seq2seq) as json_file:
            data = json.load(json_file)
        bag_s = collections.defaultdict(lambda:0)
        bag_i = collections.defaultdict(lambda:0)
        for entry in data:
            snippet= entry['snippet_tokens']
            for s in snippet:
                bag_s[s] +=1
            intent = entry['intent_tokens']
            for i in intent:
                bag_i[i] +=1
        base = os.path.basename(str(self.seq2seq))
        file_name = base.split('.')[0]
        path = os.path.dirname(str(self.seq2seq))
        intent_vocab = open(path+'/'+str(file_name)+'.intent.vocab', 'w+')
        snippet_vocab = open(path+'/'+str(file_name)+'.snippet.vocab', 'w+')
        
        for word in bag_s.keys():
            if bag_s[word] >= self.min_freq:
                snippet_vocab.write(word)
                snippet_vocab.write('\n')
        snippet_vocab.close()
        
        for word in bag_i.keys():
            if bag_i[word] >= self.min_freq:
                intent_vocab.write(word)
                intent_vocab.write('\n')
        intent_vocab.close()
        
        print('Vocab files created')
        