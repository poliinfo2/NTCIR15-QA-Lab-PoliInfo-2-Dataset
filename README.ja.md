# NTCIR15 QA Lab-Poliinfo-2 Dataset

NTCIR15 QA Lab-PoliInfo-2 データセットのリリース

私たちは、2019年6月から2020年12月まで、QA Lab-PoliInfo-2を開催しました。 
詳細については、下記のウェブサイトをご覧ください。

- https://poliinfo2.net/
- https://poliinfo2.github.io/


## Dialog Summarization

- 目標・意義
  - 政治家の発言の信憑性を判断するためには，政治課題に関する議論がどのように行われているのか，知る必要があり，議論をしている相手の発言や文脈を考慮しなければならない．政治課題に関する議論は，議会において行われており，議会会議録として質問や答弁が残されている．しかしながら，議会会議録は，発言を書き起こした文書であり，まとめられておらず，読みづらいという問題がある．特に，東京都議会をはじめとする多くの地方議会では，一問一答方式ではなく，一括質問一括答弁方式がとられており，質問と答弁が離れた位置に存在する．また，質問に対して，知事が答弁する場合と，総務部長や教育長のような知事以外の出席者が答弁する場合がある．さらには，知事による答弁を補足する形で複数の出席者が答弁することもある．従って，質疑（質問と答弁の組）を要約するためには，議論の構造を考慮することが求められる．そこで，Dialog Summarization では地方議会における「議員の質問」と「知事側の答弁」という対話構造を考慮しながら要約することを目標としている．

- 入力  
  - 東京都議会会議録
  - 出題ファイル
- 出力  
  - 質問と答弁の構造を考慮した要約結果（都議会だよりの要約を正解とする）
- 評価  
  - ROUGE
    - 動評価（Leader boardのスコア）に用いる
  - 以下の観点からの人手評価
    - Content: 参照要約との内容の合致
            Well-formed: 文法的な正しさ
            Non-twisted: 話者の考えが歪曲されていない
            Sentence goodness: それぞれの発言で見た場合の要約としての全体的な良さ
            Dialog goodness: 質問と回答のセットで見た場合の要約としての全体的な良さ


### Json example

```JSON
{
"ID":"130001_230617_2",
"Line":2,"Prefecture":"東京都",
"Volume":"平成23年_第２回",
"Number":"1",
"Year":23,
"Month":6,
"Day":17,
"Title":"平成23年_第２回定例会(第７号)",
"Speaker":"和田宗春",
"Utterance":"ただいまから平成二十三年第二回東京都議会定例会を開会いたします。"
},
```

```JSON
[
{
  "AnswerEndingLine": [
    532
  ],
  "AnswerLength": [
    50
  ],
  "AnswerSpeaker": [
    "知事"
  ],
  "AnswerStartingLine": [
    528
  ],
  "AnswerSummary": [
    "全国の先頭に立ち刻苦する被災地を支援するのは当然。今後も強力に後押しする。"
  ],
  "Date": "2011-06-23",
  "ID": "PoliInfo2-DialogSummarization-JA-Dry-Training-Segmented-00001",
  "MainTopic": "東京の総合防災力を更に高めよ<br>環境に配慮した都市づくりを",
  "Meeting": "平成23年第2回定例会",
  "Prefecture": "東京都",
  "QuestionEndingLine": 276,
  "QuestionLength": 50,
  "QuestionSpeaker": "山下太郎（民主党）",
  "QuestionStartingLine": 266,
  "QuestionSummary": "被災地が真に必要とする支援に継続して取り組むべき。知事の見解は。",
  "SubTopic": "東日本大震災"
}
]
```

### A list of files

|-- PoliInfo2-DialogSummarization-JA-Formal-GSD.json  
|--AnswerSheet  
| |--PoliInfo2-DialogSummarization-JA-Formal-Test.json  
| |--PoliInfo2-DialogSummarization-JA-Formal-Training-Segmented.json  
| |--PoliInfo2-DialogSummarization-JA-Formal-Training-Unsegmented.json  
|--TokyoMetropolitanAssemblyMinutes  
| |--Pref13_tokyo.json  

## Stance Classification

