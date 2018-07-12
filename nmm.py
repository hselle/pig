import mailmerge
from datetime import date
import pull_from_sheet


'''
Reads specific cells from a google sheet and inputs the data into a nutrition
facts information panel.
TODO: figure out how to make this application scalable/distributable
'''

def calculate_dv(data):
    dv_dict = {
        'fat_dv' : int(round(float(data['fat'])/65*100)),
        'saturated_fat_dv' : int(round(float(data['saturated_fat'])/20*100)),
        'cholesterol_dv' : int(round(float(data['cholesterol'])/300*100)),
        'sodium_dv' : int(round(float(data['sodium'])/2400*100)),
        'carb_dv' : int(round(float(data['total_carbs'])/300*100)),
        'fiber_dv' : int(round(float(data['fiber'])/25*100))
    }
    return dv_dict

def push_to_doc(template_filename, data, _ingredients):
    '''
    This places formatted values into the relevant merge fields in
    Nutrition_Label_Template.docx, and writes to a new file called
    Nutrition_Label_Output.docx
    TODO: write to pdf
    '''
    document = mailmerge.MailMerge(template_filename)
    #print(document.get_merge_fields())

    document.merge(
        calories = data['calories'],
        fat = data['fat'],
        saturated_fat = data['saturated_fat'],
        cholesterol = data['cholesterol'],
        sodium = data['sodium'],
        total_carbs = data['total_carbs'],
        fiber = data['fiber'],
        sugar = data['sugar'],
        protein = data['protein'],
        calcium = data['calcium'],
        iron = data['iron'],

        fat_dv = '{:.4}'.format(str(data['fat_dv'])),
        sat_fat_dv = '{:.4}'.format(str(data['saturated_fat_dv'])),
        cholesterol_dv = '{:.4}'.format(str(data['cholesterol_dv'])),
        sodium_dv = '{:.4}'.format(str(data['sodium_dv'])),
        carb_dv = '{:.4}'.format(str(data['carb_dv'])),
        fiber_dv = '{:.4}'.format(str(data['fiber_dv'])),

        ingredients = _ingredients
    )
    document.write("static/Nutrition_Label_Output.docx")

def process(calories_dict, nutrient_dict, vitamins_and_minerals_dict):
    '''
    Formats the data given by pull_from_sheet.py and combines it into one big
    dictionary, which is then returne d.
    '''
    def format_whole_values_data(data):
        '''
        Checks how many decimal places the value should occupy and formats
        accordingly. Returns a copy of the given dictionary with formatted values
        and an added "g", signifying grams. For sodium, a specific case is defined
        giving "mg" instead.
        '''
        for nutrient in data:
            if "{:.1f}".format(data[nutrient])[-1:] == "0":
                data[nutrient] = str("{:10.0f}".format(data[nutrient])) + "g"
            elif "{:.2f}".format(data[nutrient])[-2:] == "0":
                data[nutrient] = str("{:10.2f}".format(data[nutrient])) + "g"
            else:
                data[nutrient] = str("{:10.1f}".format(data[nutrient])) + "g"
        data['sodium'] = data['sodium'][:-1] + "mg"
        return data

    dv_dict = calculate_dv(nutrient_dict)
    formatted_nutrient_dict = format_whole_values_data(nutrient_dict)
    p_data = {
        **calories_dict,
        **formatted_nutrient_dict,
        **dv_dict,
        **vitamins_and_minerals_dict
    }
    return p_data

def build_ingredient_list(components, ingredients_in):
    '''
    Reads the percentage of each componenet in the finished product, then
    reads the percentage of each ingredient in each component. These two values
    are then multiplied to give the percentage of each ingredient in the
    finished product. For example: Peanut Butter Filling(component) makes up
    45% of the total product. Powdered Sugar makes up 10% of the Peanut Butter
    Filling. So, .10 * .45 = .045 or 4.5 percent of the total product.
    '''
    component_factors = list(map(float, (components[0][0][:-1], components[1][0][:-1])))
    component_counter = 0
    ingredients_out = list()
    for component in ingredients_in:
        for ingredient in component:
            if ingredient[0] is not '':
                ingredient[0] = float(ingredient[0])
                ingredient[0] = ingredient[0]*component_factors[component_counter]/100
                ingredients_out.append(ingredient)
        component_counter = component_counter + 1

    def getKey(item):
        return item[0]

    ingredients_sorted = sorted(ingredients_out, key=getKey, reverse=True)
    ingredient_names = ''

    for ingredient in ingredients_sorted:
        ingredient_names += (ingredient[3] + ', ')

    return ingredient_names[:-2]

def make(sheet_id):
    print("\nmaking......................\n" + str(sheet_id))
    template_filename = 'static/Nutrition_Label_Template_Dev.docx'
    calories_dict, nutrient_dict, vitamins_and_minerals_dict, components, ingredients = pull_from_sheet.pull_from_sheet(sheet_id)
    processed_data = process(calories_dict, nutrient_dict, vitamins_and_minerals_dict)
    push_to_doc(template_filename, processed_data, build_ingredient_list(components, ingredients))
    print("Done. \nWrote Label to \"Nutrition_Label_Output.docx\"")
