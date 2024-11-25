"""
This module contains logic for processing client data, model predictions,
and database interactions for a client management system.
"""

import os
import pickle
from itertools import product
import numpy as np
from app.database import get_db

column_intervention = [
    'Life Stabilization',
    'General Employment Assistance Services',
    'Retention Services',
    'Specialized Services',
    'Employment-Related Financial Supports for Job Seekers and Employers',
    'Employer Financial Supports',
    'Enhanced Referrals for Skills Development'
]

current_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(current_dir, 'model.pkl')
model = pickle.load(open(filename, "rb"))


def clean_input_data(input_data):
    """
    Cleans and transforms input data into a format suitable for the trained model.

    Args:
        data (dict): Input data from the client.

    Returns:
        list: Transformed data ready for prediction.
    """
    columns = [
        "age", "gender", "work_experience", "canada_workex", "dep_num",
        "canada_born", "citizen_status", "level_of_schooling", "fluent_english",
        "reading_english_scale", "speaking_english_scale", "writing_english_scale",
        "numeracy_scale", "computer_scale", "transportation_bool",
        "caregiver_bool", "housing", "income_source", "felony_bool",
        "attending_school", "currently_employed", "substance_use",
        "time_unemployed", "need_mental_health_support_bool"
    ]
    demographics = {
        'age': input_data['age'],
        'gender': input_data['gender'],
        'work_experience': input_data['work_experience'],
        'canada_workex': input_data['canada_workex'],
        'dep_num': input_data['dep_num'],
        'canada_born': input_data['canada_born'],
        'citizen_status': input_data['citizen_status'],
        'level_of_schooling': input_data['level_of_schooling'],
        'fluent_english': input_data['fluent_english'],
        'reading_english_scale': input_data['reading_english_scale'],
        'speaking_english_scale': input_data['speaking_english_scale'],
        'writing_english_scale': input_data['writing_english_scale'],
        'numeracy_scale': input_data['numeracy_scale'],
        'computer_scale': input_data['computer_scale'],
        'transportation_bool': input_data['transportation_bool'],
        'caregiver_bool': input_data['caregiver_bool'],
        'housing': input_data['housing'],
        'income_source': input_data['income_source'],
        'felony_bool': input_data['felony_bool'],
        'attending_school': input_data['attending_school'],
        'currently_employed': input_data['currently_employed'],
        'substance_use': input_data['substance_use'],
        'time_unemployed': input_data['time_unemployed'],
        'need_mental_health_support_bool': input_data['need_mental_health_support_bool']
    }
    output = []
    for column in columns:
        input_data = demographics.get(column, None)
        if isinstance(input_data, str):
            input_data = convert_text(column, input_data)
        output.append(input_data)
    return output


def convert_text(column, input_data: str):
    """
    Converts textual data from the frontend into corresponding numeric values
    based on predefined mappings. The mappings are specific to different
    columns and expected text values.

    Args:
        column (str): The name of the column for which the data is being converted.
        data (str): The textual data to be converted into numeric format.

    Returns:
        int: The numeric value corresponding to the text input if a match is found.
        str: The original text input if no conversion is applicable.
        None: If the input is invalid or no mapping exists.

    Notes:
        - The mappings include general boolean conversions (e.g., "yes" to 1, "no" to 0).
        - Category-specific mappings are defined for education level, housing, and income source.
        - Ensure that the mappings align with the valid answers provided in the frontend forms.
    """
    categorical_cols_integers = [
        {
            "": 0,
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
            'Grade 12 or equivalent': 5,
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
        },
        {
            'No Source of Income': 1,
            'Employment Insurance': 2,
            'Workplace Safety and Insurance Board': 3,
            'Ontario Works applied or receiving': 4,
            'Ontario Disability Support Program applied or receiving': 5,
            'Dependent of someone receiving OW or ODSP': 6,
            'Crown Ward': 7,
            'Employment': 8,
            'Self-Employment': 9,
            'Other (specify)': 10
        }
    ]
    for category in categorical_cols_integers:
        print(f"data: {input_data}")
        print(f"column: {column}")
        if input_data in category:
            return category[input_data]

    if isinstance(input_data, str) and input_data.isnumeric():
        return int(input_data)

    return input_data


