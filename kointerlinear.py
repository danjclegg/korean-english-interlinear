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

        self.kogrammarlinks = kogrammarlinks.KoGrammarLinks()

        self.missing_words = []

        self.particle_classes = ['E', 'J', 'S', 'X']

        ######################
        # connect to database and check tables are there

        self.cur = self.con.cursor()

        # sql code to create another table like the main one, this taken from KEngDic:
        create_added_table = """CREATE TABLE korean_english_added (
            id SERIAL PRIMARY KEY,
            wordid integer,
            word character varying(130),
            syn character varying(190),
            def text,
            posn integer,
            pos character varying(13),
            submitter character varying(25),
            doe timestamp without time zone,
            wordsize smallint,
            hanja character varying,
            wordid2 integer,
            extradata character varying
        );"""

        self.cur.execute("select * from information_schema.tables where table_name=%s", ('korean_english',))
        if not bool(self.cur.rowcount):
            Exception("Error, database dictionary table missing or not set up.")
            

        self.cur.execute("select * from information_schema.tables where table_name=%s", ('korean_english_added',))
        if not bool(self.cur.rowcount):
            self.cur.execute(create_added_table)
            self.cur.close()
            self.con.commit()
            self.cur = self.con.cursor()
            self.cur.execute("select * from information_schema.tables where table_name=%s", ('korean_english_added',))
            if not bool(self.cur.rowcount):
                Exception("Error, database added dictionary table missing or not set up.")

    ######################
    # Function defs
    
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


    def get_sejongtagset_colour(self, tag):
        sejong_superclass = self.get_sejongtagset_superclass(tag)
        if sejong_superclass == "":
            return ""
        return sejongtagset.SuperClass_Colours[sejong_superclass]

        
    #note, not checked for input safety
    #def print_tree(self, tree, prepend = ""):
        ##print(prepend + "print tree call on: " + str(tree))
        #if type(tree) is str:
                #print(prepend + "\"" + tree + "\"")
        #elif type(tree) is list:
            #print(prepend + "[")
            #for branch in tree:
                #self.print_tree(branch, prepend + "\t")
            #print(prepend + "]")
        #elif type(tree) == tuple:
            #print(prepend + "(" + ", ".join(tree) + ")")
        #else:
            #print(prepend + "error, unexpected branch type" + str(type(tree)))


    def get_trans_fetch(self, word, original_word):
        self.cur.execute("SELECT word, def AS trans FROM korean_english WHERE word = %s;", (word,))
        rows = self.cur.fetchall()

        if type(rows) is list and rows:
            
            #uncomment to reimplement missing word addition later maybe
            #oword_blank_defs = sum( 1 for row in rows if row[0] == original_word and (row[1] == "" or row[1] == None) )
            #oword_non_blank_defs = sum( 1 for row in rows if row[0] == original_word and (row[1] != "" and row[1] != None) )
            #if oword_non_blank_defs == 0 and oword_blank_defs > 0:
                ## then we didn't find any non-blank defs and we did find a blank def
                #if original_word not in self.missing_words:
                    #print("Note, blank dictionary definition for word: " + original_word)
                    #self.missing_words.append(original_word)

            return_rows = [
                (
                    row[1] if word == original_word else
                    " ".join([row[0], row[1]])
                )
                for row in rows if row is not None and row[1] != None and row[1] != ""
                ]
            return return_rows
        return []


    def fetch_phrase_translations(self, wordstr, nextwordstr = None, nextnextwordstr = None):
        if wordstr is not None and wordstr != "":
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
        
        ##maybe remove this as might preclude matching more stuff below? or make this plural
        #main_chunks = self.get_main_chunks(branch_wo_end_particles, ['N', 'V'])
        #for main_chunk in main_chunks:
            #translations = self.try_lemmatization_methods(main_chunk, original_word)
            #if translations:
                ##print("Found with NV merged**************************\n" + str(original_branch) + ": " + str(main_chunk) + ": " + str(translations))
                #return translations
        
        #main_chunks_M = sorted(self.get_main_chunks(branch_wo_end_particles, ['M']), key = self.get_plain_word_len)
        #main_chunks_V = sorted(self.get_main_chunks(branch_wo_end_particles, ['V']), key = self.get_plain_word_len)
        #main_chunks_N = sorted(self.get_main_chunks(branch_wo_end_particles, ['N']), key = self.get_plain_word_len)
        #main_chunks_merged = sorted(self.get_main_chunks(branch_wo_end_particles, ['N', 'V', 'M']), key = self.get_plain_word_len)
        #main_chunks_NVM = main_chunks_M
        #main_chunks_NVM.extend(main_chunks_V)
        #main_chunks_NVM.extend(main_chunks_N)
        #main_chunks_NVM.extend(main_chunks_merged)
        ##print(main_chunks_NVM)
        ##print(set(main_chunks_NVM))
        ##main_chunks_NVM = list(set(main_chunks_NVM)) #get unique
        #main_chunks_NVM_largest_sorted = sorted(main_chunks_NVM, key=self.get_plain_word_len)
        #main_chunks_NVM_largest_sorted.reverse() #put back into N, V,... order
        
        main_chunks = self.get_main_chunks(branch_wo_end_particles, ['N', 'V', 'M'])
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['M']))
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['V']))
        main_chunks.extend(self.get_main_chunks(branch_wo_end_particles, ['N']))
        main_chunks_unique = []
        for main_chunk in main_chunks:
            if main_chunk not in main_chunks_unique:
                main_chunks_unique.append(main_chunk)
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
                    for i in range(0, lenpassage):
                        # grab the word we're working on and also the following words 
                        # for various matching purposes
                        word = passage[i]
                        nextword = passage[i + 1] if i < lenpassage - 1 else None
                        nextnextword = passage[i + 2] if i < lenpassage - 1 - 1 else None
                        
                        self.format_word(word, nextword, nextnextword)
                    
                    # check if this was a list of lists of tuples (a sentence)
                    # and add sentence translate link if so
                    if type(passage[0][0]) is tuple:
                        link = "https://papago.naver.com/?sk=ko&tk=en&st=" + urllib.parse.quote(
                                    " ".join(
                                        "".join(tup[0] for tup in twig)
                                        for twig in passage)
                                    )
                        self.xprint('    <li>')
                        self.xprint('      <ol class=comment>')
                        self.xprint(f'        <li lang=es><a title="Papago line translation" class=translink target="_blank" rel="noopener noreferrer" href="{link}">{self.pointer_char}</a></li>')
                        self.xprint('      </ol>')
                        self.xprint('    </li>')

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
                self.xprint('        <li lang=en_MORPH style="color:' + sejongtagset.SuperClass_Colours["Comment"] + ';">')
                self.xprint(html.escape(passage))
                self.xprint('        </li>')
                self.xprint('      </ol>')
                self.xprint('    </li>')
                self.xprint('    </ol>')
            
            self.xprint('</div>')
        else:
            print("error, expected list or str, got something else")
    

    def format_word(self, branch, nextbranch = None, nextnextbranch = None):
        # example: branch = [('“', 'SSO'), ('톱질', 'NNG'), ('하', 'XSV'), ('세', 'EC')]
        non_symbol_branch = self.get_plain_branch(branch)
        plain_word = self.get_plain_word(branch)
        
        #fix this:
        if plain_word == "":
            if sum([1 for x in non_symbol_branch]) > 0:
                print("Warning, plain word is empty, printing branch: ")
                print(branch)





        full_word = "".join([   (   "<span style='color:" +
                                    self.get_sejongtagset_colour(x[1]) + ";'>" +
                                    html.escape(x[0]) +
                                    "</span>"
                                ) for x in branch
                            ])
        full_word_length = sum(len(x[0]) for x in branch)

        naverlink = ('<p><a title="Naver" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://en.dict.naver.com/#/search?query=" 
                    + urllib.parse.quote(plain_word) 
                    + f'">Naver{self.pointer_char}</a></p>')
        daumlink1 = ('<p><a title="Daum" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://small.dic.daum.net/search.do?q=" 
                    + urllib.parse.quote(plain_word) + "&dic=eng"
                    + f'">Daum{self.pointer_char}</a>')
        daumlink2 = ('<a title="Phrases" class=diclink target="_blank" '
                    + 'rel="noopener noreferrer" href="' 
                    + "https://small.dic.daum.net/search.do?q=" 
                    + urllib.parse.quote(plain_word) + "&dic=ee"
                    + f'"> Phrases{self.pointer_char}</a></p>')

        pos_info = "-".join([self.get_sejongtagset_abbrev(x[1]) for x in non_symbol_branch])
        
        pos_info_long = "\n".join([ (   "<span style='color:" +
                                        self.get_sejongtagset_colour(x[1]) + ";'>" +
                                        html.escape(x[0]) + " " +
                                        self.get_sejongtagset_name(x[1]) +
                                        "</span>"
                                    ) for x in non_symbol_branch ])
        
        
        hr = '<hr style="width:80%;text-align:left;margin-left:0;height:1px;border-width:0;color:#eee;background-color:#eee">'
        grammarlink_matches = self.kogrammarlinks.search(branch, nextbranch)
        grammarlink_matches_html = ''
        if grammarlink_matches:
            grammarlink_matches_html = hr + '<p style="margin-top: .5em;">'
            pos_info = pos_info + "﹡"        
            for grammarlink_match in grammarlink_matches:
                gtext = html.escape(grammarlink_match[0])
                glink = grammarlink_match[1]
                grammarlink_matches_html = (grammarlink_matches_html
                                            + '<p><a title="Koreangrammaticalforms.com" class=diclink target="_blank"' 
                                            + f'rel="noopener noreferrer" href="{glink}">{gtext} {self.pointer_char}</a></p>')
            grammarlink_matches_html = grammarlink_matches_html + '</p>'
        
        translations = self.get_translations(branch, nextbranch, nextnextbranch)
        if translations:
            translations_html = (hr + '<p style="margin-top: .5em;">'
                                + html.escape(";\n".join(translations)) + '</p>')
        else:
            translations_html = ''
            
        phrase_translations = self.fetch_phrase_translations(plain_word, self.get_plain_word(nextbranch), self.get_plain_word(nextnextbranch))
        
        if phrase_translations:
            phrase_translations_html = (hr + '<p style="margin-top: .5em;font-weight:bold;color:' + sejongtagset.SuperClass_Colours['Noun'] + '">' + html.escape(";\n".join(phrase_translations)) + '</p>')
        else:
            phrase_translations_html = ''

        total_lines_remain = 4
        
        self.wrapper.width = round(full_word_length*3.5) if full_word_length > 1 else 2*3
        
        if phrase_translations:
            tshort_t = ";\n".join(phrase_translations)
            self.wrapper.max_lines = 2
            phrase_translations_html_short = (
                      '<p style="margin-top: .5em;font-weight:bold;color:' + sejongtagset.SuperClass_Colours['Noun'] + '">'
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
            translations_html_short = "---"

        description = ("<p>" + html.escape(pos_info) 
                    + "</p><p style=\"margin-top: .5em;\">" 
                    + translations_html_short
                    + phrase_translations_html_short
                    + "</p>")

        tooltip = ( naverlink + daumlink1 + daumlink2
                    + hr + '<p style="margin-top: .5em;">'
                    + f'{pos_info_long}</p>'
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
        # to catch warnings to deal with
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

