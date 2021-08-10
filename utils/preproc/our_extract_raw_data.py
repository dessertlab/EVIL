# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

import json
import sys
import nltk
import traceback
import ast
import astor
from OurCanonical import *
from util import get_encoded_code_tokens, detokenize_code, encode_tokenized_code, encoded_code_tokens_to_code, tokenize, compare_ast

if __name__ == '__main__':

    canon = Canonical()
    
    #Add additional cannon objects here
    canonOptions = [

   

    #Pre-processing 0: No Proprecessing
        Canonical(remove=[],
                  replace={},
                  lower=False,
                  stemmer=None,
                  remove_punctuation=False,
                  std_var=False,
                  ),

        
     #Pre-processing 1: ShellBe Best preprocessing 
        Canonical(remove=[],
                replace={' in ' : ' ', ' of ': ' ', ' into ' : ' ', ' a ': ' ',' an ' : ' ', ' to ': ' ',' at ' : ' ',' on ': ' ' ,' onto ' : ' ', ' from ' : ' ', ' each ' : ' ',' with ' : ' ', ' as ': ' ',' between ':' ', ' there ': ' ',' itself ': ' ', ' the ':' ', ' in ': ' ', ' by ': ' ', ' are ' : ' ', ' is ' : ' ' },
                  lower=False,
                  stemmer=None,
                  remove_punctuation=False,
                  std_var=True,
                 ),         

    ]

    list_of_files = [('assembly-train.json','to_parse'), ('assembly-dev.json','to_parse'),('assembly-test.json','to_parse')]

   
    
    canonSelect = int(sys.argv[1])
    if canonSelect < len(canonOptions):
        print("Setting canon")
        canon = canonOptions[canonSelect]
    else:
        print("Failed to set cannon...., using default")

    
    total_snippets = 0
    total_snippet_tokens = 0
    total_intent_tokens = 0
    snippet_set = set()
    intent_set = set()
    snippet_token_set = set()
    intent_token_set = set()
    
    for file_path, file_type in list_of_files:
        num_failed = 0
        not_compile = 0
        print('extracting {} file {}'.format(file_type, file_path), file=sys.stderr)


        dataset = json.load(open(file_path))
        previous_snippet = ''
        previous_og_snippet = ''
        for i, example in enumerate(dataset):
            intent = None
            snippet = None
            intent = example['intent']
            rewritten_intent = example ['rewritten_intent']

            snippet = example['snippet']
            snippet_set.add(snippet)
            

            failed = False
            intent_tokens = []
            total_snippets += 1
      
            if file_type == 'to_parse':
                try:
                    # clean intent before or after?
                    
                    intent_set.add(rewritten_intent)
                    canonical_intent, slot_map = canon.stdz_intent(rewritten_intent) # parse
                    final_intent = canon.clean_intent(canonical_intent) # clean
                    intent_tokens = nltk.word_tokenize(final_intent)

                    canonical_snippet = canon.canonicalize_code(snippet,slot_map)
                    decanonical_snippet = canon.decanonicalize_code(canonical_snippet,slot_map)
                    #snippet_reconstr = astor.to_source(ast.parse(snippet)).strip()
                    #decanonical_snippet_reconstr = astor.to_source(ast.parse(decanonical_snippet)).strip()
                    
                    #encoded_reconstr_code = get_encoded_code_tokens(canonical_snippet.strip())
                    #decoded_reconstr_code = encoded_code_tokens_to_code(encoded_reconstr_code)
                    print('.', end='')
                    #if not compare_ast(ast.parse(decoded_reconstr_code), ast.parse(snippet)):
                    #print(i)
                    #print('Intent: %s' % intent)
                    #print('Original Snippet: %s' % snippet_reconstr)
                    #print('Tokenized Snippet: %s' % ' '.join(encoded_reconstr_code))
                    #print('decoded_reconstr_code: %s' % decoded_reconstr_code)

                except:
                    #print("Exception")
                    #print('*' * 20, file=sys.stderr)
                    #print(i, file=sys.stderr)
                    #print(intent, file=sys.stderr)
                    #print(snippet, file=sys.stderr)
                    #traceback.print_exc()
                    #num_failed += 1
                    failed = True
                finally:
                    #canonical_intent, slot_map = canon.stdz_intent(rewritten_intent)
                    example['slot_map'] = slot_map
                    #encoded_reconstr_code = get_encoded_code_tokens(canonical_snippet.strip())
                    #final_intent = canon.clean_intent(canonical_intent)                   
                    #intent_tokens = nltk.word_tokenize(final_intent)
                    #example['intent_tokens'] = intent_tokens
                    
                    #example['snippet_tokens'] = encoded_reconstr_code

            if rewritten_intent is None and not failed:
                try:
                      encoded_reconstr_code = get_encoded_code_tokens(snippet.strip())
                      #print('Error #1')
                except:
                    print('Error #1')
                    #num_failed += 1
                    failed = True
                    #traceback.print_exc()
                    encoded_reconstr_code = nltk.word_tokenize(snippet)
            elif rewritten_intent != None:
                try:
                    encoded_reconstr_code = nltk.word_tokenize(canonical_snippet.strip())
                    # change if above is worse
                    #encoded_reconstr_code = get_encoded_code_tokens(canonical_snippet.strip())
                    
                    #if 'time_str' in canonical_snippet:
                    #    print('#1:')
                    #    print(' '.join(encoded_reconstr_code))
                    #    print(canonical_snippet.strip())
                    #    print(canonical_snippet)
                    #    print(slot_map)
                     
                     
                except:
                    try:
                        encoded_reconstr_code = nltk.word_tokenize(canonical_snippet.strip())
                    except:
                        print('Error #2')
                        #num_failed += 1
                        failed = True
                        #traceback.print_exc()
                        encoded_reconstr_code = nltk.word_tokenize(snippet)
                        #if '#SPACE#' in ' '.join(encoded_reconstr_code):
                        #    print('#2:')
                        #    print(encoded_reconstr_code)
                      
            else:
                #num_failed += 1
                print('Error #3')
                print(snippet.strip())
                encoded_reconstr_code = nltk.word_tokenize(snippet)
                #if '#SPACE#' in ' '.join(encoded_reconstr_code):
                #        print('#3:')
                #        print(encoded_reconstr_code)
                #del dataset[i]
         #       encoded_reconstr_code = nltk.word_tokenize(snippet)
                

            if not intent_tokens:
                intent_tokens = nltk.word_tokenize(final_intent)
            
                
            example['intent_tokens'] = intent_tokens
            example['snippet_tokens'] = encoded_reconstr_code
            previous_snippet = ' '.join(encoded_reconstr_code)
            previous_og_snippet = snippet
            
            total_intent_tokens += len(example['intent_tokens'])
            total_snippet_tokens += len(example['snippet_tokens'])
            
       
            for token in example['intent_tokens']:
                intent_token_set.add(token)
            for token in example['snippet_tokens']:
                snippet_token_set.add(token)
                
            
        print ('Number of snippets in the set: '+ str(total_snippets))
        print ('Number of snippets that failed to be tokenized: '+ str(num_failed))
        print ('% failed is: ' + str(float(num_failed/total_snippets)*100))
        print ('Number of snippets that failed to compile in Python: '+ str(not_compile))
        print ('% snippets that do not compile: ' + str(float(not_compile/total_snippets)*100))
        print ('Number of total intent tokens in the set: '+ str(total_intent_tokens))
        print ('Number of total snippet tokens in the set: '+ str(total_snippet_tokens))
        print('\n')
        
        print ('Number of unique intent statements in the set: '+ str(len(intent_set)))
        print ('Number of unique snippet statements  in the set: '+ str(len(snippet_set)))
        #print('Intent Statements sample {}'.format(list(intent_set)[:10]))
        #print('Intent Statements sample {}'.format(list(snippet_set)[:10]))
        print('\n')
        
        
        print ('Number of unique intent tokens in the set: '+ str(len(intent_token_set)))
        print ('Number of unique snippet tokens in the set: '+ str(len(snippet_token_set)))
        #print('Intent Tokens sample {}'.format(list(intent_token_set)[:500]))
        #print('Snippet Tokens sample {}'.format(list(snippet_token_set)[:500]))
        
        print('\n')
        
        print ('Average number of intent tokens per statement: ' + str(total_intent_tokens/total_snippets))
        print ('Average number of snippet tokens per statement: ' + str(total_snippet_tokens/total_snippets))
        json.dump(dataset, open(file_path + '.seq2seq', 'w'), indent=2)
