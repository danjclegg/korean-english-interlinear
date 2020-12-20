#!/bin/bash

createdb kengdic

psql -d kengdic <<EOF
CREATE TABLE korean_english (
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
);

\COPY korean_english(wordid, word, syn, def, posn, pos, submitter, doe, wordsize, hanja, wordid2, extradata) FROM 'kengdic/kengdic_2011.tsv' NULL 'NULL';

CREATE TABLE korean_english_phrase2word (
    id SERIAL PRIMARY KEY,
    word1 character varying(130),
    word2 character varying(130),
    phrase character varying(130),
    def text
);

CREATE TABLE korean_english_phrase3word (
    id SERIAL PRIMARY KEY,
    word1 character varying(130),
    word2 character varying(130),
    word3 character varying(130),
    phrase character varying(130),
    def text
);

INSERT INTO korean_english_phrase2word (word1, word2, phrase, def) SELECT split_part(word, ' ', 1) AS word1, split_part(word, ' ', 2) AS word2, word AS phrase, def FROM korean_english WHERE word ~ '^\s*\w+\s+\w+\s*$';

INSERT INTO korean_english_phrase3word (word1, word2, word3, phrase, def) SELECT split_part(word, ' ', 1) AS word1, split_part(word, ' ', 2) AS word2, split_part(word, ' ', 3) AS word3, word AS phrase, def FROM korean_english WHERE word ~ '^\s*\w+\s+\w+\s+\w+\s*$';

delete from korean_english where word ~ '\w\s+\w';

SELECT COUNT(*) FROM korean_english;

CREATE INDEX korean_english_wordkey ON korean_english(word);

create index korean_english_phrase2wordkey on korean_english_phrase2word(word1, word2);
create index korean_english_phrases3wordkey on korean_english_phrase3word(word1, word2, word3);

\di

EOF

echo "
Direct push to heroku database from local database:
Find db with:
heroku pg -a koreaninterlinear
then:
heroku pg:reset XXXDATABASENAME --app koreaninterlinear
heroku pg:push kengdic XXXDATABSENAME --app koreaninterlinear
check out with:
heroku pg:psql -a koreaninterlinear
Maybe do:
REINDEX TABLE korean_english;
REINDEX TABLE korean_english_phrase2word;
REINDEX TABLE korean_english_phrase3word;

"
