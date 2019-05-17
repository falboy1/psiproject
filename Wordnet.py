import sqlite3
import pprint
import argparse

#-----------------------------------------
# 開始ライン : 基本処理の関数

# 上位語リストを入手する関数
def get_hypernym(conn, query):
    # lemmaがqueryと一致した行のidのカーソルオブジェを取得
    cur = conn.execute("select wordid, pos from word where lemma='%s'" % query)
    # 一致結果の行を取得 (複数ヒットする可能性がある)
    result = cur.fetchall()
    # ヒット件数を表示
    print(str(len(result)) + 'hit')
    for t in result:
        # 検索結果（品詞と検索ワード）を表示
        print('%s:%s of "%s"' % (t[0], t[1], query))
        # 概念IDを取得 (複数ヒットする可能性がある)
        wordid = t[0]
        cur = conn.execute("select synset from sense where wordid='%s'" % wordid)
        sense_result = cur.fetchall()
        # ヒット件数を表示
        print("%s hit" % len(sense_result))
        for synset in sense_result:
            print("synset:%s" % synset)
            # 単語IDを取得
            wordid = t[0]
            # 概念IDを取得
            cur = conn.execute("select pos, name from synset where synset='%s'" % synset)
            synset_result = cur.fetchall()
            print('pos="%s", name="%s"' % (synset_result[0][0], synset_result[0][1]))
            # 概念リンクを取得
            cur = conn.execute("select synset2, link from synlink where synset1='%s'" % synset)
            
        print("\n")

# 概念IDから上位概念IDリストを返す関数 # return:link
def get_hypernym_list(conn, synset_id):
    # 概念リンクを取得 (arg_ex:synset_id = 10023039-n)
    cur = conn.execute("select synset2, link from synlink where synset1='%s'" % synset_id)
    synlink_result = cur.fetchall()
    # 返却用の空リスト
    result = []
    # link = hypeの探索
    for synlink in synlink_result:
        if synlink[1] == 'hype':
            result.append(synlink[0])
    # リストを返却
    if len(result) == 0:
        return False
    else:
        return result

# 概念IDから下位概念IDリストを返す関数 # return:link
def get_hyponym_list(conn, synset_id):
    # 概念リンクを取得 (arg_ex:synset_id = 10023039-n)
    cur = conn.execute("select synset2, link from synlink where synset1='%s'" % synset_id)
    synlink_result = cur.fetchall()
    # 返却用の空リスト
    result = []
    # link = hypeの探索
    for synlink in synlink_result:
        if synlink[1] == 'hypo':
            result.append(synlink[0])
    # リストを返却
    if len(result) == 0:
        return False
    else:
        return result   

# 概念IDから概念情報{'pos'=xxx, 'name'=yyy}を返す関数
def get_synset_info(conn, synsetid):
    # 概念情報を取得
    cur = conn.execute("select pos, name from synset where synset='%s'" % synsetid)
    synset_result = cur.fetchall()
    # 返却用の空リストを作成
    result = []
    for synset in synset_result:
        dic = dict(pos=synset[0], name=synset[1])
        result.append(dic)
    # 値を返却
    return result

# 概念名から概念IDリストを返す関数
def get_synsetid_list_from_name(conn, name):
    # synsetテーブルから情報を取り出す
    cur = conn.execute("select synset from synset where name='%s'" % name)
    synset_result = cur.fetchall()
    # 返却用の空リストを作成
    result = []
    for synset in synset_result:
        result.append(synset[0])
    # 値を返却
    return result

# 概念IDから概念定義[{'lang'=xxx, 'define'=xxx}]を返す関数
def get_synset_def(conn, synsetid):
    cur = conn.execute("select lang, def from synset_def where synset='%s'" % synsetid)
    synset_def_result = cur.fetchall()
    # 返却用の空リストを作成
    result = []
    for synset_def in synset_def_result:
        if synset_def[0] != 'img':
            dic = dict (lang=synset_def[0], define=synset_def[1])
            result.append(dic)
    # 値を返却
    return result