- 目標・意義
  - 政治家の発言の信憑性を判断するためには，政治家がどのような立場で発言しているのか，知ることが必要である．政治家の立場を理解するためには，一つの政治課題に対する賛成・反対を明らかにするだけではなく，複数の政治課題に対する賛成・反対を総合して判断しなければならない．地方議会では複数の政治課題に対して同じ立場の人が集まり「会派」を組んでいる．Stance classificationでは政治家の発言から，所属する会派の立場，すなわち，それぞれの議案に対する賛否を推定することを目標とする．

- 入力 
  - 東京都議会会議録 
  - 出題ファイル 
- 出力 
  - 各議案に対する会派の「賛成 or 反対」
    - 自動評価（Leader boardのスコア）に用いる
    - ProsConsPartyListBinaryに回答
  - 各議案に対する会派の「賛成 or 反対 or 言及なし」
    - 人手評価に用いる
    - ProsConsPartyListTernaryに回答
- 評価
  - 議案ごとの正解率の総和



### Json example

```JSON
[
    {
        "Date": "2001/8/8",
        "Prefecture": "東京都",
        "ProceedingTitle": "平成十三年第一回臨時会会議録",
        "URL": "https://www.gikai.metro.tokyo.jp/record/extraordinary/2001-1.html",
        "Proceeding": [
            {
                "Speaker": "null",
                "Utterance": "　出席議員（百二十六名）\n一番谷村　孝彦君\n二番東村　邦浩君\n三番中屋　文孝君\n四番矢島　千秋君\n五番高橋かずみ君\n六番山加　朱美君\n七番柿沢　未途君\n八番後藤　雄一君\n九番福士　敬子君\n十番伊沢けい子君\n十一番大西由紀子君\n十二番青木　英二君\n十三番初鹿　明博君\n十四番山下　太郎君\n十五番河野百合恵君\n十六番長橋　桂一君\n十七番小磯　善彦君\n十八番野上じゅん子君\n十九番ともとし春久君\n二十番萩生田光一君\n二十一番串田　克巳君\n二十二番小美濃安弘君\n二十三番吉原　　修君\n二十四番山田　忠昭君\n二十五番林田　　武君\n二十六番野島　善司君\n二十七番真鍋よしゆき君\n二十八番中西　一善君\n二十九番山口　文江君\n三十番真木　　茂君\n三十一番花輪ともふみ君\n三十二番酒井　大史君\n三十三番清水ひで子君\n三十四番かち佳代子君\n三十五番小松　恭子君\n三十六番織田　拓郎君\n三十七番藤井　　一君\n三十八番東野　秀平君\n三十九番中嶋　義雄君\n四十番松原　忠義君\n四十一番田代ひろし君\n四十二番三宅　茂樹君\n四十三番川井しげお君\n四十四番いなば真一君\n四十五番近藤やよい君\n四十七番鈴木　一光君\n四十八番吉野　利明君\n四十九番小磯　　明君\n五十番新井美沙子君\n五十一番相川　　博君\n五十二番樋口ゆうこ君\n五十三番富田　俊正君\n五十四番福島　寿一君\n五十五番大塚　隆朗君\n五十六番古館　和憲君\n五十七番松村　友昭君\n五十八番丸茂　勇夫君\n五十九番鈴木貫太郎君\n六十番森田　安孝君\n六十一番曽雌　久義君\n六十二番石川　芳昭君\n六十三番土持　正豊君\n六十四番倉林　辰雄君\n六十五番遠藤　　衛君\n六十六番秋田　一郎君\n六十七番服部ゆくお君\n六十八番臼井　　孝君\n六十九番北城　貞治君\n七十番野田　和男君\n七十一番三原　將嗣君\n七十二番大西　英男君\n七十三番宮崎　　章君\n七十四番執印真智子君\n七十五番馬場　裕子君\n七十六番西条　庄治君\n七十七番土屋たかゆき君\n七十八番河西のぶみ君\n七十九番中村　明彦君\n八十番大山とも子君\n八十一番吉田　信夫君\n八十二番曽根はじめ君\n八十三番橋本辰二郎君\n八十四番大木田　守君\n八十五番前島信次郎君\n八十六番桜井良之助君\n八十七番新藤　義彦君\n八十八番星野　篤功君\n八十九番田島　和明君\n九十番樺山　卓司君\n九十一番古賀　俊昭君\n九十二番山崎　孝明君\n九十三番山本賢太郎君\n九十四番花川与惣太君\n九十五番立石　晴康君\n九十六番清原錬太郎君\n九十七番小山　敏雄君\n九十八番大河原雅子君\n九十九番名取　憲彦君\n百番藤川　隆則君\n百一番小林　正則君\n百二番林　　知二君\n百三番東ひろたか君\n百四番池田　梅夫君\n百五番渡辺　康信君\n百六番木内　良明君\n百七番石井　義修君\n百八番中山　秀雄君\n百九番藤井　富雄君\n百十番大山　　均君\n百十一番野村　有信君\n百十二番比留間敏夫君\n百十三番松本　文明君\n百十四番桜井　　武君\n百十五番佐藤　裕彦君\n百十六番川島　忠一君\n百十七番矢部　　一君\n百十八番内田　　茂君\n百十九番三田　敏哉君\n百二十番田中　晃三君\n百二十一番藤田　愛子君\n百二十二番尾崎　正一君\n百二十三番田中　　良君\n百二十四番和田　宗春君\n百二十五番坂口こうじ君\n百二十六番木村　陽治君\n百二十七番秋田かくお君\n　欠席議員（一名）\n四十六番　　高島なおき君\n　出席説明員\n知事石原慎太郎君\n副知事福永　正通君\n副知事青山やすし君\n副知事浜渦　武生君\n出納長大塚　俊郎君\n教育長横山　洋吉君\n知事本部長田原　和道君\n総務局長大関東支夫君\n財務局長安樂　　進君\n警視総監野田　　健君\n主税局長安間　謙臣君\n生活文化局長高橋　信行君\n都市計画局長木内　征司君\n環境局長赤星　經昭君\n福祉局長前川　燿男君\n衛生局長今村　皓一君\n産業労働局長浪越　勝海君\n住宅局長橋本　　勲君\n建設局長山下　保博君\n消防総監杉村　哲也君\n港湾局長川崎　裕康君\n交通局長寺内　広壽君\n水道局長飯嶋　宣雄君\n下水道局長鈴木　　宏君\n大学管理本部長鎌形　満征君\n多摩都市整備本部長石河　信一君\n中央卸売市場長碇山　幸夫君\n選挙管理委員会事務局長南　　靖武君\n人事委員会事務局長高橋　　功君\n地方労働委員会事務局長大久保　隆君\n監査事務局長中山　弘子君\n収用委員会事務局長有手　　勉君\n八月八日議事日程第一号\n第一　議長選挙\n議事日程第一号追加の一\n第一　副議長選挙\n第二　議員提出議案第二十四号\n　　東京都議会委員会条例の一部を改正する条例\n第三　常任委員選任\n第四　議会運営委員選任\n第五　東京都監査委員の選任の同意について\n　　(一三財主議第三〇一号）\n第六　東京都監査委員の選任の同意について\n　　(一三財主議第三〇二号）\n第七　議員提出議案第二十五号\n　　東京都議会議員の報酬及び期末手当の特例に関する条例\n　　　午後一時一分\n"
            },
            {
                "Speaker": "議会局長(細渕清君)",
                "Utterance": "議会局長の細渕でございます。\n　本日は改選後初の議会でございますので、先例に従いまして、私から参集のご案内を差し上げました。ご了承願います。\n　本日の会議では、議長が選挙されるまでの間、地方自治法第百七条の規定によりまして、年長議員が臨時議長の職務を行うことになっております。出席議員中、年長議員は清原錬太郎議員でございます。\n　それでは清原議員、議長席にお着きいただきたいと存じます。\n　　　〔臨時議長清原錬太郎君着席〕\n"
            },
            {
                "Speaker": "臨時議長(清原錬太郎君)",
                "Utterance": "一般選挙後の初の議会でありますので、僣越ではございますが、地方自治法第百七条の規定により、私が議長選挙のための臨時議長の職務を行うことにいたします。よろしくご協力のほどお願いいたします。\n　　　午後一時三分開会・開議\n"
            }
		]
	}
]
		
```

