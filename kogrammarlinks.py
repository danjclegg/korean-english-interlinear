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
        self.supplementary_grammar_links = {
            '~은':('Subject/Topic', '9DK', 'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic'),
            '~는':('Subject/Topic', '9DK', 'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic'),
            '~이':('Subject', '9DK', 'https://www.90daykorean.com/korean-particles/#-i-ga-subject'),
            '~가':('Subject', '9DK', 'https://www.90daykorean.com/korean-particles/#-i-ga-subject'),
            '~을':('Object', '9DK', 'https://www.90daykorean.com/korean-particles/#-eulreul-object'),
            '~를':('Object', '9DK', 'https://www.90daykorean.com/korean-particles/#-eulreul-object'),
            '~에':('Time/Location', '9DK', 'https://www.90daykorean.com/korean-particles/#-e-timelocation'),
            '~에서':('Location', '9DK', 'https://www.90daykorean.com/korean-particles/#-eseo-location'),
            '~께':('To give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            '~에게':('To give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            '~한테':('To give', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something'),
            '~께서':('To receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            '~에서':('To receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            '~한테서':('To receive', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone'),
            '~도': ('Also', '9DK', 'https://www.90daykorean.com/korean-particles/#-do-also'),
            '~(으)로': ('Direction etc.', '9DK', 'https://www.90daykorean.com/korean-particles/#-euroro-direction-and-multiple-other-meanings'),
            '~부터': ('Start', '9DK', 'https://www.90daykorean.com/korean-particles/#-buteo-start'),
            '~까지': ('Until', '9DK', 'https://www.90daykorean.com/korean-particles/#-kkaji-until'),
            '~들': ('Plural', '9DK', 'https://www.90daykorean.com/korean-particles/#-deul-plural'),
            '~만': ('Only', '9DK', 'https://www.90daykorean.com/korean-particles/#-man-only'),
            '~의': ('Possessive/\'s', '9DK', 'https://www.90daykorean.com/korean-particles/#-ui-possessive'),
            '~과': ('and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with'),
            '~와': ('and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with'),
            '~(이)랑': ('and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-irangrang-andwithas-with'),
            '~하고': ('and/with/as with', '9DK', 'https://www.90daykorean.com/korean-particles/#-hago-andwithas-with'),
            '~고': ('connective', '9DK', 'https://www.90daykorean.com/korean-particles/#-go-connective'),
            '-(으)면': ('if/when -, then', 'DAN', '#'),
            '-던': ('- was', 'DAN', '#'),
            '-에게': ('to/w.r.t. -', 'DAN', '#'),
            '~(으)며': ('while', 'STK', 'https://korean.stackexchange.com/questions/2628/when-would-i-use-%EB%A9%B4%EC%84%9C-vs-%EB%A9%B0'),
            '~(으)면서': ('concurrently', 'STK', 'https://korean.stackexchange.com/questions/2628/when-would-i-use-%EB%A9%B4%EC%84%9C-vs-%EB%A9%B0'),
            '-서': ('so/so as to', 'HAD', 'https://hanguladay.com/2009/01/24/verbs-in-infinitive-and-particle-%EC%84%9C/'),
            '-(으)세': ('lets -', 'KGF', 'http://koreangrammaticalforms.com/entry.php?eid=0000001335')
        }

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
                matches.append(("KGF: " + key, "http://koreangrammaticalforms.com/entry.php?eid=" + html.escape(self.grammarlinks[key])))
        return matches


    def supplementary_matches_search(self, pattern):
        matches = []
        for key in self.supplementary_grammar_links:
            if re.match(pattern, key) is not None:
                matches.append((self.supplementary_grammar_links[key][1] + ": " + key + " " + self.supplementary_grammar_links[key][0], self.supplementary_grammar_links[key][2]))
        return matches


    def search_word_method1(self, branch, nextbranch):
        # first strip symbols
        # example stripped: branch = [('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]
        branch = self.get_plain_branch(branch)
        if nextbranch != None: 
            nextbranch = self.get_plain_branch(nextbranch)
            
        endings = []
        for i in reversed(range(0, len(branch))):
            if branch[i][1] not in self.particleclasses:
                break
            endings.append(branch[i])
        endings.reverse()    
        
        wordcombined = "".join([e[0] for e in branch])
        endingscombined = "".join([e[0] for e in endings])
        
        # try straight all together lookup
        # then try removing one char by one char from head
        for remove in range(0, (len(endingscombined) - 1) + 1):
            #print("remove:")
            #print(remove)
            endingscombinedcut = endingscombined[remove:len(endingscombined)]
            
            # at each step, try:
            # searching for the word, optionally prepended 
            # with dash or tilde and also could be prepended 
            # by a ㄴ/ㄹ final consonant or also (이)/(으)/(느)/(는)/(를) chars
            # need to have prepared the final consonant prior and the 
            # whole char prior then match as above
            # also can have immediately trailing:
            # blank, newline, 만, 요, 도, 를,는, 은, 을        
            # --which may also have brackets around it or not
            
            #print(branch)
            #print(endingscombined)
            #print(endingscombinedcut)
                            
            # searchpattern for Korean Grammatical Forms
            pattern = '^\s*'
            # pattern for supplementary links
            suppattern = '^'
            
            if len(endingscombinedcut) < len(wordcombined):
                # then we're working on a subset of the word, not the whole word
                pattern = pattern + '[-~]?\s*'
                suppattern = suppattern + '[-~]?\s*'
                priorchar = wordcombined[len(wordcombined) - len(endingscombinedcut) - 1]
                #print(priorchar)
                priorchar_final = hangul.get_final(priorchar)
                #print(priorchar_final)
                if priorchar_final != '':
                    pattern = pattern + '(?:' + re.escape(priorchar_final) + '\s*)?'
                #pattern = pattern + '(?:\(' + re.escape(priorchar) + '\))?\s*'
                #suppattern = suppattern + '(?:\(' + re.escape(priorchar) + '\))?\s*'

            pattern = pattern + '(?:\(\w\))?\s*'
            suppattern = suppattern + '(?:\(\w\))?\s*'

            pattern = pattern + re.escape(endingscombinedcut) 
            suppattern = suppattern + re.escape(endingscombinedcut) 
            
            # pattern is matching bracketed trailing characters
            pattern = pattern + '(?:\([요는를은을]\))?[0-9]?(?:\s+|$)'
            
            if nextbranch != None and nextbranch and len(nextbranch[0]) > 0:
                # then must also match next word 
                # or also any character other than a korean character
                nextmorph = nextbranch[0][0]
                pattern = pattern + '(?:' + re.escape(nextmorph) + '.*$|\s*$)'
                #to include english text trailing add this to above: |[a-zA-Z0-9].*$|
            else:
                # then must match end as no later word
                pattern = pattern + '\s*$'
                #to include english text trailing add this to above: |[a-zA-Z0-9].*$|
            suppattern = suppattern + '$'
            
            grammarlinks = self.supplementary_matches_search(suppattern)
            #print(len(grammarlinks))
            grammarlinks.extend(self.matches_search(pattern))
            #print(len(grammarlinks))                    
         
            if grammarlinks:
                return grammarlinks
        return []


    def search_word_method2(self, branch, nextbranch):
        grammarlinks = []

        #go through each chunk of the branch
        for i in range(0, len(branch)):
            #check if chunk is particle
            if len(branch[i]) > 1 and branch[i][1] in self.particleclasses:
                
                #particle we're focusing on here
                particle = branch[i][0]
                
                #find prior character and final element of that char
                if i > 0 and len(branch[i-1]) > 1 and len(branch[i-1][1]) > 0 and branch[i-1][1][0] != "S":
                    preceeding_char = branch[i-1][0][-1]
                    preceeding_char_final = hangul.get_final(preceeding_char)
                else:
                    preceeding_char = ""
                    preceeding_char_final = ""
                
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
                
                #if particle == "면":
                    #print("branch i; particle, preceeding_char, preceeding_char_final, hit_a_symbol, last_morph_index, remaining_morphs, nextmorph_text, nextbranch")
                    #print(str(branch) + " " + str(i) + "\t" + str(particle) + "\t" + str(preceeding_char) + "\t" + str(preceeding_char_final) + "\t" + str(hit_a_symbol) + "\t'" + str(last_morph_index) + "'\t'" + str(remaining_morphs) + "'\t'" + str(nextmorph_text) + "'\t" + str(nextbranch))
                    
        #print(grammarlinks)    
        return grammarlinks

    def search(self, branch, nextbranch = None):
        # input for branch and nextbranch are output elements of 
        # list of morphemes and POS from Konlpy/Mecab
        # example input: branch = [('“', 'SSO'), ('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]

        grammarlinks = self.search_word_method2(branch, nextbranch)
        
        if grammarlinks:
            return grammarlinks
        
        grammarlinks = self.search_word_method1(branch, nextbranch)
        #if grammarlinks:
            #print("*********************found grammarlinks with fallback***********************************")
            ##if branch == [('재산', 'NNG'), ('으로', 'JKB')]:
               ##from IPython import embed; embed()  # https://switowski.com/blog/ipython-debugging
            #print(branch)
            #print(grammarlinks)
        
        return grammarlinks












