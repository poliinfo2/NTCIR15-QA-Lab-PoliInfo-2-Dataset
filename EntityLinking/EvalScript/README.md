# Evaluation Script for Entity Linking Task

`poliinfo2_eval_entity.py` is the script for evaluating your result of Entity Linking Task.
We confirmed this script works in the following environment:
- Python 3.7

## Usage
```
python poliinfo2_eval_entity.py -f [input_file] -g [gold_standard_file]
```
This script outputs the result to **STDOUT** in JSON format.

## Output
```
{
    'success': true,
    'rep_score': float, # representative score on the leaderboard (f1_title)
    "version": string   # data version
    'mention': {
        'accuracy': float,  # accuracy of mention extraction
        'precision': float, # precision of mention extraction
        'recall': float,    # recall of mention extraction
        'f1': float,        # F1 score of mention extraction
        'tp': int,          # TP of mention extraction
        'tn': int,          # TN of mention extraction
        'fp': int,          # FP of mention extraction
        'fn': int           # FN of mention extraction
    },
    'disambiguation': {
        'precision_title': float,   # The proportion of correct both BI tag ranges and Wikipedia titles in input data
        'recall_title': float,      # The proportion of gold standard's both BI tag ranges and Wikipedia titles that are matched the input data
        'f1_title': float,          # F1 score calculated from 'precision_title' and 'recall_title'
        'precision_range': float,   # The proportion of correct BI tag ranges in input data
        'recall_range': float,      # The proportion of gold standard's BI tag ranges that are matched the input data
        'f1_range': float,          # F1 score calculated from 'precision_range' and 'recall_range'
        'target_count': int,        # The number of BI tag ranges in input data
        'gs_count': int,            # The number of BI tag ranges in gold standard data
        'target_correct_title': int,# The number of correct both BI tag ranges and Wikipedia titles in input data
        'gs_correct_title': int,    # The number of gold standard's both BI tag ranges and Wikipedia titles that are matched the input data
        'target_correct_range': int,# The number of correct BI tag ranges in input data
        'gs_correct_range': int     # The number of gold standard's BI tag ranges that are matched the input data
    }
}
```