```JSON
[
    {
        "ID":"PoliInfo2-StanceClassification-JA-Dry-Training-02543",
        "Prefecture":"東京都",
        "Meeting":"平成31年第1回定例会、第1回臨時会",
        "MeetingStartDate":"2019/2/20",
        "MeetingEndDate":"2019/3/28",
        "Proponent":"知事提出議案",
        "BillClass":"予算",
        "BillSubClass":"31年度予算",
        "Bill":"一般会計",
        "BillNumber":"第一号議案",
        "SpeakerList":{
            "増子ひろき":"都ファースト",
            "吉原修":"自民党",
            "東村邦浩":"公明党",
            "清水ひで子":"日本共産党",
            "中村ひろし":"立憲・民主",
            "田の上いくこ":"都ファースト",
            "入江のぶこ":"都ファースト",
            "まつば多美子":"公明党",
            "柴崎幹男":"自民党",
            "星見てい子":"日本共産党",
            "白戸太朗":"都ファースト",
            "つじの栄作":"都ファースト",
            "伊藤こういち":"公明党",
            "大場やすのぶ":"自民党",
            "鳥居こうすけ":"都ファースト",
            "原田あきら":"日本共産党",
            "桐山ひとみ":"都ファースト",
            "うすい浩一":"公明党",
            "舟坂ちかお":"自民党",
            "鈴木邦和":"都ファースト",
            "龍円あいり":"都ファースト",
            "細田いさむ":"公明党",
            "森口つかさ":"都ファースト",
            "福島りえこ":"都ファースト",
            "藤井とものり":"立憲・民主",
            "平慶翔":"都ファースト",
            "岡本こうき":"都ファースト",
            "森澤恭子":"東京みらい",
            "おときた駿":"維新・あた",
            "山内れい子":"無（ネット）",
            "上田令子":"無（自由守る会）",
            "伊藤ゆう":"都ファースト",
            "鈴木章浩":"自民党",
            "橘正剛":"公明党",
            "和泉なおみ":"日本共産党",
            "宮瀬英治":"立憲・民主",
            "大津ひろ子":"都ファースト",
            "村松一希":"都ファースト",
            "小松大祐":"自民党",
            "高倉良生":"公明党",
            "森村隆行":"都ファースト",
            "あぜ上三和子":"日本共産党",
            "あかねがくぼかよ子":"都ファースト",
            "伊藤しょうこう":"自民党",
            "大松あきら":"公明党",
            "木下ふみこ":"都ファースト",
            "滝田やすひこ":"都ファースト",
            "とや英津子":"日本共産党",
            "小林健二":"公明党",
            "内山真吾":"都ファースト",
            "おじま紘平":"都ファースト",
            "増田一郎":"都ファースト",
            "白石たみお":"日本共産党",
            "斉藤れいな":"東京みらい",
            "やながせ裕文":"維新・あた"
        },
        "ProsConsPartyListBinary":{
            "都ファースト":"賛成",
            "公明党":"賛成",
            "立憲・民主":"賛成",
            "東京みらい":"賛成",
            "無（ネット）":"賛成",
            "自民党":"反対",
            "日本共産党":"反対",
            "維新・あた":"反対",
            "無（自由守る会）":"反対"
        },
        "ProsConsPartyListTernary":{
            "都ファースト":null,
            "公明党":null,
            "立憲・民主":null,
            "東京みらい":null,
            "無（ネット）":null,
            "自民党":null,
            "日本共産党":null,
            "維新・あた":null,
            "無（自由守る会）":null
        }
    }
]
```

