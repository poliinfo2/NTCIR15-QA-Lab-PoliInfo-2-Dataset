#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-15 QA Lab PoliInfo2 Dialog SummarizationタスクのROUGE自動評価スクリプト．
動作要件として，以下のモジュールが必要です．
・mecab-python3

【入力】評価対象データはファイル入力で以下のJSON書式を想定しています．
[
    {"ID": ..., },
    {"ID": ..., },
    ...
]

【出力】評価結果は標準出力で以下のJSON書式です．
{
    "success": true,    // スコア計算が成功したかどうか
    "rep_score": float, // 代表スコア（ROUGE-1-R 内容語のマクロ平均）
    "macro_ave": {
        "available_rate": {                   // 有効回答率
            "QA": float
            "Q": float
            "A": float
        },
        "available": {                        // 有効回答のみのスコア
            "QA": {"R1": ..., "R2": ..., }, // QA両方
            "Q": {"R1": ..., "R2": ..., },  // Qのみ
            "A": {"R1": ..., "R2": ..., }   // Aのみ
        },
        "total": {                            // トータルのスコア
            "QA": {"R1": ..., "R2": ..., },
            "Q": {"R1": ..., "R2": ..., },
            "A": {"R1": ..., "R2": ..., }
        }
    },
    "ins": [
        {
            "ID": ...,
            "QA": {"available: bool, "R1": ..., "R2": ..., }, // QA両方
            "Q": {"available: bool, "R1": ..., "R2": ..., },  // Qのみ
            "A": {"available: bool, "R1": ..., "R2": ..., }   // Aのみ
        },
        ...
    ]
}

更新：2020.07.06
作成者：乙武 北斗
"""

import sys
import argparse
import json
import MeCab
import re
import math
import fileinput
import numpy as np
from collections import defaultdict
from rouge.pythonrouge import Pythonrouge
from typing import Dict, Tuple, Optional, TypeVar, List, Union
from tqdm import tqdm

# データバージョン
DATA_VERSION = 'v20200708'

# 古いIDの接頭辞
old_id_prefix = [
    'PoliInfo2-DialogSummarization-JA-Dry-Test-00'
]

T = TypeVar('T')

functional_verbs = {"為る", "居る", "成る", "有る"}
content_words = ["助詞", "助動詞", "感動詞", "空白", "補助記号", "記号-一般"]
adverbial_nouns = {"所", "為", "くらい"}
formal_nouns = {"の", "事", "物", "積り", "訳"}
numeral_notation1_regex = re.compile(
    r'([^兆億万]+兆)?([^兆億万]+億)?([^兆億万]+万)?([^兆億万]*)')
numeral_notation2_regex = re.compile(
    r'([^千百十]*千)?([^千百十]*百)?([^千百十]*十)?([^千百十]*)')


class DSInstance(object):
    def __init__(self, json_obj: dict):
        self.id: str = json_obj['ID']
        self.date: str = json_obj['Date']
        self.prefecture: str = json_obj['Prefecture']
        self.meeting: str = json_obj['Meeting']
        self.main_topic: str = json_obj['MainTopic']
        self.question_speaker: str = json_obj['QuestionSpeaker']
        self.sub_topic: str = json_obj['SubTopic']
        self.question_summary: str = json_obj['QuestionSummary']
        self.question_length: int = json_obj['QuestionLength']
        self.question_starting_line: int = json_obj['QuestionStartingLine']
        self.question_ending_line: int = json_obj['QuestionEndingLine']
        self.answer_speaker: List[str] = json_obj['AnswerSpeaker']
        self.answer_summary: List[str] = json_obj['AnswerSummary']
        self.answer_length: List[int] = json_obj['AnswerLength']
        self.answer_starting_line: List[int] = json_obj['AnswerStartingLine']
        self.answer_ending_line: List[int] = json_obj['AnswerEndingLine']


class EvalInstance(object):
    def __init__(self, ins_id: str):
        self.id: str = ins_id
        self.qa: Dict[str, Union[bool, float]] = {'available': False}
        self.q: Dict[str, Union[bool, float]] = {'available': False}
        self.a: Dict[str, Union[bool, float]] = {'available': False}
    
    def __getitem__(self, key):
        if key == 'Q':
            return self.q
        if key == 'A':
            return self.a
        return self.qa
    
    def toDict(self) -> dict:
        return {
            'ID': self.id,
            'QA': self.qa,
            'Q': self.q,
            'A': self.a
        }


class Stats(object):
    def __init__(self, rouge_types: List[str], extract_types: List[str]):
        self.n_t: int = 0
        self.n_a: Dict[str, int] = {
            'QA': 0,
            'Q': 0,
            'A': 0
        }
        self.score_sum_a: Dict[str, Dict[str, Dict[str, float]]] = {
            'QA': Stats.init_dic(rouge_types, extract_types),
            'Q': Stats.init_dic(rouge_types, extract_types),
            'A': Stats.init_dic(rouge_types, extract_types),
        }
        self.score_sum_t: Dict[str, Dict[str, Dict[str, float]]] = {
            'QA': Stats.init_dic(rouge_types, extract_types),
            'Q': Stats.init_dic(rouge_types, extract_types),
            'A': Stats.init_dic(rouge_types, extract_types),
        }

    @staticmethod
    def init_dic(rouge_types: List[str], extract_types: List[str]) -> Dict[str, Dict[str, float]]:
        ret = {}
        for st in ['R', 'F']:
            for rt in rouge_types:
                ret[f'{rt}-{st}'] = {et: 0.0 for et in extract_types}
        return ret


def nonEmpty(s: str) -> bool:
    return s is not None and s != ''


def isEmpty(s: str) -> bool:
    return not nonEmpty(s)


def or_else(n: Optional[T], e: T) -> T:
    return n if n is not None else e


def is_content_word(pos: str) -> bool:
    for el in content_words:
        if pos.startswith(el):
            return False
    return True


def is_noun(pos: str, original: str) -> bool:
    return (pos.startswith('名詞') or pos == "記号-文字" or pos.startswith(
        "接尾辞-名詞的") or pos == "接頭辞") and (original not in adverbial_nouns) and (original not in formal_nouns)


def is_numeral(pos: str) -> bool:
    return pos == '名詞-数詞'


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-15 QA Lab PoliInfo2 Dialog SummarizationタスクのROUGE自動評価スクリプトです．
動作要件として，mecab-python3モジュールが必要です．

【入力】評価対象データはファイル入力で以下のJSON書式を想定しています．
[
    {"ID": ..., },
    {"ID": ..., },
    ...
]

【出力】評価結果は標準出力で以下のJSON書式です．
{
    "success": true,    // スコア計算が成功したかどうか
    "rep_score": float, // 代表スコア（ROUGE-1-R 内容語のマクロ平均）
    "macro_ave": {
        "available_rate": {                   // 有効回答率
            "QA": float
            "Q": float
            "A": float
        },
        "available": {                        // 有効回答のみのスコア
            "QA": {"R1": ..., "R2": ..., }, // QA両方
            "Q": {"R1": ..., "R2": ..., },  // Qのみ
            "A": {"R1": ..., "R2": ..., }   // Aのみ
        },
        "total": {                            // トータルのスコア
            "QA": {"R1": ..., "R2": ..., },
            "Q": {"R1": ..., "R2": ..., },
            "A": {"R1": ..., "R2": ..., }
        }
    },
    "ins": [
        {
            "ID": ...,
            "QA": {"available: bool, "R1": ..., "R2": ..., }, // QA両方
            "Q": {"available: bool, "R1": ..., "R2": ..., },  // Qのみ
            "A": {"available: bool, "R1": ..., "R2": ..., }   // Aのみ
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

    parser.add_argument('-d', '--unidic-path',
                        required=True,
                        help='MeCabで用いるUnidicのパスを指定します'
                        )

    return parser.parse_args()

def load_json_todic(json_str: str) -> Dict[str, DSInstance]:
    return {x['ID']: DSInstance(x) for x in json.loads(json_str)}

def load_json(json_str: str) -> List[DSInstance]:
    return [DSInstance(x) for x in json.loads(json_str)]


def word2ids(summary: List[str], reference: List[str]) -> Tuple[List[List[str]], List[List[List[str]]]]:
    id_dict = defaultdict(lambda: len(id_dict))
    rsummary = [[' '.join([str(id_dict[w]) for w in summary])]]
    rreference = [[[' '.join([str(id_dict[w]) for w in reference])]]]
    # summary = [[' '.join([str(id_dict[w]) for w in sent.split()])
    #             for sent in doc] for doc in summary]
    # reference = [[[' '.join([str(id_dict[w]) for w in sent.split()])
    #                for sent in doc] for doc in refs] for refs in reference]
    return rsummary, rreference


def replace_all_kanji_to_arabic(numerals: str) -> str:
    tmp = numerals.replace("一", "1").replace("二", "2").replace("三", "3").replace("四", "4").replace("五", "5").replace(
        "六", "6").replace("七", "7").replace("八", "8").replace("九", "9").replace("〇", "0")
    tmp = re.sub(r'[^0123456789]', '', tmp)
    tmp = re.sub(r'^0+', '', tmp)
    return tmp


def parse_kanji_numerals(kanji_numerals: str) -> Optional[int]:
    def p3(numerals: str, has_default: bool) -> Optional[int]:
        if nonEmpty(numerals):
            if has_default:
                return 1
            else:
                return None
        try:
            return int(replace_all_kanji_to_arabic(numerals))
        except Exception as err:
            print(err, file=sys.stderr)
            return None

    def p4(numerals: str) -> Optional[int]:
        numeral_array = list(reversed(replace_all_kanji_to_arabic(numerals)))
        num = 0
        for i, x in enumerate(numeral_array):
            try:
                num += int(int(x) * math.pow(10, i))
            except:
                pass
        return num

    def p2(numerals: str) -> Optional[int]:
        if isEmpty(numerals):
            return None
        mobj = numeral_notation2_regex.match(numerals)
        if mobj is not None:
            if nonEmpty(mobj.group(1)) and nonEmpty(mobj.group(2)) and nonEmpty(mobj.group(3)):
                base2 = 10
                print(numerals, file=sys.stderr)
                output2 = or_else(p3(mobj.group(1)[:-1], True), 0) * base2 * base2 * base2 + or_else(
                    p3(mobj.group(2)[:-1], True), 0) * base2 * base2 + or_else(p3(mobj.group(3)[:-1], True),
                                                                               0) * base2 + or_else(
                    p3(mobj.group(4), False), 0)
                return output2
            else:
                return p4(numerals)
        else:
            return None

    tmp = kanji_numerals.replace('ゼロ-zero', '〇').replace('零', '〇')
    matchObj = numeral_notation1_regex.match(tmp)
    if matchObj is not None:
        base = 10000
        default_string = 'a'
        output = or_else(p2(or_else(matchObj.group(1), default_string)[:-1]), 0) * base * base * base + or_else(
            p2(or_else(matchObj.group(2), default_string)[:-1]), 0) * base * base + or_else(
            p2(or_else(matchObj.group(3), default_string)[:-1]), 0) * base + or_else(p2(matchObj.group(4)), 0)
        return output
    else:
        return None


def extract_words(mecab, s: str) -> List[str]:
    parsed = mecab.parse(s)
    ret = []
    compound_nouns = []
    numerals = []

    def append(term):
        if term not in functional_verbs:
            ret.append(term)

    def extract_compound_noun():
        if len(compound_nouns) > 0:
            append(''.join(compound_nouns))
            compound_nouns.clear()

    def extractNumeral():
        if len(numerals) > 0:
            x = parse_kanji_numerals(''.join(numerals))
            if x is not None:
                compound_nouns.append(str(x))
            numerals.clear()

    def compound_noun(tokens: List[str]):
        if len(tokens) < 5:
            return

        pos = tokens[4]

        def buffer_noun():
            compound_nouns.append(tokens[3].strip())

        def buffer_numeral():
            numerals.append(tokens[3].strip())

        def extract_content_word():
            if is_content_word(pos):
                append(tokens[3].strip())

        if is_noun(pos, tokens[0]):
            if is_numeral(pos):
                buffer_numeral()
            else:
                extractNumeral()
                buffer_noun()
        else:
            extractNumeral()
            extract_compound_noun()
            extract_content_word()

    for line in filter(lambda x: x != 'EOS', parsed.splitlines()):
        tmp = line.split('\t')
        if len(tmp) > 1:
            compound_noun(tmp)
        else:
            append(tmp[0])

    extractNumeral()
    extract_compound_noun()

    return ret


def extract_all_words(mecab, s: str, is_original: bool) -> List[str]:
    parsed = mecab.parse(s)
    idx = 0 if is_original else 3
    ret = []

    def append(term):
        ret.append(term)

    for line in filter(lambda x: x != 'EOS', parsed.splitlines()):
        tmp = line.split('\t')
        if len(tmp) > 2:
            append(tmp[idx])
        else:
            append(tmp[0])
    return ret


def main():
    args = get_args()
    mecab = MeCab.Tagger('-d {0}'.format(args.unidic_path))

    # 語のとり方
    extract_types = ['内容語', '短単位（原形）', '短単位（表層形）']

    # ROUGEスコア種別
    rouge_types = ['ROUGE-1', 'ROUGE-2', 'ROUGE-3',
                   'ROUGE-4', 'ROUGE-L', 'ROUGE-SU4', 'ROUGE-W-1.2']

    # GS読み込み
    with open(args.gs_data) as f:
        gss = load_json_todic(f.read())

    # 評価対象読み込み
    with open(args.input_file) as f:
        targets = load_json(f.read())
    
    # 古いIDチェック
    if len(targets) > 0:
        if any([targets[0].id.startswith(prefix) for prefix in old_id_prefix]):
            raise Exception('入力データのIDが古いバージョンになっています．')

    # 評価結果リスト
    evals: List[EvalInstance] = []

    # 評価データ各々に対して
    for target in tqdm(targets, total=len(targets)):
    #for target, gs in [(x, y) for x, y in zip(targets, gss)][:1]:
        target: DSInstance
        gs: DSInstance = gss.get(target.id)

        # IDチェック
        if gs is None:
            raise Exception(f'入力データのIDがGSデータ上で見つかりません．(id={target.id})')

        ev = EvalInstance(gs.id)

        extracted_Qsummaries: List[List[str]] = [
            extract_words(mecab, target.question_summary),
            extract_all_words(mecab, target.question_summary, False),
            extract_all_words(mecab, target.question_summary, True)
        ]
        extracted_Qreferences: List[List[str]] = [
            extract_words(mecab, gs.question_summary),
            extract_all_words(mecab, gs.question_summary, False),
            extract_all_words(mecab, gs.question_summary, True)
        ]
        w2isQ = [word2ids(x, y) for x, y in zip(
            extracted_Qsummaries, extracted_Qreferences)]
        rougesQ = []

        extracted_Asummaries: List[List[List[str]]] = [[
            extract_words(mecab, x),
            extract_all_words(mecab, x, False),
            extract_all_words(mecab, x, True)
        ] for x in target.answer_summary]
        extracted_Areferences: List[List[List[str]]] = [[
            extract_words(mecab, x),
            extract_all_words(mecab, x, False),
            extract_all_words(mecab, x, True)
        ] for x in gs.answer_summary]
        w2isA = [[word2ids(x, y) for x, y in zip(s, r)] for s, r in zip(
            extracted_Asummaries, extracted_Areferences)]
        rougesA = [[] for i in range(len(w2isA))]

        # Question ROUGE計算
        for i in range(len(w2isQ)):
            rougesQ.append(Pythonrouge(summary_file_exist=False,
                                       summary=w2isQ[i][0], reference=w2isQ[i][1],
                                       n_gram=4, ROUGE_SU4=True, ROUGE_L=True, ROUGE_W=True))
        scoresQ = [rouge.calc_score() for rouge in rougesQ]

        # Answer ROUGE計算
        scoresA = []
        for i in range(len(w2isA)):
            for j in range(len(w2isA[i])):
                rougesA[i].append(Pythonrouge(summary_file_exist=False,
                                              summary=w2isA[i][j][0], reference=w2isA[i][j][1],
                                              n_gram=4, ROUGE_SU4=True, ROUGE_L=True, ROUGE_W=True))
            scoresA.append([rouge.calc_score() for rouge in rougesA[i]])

        # 有効回答（文字長）のチェック
        if len(target.question_summary) <= target.question_length:
            ev.q['available'] = True
        if all([len(sm) <= l for sm, l in zip(target.answer_summary, target.answer_length)]):
            ev.a['available'] = True
        ev.qa['available'] = ev.q['available'] and ev.a['available']

        # スコアの記録
        for st in ['R', 'F']:
            for rt in rouge_types:
                ev.q[f'{rt}-{st}'] = {extract_types[i]: scoresQ[i][f'{rt}-{st}']
                                      for i in range(len(extract_types))}
                ev.a[f'{rt}-{st}'] = {extract_types[i]: [sc[i][f'{rt}-{st}'] for sc in scoresA]
                                      for i in range(len(extract_types))}
                ev.qa[f'{rt}-{st}'] = {extract_types[i]: np.average([v for v in ev.a[f'{rt}-{st}'][extract_types[i]]] + [ev.q[f'{rt}-{st}'][extract_types[i]]])
                                       for i in range(len(extract_types))}
        evals.append(ev)

    # 全体スコアの計算
    stats = Stats(rouge_types, extract_types)
    for ev in evals:
        stats.n_t += 1
        for t in ['QA', 'Q', 'A']:
            stats.n_a[t] += ev[t]['available']
            for st in ['R', 'F']:
                for rt in rouge_types:
                    for et in extract_types:
                        if t != 'A':
                            stats.score_sum_t[t][f'{rt}-{st}'][et] += ev[t][f'{rt}-{st}'][et]
                        else:
                            stats.score_sum_t[t][f'{rt}-{st}'][et] += np.average(ev[t][f'{rt}-{st}'][et])
            if ev[t]['available']:
                for st in ['R', 'F']:
                    for rt in rouge_types:
                        for et in extract_types:
                            if t != 'A':
                                stats.score_sum_a[t][f'{rt}-{st}'][et] += ev[t][f'{rt}-{st}'][et]
                            else:
                                stats.score_sum_a[t][f'{rt}-{st}'][et] += np.average(ev[t][f'{rt}-{st}'][et])
    score_ave_a = {}
    score_ave_t = {}
    for t in ['QA', 'Q', 'A']:
        score_ave_a[t] = {}
        score_ave_t[t] = {}
        for st in ['R', 'F']:
            for rt in rouge_types:
                score_ave_a[t][f'{rt}-{st}'] = {et: stats.score_sum_a[t][f'{rt}-{st}'][et] / stats.n_a[t] for et in extract_types}
                score_ave_t[t][f'{rt}-{st}'] = {et: stats.score_sum_a[t][f'{rt}-{st}'][et] / stats.n_t for et in extract_types}
    
    # 出力
    return json.dumps({
        'success': True,
        'rep_score': score_ave_a['QA']['ROUGE-1-R']['内容語'],
        'version': DATA_VERSION,
        'macro_ave': {
            'available_rate': {t: stats.n_a[t] / stats.n_t for t in ['QA', 'Q', 'A']},
            'available': score_ave_a,
            'total':score_ave_t
        },
        'ins': [ev.toDict() for ev in evals]
    }, ensure_ascii=False)


if __name__ == '__main__':
    try:
        print(main())
    except Exception as e:
        print(e, file=sys.stderr)
        print(json.dumps({'success': False}))
