#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-15 QA Lab PoliInfo2 Stance Classificationタスクの自動評価スクリプト．

【入力】評価対象データはファイル入力で以下のJSON書式を想定しています．
[
    {"ID": ..., "ProsConsPartyListBinary": {"自民党": "賛成", ...}},
    {"ID": ..., },
    ...
]

【出力】評価結果は標準出力で以下のJSON書式です．
{
    "success": true,    // スコア計算が成功したかどうか
    "rep_score": float, // 代表スコア（Accuracy）
    "version": string,  // データバージョン
    'num_total': int,   // GSデータのインスタンス総数
    'num_estimate': int,    // 入力データの有効インスタンス数
    'num_correct': int, // 入力データの正解インスタンス数
    "micro_ave": {
        "A": float,     // Accuracy
        "P賛成": float, // Precision-賛成
        "P反対": float, // Precision-反対
        "R賛成": float, // Recall-賛成
        "R反対": float  // Recall-反対
    },
    "ins": [
        {
            "ID": ...,
            "C賛成": int,   // 正解した賛成の数
            "C反対": int,   // 正解した反対の数
            "T賛成": int,   // GSデータの賛成の数
            "T反対": int,   // GSデータの反対の数
            "P賛成": float, // Precision-賛成
            "P反対": float, // Precision-反対
            "R賛成": float, // Recall-賛成
            "R反対": float  // Recall-反対
        },
        ...
    ]
}

更新：2020.07.05
作成者：乙武 北斗
"""

import math
import sys
import argparse
import json
from collections import Counter
from typing import List, Dict

# データバージョン
DATA_VERSION = 'v20200708'

# 古いIDの接頭辞
old_id_prefix = [
    'PoliInfo2-StanceClassification-JA-Dry-Test-00',
    'PoliInfo2-StanceClassification-JA-Dry-Test-v20200522-',
    'PoliInfo2-StanceClassification-JA-Dry-Test-v20200605-'
]


class SCInstance(object):
    def __init__(self, json_obj: dict):
        self.id: str = json_obj['ID']
        self.pc_parties: Dict[str, str] = json_obj['ProsConsPartyListBinary']


class EvalInstance(object):
    def __init__(self, ins_id: str):
        self.id: str = ins_id
        self.c: Dict[str, int] = Counter()
        self.e: Dict[str, int] = Counter()
        self.t: Dict[str, int] = Counter()
    
    def num_total(self) -> int:
        return sum(self.t.values())
    
    def num_correct(self) -> int:
        return sum(self.c.values())
    
    def num_estimate(self) -> int:
        return sum(self.e.values())
    
    def precision(self, target: str) -> float:
        # return self.c[target] / self.e[target] if self.e[target] > 0 else math.nan
        return self.c[target] / self.e[target] if self.e[target] > 0 else None
    
    def recall(self, target: str) -> float:
        # return self.c[target] / self.t[target] if self.t[target] > 0 else math.nan
        return self.c[target] / self.t[target] if self.t[target] > 0 else None
    
    def accuracy(self) -> float:
        return self.num_correct() / self.num_total()
    
    def to_dict(self) -> dict:
        return {
            'ID': self.id,
            'C賛成': self.c['賛成'],
            'C反対': self.c['反対'],
            'T賛成': self.t['賛成'],
            'T反対': self.t['反対'],
            'P賛成': self.precision('賛成'),
            'P反対': self.precision('反対'),
            'R賛成': self.recall('賛成'),
            'R反対': self.recall('反対')
        }


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-15 QA Lab PoliInfo2 Stance Classificationタスクの自動評価スクリプト．

【入力】評価対象データはファイル入力で以下のJSON書式を想定しています．
[
    {"ID": ..., "ProsConsPartyListBinary": {"自民党": "賛成", ...}},
    {"ID": ..., },
    ...
]

【出力】評価結果は標準出力で以下のJSON書式です．
{
    "success": true,    // スコア計算が成功したかどうか
    "rep_score": float, // 代表スコア（Accuracy）
    "version": string,  // データバージョン
    'num_total': int,   // GSデータのインスタンス総数
    'num_estimate': int,    // 入力データの有効インスタンス数
    'num_correct': int, // 入力データの正解インスタンス数
    "micro_ave": {
        "A": float,     // Accuracy
        "P賛成": float, // Precision-賛成
        "P反対": float, // Precision-反対
        "R賛成": float, // Recall-賛成
        "R反対": float  // Recall-反対
    },
    "ins": [
        {
            "ID": ...,
            "C賛成": int,   // 正解した賛成の数
            "C反対": int,   // 正解した反対の数
            "T賛成": int,   // GSデータの賛成の数
            "T反対": int,   // GSデータの反対の数
            "P賛成": float, // Precision-賛成
            "P反対": float, // Precision-反対
            "R賛成": float, // Recall-賛成
            "R反対": float  // Recall-反対
        },
        ...
    ]
}""")

    parser.add_argument('-g', '--gs-data',
                        required=True,
                        help='GSデータを指定します'
                        )
    
    parser.add_argument('-f', '--input-file',
                        required=True,
                        help='入力データを指定します'
                        )
    return parser.parse_args()


