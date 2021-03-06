import html
import urllib.parse
import psycopg2
import textwrap
import json
import urllib.request
import re
from soylemma import Lemmatizer
import sejongtagset 
import kogrammarlinks
import mecablight
from hangul_romanize import Transliter
from hangul_romanize.rule import academic

# from IPython import embed; embed()  # https://switowski.com/blog/ipython-debugging

class KoInterlinear:
    def __init__(self, content, con):
        self.content = content
        self.content = [x.strip() for x in self.content.splitlines()]
        
        self.con = con
        
        self.pointer_char = "&#9094;" #&#10174; #&#10168; #&#10093;
        self.wrapper = textwrap.TextWrapper(placeholder = "…")

        self.output = []
    
        self.tipnumber = 0

        self.mecab = mecablight.MeCabLight()
        self.lemmatizer = Lemmatizer()

        self.transliterator = Transliter(academic)

        self.kogrammarlinks = kogrammarlinks.KoGrammarLinks()

        #self.missing_words = []

        self.particle_classes = ['E', 'J', 'S', 'X']

        ######################
        # connect to database and check tables are there

        self.cur = self.con.cursor()


    def get_sejongtagset_name(self, tag):
        tag = tag.split("+")[0]  # go with first tag if multiple
        if tag in sejongtagset.SejongTagset:
            return sejongtagset.SejongTagset[tag][0]
        else:
            return ""


    def get_sejongtagset_superclass(self, tag):
        tag = tag.split("+")[0]  # go with first tag if multiple
        if tag in sejongtagset.SejongTagset:
            return sejongtagset.SejongTagset[tag][1]
        else:
            print("Note: can't find " + tag + " in tagset!")
            return ""


    def get_sejongtagset_abbrev(self, tag):
        tag = tag.split("+")[0]  # go with first tag if multiple
        if tag in sejongtagset.SejongTagset:
            return sejongtagset.SejongTagset[tag][2]
        else:
            print("Note: can't find " + tag + " in tagset!")
            return ""


    def get_trans_fetch(self, word, original_word):
        self.cur.execute("SELECT word, def, extradata FROM korean_english WHERE word = %s ORDER BY extradata, wordid;", (word,))
        rows = self.cur.fetchall()
        if type(rows) is list and rows:
            return [( row[1] if word == original_word else
                      "[" + row[0] + "] " + row[1] )
                    for row in rows if row is not None and row[1] != None and row[1] != "" ]
        else:
            return []


    def fetch_phrase_translations(self, wordstr, nextwordstr = None, nextnextwordstr = None):
        if wordstr is not None and wordstr != "" and nextwordstr != "" and nextnextwordstr != "":
            if nextwordstr is None or nextwordstr == "":
                Exception("fetch_phrase_translations sent None for word2.")
            if nextnextwordstr is not None and nextnextwordstr != "":
                self.cur.execute("SELECT phrase, def AS trans FROM korean_english_phrase2word WHERE word1 = %s AND word2 = %s UNION SELECT phrase, def AS trans FROM korean_english_phrase3word WHERE word1 = %s AND word2 = %s AND word3 = %s;", (wordstr, nextwordstr, wordstr, nextwordstr, nextnextwordstr))
            else:
                self.cur.execute("SELECT phrase, def AS trans FROM korean_english_phrase2word WHERE word1 = %s AND word2 = %s;", (wordstr,nextwordstr))
        else:
            return []
        
        rows = self.cur.fetchall()

        if type(rows) is list and rows:
            return_rows = [" ".join([row[0], row[1]])
                            for row in rows if row is not None and row[1] is not None and row[1] != ""]
            return return_rows
        return []


    def try_lemmatization_methods(self, branch, original_word, block = True):
        plain_word = self.get_plain_word(branch)
        
        is_verb = any(morph[1][0] == "V" for morph in branch if len(morph) > 1 and len(morph[1]) > 0)

        if plain_word == "":
            return []

        #print("plain word " + plain_word)

        # first look up the given word in dictionary
        translations = self.get_trans_fetch(plain_word, original_word)
        if translations:
            return translations

        # then try lemmatizing with soylemma (returns multiple), see if in dic
        lemmatized_words = self.lemmatizer.lemmatize(plain_word)
        if lemmatized_words:
            #grab just the words, removing classes
            lemmatized_words = set(lemmatized[0] for lemmatized in lemmatized_words if lemmatized)
            #print("Soylemma Lemmatization of " + str(plain_word))
            #print(lemmatized_words)
            for lemmatized_word in lemmatized_words:
                # check if mecab's input was classed as verb if we're adding da,
                # soylemma's classification somtimes wrongly ascribes as verb and adds da therefore
                # so, block lemmatization that added 다 in cases where mecab didn't call it a verb
                # but soylemma added 다 anyway to a word that didn't have it to begin with
                if block and (not is_verb) and lemmatized_word[-1] == "다" and plain_word[-1] != "다":
                    #print("blocked soylemma's addition of 다 for word "+plain_word+" "+lemmatized_word)
                    continue
                translations.extend(self.get_trans_fetch(lemmatized_word, original_word))
            if translations:
                #print("Found trans with soylemma:")
                #print(translations)
                return translations

        return []
        
    
    def list_unique(self, inlist):
        unique = []
        for item in inlist:
            if item not in unique:
                unique.append(item)
        return unique
    
        
    def get_translations(self, original_branch, nextbranch = None, nextnextbranch = None):
        original_branch = self.remove_lead_trail_symbols(original_branch)
        if len(original_branch) == 0:
            return []
        original_word = self.get_plain_word(original_branch)
        
        #try cutting off trailing particle morphs one by one 
        branch = original_branch
        cutbranch = branch
        while True:                
            translations = self.try_lemmatization_methods(cutbranch, original_word)
            if translations:
                #if len(cutbranch) < len(original_branch):
                    #print("Found with cutparticle***\n" + str(original_branch) + ": " + str(cutbranch) + ": " + str(translations))
                #else:
                    #print("Found with original*\n" + str(original_branch) + ": " + str(cutbranch) + ": " + str(translations))
                return translations
            cutbranch = self.remove_single_trailing_particle(branch)
            if len(cutbranch) < len(branch):
                branch = cutbranch
            else:
                break
        
        # at this point we should have either all trailing particles off or
        # if only started with all particles, a single particle chunk left

        translations = self.try_lemmatization_methods(branch, original_word)
        if translations:
            #print("Found**\n" + str(original_branch) + ": " + str(branch) + ": " + str(translations))
            return translations

        #this might be handy if there are particles in the middle that are exposed after cuts
        branch_wo_end_particles = self.remove_all_trailing_particles(branch)
        translations = self.try_lemmatization_methods(branch_wo_end_particles, original_word)
        if translations:
            #print("Found with branchwoendparticles*********\n" + str(original_branch) + ": " + str(branch_wo_end_particles) + ": " + str(translations))
            return translations
        
        main_chunks = self.get_main_chunks(branch_wo_end_particles, ['N', 'V', 'M'])
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['M']))
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['V']))
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['N']))
        main_chunks_unique = self.list_unique(main_chunks)
        main_chunks_NVM_largest_sorted = sorted(main_chunks_unique, key=self.get_plain_word_len)
        main_chunks_NVM_largest_sorted.reverse()
        
        if main_chunks_NVM_largest_sorted:
            for main_chunk in main_chunks_NVM_largest_sorted:
                #print("-"+str(main_chunk))
                
                chunktrans = self.try_lemmatization_methods(main_chunk, original_word)
                if chunktrans:
                    #print("Found with parsed chunks********************************\n" + str(original_branch) + ": " + str(main_chunk) + ": " + str(translations))
                    translations.extend(chunktrans)
                    continue
                
                #try adding da if it's a verb 
                if main_chunk and len(main_chunk[0]) > 1 and len(main_chunk[0][1]) > 0 and main_chunk[0][1][0] == 'V':
                    main_chunk_da = main_chunk
                    main_chunk_da.append(("다","EC"))
                    translations = self.try_lemmatization_methods(main_chunk_da, original_word)
                    if translations:
                        #print("Found with 다 addition*************************************\n" + str(original_branch) + ": " + str(main_chunk_da) + ": " + str(translations))
                        continue       

                #take a morph off
                if len(main_chunk) > 1:
                    shortchunk = main_chunk[0:-1]
                    translations = self.try_lemmatization_methods(shortchunk, original_word)
                if translations:
                    #print("Found with morph off end*****************************************\n" + str(original_branch) + ": " + str(shortchunk) + ": " + str(translations))
                    continue
                # take two off
                if len(main_chunk) > 2:
                    shortchunk = main_chunk[0:-2]
                    translations = self.try_lemmatization_methods(shortchunk, original_word)
                if translations:
                    #print("Found with 2 morph off end*****************************************\n" + str(original_branch) + ": " + str(shortchunk) + ": " + str(translations))
                    continue
                
                # take char off end of total chunk flattened
                if main_chunk and len(main_chunk[0]) > 1:
                    firstclass = main_chunk[0][1]
                    word = self.get_plain_word(main_chunk)
                    word = word[0:-1]
                    translations = self.try_lemmatization_methods([(word, firstclass)], original_word)
                    if translations:
                        #print("Found with char off end*****************************************\n" + str(original_branch) + ": " + str([(word, firstclass)]) + ": " + str(translations))
                        continue
        
        translations = self.list_unique(translations)
        
        if translations:
            return translations

        ##one last-ditch try at unblocking soylemma's addition of da on end of verbs
        ##that it disagrees with mecab on
        #translations = self.try_lemmatization_methods(branch, original_word, False)
        #if translations:
            #print("Found with ublocked soylemma*********************************************\n" + str(original_branch) + ": " + str(branch) + ": " + str(translations))
            #return translations
        #translations = self.try_lemmatization_methods(branch_wo_end_particles, original_word, False)
        #if translations:
            #print("Found with ublocked soylemma*********************************************\n" + str(original_branch) + ": " + str(branch_wo_end_particles) + ": " + str(translations))
            #return translations

        return []


    def get_main_chunks(self, branch, classes = ['M', 'N', 'I', 'V']):
        inside = False
        main_chunks = []
        main_chunk = []
        for i in range(0, len(branch)):
            morph = branch[i]
            if len(morph) > 1 and len(morph[1]) > 0 and morph[1][0] in classes:
                inside = True
                main_chunk.append(morph)
            else:
                if inside:
                    main_chunks.append(main_chunk)
                    main_chunk = []
                inside = False
        if inside:
            main_chunks.append(main_chunk)
        return main_chunks


    def get_plain_branch(self, branch):
        if branch == None:
            return None
        without_symbols = [x for x in branch if len(x) > 1 and len(x[1]) > 0 and x[1][0] != "S"]
        return without_symbols


    def remove_lead_trail_symbols(self, branch):
        out = branch
        while out and len(out[-1]) > 1 and out[-1][1][0] == 'S':
            out = out[0:-1]
        while out and len(out[0]) > 1 and out[0][1][0] == 'S':
            del out[0]
        return out


    def remove_all_trailing_particles(self, branch):
        out = branch
        while len(out) > 1 and len(out[-1]) > 1 and out[-1][1][0] in self.particle_classes:
            out = out[0:-1]
        return out


    def remove_single_trailing_particle(self, branch):
        if len(branch) > 1 and len(branch[-1]) > 1 and branch[-1][1][0] in self.particle_classes:
            return branch[0:-1]
        return branch


    def get_plain_word(self, branch):
        if branch == None: 
            return None
        without_symbols = [
                                (
                                    x[0] if len(x) > 1 and
                                    len(x[1]) > 0 and
                                    x[1][0] != "S"
                                    else ""
                                ) for x in branch
                            ]
        return "".join(without_symbols)
    
    
    def get_plain_word_len(self, branch):
        if branch == None:
            Exception("NoneType branch")
        return sum([
                                (
                                    len(x[0]) if len(x) > 1 and
                                    len(x[1]) > 0 and
                                    x[1][0] != "S"
                                    else 0
                                ) for x in branch
                            ])
                                
                                
    def end_of_sentence_punc(self, word):
        for morph in word:
            if len(morph) > 1 and len(morph[1]) > 0 and morph[1][0] == 'S' and ("." in morph[0] or "?" in morph[0] or "!" in morph[0]):
                return True
        return False

    def format_passage(self, passage):
        #print("call on: ")
        #print_tree(passage)
        #print(type(passage))
        if type(passage) is list:
            #then presumably we have a passage here, but check it's not empty or weird
            if passage:
                if type(passage[0]) is list:
                    # we have a list of lists, assume passage
                    self.xprint('<div class=wrapper>')
                    self.xprint('    <ol class=sentence>')
                    
                    lenpassage = len(passage)
                    
                    #use this to track where found end of sentence punctuations
                    laststartingpoint = 0
                    
                    for i in range(0, lenpassage):
                        # grab the word we're working on and also the following words 
                        # for various matching purposes
                        word = passage[i]
                        nextword = passage[i + 1] if i < lenpassage - 1 else None
                        nextnextword = passage[i + 2] if i < lenpassage - 1 - 1 else None
                        
                        # print the passage translation if we're at 
                        # end of a sentence or end of the passage
                        if i == lenpassage - 1 or (i > 0 and self.end_of_sentence_punc(word)):
                            trans_link_passage = passage[laststartingpoint:i + 1]
                            laststartingpoint = i + 1
                        else:
                            trans_link_passage = None
                        
                        self.format_word(word, nextword, nextnextword, trans_link_passage)

                    self.xprint('    </ol>')
                    self.xprint('</div>')
                else:
                    print("error, unexpected passage type" + str(type(passage)))
        elif type(passage) is str:
            self.xprint('<div class=wrapper>')
            
            if passage != "":
                self.xprint('    <ol class=sentence>')
                self.xprint('    <li>')
                self.xprint('      <ol class=comment>')
                self.xprint('        <li lang=en_MORPH style="color: var(--page-Noun);">')
                self.xprint(html.escape(passage))
                self.xprint('        </li>')
                self.xprint('      </ol>')
                self.xprint('    </li>')
                self.xprint('    </ol>')
            
            self.xprint('</div>')
        else:
            print("error, expected list or str, got something else")
    

    def format_word(self, branch, nextbranch = None, nextnextbranch = None, trans_link_passage = None):
        # example: branch = [('“', 'SSO'), ('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]
        non_symbol_branch = self.get_plain_branch(branch)
        plain_word = self.get_plain_word(branch)

        full_word = "".join([   (   "<span style='color: var(--page-" +
                                    self.get_sejongtagset_superclass(x[1]) + ");'>" +
                                    html.escape(x[0]) +
                                    "</span>"
                                ) for x in branch
                            ])
        full_word_length = sum(len(x[0]) for x in branch)

        transliteration = '<span style="color: var(--page-InterInfo)">' + html.escape(self.transliterator.translit(plain_word)) + "</span>"

        krdictlink = ('<a title="KRDict" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://krdict.korean.go.kr/eng/smallDic/searchResult?nation=eng&nationCode=6&ParaWordNo=&mainSearchWord=" 
                    + urllib.parse.quote(plain_word) 
                    + f'">{self.pointer_char}&nbsp;KRDict</a>')
        naverlink = ('&nbsp;&nbsp;<a title="Naver" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://en.dict.naver.com/#/search?query=" 
                    + urllib.parse.quote(plain_word) 
                    + f'">{self.pointer_char}&nbsp;Naver</a><br>')
        daumlink1 = ('<a title="Daum" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://small.dic.daum.net/search.do?q=" 
                    + urllib.parse.quote(plain_word) + "&dic=eng"
                    + f'">{self.pointer_char}&nbsp;Daum</a>')
        daumlink2 = ('&nbsp;&nbsp;<a title="Phrases" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://small.dic.daum.net/search.do?q=" 
                    + urllib.parse.quote(plain_word) + "&dic=ee"
                    + f'">{self.pointer_char}&nbsp;Phrases</a>')

        pos_info = "-".join([self.get_sejongtagset_abbrev(x[1]) for x in non_symbol_branch])
        
        pos_info_long = "\n".join([ (   "<span style='color: var(--page-" +
                                        self.get_sejongtagset_superclass(x[1]) + ");'>" +
                                        html.escape(x[0]) + " " +
                                        self.get_sejongtagset_name(x[1]) +
                                        "</span>"
                                    ) for x in non_symbol_branch ])
                
        grammarlink_matches = self.kogrammarlinks.search(branch, nextbranch)
        grammarlink_matches_html = ''
        if grammarlink_matches:
            grammarlink_matches_html = '<hr><p>'
            #pos_info = pos_info + "﹡"        
            for glkey, gldef, glsource, gllink in grammarlink_matches:
                if glsource == "KRDict search" or glsource == "KRDict" or glsource == "YUF":
                    grammarlink_matches_html = (grammarlink_matches_html
                                            + '<a class=diclink onclick="particlesearch(\'' + glkey.lstrip("-~") + '\'); return false;" href="#">' + html.escape(glkey + ' ' + gldef) + ' ' + self.pointer_char + '&nbsp;' + glsource + '</a><br>')
                else:
                    grammarlink_matches_html = (grammarlink_matches_html
                                                + '<a class=diclink target="_blank" rel="noopener noreferrer" href="' + gllink + '">' + html.escape(glkey + ' ' + gldef) + ' ' + self.pointer_char + '&nbsp;' + glsource + '</a><br>')
            grammarlink_matches_html = grammarlink_matches_html + '</p>'
        
        translations = self.get_translations(branch, nextbranch, nextnextbranch)
        if translations:
            translations_html = ('<hr><p>'
                                + html.escape(";\n".join(translations)) + '</p>')
        else:
            translations_html = ''
            
        phrase_translations = self.fetch_phrase_translations(plain_word, self.get_plain_word(nextbranch), self.get_plain_word(nextnextbranch))
        
        if phrase_translations:
            phrase_translations_html = ('<hr><p style="font-weight:bold;color: var(--page-Noun);">' + html.escape(";\n".join(phrase_translations)) + '</p>')
        else:
            phrase_translations_html = ''

        if trans_link_passage and trans_link_passage[0] and type(trans_link_passage[0][0]) is tuple:
            trans_link_passage_text_encoded = urllib.parse.quote(
                                " ".join(
                                    "".join(
                                            tup[0] for tup in twig
                                    )
                                    for twig in trans_link_passage
                                ) 
                            )
                                    
            trans_link_passage_html = f'<a class=diclink target="_blank" rel="noopener noreferrer" href="https://papago.naver.com/?sk=ko&tk=en&st={trans_link_passage_text_encoded}">{self.pointer_char}&nbsp;passage Papago</a><br><a class=diclink target="_blank" rel="noopener noreferrer" href="https://translate.google.com/?sl=ko&tl=en&text={trans_link_passage_text_encoded}&op=translate">{self.pointer_char}&nbsp;passage GTrans</a><hr>'
            
            full_word = full_word + '&nbsp;<span style="color: var(--page-Particle); font-weight: normal;">' + self.pointer_char + "</span>"

        else:
            trans_link_passage_html = ""


        total_lines_remain = 4
        
        self.wrapper.width = round(full_word_length*3.5) if full_word_length > 1 else 2*3
        
        if phrase_translations:
            tshort_t = ";\n".join(phrase_translations)
            self.wrapper.max_lines = 2
            phrase_translations_html_short = (
                      '<p style="font-weight:bold;color: var(--page-Noun)">'
                      + html.escape(self.wrapper.fill(tshort_t)).replace("\n", "<BR>")
                      + '</p>'
                      )
            total_lines_remain = total_lines_remain - self.wrapper.max_lines
        else:
            phrase_translations_html_short = ""
        
        if translations:
            self.wrapper.max_lines = total_lines_remain
            translations_html_short = html.escape(
                self.wrapper.fill("; ".join(translations))
                ).replace("\n", "<BR>") #.replace(": ", ":&nbsp;")
        else:
            translations_html_short = "—"
        
        description = (html.escape(pos_info) 
                    + "<p>" 
                    + translations_html_short
                    + phrase_translations_html_short
                    + "</p>")

        tooltip = ( trans_link_passage_html
                    + transliteration + '<hr>'
                    + krdictlink + naverlink + daumlink1 + daumlink2
                    + '<hr><p>' + pos_info_long + '</p>'
                    + translations_html
                    + phrase_translations_html
                    + grammarlink_matches_html
                    ).replace("\n", "<br>")

        self.xprint('    <li>')
        self.xprint(f'      <ol class=word onclick="showtooltip(event, \'tipnumber{self.tipnumber}\')">')
        self.xprint(f'        <li lang=es>{full_word}</li>')
        self.xprint(f'        <li lang=en_MORPH class=tooltip>{description}<span class=tooltiptext id="tipnumber{self.tipnumber}">{tooltip}</span></li><br>')
        self.xprint('      </ol>')
        self.xprint('    </li>')

        self.tipnumber = self.tipnumber + 1

        #sys.stdout.flush()


    def xprint(self, message):
        self.output.append(message)


    def generate(self):
        structured_content = []
        
        for j in range(len(self.content)):
            line = self.content[j]
            if line == "":
                structured_content.append(line)
            elif line[0] == "#":
                structured_content.append(line[1:])
            else:
                # see https://pypi.org/project/python-mecab-ko/
                structured_content.append(self.mecab.pos(line))

        self.tipnumber = 0
        
        for passage in structured_content:
            self.format_passage(passage)

        self.cur.close()
        self.con.close()
        
        return "\n".join(self.output)

