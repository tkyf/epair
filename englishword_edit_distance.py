# -*- coding: utf-8 -*-

# edit tag
eq_tag =  '.'
add_tag = '+'
del_tag = '-'
sub_tag = '/'

class EditDistance(object):

    def __init__(self, eq_include=False, no_pos=False, is_test=False):
        """
        eq_include -- 差分ペアだけでなく、変化のない単語も出力する。
        no_pos -- 差分ペアに品詞をつける（添削側の品詞）
        is_test    -- True を指定すると、途中経過を表示する。
        """

        self.eq_include = eq_include
        self.with_pos = not no_pos
        self.is_test = is_test

       
    def build_edit_graph(self, src, dst):
        """[FUNCTIONS] 二つの文のあいだのエディットグラフを作る。

        Keyword argument:
        src -- 1つ目の文。例：学習者の文  :: unicode
        dst -- 2つ目の文。例：添削文      :: unicode

        Return value:
        edit_graph  :: [[int]]
        """

        # tokenize スペースで切るだけ
        src = src.split(u" ")
        dst = dst.split(u" ")

        # DPで使うエディットグラフ用の2次元配列の初期化。
        # サイズを+1するのは先頭要素("","")があるため
        m = [[0] * (len(dst)+1) for i in range(len(src) +1)]

        # LD(i,0)となる自明な箇所の初期化
        for i in xrange(len(src) + 1):
            m[i][0] = i

        # LD(0,j)となる自明な箇所の初期化
        for j in xrange(len(dst)+1):
            m[0][j] = j

        # エディットグラフの値を埋める。
        for i in xrange(1, len(src) + 1):
            for j in xrange(1, len(dst) + 1):
                if src[i - 1] == dst[j - 1]:
                    x = 0
                else:
                    x = 1
                m[i][j] = min(m[i-1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + x)

        return m


    def build_edit_trail(self, src, dst):
        """[FUNCTIONS] エディットグラフを終端（最も右下）から左上にたどり、
        二つの文の編集履歴を得る。
        編集履歴は'add', 'del', 'eq', 'sub'のリスト。

        Keyword arguments:
        src        -- 1つ目の文。例：学習者の文  :: unicode
        dst        -- 2つ目の文。例：添削文      :: unicode
        """
        m = self.build_edit_graph(src, dst)

        # tokenize スペースで切るだけ
        src = src.split(u" ")
        dst = dst.split(u" ")

        #最後からたどるために、エディットグラフの右下のインデックスを得る
        i = len(m) - 1
        j = len(m[0]) - 1
        now = m[i][j]

        edit_trail = []
        while(i > 0 or j > 0):
            up_index = m[i - 1][j]
            diagonal_index = m[i -1][j - 1]
            left_index = m[i][j - 1]

            # 優先順位は eq(diagonal),sub(diagnal), del(up), add(left)の順
            min_list = [diagonal_index, up_index, left_index]
            min_num = min(min_list)
            min_index = min_list.index(min_num)
            # これで、斜め・左・上のどのスコアが最も小さいか分かった。

            # エディットグラフの上端に到達しているときはそのまま左に進む
            if i == 0:
                j -= 1
                edit_trail.append('add')
            # 左端に到達しているときはそのまま上に進む
            elif j == 0:
                i -= 1
                edit_trail.append('del')
            # 斜めはeq または sub
            elif min_index == 0:
                if min_num == now:
                    i -= 1
                    j -= 1
                    edit_trail.append('eq')
                else:
                    i -= 1
                    j -= 1
                    edit_trail.append('sub') 
            else:
                if min_index == 1:
                    i -= 1
                    edit_trail.append('del')
                else:
                    j -= 1
                    edit_trail.append('add')
            now = m[i][j]

        # 左上からの編集履歴を得るために、reverseする。
        return list(reversed(edit_trail))


    def build_edit_rev(self, src, dst):
        """[FUNCTIONS] 編集タグ、変更前文字列、変更後文字列の三つ組を作る。
        挿入操作が行われた単語の箇所には、変更前文字列にu'＿'が挿入される。
        削除操作が行われた単語の箇所には、変更後文字列にu'＿'が挿入される。


        Keyword arguments:
        src        -- 1つ目の文。例：学習者の文  :: unicode
        dst        -- 2つ目の文。例：添削文      :: unicode

        Return value:
        (tag_list, src_list, dst_list)

        """

        edit_trail = self.build_edit_trail(src, dst)

        # tokenize スペースで切るだけ
        src = src.split(u" ")
        dst = dst.split(u" ")

        src_index = 0
        dst_index = 0
        tags = []
        srcs = []
        dsts = []
        for i, e in enumerate(edit_trail):
            if e == 'eq':
                tags.append(eq_tag)
                srcs.append(src[src_index])
                dsts.append(dst[dst_index])
                src_index += 1
                dst_index += 1
            elif e == 'add':
                tags.append(add_tag)
                srcs.append(u'＿')
                dsts.append(dst[dst_index])
                dst_index += 1
            elif e == 'del':
                tags.append(del_tag)
                srcs.append(src[src_index])
                dsts.append(u'＿')
                src_index += 1
            elif e == 'sub':
                tags.append(sub_tag)
                srcs.append(src[src_index])
                dsts.append(dst[dst_index])
                src_index += 1
                dst_index += 1
            else:
                print 'this tag is not defiened'

        return (tags, srcs, dsts)


    def extract(self, src, dst):
        """[FUNCTIONS] 学習者の表現と添削者の表現のペアを作る
        """
        edit_rev_triple = self.build_edit_rev(src, dst)

        # tokenize スペースで切るだけ
        src = src.split(u" ")
        dst = dst.split(u" ")

        sub_list = []

        tags, srcs, dsts = edit_rev_triple
        if sub_tag in tags:
            if self.with_pos:
                src_pos, dst_pos = self.pos_with_rev(edit_rev_triple)
                if self.eq_include:
                    for t, s, d, sp, dp in zip(tags, srcs, dsts, src_pos, dst_pos):
                        if t == sub_tag or t == eq_tag:
                            sub_list.append((s + u'/' + sp, d + u'/' + dp))
                else:
                    for t, s, d, sp, dp in zip(tags, srcs, dsts, src_pos, dst_pos):
                        if t == sub_tag:
                            sub_list.append((s + u'/' + sp, d + u'/' + dp))
            elif self.eq_include:
                for t, s, d in zip(tags, srcs, dsts):
                    if t == sub_tag or t == eq_tag:
                        sub_list.append((s, d))               
            else:
                for t, s, d in zip(tags, srcs, dsts):
                    if t == sub_tag:
                        sub_list.append((s, d))

        return sub_list

    def extract_isolation_window(self, src, dst, window=1):
        """[FUNCTIONS] 学習者の表現と添削者の表現のペアを作る
        独立した置換操作の箇所をすべて取り出す。
        windowが1のとき：トライグラム
                2のとき：5gram
                3のとき：7gram
                …と増えていく
        """
        def make_string(edit_rev_triple, src_pos, dst_pos, index):
            tags, srcs, dsts = edit_rev_triple
            return (srcs[index] + u'/' + src_pos[index], dsts[index] + u'/' + dst_pos[index])

        def make_window_tags(sub_index, tags, window):
            #window内のタグを返す
            window_tags = []
            window_range = range( 1, window+1)

            for window_index in window_range:
                try:
                    pre_index = sub_index - window_index
                    window_tags.append(tags[pre_index])
                except IndexError:
                    pass
                try:
                    succ_index = sub_index + window_index
                    window_tags.append(tags[succ_index])
                except IndexError:
                    pass

            return window_tags

        edit_rev_triple = self.build_edit_rev(src, dst)

        # tokenize スペースで切るだけ
        src = src.split(u" ") # 添削前の文
        dst = dst.split(u" ") # 添削後の文

        sub_list = [] # 置換ペアのリストを格納する

        tags, srcs, dsts = edit_rev_triple

        # 置換されている単語がなければ、空のままリストを返す
        if sub_tag not in tags:
            return sub_list

        src_pos, dst_pos = self.pos_with_rev(edit_rev_triple)
        sub_tag_indexes = [i for i, x in enumerate(tags) if x == sub_tag]
        if self.with_pos:
            for sub_index in sub_tag_indexes:

                if len(tags) == 1: # １単語だけの時
                    if src_pos and dst_pos :
                        sub_list.append(make_string(edit_rev_triple, src_pos, dst_pos, sub_index))
                else:
                    window_tags = make_window_tags(sub_index, tags, window)
                    if all([ x == eq_tag for x in window_tags]):
                        sub_list.append(make_string(edit_rev_triple, src_pos, dst_pos,sub_index))

        if self.eq_include:
            if self.with_pos:
                for t, s, d, sp, dp in zip(tags, srcs, dsts, src_pos, dst_pos):
                    if t == eq_tag:
                        sub_list.append((s + u'/' + sp, d + u'/' + dp))
            else:
                for t, s, d in zip(tags, srcs, dsts):
                    if t == eq_tag:
                        sub_list.append((s, d))

        return sub_list


    def pos_with_rev(self, edit_rev_triple):
        """[FUNCTIONS] 三つ組の添削前,添削後の文に品詞をつける。
        """
        import sys

        from nltk.tag import pos_tag

        def make_pos(target_tag, edit_rev):
            tags, srcs, dsts = edit_rev_triple

            # target_tag: 文中に存在する
            # 品詞を付与する前に、文中から削除・追加タグが存在する部分を取り除く
            if target_tag == del_tag:
                sentence = dsts
            elif target_tag == add_tag:
                sentence = srcs

            if target_tag in tags:
                tag_indexes = [i for i, x in enumerate(tags) if x == target_tag]
                trimed = sentence
                for tag_index in tag_indexes:
                    trimed = trimed[:tag_index] + trimed[tag_index+1:]

                posed = pos_tag(trimed)
                pos = [w[1] for w in posed]
                for tag_index in tag_indexes:
                    pos.insert(tag_index, u'')

                #debug
                None_indexes = [i for i, x in enumerate(pos) if x == u'']
                if tag_indexes != None_indexes:
                    print >>sys.stderr, tag_indexes
                    print >>sys.stderr, None_indexes
                    print >>sys.stderr, tags
                    print >>sys.stderr, pos
            else:
                posed = pos_tag(u' '.join(sentence).split())
                pos = [w[1] for w in posed]

            return pos

        tags, srcs, dsts = edit_rev_triple

        src_pos = make_pos(add_tag, edit_rev_triple)
        dst_pos = make_pos(del_tag, edit_rev_triple)

        return src_pos, dst_pos


    def distance(self, src, dst):
        """[FUNCTIONS] 二つの文字列の編集距離を返す。
        Key word argument:
        src    -- 文字列その1。例えば、学習者の文。 :: unicode
        dst    -- 文字列その2。例えば、添削文。     :: unicode

        Return value:
        edit_distance :: int
        """

        edit_graph = self.build_edit_graph(src, dst)
        return edit_graph[-1][-1]
