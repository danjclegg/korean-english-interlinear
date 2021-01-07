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
            ('-은', 'past -', 'HSK', 'https://www.howtostudykorean.com/unit-2-lower-intermediate-korean-grammar/unit-2-lessons-26-33/lesson-27/#271')
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
                matches.append((key, "http://koreangrammaticalforms.com/entry.php?eid=" + html.escape(self.grammarlinks[key])))
        return matches


    def supplementary_matches_search(self, pattern):
        matches = []
        for key, definition, source, link in self.supplementary_grammar_links:
            if re.match(pattern, key) is not None:
                matches.append((key + " " + definition, link))
        return matches


    def search_word(self, branch, nextbranch, trunc = 0):
        grammarlinks = []

        #go through each chunk of the branch
        for i in range(0, len(branch)):
            #check if chunk is particle
            if len(branch[i]) > 1 and branch[i][1] in self.particleclasses:
                
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
                        continue
                else:
                    #here we're not truncating, normal case
                    if i > 0 and len(branch[i-1]) > 1 and len(branch[i-1][1]) > 0 and branch[i-1][1][0] != "S":
                        preceeding_char = branch[i-1][0][-1]
                    else:
                        preceeding_char = ""
                
                # if we're truncating, then skip any obvious endings
                if trunc and (particle == "요" or particle == "은" or particle == "을" or particle == "는" or particle == "를" or particle == "다"):
                    continue
                
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

                grammarlinks.extend(self.supplementary_matches_search(suppattern))
                #print(len(grammarlinks))                    
                grammarlinks.extend(self.matches_search(pattern))
                #print(len(grammarlinks))
                
                ##if particle == "은":
                #print("branch i; particle, preceeding_char, preceeding_char_final, hit_a_symbol, last_morph_index, remaining_morphs, nextmorph_text, nextbranch")
                #print(str(branch) + " " + str(i) + "\t" + str(particle) + "\t" + str(preceeding_char) + "\t" + str(preceeding_char_final) + "\t" + str(hit_a_symbol) + "\t'" + str(last_morph_index) + "'\t'" + str(remaining_morphs) + "'\t'" + str(nextmorph_text) + "'\t" + str(nextbranch))
                    
        #print(grammarlinks)    
        return grammarlinks

    def search(self, branch, nextbranch = None):
        # input for branch and nextbranch are output elements of 
        # list of morphemes and POS from Konlpy/Mecab
        # example input: branch = [('“', 'SSO'), ('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]

        grammarlinks = self.search_word(branch, nextbranch)
        
        if grammarlinks:
            return grammarlinks
        
        grammarlinks = self.search_word(branch, nextbranch, 1)
        #if grammarlinks:
            #print("*********************found grammarlinks with fallback***********************************")
            ##if branch == [('재산', 'NNG'), ('으로', 'JKB')]:
               ##from IPython import embed; embed()  # https://switowski.com/blog/ipython-debugging
            #print(branch)
            #print(grammarlinks)
        
        return grammarlinks












