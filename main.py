# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import argparse
from busstone.get_score import Score
from busstone.extract_script import html_to_txt
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from busstone.download_SEC import download_files
import sys

parser = argparse.ArgumentParser(description='busstone')

parser.add_argument(
        "--mode",
        type=str,
        default="calculate",
        help="'download' for downloading SEC files; 'calculate' for calculating the tone scores"
)
parser.add_argument(
        "--date_files",
        type=str,
        help="determine whether the paragraph is splitted into sentences"
)
parser.add_argument(
        "--folder",
        type=str,
        help="determine whether the paragraph is splitted into sentences"
)
parser.add_argument(
        "--root_dir",
        type=str,
        help="root directory of all SEC files"
)
parser.add_argument(
        "--result_dir",
        default="results",
        type=str,
        help="directory where results are saved"
)
parser.add_argument(
        "--write_script",
        default='true',
        type=str,
        help="determine if the extracted paragraphs are saved"
)
parser.add_argument(
        "--to_txt",
        default='true',
        type=str,
        help="determine if the html is converted to txt"
)
parser.add_argument(
        "--to_pdf",
        default='true',
        type=str,
        help="determine if the html is converted to pdf"
)
parser.add_argument(
        "--split",
        default='false',
        type=str,
        help="determine whether the paragraph is splitted into sentences"
)



args = parser.parse_args(sys.argv[1:])

if args.mode == "calculate":
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    
    score = Score(
        args.root_dir,
        args.result_dir,
        args.to_txt.lower(),
        args.to_pdf.lower(),
        args.write_script.lower(),
        args.split.lower()
    )
    score.gen_score(model, tokenizer)
    #score.write_score()

elif args.mode == "download":
    download_files(args.date_files, args.folder)