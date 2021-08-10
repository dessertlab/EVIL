
# coding: utf-8

# In[10]:




import json
import sys
import argparse
import random
import os
import math
import re

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        
def str2int(v):
    if isinstance(v, int):
        return v
    else:
        try:
            i = int(v)
            return i
        except ValueError:

            raise argparse.ArgumentTypeError('Integer value expected.')



parser = argparse.ArgumentParser(description='Convert text dataset to json datasets')
parser.add_argument('intent', help='Directory location of the file containing English intents')
parser.add_argument('snippet', help='Directory location of the file containing  code snippets')
parser.add_argument('--split', type = str2bool, const= True, default = False, nargs = '?',
                    help='If True Splits files into train and test using 80% train, 10% dev and 10% test.')

parser.add_argument('--train', type = str2int , nargs = '?',
                    help='Specifies the number of intent-snippet pairs to use in training.')
parser.add_argument('--dev', type = str2int , nargs = '?',
                    help='Specifies the number of intent-snippet pairs to use in training.')

parser.add_argument('--test', type = str2int , nargs = '?',
                    help='Specifies the number of intent-snippet pairs to use in training.')

parser.add_argument('--django', type = str2bool, const= True, default = False, nargs = '?',
                    help='Special flag only when using the Django dataset')



args = parser.parse_args()


intent_file = open(str(args.intent), 'r')
code_file = open(str(args.snippet), 'r')


if args.django == False:
    intent_arr = intent_file.readlines()
    code_arr = code_file.readlines()
else:
    intent_text = intent_file.read()
    #re.sub('\n^().   ','') -> remove new line on lines that have ".   "
    #intent_arr = intent_file.read().split('.\n')
    intent_mismatch = re.findall(r'\n[a-z0-9A-Z\_\[\] \.\,\*\(\)\-\+\&\^\%\$\#\!\'\"\:\;\<\>\?\/\{\}=]+\.   ', intent_text)
    for intent in intent_mismatch:
            intent_text = intent_text.replace(intent,intent[1:]+'\n')
    intent_arr = intent_text.split('\n')[:-1]
    print(intent_text.split('\n')[-1])
    code_arr = code_file.readlines() # need to figure out how to do this - maybe human annotation.

if len(intent_arr) != len(code_arr):
    print('Snippets #: ' + str(len(code_arr)))
    print('Intents #: ' + str(len(intent_arr)))
    raise Exception('Number of intents does not match number of snippets - please check the files')
    
    
base = os.path.basename(str(args.intent))
file_name = os.path.splitext(base)[0]

if args.split == True and (args.train is not None or args.dev is not None or args.test is not None):
    raise Exception('Can\'t use default split and specify number of train,dev, and test pairs. Choose one or the other')
