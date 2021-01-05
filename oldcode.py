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
