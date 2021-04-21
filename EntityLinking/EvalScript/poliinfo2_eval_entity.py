#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-15 QA Lab PoliInfo2 Entity Linkingタスクの自動評価スクリプト．

【入力】評価対象データはファイル入力で以下のTSV書式テキスト（タブ区切り，UTF-8 LF改行）を想定しています．
形態素\tIOB2\tメンション\twikipediaタイトル\twikipediaページ

【出力】評価結果は標準出力で以下のJSON書式です．
{
    'success': true,    // スコア計算が成功したかどうか
    'version': string   // データバージョン
    'rep_score': float, // 代表スコア（f1_title）
    'mention': {
        'accuracy': float,  // メンション抽出 Accuracy
        'precision': float, // メンション抽出 Precision
        'recall': float,    // メンション抽出 Recall
        'f1': float,        // メンション抽出 F1 value,
        'tp': int,          // メンション抽出 TP
        'tn': int,          // メンション抽出 TN
        'fp': int,          // メンション抽出 FP
        'fn': int           // メンション抽出 FN
    },
    'disambiguation': {
        'precision_title': float,   // 入力のうちBIタグの範囲とWikipediaタイトルの両者が正解だった割合
        'recall_title': float,      // 正解データのうち，BIタグの範囲とWikipediaタイトルの両者が正解だった割合
        'f1_title': float,          // BIタグの範囲とWikipediaタイトルの両者におけるF値
        'precision_range': float,   // 入力のうちBIタグの範囲が正解だった割合
        'recall_range': float,      // 正解データのうち，BIタグの範囲が正解だった割合
        'f1_range': float,          // BIタグの範囲におけるF値
        'target_count': int,        // 入力中のBIタグで示されるカタマリの数
        'gs_count': int,            // 正解データ中のBIタグで示されるカタマリの数
        'target_correct_title': int,// 入力のうちBIタグの範囲とWikipediaタイトルの両者が正解だった個数
        'gs_correct_title': int,    // 正解データのうち，BIタグの範囲とWikipediaタイトルの両者が正解だった個数
        'target_correct_range': int,// 入力のうちBIタグの範囲が正解だった個数
        'gs_correct_range': int     // 正解データのうち，BIタグの範囲が正解だった個数
    }
}

