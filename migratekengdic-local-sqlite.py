import sqlite3
from sqlite3 import Error
import re

# This file used to set up initial database with sqlite3 from KEngDic package
# First use sqlite3 console app to run the commented commands below. 
# Then run this python program to switch data to table with index, copy phrases into other tables,
# and split phrases into words.
# Then it's set up and can run main program.

# Run these inside utility "$>sqlite3 kengdic.db":
"""
CREATE TABLE IF NOT EXISTS korean_english_import (
            /*id INTEGER PRIMARY KEY AUTOINCREMENT,*/
            wordid integer,
            word character varying(130),
            syn character varying(190),
            def text,
            posn integer,
            pos character varying(13),
            submitter character varying(25),
            doe TEXT,
            wordsize smallint,
            hanja character varying,
            wordid2 integer,
            extradata character varying
);
CREATE TABLE IF NOT EXISTS korean_english (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wordid integer,
            word character varying(130),
            syn character varying(190),
            def text,
            posn integer,
            pos character varying(13),
            submitter character varying(25),
            doe TEXT,
            wordsize smallint,
            hanja character varying,
            wordid2 integer,
            extradata character varying
);

CREATE TABLE korean_english_phrase2word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word1 character varying(130),
    word2 character varying(130),
    phrase character varying(130),
    def text
);

CREATE TABLE korean_english_phrase3word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word1 character varying(130),
    word2 character varying(130),
    word3 character varying(130),
    phrase character varying(130),
    def text
);

/* following two lines must be entered one by one */
.mode tabs
.import 'kengdic/kengdic_2011.tsv' korean_english_import

INSERT INTO korean_english SELECT NULL, wordid, word, syn, def, posn, pos, submitter, doe, wordsize, hanja, wordid2, extradata FROM korean_english_import;

DROP TABLE korean_english_import;

/*SELECT name FROM sqlite_schema ORDER BY name;*/

/*.quit*/

"""                        

database = r"kengdic.db"

# from https://stackoverflow.com/questions/5071601/how-do-i-use-regex-in-a-sqlite-query/18484596#18484596
def match(expr, item):
    return re.match(expr, item) is not None

# from https://www.sqlitetutorial.net/sqlite-python/creating-database/
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        #print(sqlite3.version)
        print("connected to db.")
        return conn
    except Error as e:
        print(e)
        return None

if __name__ == '__main__':

    #########################################
    # Set up database
        
    conn = create_connection(database)
    conn.create_function("MATCHES", 2, match)
    cur = conn.cursor()
    
    #########################################
    # First clean up inappropriate content found in this public database
    
    cur.execute("DELETE FROM korean_english WHERE MATCHES('.*(fuck|cunt|slut|whore|bitch|n\wg\w\wr|N\wg\w\wr).*', def);")
    
    cur.execute("DELETE FROM korean_english WHERE MATCHES('.*(정신박약아|정신박약자|지진아).*', word);")
    
    conn.commit()

    
    #########################################
    # Populate the 2 word phrase table

    cur.execute("INSERT INTO korean_english_phrase2word SELECT id AS id, NULL AS word1, NULL AS word2, TRIM(word) AS phrase, def AS def FROM korean_english WHERE MATCHES('^\s*\w+\s+\w+\s*$', word);")

    conn.commit()

    cur.execute("SELECT id, phrase FROM korean_english_phrase2word;")
    rows = cur.fetchall()
            
    for row in rows:
        print(row)
        rowid = row[0]
        phrase = row[1]
        splitphrase = phrase.split()
        updatequery = f"UPDATE korean_english_phrase2word SET word1 = \"{splitphrase[0]}\", word2 = \"{splitphrase[1]}\" WHERE id == \"{rowid}\";"
        #print(updatequery)
        cur.execute(updatequery)
        cur.execute(f"DELETE FROM korean_english WHERE id == \"{rowid}\" LIMIT 1;")
       
    conn.commit()


    #########################################
    # Populate the 3 word phrase table

    cur.execute("INSERT INTO korean_english_phrase3word SELECT id AS id, NULL AS word1, NULL AS word2, NULL AS word3, TRIM(word) AS phrase, def AS def FROM korean_english WHERE MATCHES('^\s*\w+\s+\w+\s+\w+\s*$', word);")

    print("inserted into korean_english_phrase3word")
    
    conn.commit()
   
    cur.execute("SELECT id, phrase FROM korean_english_phrase3word;")
    
    for row in cur.fetchall():
        print(row)
        rowid = row[0]
        phrase = row[1]
        splitphrase = phrase.split()
        updatequery = f"UPDATE korean_english_phrase3word SET word1 = \"{splitphrase[0]}\", word2 = \"{splitphrase[1]}\", word3 = \"{splitphrase[2]}\" WHERE id == \"{rowid}\";"
        #print(updatequery)
        cur.execute(updatequery)
        cur.execute(f"DELETE FROM korean_english WHERE id == \"{rowid}\" LIMIT 1;")
       
    conn.commit()

    #########################################
    # Create indices

    cur.execute("CREATE INDEX korean_english_wordkey ON korean_english(word);")
    cur.execute("CREATE INDEX korean_english_phrase2wordkey ON korean_english_phrase2word(word1, word2);")
    cur.execute("CREATE INDEX korean_english_phrases3wordkey ON korean_english_phrase3word(word1, word2, word3);")

    conn.commit()


    cur.close()
    conn.close()

    

    # .. . . continue porting from migratekengdic-local.sh

