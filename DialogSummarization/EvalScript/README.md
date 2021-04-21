# Evaluation Script for Entity Linking Task

`poliinfo2_eval_summarization_cli.py` is the script for evaluating your result of Dialog Summarization Task.

We confirmed this script works in the following environment:
- Python 3.7
- MeCab
- mecab-python3
- unidic-cwj-2.3.0

## Usage
```
python poliinfo2_eval_summarization_cli.py -f [input_file] -g [gold_standard_file] -d [unidic_path]
```
This script outputs the result to **STDOUT** in JSON format.

This script uses [Lin's ROUGE](#citation) scripts which we modified to support Japanese language by removing filters.
The ROUGE scripts are contained in **rouge** folder. 

## Output
```
{
    "success": true,
    "rep_score": float, # representative score on the leaderboard（ROUGE-1-R.内容語）
    "macro_ave": {
        "available_rate": {                   # available rate of input instances
            "QA": float # both questions and answers
            "Q": float  # questions
            "A": float  # answers
        },
        "available": {                      # ROUGE scores of available input instances
            "QA": {"R1": ..., "R2": ..., },
            "Q": {"R1": ..., "R2": ..., }, 
            "A": {"R1": ..., "R2": ..., }  
        },
        "total": {                          # ROUGE scores of all input instances
            "QA": {"R1": ..., "R2": ..., },
            "Q": {"R1": ..., "R2": ..., },
            "A": {"R1": ..., "R2": ..., }
        }
    },
    "ins": [
        {
            "ID": ...,
            "QA": {"available: bool, "R1": ..., "R2": ..., },
            "Q": {"available: bool, "R1": ..., "R2": ..., }, 
            "A": {"available: bool, "R1": ..., "R2": ..., }  
        },
        ...
    ]
}
```

## Citation
```
@inproceedings{lin-2004-rouge,
    title = "{ROUGE}: A Package for Automatic Evaluation of Summaries",
    author = "Lin, Chin-Yew",
    booktitle = "Text Summarization Branches Out",
    month = jul,
    year = "2004",
    address = "Barcelona, Spain",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W04-1013",
    pages = "74--81",
}
```
