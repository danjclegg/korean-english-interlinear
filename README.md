# korean-english-interlinear
Korean-English Interlinear Generator Web-App in Python

This program generates crude literal/word-for-word translations with the two languages stacked together with tappable/popup information boxes. It is designed for learning vocabulary and grammar with any text you choose. The generated pages are self-contained single html files ideal for downloading/saving for offline reading. As it is automatic, by simple dictionary look-ups, the translation and grammar aids are only possibilities. This roughness prevents focusing on the English and the literal translation offers unique insights into the Korean. 

It is written in Python, using Flask and GUnicorn to implement a Alpine Linux docker which I've [deployed on Heroku](https://koreaninterlinear.herokuapp.com/). I have included a simple Mecab-ko wrapper as well.

It relies on these has these dependencies:
- [Mecab-ko](http://eunjeon.blogspot.kr/),
- [Soylemma](https://github.com/lovit/korean_lemmatizer), and
- Requires the [KEngDic dictionary](https://github.com/garfieldnate/kengdic) to be manually loaded into a [PostgreSQL](https://www.postgresql.org/) database (script attached).

Credit for the interlinear css to [Pat on Stack Exchange](https://linguistics.stackexchange.com/questions/3/how-do-i-format-an-interlinear-gloss-for-html), and for inspiration for the colour scheme to [Solarized 8](https://github.com/lifepillar/vim-solarized8).
