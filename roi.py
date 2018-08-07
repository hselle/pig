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

def get_months(sheet_size):

    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = '1zB7N1C1LNIRR5d2CqXhnT29os4R_XnghTO2OBP0NXEE'
    def pull_col(col):
        RANGE_NAME = col + '2:' + col + str(sheet_size)
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME, majorDimension='COLUMNS').execute()
        return result.get("values")[0]

    channels = pull_col('C')
    skus = pull_col("AB")
    month = pull_col('AC')
    cases = pull_col('Z')

    master = [
        channels,
        skus,
        month,
        cases
    ]
    def group_index(index, master):
        return [
            master[0][index],
            master[1][index],
            master[2][index],
            master[3][index]
        ]
    def parse_months(month, master):
        parsed = list()
        for i in range(sheet_size-1):
            if master[2][i] == month:
                parsed.append(group_index(i, master))
        return parsed

    def parse_skus(master):
        sku_dict = {}

        for entry in master:
            sku_dict[entry[1]] = '0'
        for entry in master:
            sku_dict[entry[1]] = int(sku_dict[entry[1]]) + int(entry[3])
        return sku_dict

    def average_skus(master):
        master_dict = {}
        keys = master[0].keys()
        for key in keys:
            master_dict[key] = 0
        for d in master:
            for key in keys:
                master_dict[key] = int(master_dict[key]) + int(d[key])
        for key in keys:
            master_dict[key] = master_dict[key]/3
        return master_dict



    jan = parse_skus(parse_months("January", master))
    feb = parse_skus(parse_months("February", master))
    mar = parse_skus(parse_months("March", master))
    print(average_skus((jan, feb, mar)))


    apr = parse_skus(parse_months("April", master))
    may = parse_skus(parse_months("May", master))
    jun = parse_skus(parse_months("June", master))

    print(average_skus((apr, may, jun)))

    # channel_skus = list()
    # for i in range(sheet_size-1):
    #     channel_skus.append(channels[i] + " - " + skus[i] + " - " + month[i])

    # channel_sku_dict = {}
    # for i in range(sheet_size-1):
    #     channel_sku_dict[channel_skus[i]] = 0
    # for i in range(sheet_size-1):
    #     channel_sku_dict[channel_skus[i]] = channel_sku_dict[channel_skus[i]] + int(cases[i])
    #
    # return channel_sku_dict

averages = get_months(43908)


print(averages)

# channels = list(cases_per_channel.keys())
# cases = list(cases_per_channel.values())
# data = [go.Bar(
#             x=channels,
#             y=cases
#     )]
#
# py.plot(data, filename='basic-bar')
