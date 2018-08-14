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

    def group_index2(index, master):
        return [
            master[index][0],
            master[index][1],
            master[index][2],
            master[index][3]
        ]

    def parse_months(month, master):
        parsed = list()
        for i in range(sheet_size-1):
            if master[2][i] == month:
                parsed.append(group_index(i, master))
        return parsed

    def parse_channel(channel, master):
        parsed = list()
        #print("ABout to parse Chalnnel: " + str(master))
        for i in range(len(master)-1):
            if master[i][0] == channel:
                parsed.append(group_index2(i, master))
        return parsed

    def get_channels(master):
        channel_list = list()
        for i in range(len(master)-1):
            if master[i][0] not in channel_list:
                channel_list.append(master[i][0])
        return channel_list

    def get_sku_channel_dict(master):
        sku_dict = {}
        for channel in master:
            for entry in channel:
                sku_dict[entry[1] + " - " + entry[0]] = '0'
        for channel in master:
            for entry in channel:
                sku_dict[entry[1] + " - " + entry[0]] = int(sku_dict[entry[1] + " - " + entry[0]]) + int(entry[3])
        return sku_dict

    def get_sku_dict(master):
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

    def pull_month(month_name, master):
        month = parse_months(month_name, master)
        return_ = list()
        for channel in get_channels(month):
            return_.append(parse_channel(channel, month))
        return get_sku_channel_dict(return_)

    q1 = average_skus((pull_month("January", master), pull_month("February", master), pull_month("March", master)))
    q2 = average_skus((pull_month("April", master), pull_month("May", master), pull_month("June", master)))
    return (q1, q2)

averages = get_months(43908)


print(averages)

# skus = list(map(str, averages[0].keys()))
#
# trace1 = go.Bar(
#             x=averages,
#             y=list(averages[0].values())
# )
# trace2 = go.Bar(
#             x=averages,
#             y=list(averages[1].values())
# )
#
# data = [trace1, trace2]
# layout = go.Layout(
#     barmode='group'
# )
#
# fig = go.Figure(data=data, layout=layout)
# py.plot(fig, filename='grouped-bar')
# channels = list(cases_per_channel.keys())
# cases = list(cases_per_channel.values())
# data = [go.Bar(
#             x=channels,
#             y=cases
#     )]
#
# py.plot(data, filename='basic-bar')
