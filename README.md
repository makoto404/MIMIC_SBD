# MIMIC-III SBD

A simple sentence boundary detection (sentence breaking) for MIMIC-III data preparation. The program supports data from MIMIC-III v1.3.

## Usage

1. Store your data into the folder `data`. 
2. Input a list of topics that you want to extract sentences in the file `data/topics.lst` as following example.
```
Brief Hospital Course:
History of Present Illness:
```
3. Execute the below command.

```
python sbd.py <input file>
```

## Output

Output data is located in the folder `data/output<executed time>/<topic>`.
Our program returns one output file per unique patient `(SUBJECT_ID)` and his/her hospitalization admission `(HADM_ID)`. 
The output consists of 8 columns which is separated by pipe character ('|').

```
rowid           : A row identifier to data table.
subject_id      : A patient identifier in the database
hadm_id         : A unique hospitalization for each patient in the database.
sentence_order	: An order of sentence in a document.
total_sentence	: A number of total sentences in a document.
count_token	: A number of tokens in a sentence.
tag_name	: A topic name which is extracted.
sentence_text   : An extracted sentence.
```

An example of output.

```
rowid|10094|26368|1|35|24|Brief Hospital Course:|Patient intially admitted to MICU.
rowid|10094|26368|2|35|13|Brief Hospital Course:|He was continued on antibiotics (Vanc and Zosyn).
```


## Dependencies

No dependency



## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details


## Citation

This source code is used for data preparation in our KDD2017 conference paper under Bigdas@KDD 2017 workshop and Journal paper entitled "Distant Supervision with Transductive Learning for Adverse Drug Reaction Identification from Electronic Medical Records". If you use our source code, please cite our paper as below.

```
(tentative) Taewijit, S., Theeramunking, T. and Ikeda, M., 
Distant Supervision with Transductive Learning for Adverse Drug Reaction Identification 
from Electronic Medical Records, Journal of Healthcare Engineering, 2017
```

