# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import pandas as pd
import os 
import torch
import traceback

from busstone.extract_script import html_to_txt, get_paragraph, gen_script
from busstone.extract_pdf import delete_page_break, html_to_pdf, extract

class Score():
    
    def __init__(self, root,
                 result_root,
                 to_txt,
                 to_pdf,
                 write_script,
                 split):
        self.columns = ['KID', 'Year', 'Label', 'Positive', 'Negative', 'Neutral', 'Character_count']
        self.root = root
        if not os.path.exists(result_root):
            os.mkdir(result_root)
        self.result_root = result_root
        self.to_txt = to_txt
        self.to_pdf = to_pdf
        self.table = pd.DataFrame(columns=self.columns)
        self.write_script = write_script
        self.split = split

    def gen_score(self, model, tokenizer):
        all_files = sorted(os.listdir(self.root))
        log_file = os.path.join(self.result_root, 'log.txt')
        for kid in all_files[500:600] + all_files[0:100]:
            try:
                path1 = os.path.join(os.path.join(self.root, kid), r'10-K')
                for kid_v in os.listdir(path1):
                    print('analyzing {} ...'.format(kid_v))
                    prekid, date = kid_v.split('_')
                    # kid, year, _ = prekid.split('-')
                    root = os.path.join(path1, kid_v)
                    # dirc = os.path.join(root, 'full-submission.txt')
                    # to_dirc = os.path.join(root, 'script.txt')
                    # html = os.path.join(root, 'primary-document.html')
                    # to_html = os.path.join(root, 'primary-document-nobreak.html')
                    # delete_page_break(html, to_html)
                    
                    dirc = os.path.join(root, 'primary-document.html')
                    
                    to_dirc = os.path.join(root, 'script.pdf')
                    
                    #convert html to txt
                    # if self.to_txt == 'true':
                        # html_to_txt(dirc, to_dirc)
                    if self.to_pdf == 'true':
                        html_to_pdf(dirc, to_dirc)
                    elif os.path.exists(to_dirc):
                        print('{} existed'.format(to_dirc))
                    else:
                        Exception('Error: {} not found'.format(to_dirc)) 
                        
                    #extract all the paragraphs
                    paragraphs, sentences = extract(to_dirc)
                    # all_scripts, need_check = get_paragraph(to_dirc, split_sentence)
                    # save extracted paragraphs
                    to_file = os.path.join(self.result_root, kid + '-' + date + '.txt')
                    # if need_check:
                    #     to_file = os.path.join(self.result_root, 'CHECK_' + kid + '-' + date + '.txt')
                    # else:
                    #     to_file = os.path.join(self.result_root, kid + '-' + date + '.txt')
                    
                    # generate tone scores
                    
                    all_scripts = sentences if self.split == 'true' else paragraphs
                    for i, script in enumerate(all_scripts):
                        if len(script) < 35:
                            if self.write_script == 'true':
                                gen_script(script, to_file)
                            continue         
                        inputs = tokenizer(script, return_tensors="pt")   
                        with torch.no_grad():
                            logits = model(**inputs).logits.squeeze().tolist()
                        self.table = pd.concat([self.table, pd.DataFrame(
                            {
                                'KID':[kid],
                                'Date':[date],
                                'Label':[i],
                                'Positive':[logits[0]],
                                'Negative':[logits[1]],
                                'Neutral':[logits[2]],
                                'Character_count':len(script)
                            }
                        )], ignore_index=True)
                        # print(self.table)
                        if self.write_script == 'true':
                            gen_script(script, to_file)
                            gen_script(str(logits), to_file)
            except:
                print('Analyzing {} not successful'.format(dirc))
                with open (log_file, 'a', encoding='utf-8') as f:
                    f.write('Analyzing {} not successful'.format(dirc))
                    f.write(traceback.format_exc())
                    f.write('------------------')
                  
        
    def write_score(self):
        to_file = os.path.join(self.result_root, 'score.xlsx')
        self.table.to_excel(to_file)
        

    