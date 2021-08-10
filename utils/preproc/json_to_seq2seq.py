# coding=utf-8

from __future__ import print_function
import sys, json
# import imp
# imp.reload(sys)
# sys.setdefaultencoding('utf-8')



def main():
    json_file = sys.argv[1]
    seq_input = sys.argv[2]
    seq_output = sys.argv[3]

    print('loading from: '+ str(json_file))
    dataset = json.load(open(json_file))
    with open(seq_input, 'w',encoding = 'utf-8') as f_inp, open(seq_output, 'w',encoding = 'utf-8') as f_out:
        for example in dataset:
            if 'intent_tokens'in example.keys() and 'snippet_tokens' in example.keys():
                f_inp.write(' '.join(example['intent_tokens']) + '\n')
                f_out.write(' '.join(example['snippet_tokens']) + '\n')
                
            else:
                print (example)


if __name__ == '__main__':
    main()
