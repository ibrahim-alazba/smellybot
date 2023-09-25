#!/usr/bin/env python
# coding: utf-8

import requests
import os
import pandas as pd
import re


classes_file = os.path.join('data_classes.csv') #'bot\data_classes.csv'
methods_file = os.path.join('data_methods.csv') 

url_dc= "https://detdataclass-dy5owqlgaq-ww.a.run.app"
url_gc= "https://detgodclass-dy5owqlgaq-ww.a.run.app"
url_fe= "https://detfeatureenvy-dy5owqlgaq-ww.a.run.app"
url_lm= "https://detlongmethod-dy5owqlgaq-ww.a.run.app"


urls_file = {'DC': (url_dc, classes_file ), 
             'GC': (url_gc, classes_file), 
             'FE': (url_fe, methods_file), 
             'LM': (url_lm, methods_file)}



def get_results(url_file):

    resp = requests.post(url_file[0], files={'cfile': open(url_file[1] , 'rb')})
    #print(resp.content)

    return resp


def save_report(reportdf, smellytype):

    # Convert DataFrame to Markdown table
    if smellytype=='class':
        markdown_table = reportdf[['File', 'Class', 'isDC', 'isGC']].to_markdown(index=False)
    elif smellytype=='method':
        markdown_table = reportdf[['File', 'Method', 'isFE', 'isLM']].to_markdown(index=False)

    # Save Markdown table to a txt file
    with open(smellytype+'_smelly_report.md', 'w') as f:
        f.write(markdown_table)

# Define a function to clean the code
def clean_code(code):
    cleaned_code = re.sub(r'[^a-zA-Z0-9+\-=()\[\];,<>{}*!&|\/~%^]', ' ', code)  # Replace non-letter characters with spaces
    cleaned_code = re.sub(r'\s+', ' ', cleaned_code)  # Replace multiple spaces with a single space
    return cleaned_code.strip()  # Remove leading and trailing spaces



def main():

    classes_df = pd.read_csv(classes_file)
    methods_df = pd.read_csv(methods_file)

    classes_df = classes_df.dropna()
    methods_df = methods_df.dropna()

    # Apply the cleaning function to the 'code' column
    classes_df['Code'] = classes_df['Code'].apply(clean_code)
    methods_df['Code'] = methods_df['Code'].apply(clean_code)

    #classes_df.to_csv('clean_classes.csv')
    #methods_df.to_csv('clean_methods.csv')


    for key in urls_file.keys():

        print(key, '->', urls_file[key])
        cs = urls_file[key]
        resp = get_results(cs)

        print(resp)
        result = resp.json()
        if key in ['DC', 'GC']:
            classes_df['is'+ key] = list(result.values())[0]
            classes_df['is'+ key] = classes_df['is'+ key].astype(int) 

        elif key in ['FE', 'LM']:
            methods_df['is'+ key] = list(result.values())[0]
            methods_df['is'+ key] = methods_df['is'+ key].astype(int) 
        #print(methods_df)

    classes_df = classes_df.loc[(classes_df['isDC'] == 1) | (classes_df['isGC'] == 1)]
    methods_df = methods_df.loc[(methods_df['isFE'] == 1) | (methods_df['isLM'] == 1)]
    
    save_report(classes_df, 'class')
    save_report(methods_df, 'method')

    #print(resp.json())



if __name__ == "__main__":
    main()
