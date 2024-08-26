from typing import List
import pandas as pd
import json
import numpy as np
import pickle
from itertools import combinations_with_replacement
from itertools import product

column_intervention = [
    'Life Stabilization',
    'General Employment Assistance Services',
    'Retention Services',
    'Specialized Services',
    'Employment-Related Financial Supports for Job Seekers and Employers', 
    'Employer Financial Supports',
    'Enhanced Referrals for Skills Development'
]

#request would include whatever the front end gives us
#we would clean the data, does not include all of the interventions
#then we would prepare the data by duplicating it and each would have a different variation of interventions
#because of the way batching works, we don't have to do the prediction on each row, we can treat it as one 
#unit of data, then we're doing inference on 128 generated rows, then we look at the ones with highest 3 scores
#return as a JSON (talk with wayne), return interventions. success rate would 
#the user is going to have to run it
# the user will get 2 results. first is prediction with no interventions and following x will be with best results
# before friday, try to break things down 
# when make fxn to clean data, don't overcomplicate it
# when generating 127 rows that are all combinations, just say "here;s the list and return list of lists and do all that are permutations"
#have fxn that returns all combos
#API cleans it, generations of new rows, runs prediction and produces JSON and top results
#why pickle - takes memory as it is in python and takes a binary snapshot and saves it to a file  joblib
# to do: run mean test on model, write fxn to check all inputs are filled in, sanitize data
# fast API is separate from the model, no business logic, middle
# get data from website and turn into numbers 8.10

model = pickle.load(open("model.pkl","rb"))

#website address that takes input from a form, processes it and returns result
# first, we process inputs by cleaning them on and sanitizing them, 
# backend is in two parts, model is created once, that's where we would generalize or have specific data
# augment input by creating 127 copies, with a variation on the interventions
# we do a prediction using the model on the base data with no interventions-baseline score
# we predict again with 127 variations, which will each get their own score
# finally, we build a return that features the baseline & the top N combinations of interventions
# optionally, we save predictions for later examination --- 

#ensure data is in the same order.

#### app = FastAPI()


def clean_input_data(data):
    #translate input into wahtever we trained the model on, numerical data in a specific order
    #if situation where interventions are set in stone, the command below is just cleaning up and organizing the input and making up baseline without any interventions
    #we are making list of interventions
    #any data has to be given by the form or we have to get rid of it
    #align column with order in columns-match up names, assume 
    # to do every column has to be in demographics
    columns = ["age","gender","work_experience","canada_workex","dep_num",	"canada_born",	
               "citizen_status",	"level_of_schooling",	"fluent_english",	"reading_english_scale",	
               "speaking_english_scale",	"writing_english_scale",	"numeracy_scale",	"computer_scale",	
               "transportation_bool",	"caregiver_bool",	"housing",	"income_source",	"felony_bool",	"attending_school",	
               "currently_employed",	"substance_use",	"time_unemployed",	"need_mental_health_support_bool"]
    demographics = {
        # 'age': data['age'],
        # 'gender': data['gender'],
        'work_experience': data['work_experience'],
        'canada_workex': data['canada_workex'],
        'dep_num': data['dep_num'],
        'canada_born': data['canada_born'],
        'citizen_status': data['citizen_status'],
        'level_of_schooling': data['level_of_schooling'],
        'fluent_english': data['fluent_english'],
        'reading_english_scale': data['reading_english_scale'],
        'speaking_english_scale': data['speaking_english_scale'],
        'writing_english_scale': data['writing_english_scale'],
        'numeracy_scale': data['numeracy_scale'],
        'computer_scale': data['computer_scale'],
        'transportation_bool': data['transportation_bool'],
        'caregiver_bool': data['caregiver_bool'],
        'housing': data['housing'],
        'income_source': data['income_source'],
        'felony_bool': data['felony_bool'],
        'attending_school': data['attending_school'],
        'currently_employed': data['currently_employed'],
        'substance_use': data['substance_use'],
        'time_unemployed': data['time_unemployed'],
        'need_mental_health_support_bool': data['need_mental_health_support_bool']
    }
    output = []
    for column in columns:
        # data = demographics[column] #grabbing something from a dictionary, sometimes dicts might not have the key we expect 8.21
        data = demographics.get(column, None) #default is None, and if you want to pass a value, can return any value
        if type(data) == str :
            data = convert_text(data)
        output.append(data)
    return output
    print(output)
    #make list of column in correct order
    #to do, ask wayne to send numbers whenever possible
    # interventions = data['interventions']
    # to do - write a function to account for T/F Y/N input

def convert_text(data:str):
    #take string and do whatever we need to convert it into a number
    # Convert categorical variables to integers (same as before)
    #turn into a list of dictionar
    categorical_cols_integers = [
        {
            "true": 1,
            "false": 0,
            "no": 0,
            "yes": 1,
            "No": 0,
            "Yes": 1
        },
        {
            'Grade 0-8': 1,
            'Grade 9': 2,
            'Grade 10': 3,
            'Grade 11': 4,
            'Grade 12 or equivalent (GED)': 5,
            'OAC or Grade 13': 6,
            'Some college': 7,
            'Some university': 8,
            'Some apprenticeship': 9,
            'Certificate of Apprenticeship': 10,
            'Journeyperson': 11,
            'Certificate/Diploma': 12,
            'Bachelor’s degree': 13,
            'Post graduate': 14
        },
        {
            'Renting-private': 1,
            'Renting-subsidized': 2,
            'Boarding or lodging': 3,
            'Homeowner': 4,
            'Living with family/friend': 5,
            'Institution': 6,
            'Temporary second residence': 7,
            'Band-owned home': 8,
            'Homeless or transient': 9,
            'Emergency hostel': 10
        }
    ]
    for category in categorical_cols_integers:
        if data in category:
            return category[data]
    return int(data)
    
    # Convert demographics to integers