def create_matrix(row):
    """
    Create a matrix of possible intervention combinations for a given row of data.

    Args:
        row (list): Input data row.

    Returns:
        np.ndarray: Matrix of intervention combinations appended to the input row.
    """
    input_data = [row.copy() for _ in range(128)]
    perms = intervention_permutations(7)
    input_data = np.array(input_data)
    perms = np.array(perms)
    matrix = np.concatenate((input_data, perms), axis = 1)
    return np.array(matrix)


def intervention_permutations(num):
    """
    Generate a matrix of all possible combinations of 1s and 0s for a given length.

    Args:
        num (int): The length of each combination.

    Returns:
        np.ndarray: A NumPy array containing all permutations of 1s and 0s for the given length.
    """
    perms = list(product([0, 1], repeat=num))
    return np.array(perms)


def get_baseline_row(row):
    """
    Create a baseline row by appending zeros (no interventions) to the input data.

    Args:
        row (list or np.ndarray): Input data row.

    Returns:
        np.ndarray: A combined array with the input data followed by zeros
        representing no interventions.
    """
    print(type(row))
    base_interventions = np.array([0]*7) # no interventions
    row = np.array(row)
    print(row)
    print(type(row))
    line = np.concatenate((row,base_interventions))
    return line


def intervention_row_to_names(row):
    """
    Convert a row of intervention indicators into a list of intervention names.

    Args:
        row (list or np.ndarray): A binary row where 1 indicates an intervention is applied.

    Returns:
        list: A list of intervention names corresponding
        to the applied interventions (1s in the input row).
    """
    names = []
    for i, value in enumerate(row):
        if value == 1:
            names.append(column_intervention[i])
    return names


def process_results(baseline, res):
    """
    {
        baseline_probability: 80 #baseline percentage point with no interventions
        res: [
            (85, [A,B,C]) #new percentange with intervention combinations
            and list of intervention names
            (89, [B,C])
            (91, [D,E])
        ]
    }
    """
    result_list = []
    for row in res:
        percent = row[-1]
        names = intervention_row_to_names(row)
        result_list.append((percent, names))

    output = {
        "baseline": baseline[-1],  #if it's an array, want the value inside of the array
        "interventions": result_list,
    }
    return output


def interpret_and_calculate(input_data):
    """
    Processes input data to compute baseline predictions and evaluate
    the impact of various intervention combinations using a pre-trained model.

    Args:
        input_data (dict): Client data with attributes and demographics.

    Returns:
        dict: Contains 'baseline' prediction and top intervention combinations
              with their predicted success rates and intervention names.
    """
    raw_data = clean_input_data(input_data)
    baseline_row = get_baseline_row(raw_data)
    baseline_row = baseline_row.reshape(1, -1)
    print("BASELINE ROW IS",baseline_row)
    intervention_rows = create_matrix(raw_data)
    baseline_prediction = model.predict(baseline_row)
    intervention_predictions = model.predict(intervention_rows)
    intervention_predictions = intervention_predictions.reshape(-1, 1)
    result_matrix = np.concatenate((intervention_rows,intervention_predictions), axis = 1)

    # sort this matrix based on prediction
    # print("RESULT SAMPLE::", result_matrix[:5])
    result_order = result_matrix[:, -1].argsort()
    result_matrix = result_matrix[result_order]

    # slice matrix to only top N results
    result_matrix = result_matrix[-3:, -8:]
    res = process_results(baseline_prediction,result_matrix)
    # build output dict
    print(f"RESULTS: {res}")
    return res


