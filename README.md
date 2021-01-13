# korean-english-interlinear
Korean-English Interlinear Generator Web-App in Python

This app is currently [deployed on Heroku](https://koreaninterlinear.herokuapp.com/).

Designed for learning Korean with any text you want, this program generates crude literal/direct/word-for-word English translations underneath Korean text (interlinear) and supplies extra contextual information in clickable pop-up boxes. The literal translation offers insights into the Korean language that full-sentence translation obscures. The generated pages are self-contained files ideal for saving for offline reading. As it uses simple dictionary look-ups, the translations are only possibilities.

It is written in Python, using Flask and GUnicorn on an Alpine Linux docker which I've deployed as a [Heroku app](https://koreaninterlinear.herokuapp.com/). I have also written a simple Mecab-ko Python wrapper which may be of use others.

The core program has these dependencies:
- [Mecab-ko](http://eunjeon.blogspot.kr/)
- [Soylemma](https://github.com/lovit/korean_lemmatizer)
- [hangul-romanize](https://github.com/youknowone/hangul-romanize)
- Requires the [KEngDic dictionary](https://github.com/garfieldnate/kengdic) to be manually loaded into a [PostgreSQL](https://www.postgresql.org/) database (see shell script)

Credit for the interlinear css to [Pat on Stack Exchange](https://linguistics.stackexchange.com/questions/3/how-do-i-format-an-interlinear-gloss-for-html), and for inspiration for the colour scheme to [Solarized 8](https://github.com/lifepillar/vim-solarized8). Inspiration for the project came from [BibleHub's Greek-English interlinear](https://biblehub.com/interlinear/john/1-1.htm) site which has been a big help to me. 

Thanks also to the various other dictionaries and grammar sites I link to, including:
- Yufina88's [Korean particle summaries](https://www.reddit.com/r/Korean/comments/84ni3g/korean_particle_frequency_list/)
- [Dr. Ross King](https://asia.ubc.ca/profile/ross-king/)'s [Korean Grammar Dictionary](http://koreangrammaticalforms.com/)
- [8-Day Korean](https://www.90daykorean.com/korean-particles/)'s definitions of Korean particles
- National Institute of Korean Language's [Korean-English Learners' Dictionary](https://krdict.korean.go.kr/eng/mainAction?nation=eng)
