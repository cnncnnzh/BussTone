# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import requests
import fitz

def pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            output = page.get_text("blocks")
            previous_block_id = 0 # Set a variable to mark the block id
            for block in output:
                if block[6] == 0: # We only take the text
                    if previous_block_id != block[5]:
                        # Compare the block number
                        text += "\n"
                    text += block[4]
    return text

API_ENDPOINT = "https://api.sec-api.io/filing-reader"
API_KEY = "3a4102b4710db02169ba0f0a6638f8d2b155bed658ab97e283529d867133a942"

# filing_url = "https://www.sec.gov/Archives/edgar/data/1294133/000156459020006402/ingn-10k_20191231.htm"
# filing_url = "https://www.sec.gov/ix?doc=/Archives/edgar/data/1304421/000155837021001947/cnsl-20201231x10k.htm"
# filing_url = "https://www.sec.gov/Archives/edgar/data/5513/000000551322000030/unm-20211231.htm"
# filing_url = "https://www.sec.gov/Archives/edgar/data/26058/000156459022007183/cts-10k_20211231.htm"
filing_url = 'https://www.sec.gov/Archives/edgar/data/21344/000002134422000009/ko-20211231.htm'
pdf_path = r'D:\Dropbox\Shan\PDFs\filing3.pdf'
txt_path = r'D:\Dropbox\Shan\PDFs\test3.txt'

api_url = API_ENDPOINT + "?token=" + API_KEY + "&url=" + filing_url + "&type=pdf"
response = requests.get(api_url)

with open(pdf_path, 'wb') as f:
    f.write(response.content)

text = pdf_to_text(pdf_path)

with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(text)