###############
# mecab-ko used by konlpy seems to be using Sejong tagset as seen:
# http://semanticweb.kaist.ac.kr/nlp2rdf/resource/sejong.owl
# summary table here: https://www.aclweb.org/anthology/W12-5201.pdf
# doesn't look like Penn Korean Treebank:
# ftp://ftp.cis.upenn.edu/pub/ircs/tr/01-09/01-09.pdf
# , http://www.sfu.ca/~chunghye/papers/paclic-tb-paper2.pdf
# ,https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
# following I derrived from .owl file from kiast above with additional
# superclasses from summary table noted above (slightly abbreviated),
# and my made up abbreviations in third entries:
#   'CODE': ('SejongCodeDef',   'Superclass',   'Abbrev'),
SejongTagset = {
    'EC':   ('VerbalEnding',    'Particle',     'VEn'),
    'EF':   ('VerbalEnding',    'Particle',     'VEn'),
    'EP':   ('VerbalEnding',    'Particle',     'VEn'),
    'ETM':  ('VerbalEnding',    'Particle',     'VEn'),
    'ETN':  ('VerbalEnding',    'Particle',     'VEn'),
    'IC':   ('Interjection',    'Interjection', 'Int'),
    'JC':   ('AuxPostposition', 'Particle',     'Pos'),
    'JKB':  ('CaseMarker',      'Particle',     'Cas'),
    'JKC':  ('CaseMarker',      'Particle',     'Cas'),
    'JKG':  ('CaseMarker',      'Particle',     'Cas'),
    'JKO':  ('CaseMarker',      'Particle',     'Cas'),
    'JKQ':  ('CaseMarker',      'Particle',     'Cas'),
    'JKS':  ('CaseMarker',      'Particle',     'Cas'),
    'JKV':  ('CaseMarker',      'Particle',     'Cas'),
    'JX':   ('AuxPostposition', 'Particle',     'Pos'),
    'MAG':  ('GeneralAdverb',   'Adverb',       'Ad'),
    'MAJ':  ('Conjunct.Adverb', 'Adverb',       'CAd'),
    'MM':   ('Determiner',      'Determiner',   'Det'),
    'NA':   ('LikelyNoun',      'Noun',         'Nn?'),
    'NF':   ('LikelyNoun',      'Noun',         'Nn?'),
    'NNB':  ('CommonNoun',      'Noun',         'Nn'),
    'NNG':  ('CommonNoun',      'Noun',         'Nn'),
    'NNP':  ('ProperNoun',      'Noun',         'Nn'),
    'NP':   ('Pronoun',         'Pronoun',      'PrN'),
    'NV':   ('Verb',            'Verb',         'Ver'),
    'SE':   ('Symbol',          'Symbol',       'Sym'),
    'SF':   ('Symbol',          'Symbol',       'Sym'),
    'SH':   ('ForeignWord',     'ForeignWord',  'For'),
    'SL':   ('ForeignWord',     'ForeignWord',  'For'),
    'SN':   ('CardinalNumber',  'CardinalNumber', '#'),
    'SO':   ('Symbol',          'Symbol',       'Sym'),
    'SP':   ('Symbol',          'Symbol',       'Sym'),
    'SS':   ('Symbol',          'Symbol',       'Sym'),
    'VA':   ('Adjective',       'Verb',         'VAd'),
    'VC':   ('Copula',          'Verb',         'Cop'),
    'VCN':  ('Copula',          'Verb',         'Cop'),
    'VCP':  ('Copula',          'Verb',         'Cop'),
    'VV':   ('VerbalPredicate', 'Verb',         'VPr'),
    'VX':   ('AuxPredicate',    'Verb',         'Pr'),
    'XN':   ('CardinalNumber',  'CardinalNumber', '#'),
    'XPN':  ('Prefix',          'Particle',     'Pfx'),
    'XR':   ('Radical',         'Particle',     'Rad'),
    'XSA':  ('Suffix',          'Particle',     'Sfx'),
    'XSN':  ('Suffix',          'Particle',     'Sfx'),
    'XSV':  ('Suffix',          'Particle',     'Sfx'),
    
    # just added following weird ones I ran into
    # https://lucene.apache.org/core/7_4_0/analyzers-nori/org/apache/lucene/analysis/ko/POS.Tag.html
    'SC':   ('Separator',       'Symbol',       '-'),
    'SSO':  ('OpeningBracket',  'Symbol',       '['),
    'SSC':  ('ClosingBracket',  'Symbol',       ']'),
    'SY':   ('OtherSymbol',     'Symbol',       'Sym'),
    'NR':   ('Numeral',         'Symbol',       '#'),
    'NNBC': ('DependantNoun',   'Noun',         'Nn'),
    'UNKNOWN': ('UNKNOWN',      'UNKNOWN',      '???')
}

# https://praacticalaac.org/praactical/how-we-do-it-using-language-boards-to-support-aac-use-by-nerissa-hall-and-hillary-jellison/
# https://alltogether.wordpress.com/2007/09/17/goossens-crain-elder-communication-overlay-color-reminder/
# https://vimawesome.com/plugin/solarized-8

# Full-strength:
#SuperClass_Colours = {
    #'Background':   '#fdf6e4',
    #'Adverb':       '#b78a00',
    #'Noun':         'hsl(0, 0%, 20%)',
    #'Pronoun':      '#25a399',
    #'Verb':         '#cc4a0e',
    #'CardinalNumber': 'hsl(0, 0%, 20%)',
    #'Determiner':   '#729f01',
    #'ForeignWord':  'hsl(0, 0%, 70%)',
    #'Interjection': '#cc4a0e',
    #'Symbol':       'hsl(0, 0, 20%)',
    #'Particle':     '#657b85',
    #'UNKNOWN':      'hsl(0, 0, 20%)'
#}

# Muted:
SuperClass_Colours = {
    'Background':   '#f0eada',
    'WordCell':     '#f8f6f2',
    'Tooltip':      '#fbf9f5',
    'Adverb':       '#a88c41',
    'Noun':         '#43423f',
    'Pronoun':      '#5ba195',
    'Verb':         '#b75f37',
    'CardinalNumber': '#43423f',
    'Determiner':   '#8da44d',
    'ForeignWord':  'hsl(0, 0%, 70%)',
    'Interjection': '#b75f37',
    'Symbol':       '#2b2a28',
    'Particle':     '#7c888b',
    'Comment':      '#7c888b',
    'UNKNOWN':      '#43423f'
}
