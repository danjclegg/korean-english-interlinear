import os
from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)
from markupsafe import escape
import psycopg2

from kointerlinear import KoInterlinear
import sejongtagset

DATABASE_URL = os.environ.get('DATABASE_URL')

##if __name__ == '__main__':
#import os.path
#script_dir = os.path.dirname(os.path.realpath(__file__))
#from werkzeug.middleware.profiler import ProfilerMiddleware
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[10], profile_dir=script_dir + '/.profile')
##app.run(debug=True)


def run_generator(entry):
    if DATABASE_URL == "postgresql://localhost/kenddic":
        con = psycopg2.connect(database="kengdic", user='', password='', host="localhost")
    else:
        con = psycopg2.connect(DATABASE_URL, sslmode='require')

    generator = KoInterlinear(entry, con)
    body = generator.generate()

    con.close()

    return body

@app.route('/generate',methods = ['POST', 'GET'])
def login():
    if request.method != 'POST':
        return redirect(url_for('entry'))
    
    entrylong = request.form['entry']
    entry = (entrylong[:5200] + '...max length exceeded') if len(entrylong) > 5200 else entrylong    
    
    body = run_generator(entry)

    if request.form['mode'] != "dark":
        mode = "light"
    else:
        mode = "dark"
    
    return render_template("generate.html", body = body, mode = mode)

@app.route('/', methods=['GET'])
def entry():
    #prime the dyno
    run_generator("저")
    
    return render_template("entry.html", mode = "light")


