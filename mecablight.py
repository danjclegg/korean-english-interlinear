import os.path
import sejongtagset 
from MeCab import Tagger

# wrote this to have an easy access to mecab output

class MeCabLight:
    
    def __init__(self):
        self.tagger = Tagger('-d /usr/local/lib/mecab/dic/mecab-ko-dic')

    def parse_mecab_output(self, output):
        lines = output.splitlines()[:-1]
        branch = []
        for line in lines:
            morph, rest = line.split('\t', 1)
            sejongtag = rest.split(',', 1)[0]
            branch.append((morph, sejongtag))
        return branch

    def pos(self, passage):
        if not (type(passage) is str):
            Exception("Passage is not basestring!")
        words = passage.split()
        branches = [self.parse_mecab_output(self.tagger.parse(word)) for word in words]
        return branches

    

    
