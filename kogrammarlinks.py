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
        self.ninetydaykoreanlinks = {
            '~은 (Subject/Topic)':		'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic',
            '~는 (Subject/Topic)':		'https://www.90daykorean.com/korean-particles/#-eun-neun-subjecttopic',
            '~이 (Subject)': 			'https://www.90daykorean.com/korean-particles/#-i-ga-subject',
            '~가 (Subject)': 			'https://www.90daykorean.com/korean-particles/#-i-ga-subject',
            '~을 (Object)': 				'https://www.90daykorean.com/korean-particles/#-eulreul-object',
            '~를 (Object)': 				'https://www.90daykorean.com/korean-particles/#-eulreul-object',
            '~에 (Time/Location)': 		'https://www.90daykorean.com/korean-particles/#-e-timelocation',
            '~에서 (Location)': 			'https://www.90daykorean.com/korean-particles/#-eseo-location',
            '~께 (To give)':		        'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something',
            '~에게 (To give)':		    'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something',
            '~한테 (To give)':		    'https://www.90daykorean.com/korean-particles/#-kkeegehante-to-give-someone-something',
            '~께서 (To receive)': 	    'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone',
            '~에서 (To receive)':        'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone',
            '~한테서 (To receive)': 	    'https://www.90daykorean.com/korean-particles/#-kkeseoeseohanteseo-to-receive-something-from-someone',
            '~도 (Also)': 				'https://www.90daykorean.com/korean-particles/#-do-also',
            '~(으)로 (Direction etc.)':	'https://www.90daykorean.com/korean-particles/#-euroro-direction-and-multiple-other-meanings',
            '~부터 (Start)': 			'https://www.90daykorean.com/korean-particles/#-buteo-start',
            '~까지 (Until)': 			'https://www.90daykorean.com/korean-particles/#-kkaji-until',
            '~들 (Plural)': 			    'https://www.90daykorean.com/korean-particles/#-deul-plural',
            '~만 (Only)': 				'https://www.90daykorean.com/korean-particles/#-man-only',
            '~의 (Possessive)': 			'https://www.90daykorean.com/korean-particles/#-ui-possessive',
            '~과 (and/with/as with)': 	'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with',
            '~와 (and/with/as with)': 	'https://www.90daykorean.com/korean-particles/#-gwawa-andwithas-with',
            '~(이)랑 (and/with/as with)':'https://www.90daykorean.com/korean-particles/#-irangrang-andwithas-with',
            '~하고 (and/with/as with)': 	'https://www.90daykorean.com/korean-particles/#-hago-andwithas-with',
            '~고 (connective)': 			'https://www.90daykorean.com/korean-particles/#-go-connective'
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
        for key in self.ninetydaykoreanlinks:
            if re.match(pattern, key) is not None:
                matches.append(("9DK: " + key, self.ninetydaykoreanlinks[key]))
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
                pattern = pattern + '(?:\(' + re.escape(priorchar) + '\))?\s*'
                suppattern = suppattern + '(?:\(' + re.escape(priorchar) + '\))?\s*'

            pattern = pattern + re.escape(endingscombinedcut) 
            suppattern = suppattern + re.escape(endingscombinedcut) 
            
            # pattern is matching bracketed trailing characters
            pattern = pattern + '(?:\(?[요는를은을]\)?)?[0-9]?(?:\s+|$)'
            
            # suppattern is matching bracketed translations so can be separated by 
            # whitespace at beginning here
            suppattern = suppattern + '\s*(?:\([^\)]*\))?'
            
            if nextbranch != None and nextbranch and len(nextbranch[0]) > 0:
                # then must also match next word 
                # or also any character other than a korean character
                nextmorph = nextbranch[0][0]
                pattern = pattern + '(?:' + re.escape(nextmorph) + '.*$|[a-zA-Z0-9].*$|\s*$)'
            else:
                # then must match end as no later word
                pattern = pattern + '(?:[a-zA-Z0-9].*$|\s*$)'
            suppattern = suppattern + '\s*$'
            
            grammarlinks = self.matches_search(pattern)
            #print(len(grammarlinks))
            grammarlinks.extend(self.supplementary_matches_search(suppattern))
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
                
                #print("branch i; particle, preceeding_char, preceeding_char_final, hit_a_symbol, last_morph_index, remaining_morphs, nextmorph_text, nextbranch")
                #print(str(branch) + " " + str(i) + "\t" + str(particle) + "\t" + str(preceeding_char) + "\t" + str(preceeding_char_final) + "\t" + str(hit_a_symbol) + "\t'" + str(last_morph_index) + "'\t'" + str(remaining_morphs) + "'\t'" + str(nextmorph_text) + "'\t" + str(nextbranch))
                
                pattern = '^\s*'
                # pattern for supplementary links
                suppattern = '^'
                
                if preceeding_char != "":
                    pattern = pattern + '[-~]?\s*'
                    suppattern = suppattern + '[-~]?\s*'
                    if preceeding_char_final != '':
                        pattern = pattern + '(?:' + re.escape(preceeding_char_final) + '\s*)?'
                    pattern = pattern + '(?:\(' + re.escape(preceeding_char) + '\))?\s*'
                    suppattern = suppattern + '(?:\(' + re.escape(preceeding_char) + '\))?\s*'

                pattern = pattern + re.escape(particle) 
                suppattern = suppattern + re.escape(particle) 
                
                if remaining_morphs_text != "":
                    # matching remainaing_morphs
                    pattern = pattern + '(?:\(?' + re.escape(remaining_morphs_text) + '\)?)?'
                    suppattern = suppattern + '(?:\(?' + re.escape(remaining_morphs_text) + '\)?)?'
                
                # matching bracketed trailing characters 
                pattern = pattern + '(?:\(?[요는를은을다가요이]\)?)?[0-9]?(?:\s+|$)'
                
                # matching bracketed translations so can be separated by 
                # whitespace at beginning here
                suppattern = suppattern + '\s*(?:\([^\)]*\))?'
                
                if nextmorph_text != "":
                    # then must also match next word 
                    # or also any character other than a korean character
                    pattern = pattern + '(?:' + re.escape(nextmorph_text) + '.*$|[a-zA-Z0-9].*$|\s*$)'
                else:
                    # then must match end as no later word
                    pattern = pattern + '(?:[a-zA-Z0-9].*$|\s*$)'
                suppattern = suppattern + '\s*$'
                
                #print(pattern)
                #print(suppattern)

                grammarlinks.extend(self.matches_search(pattern))
                #print(len(grammarlinks))
                grammarlinks.extend(self.supplementary_matches_search(suppattern))
                #print(len(grammarlinks))                    
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
            #if branch == [('재산', 'NNG'), ('으로', 'JKB')]:
            #    from IPython import embed; embed()  # https://switowski.com/blog/ipython-debugging
            #print(branch)
        
        return grammarlinks












