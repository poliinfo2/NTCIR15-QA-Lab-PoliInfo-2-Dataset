# Evaluation Script for Entity Linking Task

`poliinfo2_eval_classification.py` is the script for evaluating your result of Stance Classification Task.
We confirmed this script works in the following environment:
- Python 3.7

## Usage
```
python poliinfo2_eval_classification.py -f [input_file] -g [gold_standard_file]
```
This script outputs the result to **STDOUT** in JSON format.

## Output
```
{
    "success": true,
    "rep_score": float, # representative score on the leaderboard（Accuracy）
    "version": string,  # data version
    'num_total': int,   # the number of instances in gold standard data
    'num_estimate': int,    # the number of instances in input data
    'num_correct': int, # the number of correct instances in input data
    "micro_ave": {
        "A": float,     # Accuracy
        "P賛成": float, # Precision-AGREE
        "P反対": float, # Precision-DISAGREE
        "R賛成": float, # Recall-AGREE
        "R反対": float  # Recall-DISAGREE
    },
    "ins": [
        {
            "ID": ...,
            "C賛成": int,   # the number of correct AGREE instances in input data
            "C反対": int,   # the number of correct DISAGREE instances in input data
            "T賛成": int,   # the number of AGREE instances in gold standard data
            "T反対": int,   # the number of DISAGREE instances in gold standard data
            "P賛成": float, # Precision-AGREE
            "P反対": float, # Precision-DISAGREE
            "R賛成": float, # Recall-AGREE
            "R反対": float  # Recall-DISAGREE
        },
        ...
    ]
}
```