# coding=utf-8

from __future__ import print_function
import re
import ast
import astor
import string
import traceback
import sys
import spacy
from words2num import w2n
import os
from spacy.util import compile_prefix_regex,compile_suffix_regex
from nltk.corpus import wordnet as wn
#from nltk.stem import PorterStemmer

#You may need to import your stemmer here too


QUOTED_STRING_RE = re.compile(r"(?P<quote>[`'\"])(?P<string>.*?)(?P=quote)")
BRACKET_STRING_RE = re.compile(r"\[(.*?)\]")
CAMEL_CASE = re.compile(r"(?<=\W)[a-z]*[A-Z]\w+") #DateTime & camelCase
UNDERSCORED_TOKENS = re.compile(r"(?<=\W)[a-z]+_\w+") #df_1
HEX_TOKENS = re.compile(r"(?<=\W)0x[a-f0-9]+") #0xd123e
HEX_ARRAY = re.compile(r"(?<=\W)[, ]*0x[a-f0-9]+,*")

ASSEMBLY_RESERVED = ['label','address','location','value','flag','variable','memory','negative','bytes','byte','register','result','bits','operation','comparison','pointer','data', 'between','equal','if','else','by','stack', 'are' 'not', 'operand', 'with', 'representation','sh','execve','syscall','system','call','bin','word','dword','double','section','doubleword','/bin','/sh']
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        if s.isnumeric() == True:
            return True
        else:
            return False
def check_if_tagged (matches,match):
    for m in matches:
        if match in m:
            return True
        else:
            return False
        
def get_var_num(txt, matches, match):
    list_m = []
    for m in matches:
        #try:
        if m in txt:
            list_m.append((m,txt.index(m)))
        #except TypeError:
            #print('ERROR BADEED: ' + str(m) + '\t' +matches)
        #print(m)
    list_m = sorted(list_m,key = lambda k: k[1])
    #print(list_m)
    list_m = [l[0] for l in list_m]
    return list_m.index(match)


def replace_strings_in_ast(py_ast, string2slot):
    for node in ast.walk(py_ast):
        for k, v in list(vars(node).items()):
            if k in ('lineno', 'col_offset', 'ctx'):
                continue
            # Python 3
            # if isinstance(v, str) or isinstance(v, unicode):
            if isinstance(v, str):
                if v in string2slot:
                    val = string2slot[v]
                    # Python 3
                    # if isinstance(val, unicode):
                    #     try: val = val.encode('ascii')
                    #     except: pass
                    setattr(node, k, val)
                else:
                    # Python 3
                    # if isinstance(v, str):
                    #     str_key = unicode(v)
                    # else:
                    #     str_key = v.encode('utf-8')
                    str_key = v

                    if str_key in string2slot:
                        val = string2slot[str_key]
                        if isinstance(val, str):
                            try:
                                val = val.encode('ascii')
                            except:
                                traceback.print_exc()
                                pass
                        setattr(node, k, val)
                        
                        

