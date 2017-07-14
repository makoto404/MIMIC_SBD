# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This source code is sentence boundary detection for MIMIC-III data preparation.
# The code will extract sentence based on a given list of topics from MIMIC-III data such as "Brief Hospital Course:", "History of Present Illness:" 
# This source code is used for data preparation in our KDD2017 conference paper under Bigdas@KDD 2017 workshop 
# and Journal paper entitled "Distant Supervision with Transductive Learning for Adverse Drug Reaction Identification from Electronic Medical Records"
# If you use our source code, please cite our paper as below.
# (tentative) Taewijit, S., Theeramunking, T. and Ikeda, M., Distant Supervision with Transductive Learning for Adverse Drug Reaction Identification from Electronic Medical Records, Journal of Healthcare Engineering, 2017

import os
import re
import sys
from datetime import datetime
from time import gmtime, strftime


class const:
    p_folder = "data/"
    p_sfolder = "data/output" + strftime("%H%M%S", gmtime()) + "/"
    f_topics_list = p_folder + "topics.lst"
    tag_row = 'rowid|'
    tag_topic = ''
    header = 'rowid|subject_id|hadm_id|sentence_order|total_sentence|count_token|tag_name|sentence_text\n'

        
# print tag
def print_tag(row_id, txt, tag_topic, f_name):
    idx = 0
    new_str_list = {}
    #split sentence
    str_list = txt.rstrip('.').split('.')
    
    for val in str_list:
        val = val.strip() 
        
        # no the first line and not start with upper case letter -> concatenate this line with the previous line.
        if re.search(r"^[\#]", val) : 
            new_str_list[idx] = val
            idx = idx + 1

        elif  (new_str_list) and (not re.search(r"^[A-Z]", val)):
            
            # before ends with str and current start with int -> separate line
            if (not re.search(r'\d+$', new_str_list[idx-1])) and (re.search(r"^[0-9]", val)):
                new_str_list[idx] = val
                idx = idx + 1
            
            # previous text not end with digit and current_text not end with digit -> concatenate line with dot
            elif (not re.search(r'\d+$', new_str_list[idx-1])) and (not re.search(r"^[0-9]", val)):
                new_str_list[idx-1] = " " + new_str_list[idx-1] + "." + val.replace('\n',' ').replace('\r',' ')
                
            # previous text starts with digit and also end with digit, current_text not start with digit -> concatenate line with dot
            elif (re.search(r'^[1-9]', new_str_list[idx-1])) and (re.search(r'\d+$', new_str_list[idx-1])) and (not re.search(r"^[0-9]", val)):
                new_str_list[idx-1] = " " + new_str_list[idx-1] + "." + val.replace('\n',' ').replace('\r',' ')
                                
            # previous text ends with digit and current_text not start with digit -> concatenate line with space
            elif (re.search(r'\d+$', new_str_list[idx-1])) and (not re.search(r"^[0-9]", val)):
                new_str_list[idx-1] = " " + new_str_list[idx-1] + " " + val.replace('\n',' ').replace('\r',' ')
                     
            else:    
                new_str_list[idx-1] = new_str_list[idx-1] + "." + val.replace('\n',' ').replace('\r',' ')
                
        else:
            new_str_list[idx] = val
            idx = idx + 1
                
    with open(f_name, 'a') as fw: 
        sentence_length = (len(new_str_list))
        
        for k, v in new_str_list.items():
            token = new_str_list[k].count(' ') + 1
            ostr = new_str_list[k] + "."
            
            #replace multiple dots with single dot
            ostr = re.sub(r'(\.)\1+', r'\1', ostr)
            
            #print only line that is more than 2 tokens
            if ((token >= 3) or ((re.search(r"^[a-zA-Z]",ostr.strip()))) and token >=2) :
                fw.write(row_id + "{0}|".format(k+1) + "{0}|".format(sentence_length) + "{0}|".format(token) + tag_topic + "|" + ostr.strip() + '\n')
                
    fw.close()  
        
        
def print_header():
    
    cdel = 0
    cexst = 0
    
    #note Loop for all generated file and add header
    for fn in os.listdir('.'):
        
        if os.path.isfile(fn):
            if os.stat(fn).st_size == 0:
                os.remove(fn)
                cdel = cdel + 1
            else:
                with open(fn, 'r+') as fw2:
                    content = fw2.read()
                    fw2.seek(0, 0)
                    fw2.write(const.header.rstrip('\r\n') + '\n' + content)
                    cexst = cexst + 1
                fw2.close()
    
    return cdel, cexst
    

