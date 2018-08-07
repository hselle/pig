from __future__ import print_function
import pull_from_sheet
from googleapiclient.errors import HttpError
import plotly
import  plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='hselle97', api_key='92LUmN4eQwLLxDGPpSv0')

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import re

def get_cases_per_channel(sheet_size):

    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = '1zB7N1C1LNIRR5d2CqXhnT29os4R_XnghTO2OBP0NXEE'
    RANGE_NAME = 'C2:C' + str(sheet_size)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME, majorDimension='COLUMNS').execute()
    channels = result.get("values")[0]

    RANGE_NAME = 'Z2:Z' + str(sheet_size)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME, majorDimension='COLUMNS').execute()
    cases = result.get("values")[0]

    channel_dict = {}

    for i in range(sheet_size-1):
        try:
            channel_dict[channels[i]] = 0
        except IndexError:
            print(i)

    for i in range(sheet_size-1):
        channel_dict[channels[i]] = channel_dict[channels[i]] + int(cases[i])

    return channel_dict

cases_per_channel = get_cases_per_channel(43908)
channels = list(cases_per_channel.keys())
cases = list(cases_per_channel.values())
data = [go.Bar(
            x=channels,
            y=cases
    )]

py.plot(data, filename='basic-bar')
