# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import pandas as pd
from busstone.extract_script import html_to_txt, get_paragraph, gen_script
import os 
import torch

class Score():
    
    def __init__(self, root,
                 result_root,
                 to_txt,
                 write_script):
        self.columns = ['KID', 'Year', 'Label', 'Positive', 'Negative', 'Neutral']
        self.root = root
        if not os.path.exists(result_root):
            os.mkdir(result_root)
        self.result_root = result_root
        self.to_txt = to_txt
        self.table = pd.DataFrame(columns=self.columns)
        self.write_script = write_script

    def gen_score(self, model, tokenizer, split_sentence):
        all_files = sorted(os.listdir(self.root))
        for kid in all_files[0:10]:
            path1 = os.path.join(os.path.join(self.root, kid), r'10-K')
            for kid_v in os.listdir(path1):
                print('analyzing {} ...'.format(kid_v))
                
                kid, year, _ = kid_v.split('-')
                root = os.path.join(path1, kid_v)
                dirc = os.path.join(root, 'full-submission.txt')
                to_dirc = os.path.join(root, 'script.txt')
                
                #convert html to txt
                if self.to_txt == 'true':
                    html_to_txt(dirc, to_dirc)
                
                #extract all the paragraphs
                all_scripts = get_paragraph(to_dirc, split_sentence)
                
                # save extracted paragraphs
                if self.write_script == 'true':
                    to_file = os.path.join(self.result_root, kid + '-' + year + '.txt')
                    
                    gen_script(all_scripts, to_file)
                    
                # generate tone scores
                for i, script in enumerate(all_scripts):
                    inputs = tokenizer(script, return_tensors="pt")   
                    with torch.no_grad():
                        logits = model(**inputs).logits.squeeze().tolist()
                    self.table = pd.concat([self.table, pd.DataFrame(
                        {
                            'KID':[kid],
                            'Year':[year],
                            'Label':[i],
                            'Positive':[logits[0]],
                            'Negative':[logits[1]],
                            'Neutral':[logits[2]]
                        }
                    )], ignore_index=True)
                    # print(self.table)
                    if self.write_script == 'true':
                        with open(to_file, 'a', encoding='utf-8') as f:
                            f.write('\n')
                            f.write(str(logits))
        
    def write_score(self):
        to_file = os.path.join(self.result_root, 'score.xlsx')
        self.table.to_excel(to_file)
        

    