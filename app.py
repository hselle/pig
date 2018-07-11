from flask import (
    Flask, request, render_template, redirect, url_for, send_file
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine
import os
import requests
import operator
import re
import nmm
import pull_from_sheet
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
# Session = sessionmaker(bind=db)
# session = Session()
from models import Result

@app.route('/', methods=('GET', "POST"))
def index():
    if request.method == 'POST':
        title = request.form['title']
        print("title:   " + title)
        error = None

        sheet_id = db.session.execute(
            'SELECT sheet_id'
            ' FROM formulas d'
            ' WHERE d.title =:param',
            {"param":title}
        ).fetchone()
        _sheet_id = sheet_id["sheet_id"]
        print(_sheet_id)
        if _sheet_id is None:
            abort(404, "formula {0} doesn't exist.".format(id))

        try:
            nmm.make(_sheet_id)
            return send_file("static/Nutrition_Label_Output.docx", attachment_filename="Nutrition_Label.docx")
        except HttpError:
            abort(404, "sheet id is invalid".format(id))
    formulas = db.session.execute(
        'SELECT title, sheet_id'
        ' FROM formulas f'
    ).fetchall()
    return render_template('recipe-list.html', formulas=formulas)

@app.route('/create', methods=('GET', "POST"))
def create():
    if request.method == 'POST':
        r_title = request.form['title']
        r_sheet_id = request.form['sheet_id']
        error = None

        if not r_title:
            error = 'Please enter product #'
        if error is not None:
            flash(error)
        else:
            try:
                print("Creating:" + r_title + '|' + r_sheet_id)
                result = Result(
                    title=r_title,
                    sheet_id=r_sheet_id
                )
                db.session.add(result)
                db.session.commit()
                return redirect(url_for('index'))
            except:
                print('fcuck')
    return render_template('create.html')
if __name__ == '__main__':
    app.run()
