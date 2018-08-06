from flask import (
    Flask, request, render_template, redirect, url_for, send_file, flash, Markup
)
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine
import os
import helper
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
from models import Result

@app.route('/', methods=('GET', "POST"))
def index():
    return render_template('home.html')

@app.route('/formulas')
def formulas():

    formulas = db.session.execute(
        'SELECT title, sheet_id'
        ' FROM formulas f'
    ).fetchall()
    formula_tabs = list()
    for formula in formulas:
        sheet_id = formula[1]
        tabs = pull_from_sheet.get_tabs(sheet_id)
        formula_tabs.append((formula, tabs))

    print("Tabs:   " + str(formula_tabs))

    return render_template('formulas.html', formulas=formula_tabs)

@app.route('/formulas/download')
def download():
    title = request.args.get('title')
    tab_name = request.args.get('tab')
    error = None
    print(title, tab_name)

    sheet_id = db.session.execute(
        'SELECT sheet_id'
        ' FROM formulas d'
        ' WHERE d.title =:param',
        {"param":title}
    ).fetchone()

    _sheet_id = sheet_id["sheet_id"]

    if _sheet_id is None:
        abort(404, "formula {0} doesn't exist.".format(id))

    nmm.make(title, _sheet_id, tab_name)

    now = datetime.datetime.now()
    date = str(now.month) + "-" + str(now.day) + "-" + str(now.year)
    file_name = title + "_" + tab_name + "_" + date + ".docx"

    print(file_name)

    return send_file(
        "static/" + file_name, as_attachment = True,
        attachment_filename = file_name
    )

@app.route('/formulas/create', methods=('GET', "POST"))
def create():
    if request.method == 'POST':
        r_title = request.form['title']
        r_sheet_id = request.form['sheet_id']

        error = ''
        error += helper.title_check(r_title)
        error += helper.sheet_check(r_sheet_id)

        if not r_title:
            flash('Please enter product #')
        if error is not '':
            flash(error)
        else:
            try:
                result = Result(
                    title=r_title,
                    sheet_id=r_sheet_id
                )
                db.session.add(result)
                db.session.commit()
                return redirect(url_for('formulas'))
            except:
                flash("Problem adding to the database")

    return render_template('create.html')

@app.route('/formulas/delete', methods=('GET', "POST"))
def delete():
    if request.method == 'POST':
        title = request.form['delete']
        print("Deleting....\n")
        print("Title:..." + title)
        db.session.execute(
            'DELETE FROM formulas'
            ' WHERE title =:param',
            {"param":title}
        )
        db.session.commit()
        return redirect(url_for('formulas'))
    formulas = db.session.execute(
        'SELECT title, sheet_id'
        ' FROM formulas f'
    ).fetchall()
    return render_template('delete.html', formulas=formulas)

@app.route('/analytics')
def analytics():
    sheet_id = '1M0pO_RyVcF-4OnghydE-sYARZT_Wwrzvn0MhZrnSpiQ'
    sheet_range = 'Total!C19:N19'
    revenue = pull_from_sheet.sales_analytics(sheet_id, sheet_range, False)
    sheet_range = 'Total!C21:N21'
    promos = pull_from_sheet.sales_analytics(sheet_id, sheet_range, False)
    labels = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    boundary = max(revenue)
    return render_template('analytics.html',
        revenue=revenue,
        promos=promos,
        labels=labels,
        boundary=boundary)

@app.route('/analytics/pie')
def pie():
    month_2_num = {
        "January":0,
        "February":1,
        "March":2,
        "April":3,
        "May":4,
        "June":5,
        "July":6,
        "August":7,
        "September":8,
        "October":9,
        "November":10,
        "December":11
    }
    month_name = request.args.get('month')
    if month_name != None:
        sheet_id = '1M0pO_RyVcF-4OnghydE-sYARZT_Wwrzvn0MhZrnSpiQ'
        sheet_range = 'Total!C10:N18'
        units_sold = pull_from_sheet.sales_analytics(sheet_id, sheet_range, True)
        labels = ["125", "127", "129", "220", "221", "222", "225", "207", "209"]

        units_by_month = list()
        for month_of_data in units_sold:
            units_by_month.append(month_of_data[month_2_num[month_name]])
        return render_template('pie.html',
            promos=units_by_month,
            labels=labels,
            month_name=month_name
        )
    else:
        sheet_id = '1M0pO_RyVcF-4OnghydE-sYARZT_Wwrzvn0MhZrnSpiQ'
        sheet_range = 'Total!O10:O18'
        units_sold = pull_from_sheet.sales_analytics(sheet_id, sheet_range, True)
        labels = ["125", "127", "129", "220", "221", "222", "225", "207", "209"]
        month_name = request.args.get('month')
        units_by_month = list()
        for data in units_sold:
            units_by_month.append(data)
        return render_template('pie.html',
            promos=units_by_month,
            labels=labels,
            month_name="2018"
        )

@app.route('/analytics/promotions')
def promotions():
    sheet_id = '1M0pO_RyVcF-4OnghydE-sYARZT_Wwrzvn0MhZrnSpiQ'

    sheet_range = 'Total!O19'
    annual_revenue = pull_from_sheet.sales_analytics(sheet_id, sheet_range, False)

    sheet_range = 'Total!C19:N19'
    revenue = pull_from_sheet.sales_analytics(sheet_id, sheet_range, False)

    sheet_range = 'Total!C21:N21'
    promos = pull_from_sheet.sales_analytics(sheet_id, sheet_range, False)

    average_revenue_per_month = (annual_revenue[0]/12)
    sales_by_dollar_promotion = list()
    for i in range(1,12):
        revenue_growth = revenue[i] - revenue[i-1]
        sales_by_dollar_promotion.append(revenue_growth/promos[i])
    boundary = max(sales_by_dollar_promotion)
    labels = ["February","March","April","May","June","July","August","September","October","November","December"]
    return render_template('analytics-promotions.html', revenue=sales_by_dollar_promotion, labels=labels, boundary=boundary)



if __name__ == '__main__':
    app.run()