### A list of files

|--PoliInfo2-StanceClassification-JA-Formal-GSD.json  
|--AnswerSheet  
| |--PoliInfo2-StanceClassification-JA-Formal-Test.json  
| |--PoliInfo2-StanceClassification-JA-Formal-Training.json  
|--TokyoMetropolitanAssemblyMinutes  
| |--Committees  
| | |--utterances_tokyo_assembly-administration.json  
| | |--utterances_tokyo_bank.json  
| | |--utterances_tokyo_budget.json  
| | |--utterances_tokyo_construction-housing.json  
| | |--utterances_tokyo_disaster-prevention.json  
| | |--utterances_tokyo_draft.json  
| | |--utterances_tokyo_economic-port-and-harbor.json  
| | |--utterances_tokyo_educational.json  
| | |--utterances_tokyo_environmental-construction.json  
| | |--utterances_tokyo_financial.json  
| | |--utterances_tokyo_general-affairs.json  
| | |--utterances_tokyo_market-relocation-task-force.json  
| | |--utterances_tokyo_market-relocation.json  
| | |--utterances_tokyo_market.json  
| | |--utterances_tokyo_municipal-utility-account.json  
| | |--utterances_tokyo_olympic-propulsion.json  
| | |--utterances_tokyo_olympic.json  
| | |--utterances_tokyo_olympic2020.json  
| | |--utterances_tokyo_op-rwc.json  
| | |--utterances_tokyo_police-fire-fighting.json  
| | |--utterances_tokyo_public-enterprise.json  
| | |--utterances_tokyo_rugby-world-cup.json  
| | |--utterances_tokyo_social-welfare-corporation.json  
| | |--utterances_tokyo_special-accountiong.json  
| | |--utterances_tokyo_subcommittee.json  
| | |--utterances_tokyo_task-force.json  
| | |--utterances_tokyo_union-exam.json  
| | |--utterances_tokyo_urban-development.json  
| | |--utterances_tokyo_urban-environmental.json  
| | |--utterances_tokyo_welfare.json  
| |--Proceedings  
| | |--utterances_tokyo_extraordinary_withURL.json  
| | |--utterances_tokyo_proceeding_withURL.json  
  