class Canonical:
    #remove -regex matches you want to remove
    #replace regex matches you want to replace with another word (regex:word)
    #stemmer the stmmer object you want to use, calls .stem() on tokens
    #remove_punctuation removes punctuation when set to True
    #lower converts intent to lower case when set to True
    #std_var Standardize Variables, replaces variables with standardized names when set to True
    def __init__(self, remove = [], replace = {}, stemmer = None, remove_punctuation = False, lower = False, std_var = False):
        
        #Compile all the removes!
        #self.remove = re.compile('|'.join(re.compile(x).pattern for x in remove))
        self.remove = remove

        #Compile the replaces too
        self.replace = {}
        for match, repl in replace.items(): self.replace[re.compile(match)] = repl

        self.std_var = std_var
        self.stemmer = stemmer
        self.remove_punctuation = remove_punctuation
        self.lower = lower
        self.translator = str.maketrans('', '', string.punctuation)
        #print(self.reserved_words)
        if (self.std_var):
            shellbe_index = os.path.abspath(".").index('ShellBe')
            home_dir = os.path.abspath(".")[:shellbe_index+len('ShellBe')]
        
            # make an exception for _ so _close for instance counts as one token.
            
            self.nlp = spacy.load('en_core_web_lg')
            prefixes = list(self.nlp.Defaults.suffixes)
            suffixes = list(self.nlp.Defaults.suffixes)
            prefixes.remove("_")
            suffixes.remove("_")

            prefix_regex = spacy.util.compile_prefix_regex(prefixes)
            self.nlp.tokenizer.prefix_search = prefix_regex.search

            suffix_regex = spacy.util.compile_suffix_regex(suffixes)
            self.nlp.tokenizer.suffix_search = suffix_regex.search

    def canonicalize_intent(self, intent):
        str_matches = QUOTED_STRING_RE.findall(intent)

        # Here we can also add ways to find variables functions names or entities in intents

        slot_map = dict()
        #if (not self.std_var):
         #   return intent
        var_num = 0
        for i in range(len(str_matches)):
            if not str_matches[i][1] in slot_map:
                slot_map[str_matches[i][1]] = "var"+str(var_num)
                var_num += 1
            intent = intent.replace(str_matches[i][0] + str_matches[i][1] + str_matches[i][0], slot_map[str_matches[i][1]])

        return intent, slot_map
    
    def stdz_intent(self, intent):
 
        # We use a pretrained dependency parser to identify identifiers in intents and then standardize them


        # Here we can also add ways to find variables functions names or entities in intents
        
        if (not self.std_var):
            return intent, dict()
        
       
        og_intent = intent    
        doc = self.nlp(intent)
        slot_map = dict()
        escape_words = ['is','be','the','into','of','to','in','onto','at','has','from','it','an', 'a', 'and','method','tuple','list','dictionary','function','string','/', 'or','xor'] + ASSEMBLY_RESERVED
      
        #escape_words = []
        quote_matches =  [x for x in QUOTED_STRING_RE.findall(intent)]
        bracket_matches =  [x for x in BRACKET_STRING_RE.findall(intent)]
        
        
        
        
        
        #str_matches = [t.text for t in doc if (t.dep_ == "IDENTIFIER" and t.pos_!='VERB' and t.pos_!= 'PUNCT' and t.text not in escape_words) and t.pos_ != 'NUM' and t.text not in quote_matches and t.text not in bracket_matches]
        all_matches = [match[0]+match[1] + match[0] for match in quote_matches] + bracket_matches#  + str_matches
        num_matches = [t.text for t in doc if (not check_if_tagged(all_matches,t.text) and t.pos_ =='NUM') ] #and t.dep_ == "IDENTIFIER")]
        
        #all_matches += num_matches
        #num_matches = []
        
        
        
        camel_case_matches = [x for x in CAMEL_CASE.findall(intent) if not check_if_tagged(all_matches,x) and x not in escape_words]
        underscore_matches = [x for x in UNDERSCORED_TOKENS.findall(intent) if not check_if_tagged(all_matches,x) and x not in escape_words]
        all_matches = all_matches + camel_case_matches + underscore_matches 
        
        not_lexicon = [t.text for t in doc if len(wn.synsets(t.text))  == 0 and not check_if_tagged(all_matches,t.text) and (t.pos_!= 'PUNCT' and t.text not in escape_words) and t.pos_ != 'NUM']
        all_matches = all_matches + not_lexicon
        
        new_matches =  camel_case_matches + underscore_matches + not_lexicon
        hex_matches = [x for x in HEX_TOKENS.findall(intent) if not check_if_tagged(all_matches,x)]
        if len(hex_matches) < 3 and ',' not in intent :
            # Can't have more than two hex in an intent unless it's an array
            # add only unique hexadecimal values
            for h in hex_matches:
                if h not in all_matches:
                    all_matches = all_matches + [h]
                    new_matches = new_matches + [h]   
                
                elif ',' in intent:
                     hex_array = ''.join([x for x in HEX_ARRAY.findall(intent) if not check_if_tagged(all_matches,x)])
                     all_matches = all_matches + [hex_array]
                     new_matches = new_matches + [hex_array]
                
            
        
        var_num = 0
        
        for match in quote_matches:
            if match not in slot_map:
                match = match[0]+match[1]+match[0]
                if any([x in match for x in ['*','+','-','\/','%','[',']','\'','\"','|','(',')','$','/']]) and '\\' not in match:
                    for i in ['*','+','-','\'','\"']:
                        match = match.replace(i,'\\'+str(i))
                    for i in ['[',']']:
                        match = match.replace(i,'\\'+str(i))
                    for i in ['|','(',')','$','/']:
                        match = match.replace(i,'\\'+str(i))
                    var_num = get_var_num(og_intent,all_matches,str(match).replace('\\',''))
                    slot_map[str(match).replace('\\','')] = "var"+str(var_num)
                    intent = re.sub(str(match),str(slot_map[str(match).replace('\\','')]),intent)
                    #var_num += 1
                elif '\\' in match:
                    var_num = get_var_num(og_intent,all_matches,match)
                    slot_map[str(match)] = "var"+str(var_num)
                    intent = intent.replace(str(match),slot_map[match])
                    #var_num += 1
                if match in intent and intent.index(match) == 0:
                    intent = re.sub(r'\b'+str(match)+r'\b',slot_map[str(match)],intent,1)
                elif match in intent and intent.rindex(match) == (len(intent) - len(match)):
                    index = intent.rindex(match)
                    intent = intent[0:index] + slot_map[str(match)] + intent[index+len(match):]

                  # Make sure it does not break assembly
                #intent = re.sub(r' '+str(match)+r' ',' ' + str(slot_map[str(match).replace('\\','')]) + ' ',intent)
        
        for match in bracket_matches:
            if match not in slot_map:
                if any([x in match for x in ['*','+','-','\/','%','[',']','\'','\"']]):
                    for i in ['*','+','-','\'','\"']:
                        match = match.replace(i,'\\'+str(i))
                    for i in ['[',']']:
                        match = match.replace(i,'\\'+str(i))
                var_num = get_var_num(og_intent,all_matches,str(match).replace('\\',''))
                slot_map[str(match).replace('\\','')] = "var"+str(var_num)
                #var_num += 1 
                if match in intent and intent.index(match) == 0:
                    intent = re.sub(r'\b'+str(match)+r'\b',slot_map[str(match)],intent,1)
                elif match in intent and intent.rindex(match) == (len(intent) - len(match)):
                    index = intent.rindex(match)
                    intent = intent[0:index] + slot_map[str(match)] + intent[index+len(match):]


                intent = re.sub(r'\['+str(match)+r'\]',' [' + str(slot_map[str(match).replace('\\','')]) + ']',intent)
        
        #for match in str_matches+new_matches:
        for match in new_matches:    
            if match not in slot_map and '\''+match+'\'' not in slot_map and '\"'+match+'\"' not in slot_map and '['+match+']' not in slot_map:
                if is_number(str(match)) == True:
                    # If it's a digit match
                    var_num = get_var_num(og_intent,all_matches,match)
                    slot_map[str(match)] = "var"+str(var_num)
                elif match in num_matches and any([x in match for x in ['*','+','-','\/','%','x','\'','\"']]) == False and match.isalpha():
                    # If it is a alphanumeric match like 'zero'
                    alpha_numeric = match
                    match = str(w2n(match))
                    var_num = get_var_num(og_intent,all_matches,match)
                    slot_map[match] = "var"+str(var_num)
                    intent = intent.replace(str(alpha_numeric),slot_map[str(match)])
                elif (match in num_matches and 'var' not in match) or (match in num_matches and any([x in match for x in ['*','+','-','\/','%','\'','\"']]) == True):
                    # if it's an expression match like 2*c
                    #create list list1
                    var_num = get_var_num(og_intent,all_matches,match)
                    slot_map[match] = "var"+str(var_num)
                    #var_num += 1 
                    intent = intent.replace(str(match),slot_map[str(match)])
                    continue
                elif any([x in match for x in ['*','+','-','\/','%','[',']','|','(',')','$']]):
                    for i in ['*','+','-']:
                        match = match.replace(i,'\\'+str(i))
                    for i in ['[',']']:
                        match = match.replace(i,'\\'+str(i))
                    for i in ['|','(',')','$']:
                        match = match.replace(i,'\\'+str(i))
                    var_num = get_var_num(og_intent,all_matches,str(match).replace('\\',''))    
                    slot_map[str(match).replace('\\','')] = "var"+str(var_num)      
                else:
                    #store identifiers that are not stopwords into the slotmap
                    var_num = get_var_num(og_intent,all_matches,match)
                    slot_map[match] = "var"+str(var_num)
                #var_num += 1 
                if match in intent and intent.index(match) == 0:
                    intent = re.sub(r'\b'+str(match)+r'\b',slot_map[str(match)],intent,1)
                elif match in intent and intent.rindex(match) == (len(intent) - len(match)):
                    index = intent.rindex(match)
                    intent = intent[0:index] + slot_map[str(match)] + intent[index+len(match):]
                    #intent = re.sub(r' '+str(match),' '+ slot_map[str(match)],intent)
                    
            
                
                #intent = re.sub(r' '+str(match)+r' ',' ' + str(slot_map[str(match).replace('\\','')]) + ' ',intent)
                intent = re.sub(r'[./?*, ]+'+str(match)+r'[./?*, ]+',' ' + str(slot_map[str(match).replace('\\','')]) + ' ',intent)
            
            #for match in num_matches:
            #    if is_number(str(match)) == True:
            #        slot_map[str(match)] = "var"+str(var_num)
            #    else:
            #        match = str(w2n(match))
            #        slot_map[match] = "var"+str(var_num)
            #    var_num += 1
           #     intent = intent.replace(match, slot_map[match])
                
        
            
        return intent, slot_map

    def canonicalize_code(self, code, slot_map):
        
        
        # one letter variable names
        # after/before = sign
        #find some pos tagger like tokenizer
        # can also standardize stuff in code only without relating it to a relationship to the intent using astgen      
        symbols = ['\\*','\\+','\\-','\\[','\\]','\'','\"','\\/','\\$','\\(','\\)','\\|']
        try:
            canonical_code = code
            canonical_code = re.sub('(?<=[\(\[]) ', '', canonical_code)
            canonical_code = re.sub(' (?=[:,!?\]\(\)])', '', canonical_code)

                
            if len(slot_map)!= 0 :
                for slot_name, slot_info in slot_map.items():
                    is_expr = False
                    if slot_name in canonical_code:
                            vanilla_slot_name = slot_name
                            if any([x in slot_name for x in ['*','+','-','\/','%']]):
                                for i in ['*','+','-']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))
                                is_expr = True
                            if any([x in slot_name for x in ['[',']']]):
                                for i in ['[',']']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))

                            if any([x in slot_name for x in ['\'']]):
                                    slot_name = slot_name.replace("\'",'\"')
                                    vanilla_slot_name = vanilla_slot_name.replace("\'",'\"')
                            if any([x in canonical_code for x in ['\'']]):
                                    canonical_code = canonical_code.replace("\'",'\"')
                            if any([x in slot_name for x in ['|','(',')','$','/']]):
                                for i in ['|','(',')','$','/']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))
                                    
                         



                            if  is_expr == False and slot_name in canonical_code and canonical_code.index(slot_name) == 0 :
                                canonical_code = re.sub(r'\b'+str(slot_name)+r'\b',str(slot_info),canonical_code,1)
                            #elif canonical_code.rindex(slot_name) == (len(canonical_code) - len(slot_name)):

                            
                            if slot_name != 'var' and slot_name not in symbols and len(slot_name) >  1:
                                # identifying p as identifier but then seeing plist -> bad
                                canonical_code = re.sub(r' '+str(slot_name),' '+ slot_info,canonical_code)
                                canonical_code = canonical_code.replace(str(vanilla_slot_name) + ' ', slot_info+' ')

                            canonical_code = re.sub(r' '+str(slot_name)+r' ',' ' + str(slot_info) + ' ',canonical_code)
                            # specific for assembly

                            canonical_code = re.sub(r'\['+str(slot_name)+r'\]','[' + str(slot_info) + ']',canonical_code)

                            canonical_code = re.sub(r'\{'+str(slot_name)+r'\}','{' + str(slot_info) + '}',canonical_code)

                            canonical_code = re.sub(r'\('+str(slot_name)+r'\)','(' + str(slot_info) + ')',canonical_code)

                            canonical_code = re.sub(r'\''+str(slot_name)+r'\'','\'' + str(slot_info) + '\'',canonical_code)
                            canonical_code = re.sub(r'\"'+str(slot_name)+r'\"','\"' + str(slot_info) + '\"',canonical_code)
                            canonical_code = canonical_code.replace(' ' + str(slot_name) + ' ',' ' + slot_info+' ')

                            canonical_code = canonical_code.replace(' '+ str(vanilla_slot_name) + ' ', ' '+ slot_info +' ')

                            canonical_code = re.sub(r'(?<=[\[\(\{\'\"\.\/\?\*, ])'+str(slot_name)+r'(?=[\]\)\}\'\"\.\/\?\*, ])',str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\[\(\{\'\"\.\/\?\*, ])'+str(vanilla_slot_name)+r'(?=[\]\)\}\'\"\.\/\?\*, ])',str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\[\(\{\'\"\.\/\?\*,])'+str(slot_name)+r'(?=[\]\)\}\'\"\.\/\?\*,])',str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\.\/\?\*\,])'+str(slot_name),str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\.\/\?\*\,] )'+str(slot_name),str(slot_info),canonical_code)

                                
                                                         

    #                 if canonical_code.index(slot_name) == 0:
    #                     canonical_code = re.sub(r'\b'+str(slot_name)+r'\b',str(slot_info),canonical_code,1)
    #                 elif canonical_code.rindex(slot_name) == (len(canonical_code) - len(slot_name)):
    #                     canonical_code = re.sub(r' '+str(slot_name),' '+ slot_info,canonical_code)


    #                 canonical_code = re.sub(r' '+str(slot_name)+r' ',' ' + str(slot_info) + ' ',canonical_code)

                    #canonical_code = canonical_code.replace(slot_name, slot_info)

            return canonical_code
        except:
            canonical_code = code

            canonical_code = re.sub('(?<=[\(\[]) ', '', canonical_code)
            canonical_code = re.sub(' (?=[:,!?\]\(\)])', '', canonical_code)
                
            #print(code, file=sys.stderr)
            #print(slot_map, file=sys.stderr)
            #traceback.print_exc()
            for slot_name, slot_info in slot_map.items():
                    is_expr = False
                    if slot_name in canonical_code:
                            vanilla_slot_name = slot_name
                            if any([x in slot_name for x in ['*','+','-','\/','%']]):
                                for i in ['*','+','-']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))
                                is_expr = True
                            if any([x in slot_name for x in ['[',']']]):

                                for i in ['[',']']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))

                            if any([x in slot_name for x in ['\'']]):
                                    slot_name = slot_name.replace("\'",'\"')
                                    vanilla_slot_name = vanilla_slot_name.replace("\'",'\"')
                            if any([x in canonical_code for x in ['\'']]):
                                    canonical_code = canonical_code.replace("\'",'\"')
                            
                            if any([x in slot_name for x in ['|','(',')','$','/']]):
                                for i in ['|','(',')','$','/']:
                                    slot_name = slot_name.replace(i,'\\'+str(i))



                            if  is_expr == False and slot_name in canonical_code and canonical_code.index(slot_name) == 0 :
                                canonical_code = re.sub(r'\b'+str(slot_name)+r'\b',str(slot_info),canonical_code,1)
                            #elif canonical_code.rindex(slot_name) == (len(canonical_code) - len(slot_name)):

                            # ERFAN: Verify this works in assembly also...
                            if slot_name != 'var' and slot_name not in symbols and len(slot_name) >  1:
                                # identifying p as identifier but then seeing plist -> bad
                                canonical_code = re.sub(r' '+str(slot_name),' '+ slot_info,canonical_code)
                                canonical_code = canonical_code.replace(str(vanilla_slot_name) + ' ', slot_info+' ')

                            canonical_code = re.sub(r' '+str(slot_name)+r' ',' ' + str(slot_info) + ' ',canonical_code)
                            # specific for assembly

                            canonical_code = re.sub(r'\['+str(slot_name)+r'\]','[' + str(slot_info) + ']',canonical_code)

                            canonical_code = re.sub(r'\{'+str(slot_name)+r'\}','{' + str(slot_info) + '}',canonical_code)

                            canonical_code = re.sub(r'\('+str(slot_name)+r'\)','(' + str(slot_info) + ')',canonical_code)

                            canonical_code = re.sub(r'\''+str(slot_name)+r'\'','\'' + str(slot_info) + '\'',canonical_code)
                            canonical_code = re.sub(r'\"'+str(slot_name)+r'\"','\"' + str(slot_info) + '\"',canonical_code)
                            canonical_code = canonical_code.replace(' ' + str(slot_name) + ' ',' ' + slot_info+' ')

                            canonical_code = canonical_code.replace(' '+ str(vanilla_slot_name) + ' ', ' '+ slot_info +' ')
                            
                            canonical_code = re.sub(r'(?<=[\[\(\{\'\"\.\/\?\*, ])'+str(slot_name)+r'(?=[\]\)\}\'\"\.\/\?\*, ])',str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\[\(\{\'\"\.\/\?\*, ])'+str(vanilla_slot_name)+r'(?=[\]\)\}\'\"\.\/\?\*, ])',str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\.\/\?\*\,])'+str(slot_name),str(slot_info),canonical_code)
                            canonical_code = re.sub(r'(?<=[\.\/\?\*\,] )'+str(slot_name),str(slot_info),canonical_code)
                                                 

            return canonical_code

          

    def decanonicalize_code(self,code, slot_map):
            
            try:
                raw_code = slot_map
                    
                if len(slot_map)!= 0 and raw_code.strip() == code.strip() :
                    for slot_name,slot_info  in slot_map.items():
                        is_expr = False
                        if slot_info in raw_code:
                            if  is_expr == False and slot_info in raw_code and raw_code.index(slot_info) == 0 :
                                raw_code = re.sub(r'\b'+str(slot_info)+r'\b',str(slot_name),raw_code,1)
                            #elif raw_code.rindex(slot_info) == (len(raw_code) - len(slot_info)):

                            raw_code = re.sub(r' '+str(slot_info),' '+ slot_name,raw_code)


                            raw_code = re.sub(r' '+str(slot_info)+r' ',' ' + str(slot_name) + ' ',raw_code)
                            # specific for assembly

                            raw_code = re.sub(r'\['+str(slot_info)+r'\]','[' + str(slot_name) + ']',raw_code)

                            raw_code = re.sub(r'\{'+str(slot_info)+r'\}','{' + str(slot_name) + '}',raw_code)

                            raw_code = re.sub(r'\('+str(slot_info)+r'\)','(' + str(slot_name) + ')',raw_code)
                            #raw_code = raw_code.replace(slot_info,slot_name)
                            
                raw_code = re.sub('(?<=[\(\[]) ', '', raw_code)
                raw_code = re.sub(' (?=[:,!?\]\(\)])', '', raw_code) 
              
                    
                
                #raw_code = re.sub('\\\\n', '\\n', raw_code)
                #raw_code = re.sub('\\\"', '\"', raw_code)   
                return raw_code.strip()
            except:
                #print(code, file=sys.stderr)
                #print(slot_map, file=sys.stderr)
                #traceback.print_exc()
                raw_code = code
                for slot_name, slot_info  in slot_map.items():
                    is_expr = False
                    if slot_info in raw_code:
                        if  is_expr == False and slot_info in raw_code and raw_code.index(slot_info) == 0 :
                            raw_code = re.sub(r'\b'+str(slot_info)+r'\b',str(slot_name),raw_code,1)
                        #elif raw_code.rindex(slot_info) == (len(raw_code) - len(slot_info)):

                        raw_code = re.sub(r' '+str(slot_info),' '+ slot_name,raw_code)


                        raw_code = re.sub(r' '+str(slot_info)+r' ',' ' + str(slot_name) + ' ',raw_code)
                        # specific for assembly

                        raw_code = re.sub(r'\['+str(slot_info)+r'\]','[' + str(slot_name) + ']',raw_code)

                        raw_code = re.sub(r'\{'+str(slot_info)+r'\}','{' + str(slot_name) + '}',raw_code)

                        raw_code = re.sub(r'\('+str(slot_info)+r'\)','(' + str(slot_name) + ')',raw_code)
                        #raw_code = raw_code.replace(slot_info,slot_name)

                 #raw_code = raw_code.replace(slot_info,slot_name)

                raw_code = re.sub('(?<=[\(\[]) ', '', raw_code)
                raw_code = re.sub(' (?=[:,!?\]\(\)])', '', raw_code) 
               
                    
                #raw_code = re.sub('\\\\n', '\\n', raw_code) 
                return raw_code.strip()



    #                     if raw_code.index(slot_name) == 0:
    #                             raw_code = re.sub(r'\b'+str(slot_name)+r'\b',str(slot_info),raw_code,1)
    #                     elif raw_code.rindex(slot_name) == (len(raw_code) - len(slot_name)):
    #                             raw_code = re.sub(r' '+str(slot_name),' '+ slot_info,raw_code)


    #                     raw_code = re.sub(r' '+str(slot_name)+r' ',' ' + str(slot_info) + ' ',raw_code) 

                    #raw_code = raw_code.replace(slot_name,slot_info)

    #Strips the intent based off of the object's parameters
    def clean_intent(self, intent):
        
        if (self.lower):
            i = ''
            skip = False
            for w in intent.split(' '):
                if w not in ['False','None','True']:
                    if skip == True:
                        if w in ['\"',"\'"]:
                            skip = False
                        continue
                    if w in ['\"',"\'"]:
                        skip = True
                        continue
                        
                    i+= w.lower() + ' '
                   
                        
            intent = i

        if (self.remove_punctuation): intent = intent.translate(self.translator) 

        for rgx_match in self.remove:
            intent = re.sub(rgx_match, '', intent)

        for match, repl in self.replace.items():
            intent = match.sub(repl, intent)

        intent = re.sub(' +',' ', intent) #Clean up any extra spaces....

        #If we are using a tokenizer, use it!
        if (self.stemmer is not None):
            tokens = intent.split(" ")
            for i in range(0, len(tokens)):
                tokens[i] = self.stemmer.stem(tokens[i])
            intent = " ".join(tokens)

        return intent