#first step is to repeat row of data 127 times, create 127 combinations, combine them
def create_matrix(row):
    data = [row.copy() for _ in range(128)] #127 because we have 7 interventions
    perms = intervention_permutations(7)
    # print("this is perms",perms)
    data = np.array(data)
    perms = np.array(perms)
    matrix = np.concatenate((data,perms), axis = 1) #two 
    return np.array(matrix)
#create matrix of permutations of 1 and 0 of num length
def intervention_permutations(num):
    perms = list(product([0,1],repeat=num))
    return np.array(perms)

def get_baseline_row(row):
    # print("GET BASELINE ROW FXN:: ROW",row)
    print(type(row))
    base_interventions = np.array([0]*7) # no interventions
    # print("GET BASELINE ROW::BASE INTERVENTIONS",base_interventions)
    print(type(base_interventions))
    #8.23 TO DO 

    row = np.array(row) #TO DO FIX how line is created 8.21
    print(row)
    print(type(row))
    line = np.concatenate((row,base_interventions))
    #to do, read way np concatenate works
    return line
    #set up print statements, 

    #test function on its own 8.23, 

#[ , 0, 0, 0, 0, 0, 0, 0] <-list of numbers

#give a list of numbers, 

def intervention_row_to_names(row):
    names = []
    for i, value in enumerate(row):
        if value == 1: 
            names.append(column_intervention[i])
    return names

def process_results(baseline, results):
    ##Example:
    """
    {
        baseline_probability: 80 #baseline percentage point with no interventions
        results: [
            (85, [A,B,C]) #new percentange with intervention combinations and list of intervention names
            (89, [B,C])
            (91, [D,E])
        ]
    }
    """
    result_list= []
    for row in results:
        percent = row[-1] 
        names = intervention_row_to_names(row)
        result_list.append((percent,names))


    output = {
        "baseline": baseline[-1], #if it's an array, want the value inside of the array
        "interventions": result_list,
    }
    #placeholder, go through matrix and produce a list of intervention names for each row of the matrix, format, 
    #process, and return
    #returns list or dict
    return output
#whatever wayne and I agree with is not necessarily this, might have to update
def interpret_and_calculate(data):
    # 8.23 TO DO create a fxn, test
    # Separate demographics and interventions
    raw_data = clean_input_data(data)
    #expand into rows of data that include the interventions, then make predictions and format into output
    baseline_row = get_baseline_row(raw_data)

    baseline_row = baseline_row.reshape(1, -1)
    print("BASELINE ROW IS",baseline_row)
    intervention_rows = create_matrix(raw_data)
    baseline_prediction = model.predict(baseline_row)
    intervention_predictions = model.predict(intervention_rows)

    # need to tie interventions to percentages
    # concat predictions to intervention matrix
    intervention_predictions = intervention_predictions.reshape(-1, 1) #want shape to be a vertical column, not a row
    print("SHAPE OF INTERVENTION ROWS::",intervention_rows.shape)
    print("SHAPE OF INTERVENTION PREDICTIONS::",intervention_predictions.shape)
    result_matrix = np.concatenate((intervention_rows,intervention_predictions), axis = 1) ##CHANGED AXIS
    
    # sort this matrix based on prediction
    print("RESULT SAMPLE::", result_matrix[:5])
    # result_matrix = np.sort(result_matrix, order = -1, axis = 0) #note, sorted by ascending
    result_order = result_matrix[:,-1].argsort() #take all rows and only last column, gives back list of indexes sorted
    result_matrix = result_matrix[result_order] #indexing the matrix by the order

    # slice matrix to only top N results
    result_matrix = result_matrix[-3:,-8:] #-8 for interventions and prediction, want top 3, 3 combinations of intervention
    # post process results if needed ie make list of names for each row
    results = process_results(baseline_prediction,result_matrix)
    # build output dict
    return results

if __name__ == "__main__":
    print("running")
    data = {
        "age": "23",
        "gender": "1",
        "work_experience": "1",
        "canada_workex": "1",
        "dep_num": "0",
        "canada_born": "1",
        "citizen_status": "2",
        "level_of_schooling": "2",
        "fluent_english": "3",
        "reading_english_scale": "2",
        "speaking_english_scale": "2",
        "writing_english_scale": "3",
        "numeracy_scale": "2",
        "computer_scale": "3",
        "transportation_bool": "2",
        "caregiver_bool": "1",
        "housing": "1",
        "income_source": "1",
        "felony_bool": "1",
        "attending_school": "0",
        "currently_employed": "1",
        "substance_use": "1",
        "time_unemployed": "1",
        "need_mental_health_support_bool": "1"
    }
    # print(data)
    results = interpret_and_calculate(data)
    print(results)

    # Predict baseline return to work and success increase
    # baseline_return_to_work = rf_model_baseline.predict(X_pred_baseline)[0]
    # success_increase_results = {}
    # for intervention in interventions:
    #     X_pred_success[intervention] = 1
    #     success_increase_results[intervention] = rf_model_success_increase.predict(X_pred_success)[0]
    #     X_pred_success[intervention] = 0
    
    # total_increase = baseline_return_to_work + sum(success_increase_results.values())

    # result = {
    #     "baseline_return_to_work": baseline_return_to_work, #need to know the type
    #     "success_increase_for_each_intervention": success_increase_results, #what is this type, list, dict, etc.
    #     "total_increase": total_increase #define this type, will be dict
    # }
    
    # return result

#endpoints, a get and a post endpoint
#data has to follow format of prediction input



# what is he expecting to get back re: interventions, a list of interventions by name and expected success?
# to do: run the code

#run it as a server, how to connect the two
# will get a json file