## Entity Linking


- 目標・意義 
  - 政治家の発言の信憑性を判断するためには，発言の根拠となる一次情報が存在を明らかにする必要がある．一次情報は，過去の会議録，法令集，文書等に記載されている可能性があり，これを現在の発言と結びつけることで，フェイクニュース検出やファクトチェックに役に立つと考えられる．Entity Linkingサブタスクでは，参照すべき一次情報が，会議録外の知識ベース・言語資源に集約されていることを想定して，議会での発言とwikipediaを結びつけることを目指す．

- 入力 
  - 地方議会会議録および国会会議録
  -  Wikipedia dump（2019-12-01）
- 出力
  - 抽出された法律名（メンション）
  - メンションに対応する Wikipedia URL
- 評価
  - 抽出：形態素単位の抽出精度
  - 連結：連結したURLの正解率



### A list of files

|--PoliInfo2-EntityLinking-JA-Formal-GSD.tsv  
|--AnswerSheet  
| |--PoliInfo2-EntityLinking-JA-Formal-Test.tsv  
| |--PoliInfo2-EntityLinking-JA-Formal-Training.tsv  
|--WikipediaTitlePageID  
| |--wikipedia_title_pageid_20191201.txt  


## Topiec Detection

- 目標・意義
  - 各地方自治体が発行する「議会だより」は、地域住民に議会の内容を分かりやすく伝える一つの方法であるが、人手により作成されるため発行までに時間がかかる。一方では、議員からの代表質問や一般質問などの内容を素早く伝えるために会議録の「速報版」を公開しているが、議題や論点の分かりやすさという点では改善の余地がある。そこで、Topic Detectionでは、会議録の速報版から、議題や論点として「適切な議題の一覧」を議員ごとにまとめて提示すること目的とする。また、「適切な議題とは何か」ということに関しても議論していきたい。

- 入力
  - 東京都議会の令和2年第1回および第2回定例会における速報版(または代表質問と一般質問)
- 出力
  - 議員ごとにまとめられた議題(Dialog Topic)となる語句の一覧
- 評価
  - 提案から提出までの時間的な制約もあるため、オープンタスクと位置づけ、スコアによる優劣はつけない。参加者からの結果の提出後、タスクオーガナイザと参加者間で以下の点などを話し合う。

## Bibtex
- Please use the following bibtex, when you refer NTCIR15 QA Lab-PoliInfo-2 dataset from your papers.


```
@article{PoliInfo2,
title = {Overview of the NTCIR-15 QA Lab-PoliInfo-2 Task},
author = {Yasutomo Kimura and Hideyuki Shibuki and Hokuto Ototake and Yuzu Uchida and Keiichi Takamaru and Madoka Ishioroshi and Teruko Mitamura and Masaharu Yoshioka and Tomoyosi Akiba and Yasuhiro Ogawa and Minoru Sasaki and Kenichi Yokote and Tatsunori Mori and Kenji Araki and Satoshi Sekine and Noriko Kando},
journal = {Proceedings of The 15th NTCIR Conference},
month = {12},
year = {2020}
}
```

