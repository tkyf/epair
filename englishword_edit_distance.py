# -*- coding: utf-8 -*-

# edit tag
eq_tag =  '.'
add_tag = '+'
del_tag = '-'
sub_tag = '/'

class EditDistance(object):

    def __init__(self, eq_include=False, no_pos=False, is_test=False):
        """
        eq_include -- Output words not only difference pairs but also no changes if a specified condition is True.
        no_pos -- Append parts of speech to difference pairs if a specified condition is True.
        is_test -- Show progress if a specified condition is True.
        """

        self.eq_include = eq_include
        self.with_pos = not no_pos
        self.is_test = is_test

       
    def build_edit_graph(self, src, dst):
        """[FUNCTIONS] Build edit graph between two sentences.

        Keyword argument:
        src -- first sentence e.g. a sentence written by learner :: unicode
        dst -- second sentence e.g. a revised sentence  :: unicode

        Return value:
        edit_graph  :: [[int]]
        """

        # tokenize
        src = src.split(u" ")
        dst = dst.split(u" ")

        # Initialize a two-dimesional for edit graph to be used for dynamic programming
        m = [[0] * (len(dst)+1) for i in range(len(src) +1)]

        # Initialize LD(i,0)
        for i in xrange(len(src) + 1):
            m[i][0] = i

        # Initialize LD(0,j)
        for j in xrange(len(dst)+1):
            m[0][j] = j

        # build edit graph
        for i in xrange(1, len(src) + 1):
            for j in xrange(1, len(dst) + 1):
                if src[i - 1] == dst[j - 1]:
                    x = 0
                else:
                    x = 1
                m[i][j] = min(m[i-1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + x)

        return m


    def build_edit_trail(self, src, dst):
        """[FUNCTIONS] Trace the edit graph from end to make a revision history.
        The revision history is a list composed of strings 'add', 'del', 'eq' and 'sub'.

        Keyword arguments:
        src -- first sentence e.g. a sentence written by learner :: unicode
        dst -- second sentence e.g. a revised sentence  :: unicode
        """
        m = self.build_edit_graph(src, dst)

        # tokenize
        src = src.split(u" ")
        dst = dst.split(u" ")

        #最後からたどるために、エディットグラフの右下のインデックスを得る
        # Get index at end of the edit graph.
        i = len(m) - 1
        j = len(m[0]) - 1
        now = m[i][j]

        edit_trail = []
        while(i > 0 or j > 0):
            up_index = m[i - 1][j]
            diagonal_index = m[i -1][j - 1]
            left_index = m[i][j - 1]

            # priority: eq(diagonal),sub(diagonal), del(up), add(left)
            min_list = [diagonal_index, up_index, left_index]
            min_num = min(min_list)
            min_index = min_list.index(min_num)

            # at top
            if i == 0:
                j -= 1
                edit_trail.append('add')
            # at left end
            elif j == 0:
                i -= 1
                edit_trail.append('del')
            # diagonal
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

        # Reverse to get revision history from start.
        return list(reversed(edit_trail))


    def build_edit_rev(self, src, dst):
        """[FUNCTIONS] Build a triple composed by a edit tag, a string before change, a string after change
        Insert u'＿' to position of a added word in a string before change.
        Insert u'＿' to position of a deleted word in a string after change.

        Keyword arguments:
        src -- first sentence e.g. a sentence written by learner :: unicode
        dst -- second sentence e.g. a revised sentence  :: unicode

        Return value:
        (tag_list, src_list, dst_list)

        """

        edit_trail = self.build_edit_trail(src, dst)

        # tokenize
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
                print 'this tag is not defined'

        return (tags, srcs, dsts)


    def extract(self, src, dst):
        """[FUNCTIONS] make a list of expression pair of two strings.
        """
        edit_rev_triple = self.build_edit_rev(src, dst)

        # tokenize
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
        """[FUNCTIONS] make a list of expression pair of two strings.
        Extract all words isolation replace operations.
        window 1: tri-gram
               2: 5gram
               3: 7gram
               ...
        """
        def make_string(edit_rev_triple, src_pos, dst_pos, index):
            tags, srcs, dsts = edit_rev_triple
            return (srcs[index] + u'/' + src_pos[index], dsts[index] + u'/' + dst_pos[index])

        def make_window_tags(sub_index, tags, window):
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

        # tokenize
        src = src.split(u" ")
        dst = dst.split(u" ")

        sub_list = [] # difference list

        tags, srcs, dsts = edit_rev_triple

        if sub_tag not in tags:
            return sub_list

        src_pos, dst_pos = self.pos_with_rev(edit_rev_triple)
        sub_tag_indexes = [i for i, x in enumerate(tags) if x == sub_tag]
        if self.with_pos:
            for sub_index in sub_tag_indexes:

                if len(tags) == 1:
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
        """[FUNCTIONS] Add parts of speech to a sentence before change and a sentence after change.
        """
        import sys

        from nltk.tag import pos_tag

        def make_pos(target_tag, edit_rev):
            tags, srcs, dsts = edit_rev_triple

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
        """[FUNCTIONS] return a levenshtein distance of two sentences.
        Key word argument:
        src -- first sentence e.g. a sentence written by learner :: unicode
        dst -- second sentence e.g. a revised sentence  :: unicode

        Return value:
        edit_distance :: int
        """

        edit_graph = self.build_edit_graph(src, dst)
        return edit_graph[-1][-1]