def main():
    
    txt = ""
    row_id = ""
    is_intag = False
    
    if len(sys.argv) < 2:
        print "How to: Please store your data into data folder and refer <input file> by exclude folder name."
        print "Command usage: python sbd.py <input file>"
        exit()
    else:
        f_input = const.p_folder + sys.argv[1]
        print "input file : ", str(f_input)
        print "output folder: ", str(const.p_sfolder)
        
        # create new directory to store output.
        if not os.path.exists(const.p_sfolder):
            os.makedirs(const.p_sfolder)
            
        rootpath = os.getcwd()
        # read topics.lst in order to extract for each topic.  
        with open(const.f_topics_list, 'r') as fr_tp:
            # loop each line.
            for tp in fr_tp:
                
                # read the current topic to extract information from mimic discharge.
                tag_topic = tp.strip()
                
                # create new directory to keep output.
                p_ssfolder = const.p_sfolder + tag_topic.strip(':').replace(" ", "_") + "/"
                
                if not os.path.exists(p_ssfolder):
                    os.makedirs(p_ssfolder)
                    
                print "Processing topic [" + tag_topic + "].....",
                
                crow = 0
                cerr = 0
                f_name = ""
                row_id = ""
                
                f_error = p_ssfolder + re.sub('[^0-9a-zA-Z ]+', '', tag_topic).replace(" ","_") + ".err"
                
                # read file to create list of all terms.
                with open(f_input, 'r') as fr:
                    for line in fr:
                        
                        # replace duplicate dots with single dot.
                        line = re.sub(r'(\.)\1+', r'\1', line)
                        
                        # replace duplicate spaces with single space.
                        line = re.sub(r'( )\1+', r'\1', line)
                        
                        # remove newline and question mark.
                        line = line.replace('\n',' ').replace('\r',' ').replace('?','').rstrip(" ")
            
        
                        # replace white space in the de-identified text by underscore.
                        for match in re.finditer(r"\[\*\*((?!\*).)*\*\*\]", line):
                            a = match.group(0)
                            b = a.replace(' ','_') 
                            line = line.replace(a, b)
                            
                        # extract topic.
                        if const.tag_row in line:
                            if (row_id != "") and (is_intag == True) and (os.path.isfile(f_name) == False):
                                cerr = cerr + 1
                                # read a file to create a list of all terms.
                                with open(f_error, 'a') as fw3:
                                    fw3.write(str(cerr) + ". row_id = " + row_id + '\n')
                                fw3.close()
                            
                            row_id = line
                            crow = crow + 1
                            
                            # create a new file that its filename associates with a current extracted topic. 
                            f_name = p_ssfolder + re.sub('[^0-9a-zA-Z ]+', '', tag_topic).replace(" ","_") + "_" + row_id.replace("|","_").rstrip("_") + ".st"
                        elif (tag_topic.lower() in line.lower()):
                            is_intag = True                
                        elif ((re.search(r"(^[A-Z]\w+[a-z]\w+[a-zA-Z ]*\w+[:]$)", line)) or (re.search(r"(^[A-Z]\w+[A-Z]\w+[\-A-Z ]*\w+[:])", line)) or (const.tag_row in line)):
                            print_tag(row_id, txt, tag_topic, f_name)
                            # reset data for a new tag.    
                            txt = ""
                            is_intag = False
                        elif (is_intag == True):
                            txt = txt + ' ' + line
                            # replace duplicates dots with single dot.
                            txt = re.sub(r'( )\1+', r'\1', txt)
                            
                    # exception for the last document.   
                    if (is_intag):
                        print_tag(row_id, txt, tag_topic, f_name)
                        # reset data for new tag.    
                        txt = ""
                        is_intag = False
  
                fr.close()
                
                os.chdir(p_ssfolder)        
                cdel, cexst = print_header()
            
                # change path to the root path.
                os.chdir(rootpath)
                
                print "Done ( total document = " + str(crow) + " / no topic = " + str(cdel) + " / contains topic = " + str(cexst) + " / file error = " + str(cerr) +" )"
            
        fr_tp.close()
    print "\nCompleted.......100%"
    print "Have a nice day!"

if __name__ == "__main__":
    start_time = datetime.now()
    
    try:
        main()
    except Exception as e:
        print "\nError: ", str(e)
        
    end_time = datetime.now()
    print('Elapsed time: {}'.format(end_time - start_time))
    print "\n"
    
    