# queryから単語情報[(wordid,pos)]を返す関数
def get_wordid_list(conn, query):
    cur = conn.execute("select wordid, pos from word where lemma='%s'" % query)
    word_result = cur.fetchall()
    # 返却用の空リストを作成
    result = []
    for word in word_result:
        dic = dict(wordid=word[0], pos=word[1])
        result.append(dic)
    
    if len(result) == 0:
        return False
    else:
        return result

# word_idから単語[(lemma, pos)]を返す関数
def get_word(conn, wordid):
    cur = conn.execute("select lemma, pos from word where lemma='%s'" % wordid)
    word_result = cur.fetchall()
    return word_result

# 単語の属する概念IDリストを返す関数　(単語IDを使用)
def get_synsetid_list_from_wordid(conn, wordid):
    cur = conn.execute("select synset from sense where wordid='%s'" % wordid)
    sense_result = cur.fetchall()
    # 空リスト作成
    result = []
    for sense in sense_result:
        result.append(sense[0])
    return result

# 終了ライン : 基本処理の関数
# ------------------------------------------------
# 開始ライン : 基本処理を使った出力までを行う関数

# 単語の情報を検索する関数
def search_word_info(conn, query):
    # 単語IDのリストを取得 (複数一致の可能性あり)
    wordid_list = get_wordid_list(conn, query)
    # 一致情報がなかった場合は関数を抜ける
    if wordid_list is False:
        print("No hit")
        return
    # ヒット件数を表示
    print("%s hit" % str(len(wordid_list)))

    for d in wordid_list:
        # 検索結果（品詞と検索ワード）を表示
        print('%s:%s" of "%s"' % (d['wordid'], d['pos'], query))
        # 単語IDを取得
        word_id = d['wordid']
        # 単語の属する概念ID一覧を取得 (複数ヒットする可能性がある)
        synsetid_list = get_synsetid_list_from_wordid(conn, word_id)
        # ヒット件数を表示
        print("%s hit" % len(synsetid_list))
        for synsetid in synsetid_list:
            print("synsetid:%s" % synsetid)
            # 概念を取得
            synset = get_synset_info(conn, synsetid)
            # 取得した概念を表示
            for s in synset:
                print("pos:%s, name:%s" % (s['pos'], s['name']))
            print("\n")
            # 概念定義を取得
            define = get_synset_def(conn, synsetid)
            # 取得した概念定義を表示
            for d in define:
                print("lang:%s, def:%s" % (d['lang'], d['define'][:25])) # 長い時があるから25文字でスライス
        print('\n')

# 上位語を見ていく関数
# def hypernym_loop(conn, query):

# 概念名の定義を出力する関数
def search_synset_def(conn, query):
    list1 = get_synsetid_list_from_name(conn, query)
    for d in list1:
        print("synset_id:%s" % d)
        define = get_synset_def(conn, d)
        for d2 in define:
            print("def:%s" % d2)
        print("\n")

def main():
    # ファイルパス
    filepath = 'data/wnjpn.db'
    # データベースにコネクト
    conn = sqlite3.connect(filepath)

    # argparseのオブジェクトを作成
    parser = argparse.ArgumentParser(description="検索クエリとオプションを指定して実行")

    # パラメータを追加
    parser.add_argument("query", help="検索クエリー")
    parser.add_argument("-w", "--word_info", help="単語情報の検索", action='store_true')
    parser.add_argument("-s", "--synset_def", help="概念説明の検索", action='store_true')

    # 引数を取得
    args = parser.parse_args()

    # 単語情報の簡易検索
    if (args.word_info is True):
        search_word_info(conn, args.query)

    # 概念定義を検索
    if (args.synset_def is True):
        search_synset_def(conn, args.query)

    

if __name__ == '__main__':
    main()