elif args.split == True:
    
    random.seed(230)
    temp = list(zip(intent_arr, code_arr))
    random.shuffle(temp)
    intent_arr, code_arr = zip(*temp)
    split_1 = math.ceil(len(intent_arr) * 0.8)
    split_2 = math.ceil(len(intent_arr) * 0.9)
    
    train_intent_arr = intent_arr[:split_1]
    train_code_arr = code_arr[:split_1]
    
    dev_intent_arr = intent_arr[split_1:split_2]
    dev_code_arr = code_arr[split_1:split_2]
    
    test_intent_arr = intent_arr[split_2:]
    test_code_arr = code_arr[split_2:]
    
    # Testset
    if len(test_intent_arr) == len(test_code_arr):
        test_json_arr = []
        for file_1_line, file_2_line in zip(test_intent_arr, test_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            test_json_arr.append(json_temp)
        test_output_file = open(file_name +'-test.json', 'w')
        json_string = "["
        for i in range(len(test_json_arr)):
            if (i < len(test_json_arr) - 1):
                json_string = json_string + test_json_arr[i] + ","
            else:
                json_string = json_string + test_json_arr[i]
        json_string = json_string + "]"
        test_output_file.write(json_string)
        test_output_file.close()
    else:
         raise Exception('Number of test intents does not match number of snippets - please check the files')
            
            
    # Train set
    if len(train_intent_arr) == len(train_code_arr):
        train_json_arr = []
        for file_1_line, file_2_line in zip(train_intent_arr, train_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            train_json_arr.append(json_temp)
        train_output_file = open(file_name+'-train.json', 'w')
        json_string = "["
        for i in range(len(train_json_arr)):
            if(i < len(train_json_arr)-1):
                json_string = json_string + train_json_arr[i] + ","
            else:
                json_string = json_string + train_json_arr[i]
        json_string = json_string + "]"
        train_output_file.write(json_string)
        train_output_file.close()
    else:
         raise Exception('Number of training intents does not match number of snippets - please check the files')
            
            
            
     # Dev set       
    if len(dev_intent_arr) == len(dev_code_arr):
        dev_json_arr = []
        for file_1_line, file_2_line in zip(dev_intent_arr, dev_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            dev_json_arr.append(json_temp)
        dev_output_file = open(file_name +'-dev.json', 'w')
        json_string = "["
        for i in range(len(dev_json_arr)):
            if(i < len(dev_json_arr)-1):
                json_string = json_string + dev_json_arr[i] + ","
            else:
                json_string = json_string + dev_json_arr[i]
        json_string = json_string + "]"
        dev_output_file.write(json_string)
        dev_output_file.close()
    else:
         raise Exception('Number of dev intents does not match number of snippets - please check the files')
elif (args.train is not None or args.dev is not None or args.test is not None) and (args.train is None or args.dev is None or args.test is None):
    raise Exception('All args of train, dev, and test must be specified, if one of them is specified.')
    
elif (args.train is not None and args.dev is not None and args.test is not None):
    random.seed(230)
    temp = list(zip(intent_arr, code_arr))
    random.shuffle(temp)
    intent_arr, code_arr = zip(*temp)
    split_1 = math.ceil(args.train)
    split_2 = math.ceil(args.train+args.dev)
    
    train_intent_arr = intent_arr[:split_1]
    train_code_arr = code_arr[:split_1]
    
    dev_intent_arr = intent_arr[split_1:split_2]
    dev_code_arr = code_arr[split_1:split_2]
    
    test_intent_arr = intent_arr[split_2:]
    test_code_arr = code_arr[split_2:]
    
    # Testset
    if len(test_intent_arr) == len(test_code_arr):
        test_json_arr = []
        for file_1_line, file_2_line in zip(test_intent_arr, test_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            test_json_arr.append(json_temp)
        test_output_file = open(file_name +'-test.json', 'w')
        json_string = "["
        for i in range(len(test_json_arr)):
            if (i < len(test_json_arr) - 1):
                json_string = json_string + test_json_arr[i] + ","
            else:
                json_string = json_string + test_json_arr[i]
        json_string = json_string + "]"
        test_output_file.write(json_string)
        test_output_file.close()
    else:
         raise Exception('Number of test intents does not match number of snippets - please check the files')
            
            
    # Train set
    if len(train_intent_arr) == len(train_code_arr):
        train_json_arr = []
        for file_1_line, file_2_line in zip(train_intent_arr, train_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            train_json_arr.append(json_temp)
        train_output_file = open(file_name+'-train.json', 'w')
        json_string = "["
        for i in range(len(train_json_arr)):
            if(i < len(train_json_arr)-1):
                json_string = json_string + train_json_arr[i] + ","
            else:
                json_string = json_string + train_json_arr[i]
        json_string = json_string + "]"
        train_output_file.write(json_string)
        train_output_file.close()
    else:
         raise Exception('Number of training intents does not match number of snippets - please check the files')
            
            
            
     # Dev set       
    if len(dev_intent_arr) == len(dev_code_arr):
        dev_json_arr = []
        for file_1_line, file_2_line in zip(dev_intent_arr, dev_code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            dev_json_arr.append(json_temp)
        dev_output_file = open(file_name +'-dev.json', 'w')
        json_string = "["
        for i in range(len(dev_json_arr)):
            if(i < len(dev_json_arr)-1):
                json_string = json_string + dev_json_arr[i] + ","
            else:
                json_string = json_string + dev_json_arr[i]
        json_string = json_string + "]"
        dev_output_file.write(json_string)
        dev_output_file.close()
    
# If no split           
else:
    
    if len(intent_arr) == len(code_arr):
        json_arr = []
        for file_1_line, file_2_line in zip(intent_arr, code_arr):
            json_data = {"intent": file_1_line.strip(), "rewritten_intent": file_1_line.strip(), "snippet": file_2_line.strip()}
            json_temp = json.dumps(json_data)
            json_arr.append(json_temp)
        output_file = open(file_name+'.json', 'w')
        json_string = "["
        for i in range(len(json_arr)):
            if(i < len(json_arr)-1):
                json_string = json_string + json_arr[i] + ","
            else:
                json_string = json_string + json_arr[i]
        json_string = json_string + "]"
        output_file.write(json_string)
        output_file.close()
    else:
         raise Exception('Number of intents does not match number of snippets - please check the files')
    

print ('Done!')
