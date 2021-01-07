#stuff for adding defintions
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


/* for dark mode */
        /*--dark-Background: #16110e;
        --dark-WordCell: #040402;
        --dark-Border: #181512;
        --dark-Tooltip: #010000;
        
        --dark-Particle: #546263;
        --dark-Comment: #546263;
        
        --dark-InterInfo: #3e3b38;
        --dark-ForeignWord: #3e3b38;
        
        --dark-Adverb: #9c7b3b;
        
        --dark-Noun: #a8a190;
        --dark-Symbol: #a8a190;
        --dark-CardinalNumber: #a8a190;
        --dark-UNKNOWN: #a8a190;
        
        --dark-Pronoun: #427e70;
        
        --dark-Verb: #aa4538;
        --dark-Interjection: #aa4538;
        
        --dark-Determiner: #788d3a;*/
        
        /* for dark mode credit to groovebox: https://github.com/morhetz/gruvbox */
        /*--dark-Background: #1e1e1e;
        --dark-Tooltip: var(--dark-Background);
        
        --dark-WordCell: #282828;
        
        --dark-Border: #3c3836;
        
        --dark-Particle: #84a598;
        --dark-Comment: var(--dark-Particle);
        
        --dark-InterInfo: #928375;
        --dark-ForeignWord: var(--dark-InterInfo);
        
        --dark-Adverb: #f9bc41;
        
        --dark-Noun: #ebdab4;
        --dark-Symbol: var(--dark-Noun);
        --dark-CardinalNumber: var(--dark-Noun);
        --dark-UNKNOWN: var(--dark-Noun);
        
        --dark-Pronoun: #8fbf7f;
        
        --dark-Verb: #f84b3c;
        --dark-Interjection: var(--dark-Verb);
        
        --dark-Determiner: #b8ba37;
        */