def load_json(json_str: str) -> Dict[str, SCInstance]:
    return {x['ID']: SCInstance(x) for x in json.loads(json_str)}


def main():
    args = get_args()

    # GS読み込み
    with open(args.gs_data) as f:
        gss = load_json(f.read())
    
    # 評価対象読み込み
    with open(args.input_file) as f:
        targets = load_json(f.read())
    
    # 古いIDチェック
    if len(targets) > 0:
        if any([list(targets.keys())[0].startswith(prefix) for prefix in old_id_prefix]):
            raise Exception('入力データのIDが古いバージョンになっています．')
    
    # 評価結果
    evals: Dict[str, EvalInstance] = {}
    total_eval = EvalInstance('#TOTAL#')

    # GSデータ各々に対して
    for gs in gss.values():
        gs: SCInstance
        target = targets.get(gs.id)

        ev = EvalInstance(gs.id)

        for party, label in gs.pc_parties.items():
            ev.t[label] += 1
            total_eval.t[label] += 1
            if target is not None:
                ev.e[target.pc_parties[party]] += 1
                total_eval.e[target.pc_parties[party]] += 1
                if label == target.pc_parties[party]:
                    ev.c[label] += 1
                    total_eval.c[label] += 1
    
        # スコアの記録
        evals[gs.id] = ev

    # 評価データ各々に対して
    # for target in targets.values():
    #     target: SCInstance
    #     gs: SCInstance = gss.get(target.id)

    #     # IDチェック
    #     if gs is None:
    #         # print(f'入力データのIDがGSデータ上で見つかりません．(id={target.id})', file=sys.stderr)
    #         # exit(1)
    #         raise Exception(f'入力データに不正なIDがありました．(id={target.id})')
        
    #     ev = EvalInstance(gs.id)

    #     for party, label in gs.pc_parties.items():
    #         ev.t[label] += 1
    #         total_eval.t[label] += 1
    #         ev.e[target.pc_parties[party]] += 1
    #         total_eval.e[target.pc_parties[party]] += 1
    #         if label == target.pc_parties[party]:
    #             ev.c[label] += 1
    #             total_eval.c[label] += 1
    
    #     # スコアの記録
    #     evals[target.id] = ev
    
    # 出力
    return json.dumps({
        'success': True,
        'rep_score': total_eval.accuracy(),
        'version': DATA_VERSION,
        'num_total': total_eval.num_total(),
        'num_estimate': total_eval.num_estimate(),
        'num_correct': total_eval.num_correct(),
        'micro_ave': {
            'A': total_eval.accuracy(),
            'P賛成': total_eval.precision('賛成'),
            'P反対': total_eval.precision('反対'),
            'R賛成': total_eval.recall('賛成'),
            'R反対': total_eval.recall('反対')
        },
        'ins': [ev.to_dict() for ev in evals.values()]
    }, ensure_ascii=False)


if __name__ == "__main__":
    try:
        print(main())
    except Exception as e:
        tb = sys.exc_info()[2]
        print(e.with_traceback(tb), file=sys.stderr)
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False))