更新：2020.05.12
作成者：乙武 北斗
"""

import math
import sys
import argparse
import json
import fileinput
from typing import List
from collections import Counter

# データバージョン
DATA_VERSION = 'v20200708'


class ELInstance(object):
    def __init__(self, line: str, idx: int):
        self.index = idx
        self.morph: str = ''
        self.iob2: str = ''
        self.mention: str = None
        self.wikipedia_title: str = None
        self.wikipedia_page: str = None
        tmp = line.split("\t")
        if len(tmp) > 0:
            self.morph = tmp[0]
        if len(tmp) > 1 and tmp[1] != '':
            self.iob2 = tmp[1]
        if len(tmp) > 2 and tmp[2] != '':
            self.mention = tmp[2]
        if len(tmp) > 3 and tmp[3] != '':
            self.wikipedia_title = tmp[3]
        if len(tmp) > 4 and tmp[4] != '':
            self.wikipedia_page = tmp[4]


class MentionInstance(object):
    def __init__(self, start_el_ins: ELInstance):
        self.start_idx = start_el_ins.index
        self.mention = start_el_ins.mention
        self.wikipedia_title: str = start_el_ins.wikipedia_title
        self.wikipedia_page: str = start_el_ins.wikipedia_page
    
    def set_end_el(self, end_el_ins: ELInstance):
        self.end_idx = end_el_ins.index

class MentionEval(object):
    def __init__(self):
        self.cnt = Counter()
    
    def add_eval(self, label_gs: str, label_tg: str):
        # BIタグ以外はOとみなす
        if label_tg not in ('B', 'I'):
            label_tg = ''
        if label_gs == label_tg:
            if label_gs == '':
                self.cnt['tn'] += 1
            else:
                self.cnt['tp'] += 1
        else:
            if label_gs == '':
                self.cnt['fp'] += 1
            else:
                self.cnt['fn'] += 1
    
    def accuracy(self) -> float:
        return (self.cnt['tp'] + self.cnt['tn']) / (self.cnt['tp'] + self.cnt['tn'] + self.cnt['fp'] + self.cnt['fn'])
    
    def precision(self) -> float:
        div = self.cnt['tp'] + self.cnt['fp']
        # return self.cnt['tp'] / div if div > 0 else math.nan
        return self.cnt['tp'] / div if div > 0 else None
    
    def recall(self) -> float:
        return self.cnt['tp'] / (self.cnt['tp'] + self.cnt['fn'])
    
    def f1(self) -> float:
        p = self.precision()
        r = self.recall()
        if p is None or r is None:
            return None
        return (2 * p * r) / (p + r)


class SDEval(object):
    def __init__(self):
        self.cnt = Counter()
    
    def eval(self, m_gs: List[MentionInstance], m_tg: List[MentionInstance]):
        gs_map = {m.start_idx:m for m in m_gs}
        tg_map = {m.start_idx:m for m in m_tg}

        # precision
        for tg in m_tg:
            self.cnt['tg_cnt'] += 1
            gs = gs_map.get(tg.start_idx)
            if gs is not None and tg.end_idx == gs.end_idx:
                self.cnt['tg_crr_range'] += 1
                if gs.wikipedia_title == tg.wikipedia_title:
                    self.cnt['tg_crr_title'] += 1
        # recall
        for gs in m_gs:
            self.cnt['gs_cnt'] += 1
            tg = tg_map.get(gs.start_idx)
            if tg is not None and tg.end_idx == gs.end_idx:
                self.cnt['gs_crr_range'] += 1
                if gs.wikipedia_title == tg.wikipedia_title:
                    self.cnt['gs_crr_title'] += 1
    
    def precision_range(self):
        # return self.cnt['tg_crr_range'] / self.cnt['tg_cnt'] if self.cnt['tg_cnt'] > 0 else math.nan
        return self.cnt['tg_crr_range'] / self.cnt['tg_cnt'] if self.cnt['tg_cnt'] > 0 else None
    
    def precision_title(self):
        # return self.cnt['tg_crr_title'] / self.cnt['tg_cnt'] if self.cnt['tg_cnt'] > 0 else math.nan
        return self.cnt['tg_crr_title'] / self.cnt['tg_cnt'] if self.cnt['tg_cnt'] > 0 else None
    
    def recall_range(self):
        # return self.cnt['gs_crr_range'] / self.cnt['gs_cnt'] if self.cnt['gs_cnt'] > 0 else math.nan
        return self.cnt['gs_crr_range'] / self.cnt['gs_cnt'] if self.cnt['gs_cnt'] > 0 else None
    
    def recall_title(self):
        # return self.cnt['gs_crr_title'] / self.cnt['gs_cnt'] if self.cnt['gs_cnt'] > 0 else math.nan
        return self.cnt['gs_crr_title'] / self.cnt['gs_cnt'] if self.cnt['gs_cnt'] > 0 else None
    
    def f1_title(self) -> float:
        p = self.precision_title()
        r = self.recall_title()
        if p is None or r is None:
            return None
        return (2 * p * r) / (p + r)
    
    def f1_range(self) -> float:
        p = self.precision_range()
        r = self.recall_range()
        if p is None or r is None:
            return None
        return (2 * p * r) / (p + r)


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-15 QA Lab PoliInfo2 Entity Linkingタスクの自動評価スクリプト．

【入力】評価対象データはファイル入力で以下のTSV書式テキスト（タブ区切り，UTF-8 LF改行）を想定しています．
形態素\tIOB2\tメンション\twikipediaタイトル\twikipediaページ

【出力】評価結果は標準出力で以下のJSON書式です．
{
    'success': true,    // スコア計算が成功したかどうか
    'rep_score': float, // 代表スコア（f1_title）
    "version": string   // データバージョン
    'mention': {
        'accuracy': float,  // メンション抽出 Accuracy
        'precision': float, // メンション抽出 Precision
        'recall': float,    // メンション抽出 Recall,
        'f1': float,        // メンション抽出 F1 value,
        'tp': int,          // メンション抽出 TP
        'tn': int,          // メンション抽出 TN
        'fp': int,          // メンション抽出 FP
        'fn': int           // メンション抽出 FN
    },
    'disambiguation': {
        'precision_title': float,   // 入力のうちBIタグの範囲とWikipediaタイトルの両者が正解だった割合
        'recall_title': float,      // 正解データのうち，BIタグの範囲とWikipediaタイトルの両者が正解だった割合
        'f1_title': float,          // BIタグの範囲とWikipediaタイトルの両者におけるF値
        'precision_range': float,   // 入力のうちBIタグの範囲が正解だった割合
        'recall_range': float,      // 正解データのうち，BIタグの範囲が正解だった割合
        'f1_range': float,          // BIタグの範囲におけるF値
        'target_count': int,        // 入力中のBIタグで示されるカタマリの数
        'gs_count': int,            // 正解データ中のBIタグで示されるカタマリの数
        'target_correct_title': int,// 入力のうちBIタグの範囲とWikipediaタイトルの両者が正解だった個数
        'gs_correct_title': int,    // 正解データのうち，BIタグの範囲とWikipediaタイトルの両者が正解だった個数
        'target_correct_range': int,// 入力のうちBIタグの範囲が正解だった個数
        'gs_correct_range': int     // 正解データのうち，BIタグの範囲が正解だった個数
    }
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


def load_tsv(filepath: str) -> List[ELInstance]:
    ret = []
    for i, line in enumerate(fileinput.input(filepath)):
        if i == 0:
            continue
        ret.append(ELInstance(line.rstrip(), i-1))
    return ret


def extract_mentions(els: List[ELInstance]) -> List[MentionInstance]:
    ret = []
    current = None
    for i, ins in enumerate(els):
        if ins.iob2 == 'B':
            if current is not None:
                ret.append(current)
            current = MentionInstance(ins)
            current.set_end_el(ins)
        elif ins.iob2 == 'I':
            if current is not None:
                current.set_end_el(ins)
        else:
            if current is not None:
                ret.append(current)
                current = None
    if current is not None:
        ret.append(current)
    return ret


def main():
    args = get_args()

    # GS読み込み
    gs_els = load_tsv(args.gs_data)
    gs_mentions = extract_mentions(gs_els)
    
    # 評価対象読み込み
    tg_els = load_tsv(args.input_file)
    tg_mentions = extract_mentions(tg_els)

    m_eval = MentionEval()
    s_eval = SDEval()

    # メンション抽出
    for gs, tg in zip(gs_els, tg_els):
        m_eval.add_eval(gs.iob2, tg.iob2)
    
    # 曖昧性解消抽出
    s_eval.eval(gs_mentions, tg_mentions)
    
    # 出力
    return json.dumps({
        'success': True,
        'rep_score': s_eval.f1_title(),
        'version': DATA_VERSION,
        'mention': {
            'accuracy': m_eval.accuracy(),
            'precision': m_eval.precision(),
            'recall': m_eval.recall(),
            'f1': m_eval.f1(),
            'tp': m_eval.cnt['tp'],
            'tn': m_eval.cnt['tn'],
            'fp': m_eval.cnt['fp'],
            'fn': m_eval.cnt['fn']
        },
        'disambiguation': {
            'precision_title': s_eval.precision_title(),
            'recall_title': s_eval.recall_title(),
            'f1_title': s_eval.f1_title(),
            'precision_range': s_eval.precision_range(),
            'recall_range': s_eval.recall_range(),
            'f1_range': s_eval.f1_range(),
            'target_count': s_eval.cnt['tg_cnt'],
            'gs_count': s_eval.cnt['gs_cnt'],
            'target_correct_title': s_eval.cnt['tg_crr_title'],
            'gs_correct_title': s_eval.cnt['gs_crr_title'],
            'target_correct_range': s_eval.cnt['tg_crr_range'],
            'gs_correct_range': s_eval.cnt['gs_crr_range']
        }
    }, ensure_ascii=False)


if __name__ == "__main__":
    try:
        print(main())
    except Exception as e:
        print(e.with_traceback(), file=sys.stderr)
        print(json.dumps({'success': False}))