from flask import (
    Flask, request, render_template, redirect, url_for, send_file
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
import os
import nmm
import pull_from_sheet
from googleapiclient.errors import HttpError


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session = sessionmaker(bind=db)
session = Session()
db = SQLAlchemy(app)
import models



@app.route('/', methods=('GET', "POST"))
def index():
    if request.method == 'POST':
        title = request.form['title']
        print("title:   " + title)
        error = None

        db = SQLAlchemy(app)
        sheet_id = db.engine.execute(
            'SELECT sheet_id'
            ' FROM formulas d'
            ' WHERE d.title = %s',
            (title)
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

    db = SQLAlchemy(app)
    formulas = db.engine.execute(
        'SELECT title, sheet_id'
        ' FROM formulas f'
    ).fetchall()
    print('FORMULA::::' + str(formulas))
    return render_template('recipe-list.html', formulas=formulas)

@app.route('/create', methods=('GET', "POST"))
def create():
    if request.method == 'POST':
        title = request.form['title']
        sheet_id = request.form['sheet_id']
        error = None

        if not title:
            error = 'Please enter product #'
        if error is not None:
            flash(error)
        else:
            db = SQLAlchemy(app)
            print("Creating:" + title + '|' + sheet_id)
            db.engine.execute(
                'INSERT INTO formulas (title, sheet_id)'
                ' VALUES (%s,%s)',
                (title, sheet_id)
            )
            session.flush
            return redirect(url_for('index'))
    return render_template('create.html')
