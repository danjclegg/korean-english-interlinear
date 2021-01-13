import os.path
import json
import re
import urllib.request
from korean import hangul
import html

class KoGrammarLinks:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        self.grammarfilename = script_dir + "/kogrammarlinks.json"
        if not os.path.exists(self.grammarfilename):
            Exception("Error, grammar links file not found, run generate script first.")
            
        with open(self.grammarfilename, 'r') as f:
            grammarlinks = json.load(f)
        self.grammarlinks = dict((y, x) for x, y in grammarlinks)

        # for selecting particles in these superclasses:
        # VerbalEnding, AuxPostposition, CaseMarker bits
        # which in Mecab's notation comprise following codes:
        self.particleclasses = ['EC', 'EF', 'EP', 'ETM', 'ETN', 'JC', 'JKB', 'JKC', 'JKG', 'JKO', 'JKQ', 'JKS', 'JKV', 'JX', 'XPN', 'XR', 'XSA', 'XSN', 'XSV']

        #supplementary list of basic particles
        self.supplementary_grammar_links = [
            ('~은', 'subject/topic', '9DK', 'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic'),
            ('~는', 'subject/topic', '9DK', 'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic'),
            ('~이', 'subject', '9DK', 'https://www.90daykorean.com/korean-particles/#-i-ga-subject'),
            ('~가', 'subject', '9DK', 'https://www.90daykorean.com/korean-particles/#-i-ga-subject'),
            ('~을', 'object', '9DK', 'https://www.90daykorean.com/korean-particles/#-eulreul-object'),
            ('~를', 'object', '9DK', 'https://www.90daykorean.com/korean-particles/#-eulreul-object'),
            ('~에', 'time/location', '9DK', 'https://www.90daykorean.com/korean-particles/#-e-timelocation'),
            ('~에서', 'location', '9DK', 'https://www.90daykorean.com/korean-particles/#-eseo-location'),
            ('~께', 'to give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            ('~에게', 'to give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            ('~한테', 'to give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            ('~께서', 'to receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            ('~에서', 'to receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            ('~한테서', 'to receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            ('~도', 'also', '9DK', 'https://www.90daykorean.com/korean-particles/#-do-also'),
            ('~(으)로', 'direction etc.', '9DK', 'https://www.90daykorean.com/korean-particles/#-euroro-direction-and-multiple-other-meanings'),
            ('~부터', 'start', '9DK', 'https://www.90daykorean.com/korean-particles/#-buteo-start'),
            ('~까지', 'until', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkaji-until'),
            ('~들', 'plural', '9DK', 'https://www.90daykorean.com/korean-particles/#-deul-plural'),
            ('~만', 'only', '9DK', 'https://www.90daykorean.com/korean-particles/#-man-only'),
            ('~의', 'possessive/\'s', '9DK', 'https://www.90daykorean.com/korean-particles/#-ui-possessive'),
            ('~과', 'and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with'),
            ('~와', 'and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with'),
            ('~(이)랑', 'and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-irangrang-andwithas-with'),
            ('~하고', 'and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-hago-andwithas-with'),
            ('~고', 'connective', '9DK', 'https://www.90daykorean.com/korean-particles/#-go-connective'),
            ('-(으)면', 'if/when -, then', 'DAN', '#'),
            ('-에게', 'to/w.r.t. -', 'DAN', '#'),
            ('~(으)며', 'while', 'STK', 'https://korean.stackexchange.com/questions/2628/when-would-i-use-%EB%A9%B4%EC%84%9C-vs-%EB%A9%B0'),
            ('~(으)면서', 'concurrently', 'STK', 'https://korean.stackexchange.com/questions/2628/when-would-i-use-%EB%A9%B4%EC%84%9C-vs-%EB%A9%B0'),
            ('-서', 'so/so as to', 'HAD', 'https://hanguladay.com/2009/01/24/verbs-in-infinitive-and-particle-%EC%84%9C/'),
            ('-(으)세', 'lets -', 'KGF', 'http://koreangrammaticalforms.com/entry.php?eid=0000001335'),
            ('-(이)라는', '-called', '1LK', 'https://123learnkorean.wordpress.com/2009/08/25/%EC%9D%B4%EB%9D%BC%EB%8A%94-called/'),
            ('-게', 'so that -, - caused by', 'HSK', 'https://www.howtostudykorean.com/unit-3-intermediate-korean-grammar/unit-3-lessons-51-58/lesson-56/#56new'),
            ('-자', 'let\'s -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-42-50/lesson-44/#441'),
            #next one should match both
            #('-읍시다', 'let\'s -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-42-50/lesson-44/#441'),
            ('-ㅂ시다', 'let\'s -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-42-50/lesson-44/#441'),
            ('-던', 'past experience -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-26-33/lesson-27/#271'),
            ('-았던', 'past experience -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-26-33/lesson-27/#271'),
            ('-었던', 'past experience -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-26-33/lesson-27/#271'),
            ('-은', 'past -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-26-33/lesson-27/#271'),
            
            ('-에게', 'to/at (animate)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/dative_particle'),
            ('-한테', 'to/at (animate)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/dative_particle'),
            ('-게', 'to/at (animate hon.)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/dative_particle'),
            ('-에', 'to/at (inanimate)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/dative_particle'),
            ('-에서', 'where action happen', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/direction'),
            ('-에서', 'point of departure', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/direction'),
            ('-에게서', 'from (animate)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/direction'),
            ('-한테서', 'from (animate)', 'ZKO', 'https://zkorean.com/reference/grammar_lessons/direction'),
            
            ('-지만', '-is true but not …', 'KRDict', ''),
            ('-여', 'before, polite, cause, exceed', 'KRDict', ''),
            ('-지', 'deny -, prohibit -, contradict, confirming, place', 'KRDict', ''),
            ('-한', '-related person', 'KRDict', ''),
            
            # following summaries written by Yufina88 on Reddit r/korean, 
            # further shortened by myself
            # https://www.reddit.com/r/Korean/comments/84ni3g/korean_particle_frequency_list/
            ('을', 'direct object', 'YUF', ''),
            ('를', 'direct object', 'YUF', ''),
            ('이', 'subject', 'YUF', ''),
            ('가', 'subject', 'YUF', ''),
            ('은', 'as for', 'YUF', ''),
            ('는', 'as for', 'YUF', ''),
            ('에', 'to/in/at/per/plus', 'YUF', ''),
            ('의', 'possessive', 'YUF', ''),
            ('(으)로', 'as/by/with', 'YUF', ''),
            ('도', 'also, even', 'YUF', ''),
            ('들', 'plural', 'YUF', ''),
            ('에서', 'from/at/in', 'YUF', ''),
            ('와/과', 'and/with', 'YUF', ''),
            ('(이)나', 'about/or', 'YUF', ''),
            ('만', 'only', 'YUF', ''),
            ('에게', 'for/towards/to', 'YUF', ''),
            ('까지', 'to, until, including', 'YUF', ''),
            ('처럼', 'like', 'YUF', ''),
            ('보다', 'more than, as … as', 'YUF', ''),
            ('께서', 'honorific of 이/가', 'YUF', ''),
            ('부터', 'from', 'YUF', ''),
            ('서', 'from/at/in (in speech)', 'YUF', ''),
            ('서', 'all by/just (혼자, 둘이)', 'YUF', ''),
            ('야', 'vocative part.', 'YUF', ''),
            ('아', 'vocative part.', 'YUF', ''),
            ('(으)로서', 'as', 'YUF', ''),
            ('(이)라도', 'even, at least', 'YUF', ''),
            ('아요', 'informal polite', 'YUF', ''),
            ('어요', 'informal polite', 'YUF', ''),
            ('여요', 'informal polite', 'YUF', ''),
            ('마다', 'every', 'YUF', ''),
            ('한테', 'for/towards/to', 'YUF', ''),
            ('(이)란', 'a thing called…', 'YUF', ''),
            ('밖에', 'nothing but', 'YUF', ''),
            ('(으)로부터', 'from', 'YUF', ''),
            ('(이)야', 'if it\'s/if it were', 'YUF', ''),
            ('뿐', 'only, just', 'YUF', ''),
            ('께', 'for/towards/to (honorific)', 'YUF', ''),
            ('라고', 'quoted speech', 'YUF', ''),
            ('(으)로써', 'by means', 'YUF', ''),
            ('에다', 'in/on/addition to', 'YUF', ''),
            ('에다가', 'in/on/addition to', 'YUF', ''),
            ('대로', 'in accordance with', 'YUF', ''),
            ('게', 'for/towards/to', 'YUF', ''),
            ('(이)랑', 'and/with', 'YUF', ''),
            ('조차', 'every', 'YUF', ''),
            ('하고', 'and/with', 'YUF', ''),
            ('만큼', 'as …as', 'YUF', ''),
            ('같이', 'like', 'YUF', ''),
            ('고', 'quoted speech', 'YUF', ''),
            ('에게서', 'from', 'YUF', ''),
            ('마저', 'every', 'YUF', ''),
            ('(에)서부터', 'from (a place)', 'YUF', ''),
            ('(이)든지', 'whether/either …or…', 'YUF', ''),
            ('(이)든가', 'whether/either …or…', 'YUF', ''),
            ('(이)든', 'whether/either …or…', 'YUF', ''),
            ('(이)고', 'and (equal)', 'YUF', ''),
            ('한테서', 'from', 'YUF', ''),
            ('더러', 'to (quoted speech, commands)', 'YUF', ''),
            ('은커녕', 'far from', 'YUF', ''),
            ('는커녕', 'far from', 'YUF', ''),
            ('(이)야말로', 'indeed', 'YUF', ''),
            ('(이)니', 'and (equal)', 'YUF', ''),
            ('마냥', 'like', 'YUF', ''),
            ('(이)라든가', 'such as … or', 'YUF', ''),
            ('(이)며', 'and (long lists)', 'YUF', ''),
            ('(이)ㄴ들', 'even tough', 'YUF', ''),
            ('치고', 'without exception', 'YUF', ''),
            ('에게로', 'for/towards/to', 'YUF', ''),
            ('(이)라든지', 'such as … or', 'YUF', ''),
            ('보고', 'to', 'YUF', ''),
            ('(이)나마', 'At least/although (displeasing)', 'YUF', ''),
            ('따라', 'usually (오늘, 그날)', 'YUF', '')
            #less prevalent blank entries to be completed if not already above
            #('(이)라고', '', 'YUF', ''),
            #('깨나', '', 'YUF', ''),
            #('(이)라면', '', 'YUF', ''),
            #('마(는)', '', 'YUF', ''),
            #('만치', '', 'YUF', ''),
            #('만(은)', '', 'YUF', ''),
            #('(이)면', '', 'YUF', ''),
            #('하며', '', 'YUF', ''),
            #('(이)다', '', 'YUF', '')
        ]

    #to be used manually only to cache links for lookup by rest of this class
    def download_links():
        if os.path.exists(self.grammarfilename):
            print("File already exists " + self.grammarfilename)
            return
        
        if(input("\nFetch grammar links? (y/n):") == "y"):
            print("Compiling links for grammar...")
            pagereq = urllib.request.urlopen('http://koreangrammaticalforms.com/')
            pagedata = pagereq.read().decode('utf-8')
            subpages = re.findall(r'javascript: GetPage\(\'([^\']*)\'\);', pagedata)
            entrylinkstotal = []
            
            for subpage in subpages:            
                subpage = "http://koreangrammaticalforms.com/" + subpage
                print(subpage)
                subpagereq = urllib.request.urlopen(subpage)
                subpagedata = subpagereq.read().decode('utf-8')
                entrylinks = re.findall(r'<a href="entry\.php\?eid=([0-9]*)" target="_blank">([^<]*)</a>', subpagedata)
                entrylinkstotal.extend(entrylinks)
            
            with open(self.grammarfilename, 'w') as f:
                json.dump(entrylinkstotal, f)
                
            print("Written to " + self.grammarfilename)
    
    
    def get_plain_branch(self, branch):
        without_symbols = [x for x in branch if len(x) > 1 and len(x[1]) > 0 and x[1][0] != "S"]
        return without_symbols
    
    
    def matches_search(self, pattern):
        matches = []
        for key in self.grammarlinks:
            if re.match(pattern, key) is not None:
                matches.append((key, "", "KGF", "http://koreangrammaticalforms.com/entry.php?eid=" + html.escape(self.grammarlinks[key])))
        return matches

    
    #this can be made to use list comprehension inline later:
    def supplementary_matches_search(self, pattern):
        matches = []
        for suplink in self.supplementary_grammar_links:
            if re.match(pattern, suplink[0]) is not None:
                matches.append(suplink)
        return matches


    def search_particle(self, i, branch, nextbranch, trunc = 0):
        #particle we're focusing on here
        particle = branch[i][0]
        
        if trunc:
            #if we're asked to cut off head of this particle 
            if len(particle) > trunc:
                particle = particle[trunc:]
                preceeding_char = particle[trunc - 1]
            else:
                # skip this particle if too short to trunc 
                # as this method only used as backup
                return []
        else:
            #here we're not truncating, normal case
            if i > 0 and len(branch[i-1]) > 1 and len(branch[i-1][1]) > 0 and branch[i-1][1][0] != "S":
                preceeding_char = branch[i-1][0][-1]
            else:
                preceeding_char = ""
        
        # if we're truncating, then skip any obvious endings
        if trunc and (particle == "요" or particle == "은" or particle == "을" or particle == "는" or particle == "를" or particle == "다"):
            return []
        
        #get final element of that char
        preceeding_char_final = hangul.get_final(preceeding_char)
        
        #get the rest of the branch up to symbol or end
        hit_a_symbol = False
        last_morph_index = -1
        if len(branch) > i + 1:
            for j in range(i + 1, len(branch)):
                #print(j)
                if len(branch[j]) > 1 and len(branch[j][1]) > 0 and branch[j][1][0] == "S":
                    hit_a_symbol = True
                    last_morph_index = j - 1
                    break
                elif j == len(branch) - 1:
                    #then hit end without finding symbol
                    last_morph_index = j
                    break
        remaining_morphs = []
        if last_morph_index >= i + 1:
            remaining_morphs = branch[i + 1: last_morph_index + 1]
        remaining_morphs_text = "".join(morph[0] for morph in remaining_morphs if morph)
        
        nextmorph_text = ""
        if not hit_a_symbol and nextbranch != None and nextbranch and len(nextbranch[0]) > 0:
            nextmorph_text = nextbranch[0][0]
        
        pattern = '^\s*'
        # pattern for supplementary links
        suppattern = '^'
        
        if preceeding_char != "":
            pattern = pattern + '[-~]?\s*'
            suppattern = suppattern + '[-~]?\s*'
            if preceeding_char_final != '':
                pattern = pattern + '(?:' + re.escape(preceeding_char_final) + '\s*)?'
            #pattern = pattern + '(?:\(' + re.escape(preceeding_char) + '\))?\s*'
            #suppattern = suppattern + '(?:\(' + re.escape(preceeding_char) + '\))?\s*'
        
        pattern = pattern + '(?:\(\w\))?\s*'
        suppattern = suppattern + '(?:\(\w\))?\s*'

        pattern = pattern + re.escape(particle) 
        suppattern = suppattern + re.escape(particle) 
        
        if remaining_morphs_text != "":
            # matching remainaing_morphs
            pattern = pattern + '(?:\(?' + re.escape(remaining_morphs_text) + '\)?)?'
            suppattern = suppattern + '(?:\(?' + re.escape(remaining_morphs_text) + '\)?)?'
        
        # matching bracketed trailing characters 
        pattern = pattern + '(?:\([요는를은을요이]\))?[0-9]?(?:\s+|$)'
        
        if nextmorph_text != "":
            # then must also match next word 
            pattern = pattern + '(?:' + re.escape(nextmorph_text) + '.*$|\s*$)'
            #to include english text trailing add this to above: |[a-zA-Z0-9].*$|
        else:
            # then must match end as no later word
            pattern = pattern + '\s*$'
            #to include english text trailing add this to above: |[a-zA-Z0-9].*$|
        suppattern = suppattern + '$'
        
        #print(pattern)
        #print(suppattern)
        
        grammarlinks = []
        grammarlinks.extend(self.supplementary_matches_search(suppattern))
        #print(len(grammarlinks))                    
        #grammarlinks.extend(self.matches_search(pattern))
        #print(len(grammarlinks))
        
        ##if particle == "은":
        #print("branch i; particle, preceeding_char, preceeding_char_final, hit_a_symbol, last_morph_index, remaining_morphs, nextmorph_text, nextbranch")
        #print(str(branch) + " " + str(i) + "\t" + str(particle) + "\t" + str(preceeding_char) + "\t" + str(preceeding_char_final) + "\t" + str(hit_a_symbol) + "\t'" + str(last_morph_index) + "'\t'" + str(remaining_morphs) + "'\t'" + str(nextmorph_text) + "'\t" + str(nextbranch))
        
        return grammarlinks        
    
    def get_trailing_particles_text(self, branch):
        out = branch
        trailing = ""
        #first strip trailing symbols
        while len(out) > 1 and len(out[-1]) > 1 and out[-1][1][0] == 'S':
            out = out[0:-1]
        #then find consecutive trailing particles
        while len(out) > 1 and len(out[-1]) > 1 and out[-1][1][0] in ['E', 'J', 'X']:
            trailing = out[-1][0] + trailing
            out = out[0:-1]
        return trailing

    def list_unique(self, inlist):
        unique = []
        for item in inlist:
            if item not in unique:
                unique.append(item)
        return unique

    def search(self, branch, nextbranch = None):
        # input for branch and nextbranch are output elements of 
        # list of morphemes and POS from Konlpy/Mecab
        # example input: branch = [('“', 'SSO'), ('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]
        
        grammarlinks = []
        #go through each chunk of the branch
        for i in range(0, len(branch)):
            #check if chunk is particle
            if len(branch[i]) > 1 and branch[i][1] in self.particleclasses:
                particle_grammarlinks = self.search_particle(i, branch, nextbranch, 0)
                if particle_grammarlinks:
                    grammarlinks.extend(particle_grammarlinks)
                else:
                    particle_grammarlinks = self.search_particle(i, branch, nextbranch, 1)
                    grammarlinks.extend(particle_grammarlinks)
                grammarlinks.extend([(branch[i][0], "", "KRDict search", urllib.parse.quote(branch[i][0]))])

        trailingparticlestext = self.get_trailing_particles_text(branch)
        if trailingparticlestext:
            grammarlinks.extend([(trailingparticlestext, "", "KRDict search", urllib.parse.quote(trailingparticlestext))])

        grammarlinks = self.list_unique(grammarlinks)

        #print(grammarlinks)    
        return grammarlinks












