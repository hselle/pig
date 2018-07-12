from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.errors import HttpError


def sheet_check(sheet_id):
    try:
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage('static/credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=creds.authorize(Http()))

        # Call the Sheets API
        SPREADSHEET_ID = sheet_id

        RANGE_NAME = 'E15:S15'
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
        values = result.get("values")[0]

        return None
    except HttpError:
        return "Could not access sheet with sheet id: " + sheet_id + "\n")

def title_check(title):
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import engine
    import os
    import requests
    import operator
    import app
    titles = app.db.session.execute(
        'SELECT title'
        ' FROM formulas f'
    ).fetchall()
    for t in titles:
        if t[0]==title:
            return "Title already in use.\n"
    return None
