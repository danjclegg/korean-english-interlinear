# korean-english-interlinear
Korean-English Interlinear Generator Web-App in Python

Designed for learning Korean with any text you want, this program generates crude literal/direct/word-for-word English translations underneath Korean text (interlinear) and supplies extra contextual information in clickable pop-up boxes. The literal translation offers insights into the Korean language that full-sentence translation obscures. The generated pages are self-contained files ideal for saving for offline reading. As it uses simple dictionary look-ups, the translations are only possibilities.

It is written in Python, using Flask and GUnicorn to implement an Alpine Linux docker which I've deployed as a [Heroku app](https://koreaninterlinear.herokuapp.com/). I have included a simple Mecab-ko Python wrapper as well.

It has these dependencies for the core program:
- [Mecab-ko](http://eunjeon.blogspot.kr/)
- [Soylemma](https://github.com/lovit/korean_lemmatizer)
- [hangul-romanize](https://github.com/youknowone/hangul-romanize)
- Requires the [KEngDic dictionary](https://github.com/garfieldnate/kengdic) to be manually loaded into a [PostgreSQL](https://www.postgresql.org/) database (see shell script)

Credit for the interlinear css to [Pat on Stack Exchange](https://linguistics.stackexchange.com/questions/3/how-do-i-format-an-interlinear-gloss-for-html), and for inspiration for the colour scheme to [Solarized 8](https://github.com/lifepillar/vim-solarized8). Inspiration for the project came from [BibleHub's Greek-English interlinear](https://biblehub.com/interlinear/john/1-1.htm) site which has been a big help to me. Thanks also to [Dr. Ross King](https://asia.ubc.ca/profile/ross-king/) for his [Korean Grammar Dictionary](http://koreangrammaticalforms.com/) which I link to, and also [8-Day Korean](https://www.90daykorean.com/korean-particles/) for their page on definitions of Korean particles.