def create_client_data(client_data: dict):
    """
    Insert a new client record into the database.

    Args:
        client_data (dict): A dictionary containing the client data to be inserted.

    Returns:
        dict: The inserted client data if successful; None otherwise.
    """
    db = next(get_db())
    cursor = db.cursor()

    # Define the SQL INSERT statement
    query = """
    INSERT INTO clients (age, gender, work_experience, canada_workex, dep_num,
    canada_born, citizen_status, level_of_schooling, fluent_english,
    reading_english_scale, speaking_english_scale, writing_english_scale,
    numeracy_scale, computer_scale, transportation_bool, caregiver_bool,
    housing, income_source, felony_bool, attending_school, currently_employed,
    substance_use, time_unemployed, need_mental_health_support_bool,
    employment_assistance, life_stabilization, retention_services,
    specialized_services, employment_related_financial_supports,
    employer_financial_supports, enhanced_referrals, success_rate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare the values from the client_data dictionary
    values = (
        client_data['age'], client_data['gender'],
        client_data['work_experience'], client_data['canada_workex'],
        client_data['dep_num'], client_data['canada_born'],
        client_data['citizen_status'], client_data['level_of_schooling'],
        client_data['fluent_english'], client_data['reading_english_scale'],
        client_data['speaking_english_scale'],
        client_data['writing_english_scale'], client_data['numeracy_scale'],
        client_data['computer_scale'],
        client_data['transportation_bool'], client_data['caregiver_bool'],
        client_data['housing'], client_data['income_source'],
        client_data['felony_bool'], client_data['attending_school'],
        client_data['currently_employed'],
        client_data['substance_use'], client_data['time_unemployed'],
        client_data['need_mental_health_support_bool'],
        client_data['employment_assistance'], client_data['life_stabilization'],
        client_data['retention_services'],
        client_data['specialized_services'],
        client_data['employment_related_financial_supports'],
        client_data['employer_financial_supports'], client_data['enhanced_referrals'],
        client_data['success_rate']
    )

    # Execute the query and commit the transaction
    try:
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        return client_data  # Returning the inserted data
    except Exception as e:
        print(f"Error inserting client data: {e}")
        db.rollback()
        cursor.close()
        return None


def get_client_data(age: int, gender: int, work_experience: int):
    """
    Retrieve a single client's data from the database based on their attributes.

    Args:
        age (int): The age of the client.
        gender (int): The gender of the client.
        work_experience (int): The client's years of work experience.

    Returns:
        dict: A dictionary containing the client's data if found,
        or None if no matching client exists.

    Notes:
        - The attributes (age, gender, work_experience) are used
        as unique identifiers to locate the client record.
        - Returns the client's data as a dictionary with column names as keys.
    """
    db = next(get_db())
    cursor = db.cursor()
    query = "SELECT * FROM clients WHERE age = %s AND gender = %s AND work_experience = %s"
    values = (age, gender, work_experience)
    cursor.execute(query, values)
    result = cursor.fetchone()
    cursor.close()
    if result:
        return dict(zip(cursor.column_names, result))
    return None


def update_client_data(client_update: dict):
    """
    Update an existing client's data in the database.

    Args:
        client_update (dict): A dictionary containing the updated client data.
            The dictionary should include the identifying attributes (age, gender, work_experience)
            along with any other updated fields.

    Returns:
        dict: A dictionary containing the updated client data if the update is successful,
        or None if no matching client is found.

    Notes:
        - The function updates the client's data based on their unique attributes
        (age, gender, work_experience).
        - After the update, the function retrieves and returns the updated record.
    """
    db = next(get_db())
    cursor = db.cursor()
    query = "UPDATE clients SET ... WHERE age = %s AND gender = %s AND work_experience = %s"
    values = (client_update['age'], client_update['gender'], client_update['work_experience'])
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    updated_client = get_client_data(client_update['age'], client_update['gender'],
                                     client_update['work_experience'])
    return updated_client


def delete_client_data(age: int, gender: int, work_experience: int):
    """
    Delete a client's data from the database.

    Args:
        age (int): The age of the client.
        gender (int): The gender of the client.
        work_experience (int): The client's years of work experience.

    Returns:
        bool: True if the client's record was successfully deleted, False otherwise.

    Notes:
        - The attributes (age, gender, work_experience) are used
        as unique identifiers to locate and delete the client record.
        - If no matching record is found, the function returns False.
    """
    db = next(get_db())
    cursor = db.cursor()
    query = "DELETE FROM clients WHERE age = %s AND gender = %s AND work_experience = %s"
    values = (age, gender, work_experience)
    cursor.execute(query, values)
    db.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    return affected_rows > 0


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
        "income_source": "5",
        "felony_bool": "1",
        "attending_school": "0",
        "currently_employed": "1",
        "substance_use": "1",
        "time_unemployed": "1",
        "need_mental_health_support_bool": "1"
    }
    results = interpret_and_calculate(data)
    print(results)
