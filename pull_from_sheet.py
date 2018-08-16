from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.errors import HttpError
import re

def get_tabs(sheet_id):
    '''
    Retrieves and returns all tab names from a google sheet with a given sheet Id
    '''
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = sheet_id

    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    tabs = list()
    for sheet in sheets:
        title = sheet.get("properties", {}).get("title", "Sheet1")
        tabs.append(title)
    return tabs

def _pull_row(sheet_id, range):
    '''
    Helper method that pulls from a given sheet a given range of cells.
    Hack: Google API returns a 2d array: [rows][columns]. Hence, this function
    only returns the [0]th row.
    '''
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = sheet_id
    RANGE_NAME = range
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME).execute()
    values = result.get("values")[0]

    return values

def _pull_2d(sheet_id, range):
    '''
    Helper method that pulls from a given sheet a given range of cells as a 2d
    array: [rows][columns]
    '''
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = sheet_id
    RANGE_NAME = range
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME).execute()
    values = result.get("values")
    return values

def sales_analytics(sheet_id, range, is2D):
    '''
    Organizes sales data stored in string lists into integer lists.
    '''
    def toInt(revenue_strings):
        '''
        This function takes a dirty list of strings and cleans itto be an
        int list. It throws out blank cells and destroys periods, commas and any
        other non-numeric character.
        '''
        int_list = list()
        for s in revenue_strings:
            num = ''
            for char in s:
                if char == ".":
                    break
                else:
                    try:
                        num = num + str(int(char))
                    except ValueError:
                        pass

            int_list.append(int(num))
        return int_list

    def toInt_2d(revenue_strings):
        '''
        A version for a list with 2 dimensions. See above function
        '''
        month_list = list()
        for month in revenue_strings:
            int_list = list()
            for promo in month:
                num = ''
                for char in promo:
                    if char == ".":
                        break
                    else:
                        try:
                            num = num + str(int(char))
                        except ValueError:
                            pass
                if num == '':
                    int_list.append(0)
                else:
                    int_list.append(int(num))
            month_list.append(int_list)
        return month_list

    if is2D:
        values = _pull_2d(sheet_id, range)
        return toInt_2d(values)
    else:
        values = _pull_row(sheet_id, range)
        return toInt(values)

def pull_from_sheet(sheet_id, tab_name):
    '''
    This pulls the 15th row of Kris's google Sheet, which contains rounded
    values for nutrition facts.
    '''
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('static/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # Call the Sheets API
    SPREADSHEET_ID = sheet_id


    def get_nutrition_facts(tab_name):
        '''
        Pulls from the table and catagorizes the data in dictrionaries
        '''
        RANGE_NAME = tab_name + '!F15:T15'

        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
        values = result.get("values")[0]

        calories_dict = {
            'calories' : values[0],
            'calories_from_fat' : values[1]
        }


        nutrient_dict = {
            'sugar' : float(values[2]),
            'fat' : float(values[3]),
            'fiber' : float(values[4]),
            'total_carbs' : float(values[5]),
            'protein' : float(values[6]),
            #'sodium_grams' : float(values[7]),
            'sodium' : float(values[8]),
            'saturated_fat' : float(values[9]),
            'cholesterol' : float(values[10])
        }

        vitamins_and_minerals_dict = {
            'vitamin_a' : values[11],
            'vitamin_c' : values[12],
            'calcium' : values[13],
            'iron' : values[14]
        }

        data_dict = {
            **calories_dict,
            **nutrient_dict,
            **vitamins_and_minerals_dict
        }
        return calories_dict, nutrient_dict, vitamins_and_minerals_dict

    def get_ingredients(tab_name):
        '''
        Pulls from the table and returns a tuple (components, ingredients)
        '''
        def get_components(tab_name):
            RANGE_NAME = tab_name + '!B5:C10'
            result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
            components = result.get("values")
            return components

        def get_each_ingredient(ranges, tab_name):
            ingredients_total = list()
            for range in ranges:
                RANGE_NAME = tab_name + range
                result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
                ingredients_one_component = result.get("values")
                ingredients_total.append(ingredients_one_component)
            return ingredients_total

        ingredient_ranges = ('!B23:E33', '!B45:E45')
        components = get_components(tab_name)
        ingredients = get_each_ingredient(ingredient_ranges, tab_name)

        return components, ingredients

    components, ingredients = get_ingredients(tab_name)
    calories_dict, nutrient_dict, vitamins_and_minerals_dict = get_nutrition_facts(tab_name)
    return calories_dict, nutrient_dict, vitamins_and_minerals_dict, components, ingredients
