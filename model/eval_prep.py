import json
import argparse

dataset = 'Shellcode_IA32'
f = open('model/finetuned_model/'+ str(dataset) +'/test_1.gold')
f2 = open('model/finetuned_model/'+ str(dataset) +'/test_1.output')
gold_list = f.readlines()
output_list = f2.readlines()

def clean_code (code_list):
    for i in range(0,len(code_list)):
        if code_list[i][-1] == '\n':
            code_list[i] = code_list[i][:-1]
        tab_index = code_list[i].index('\t')
        code_list[i] = code_list[i][tab_index+1:]
    return code_list
gold_list= clean_code(gold_list)
output_list = clean_code(output_list)

f3 = open('model/finetuned_model/'+ str(dataset) +'/test_1.hyp','w+')
for s in output_list:
    f3.write(s+'\n')
f3.close()
print('Final Evaluation of ShellBe on the {} testset:'.format(dataset))