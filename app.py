from flask import Flask, request, render_template
from pymongo import MongoClient

class Rule:
    def __init__(self, parameter, operator, value, unit, age_range, gender, valid_until, first_condition=None):
        self.parameter = parameter
        self.operator = operator
        self.value = value
        self.unit = unit
        self.age_range = age_range
        self.gender = gender
        self.valid_until = valid_until
        self.first_condition = first_condition

    def to_dict(self):
        return {
            'parameter': self.parameter,
            'operator': self.operator,
            'value': self.value,
            'unit': self.unit,
            'age_range': self.age_range,
            'gender': self.gender,
            'valid_until': self.valid_until,
            'first_condition': self.first_condition
        }

class Disease:
    def __init__(self, disease_code, disease_name, rules):
        self.disease_code = disease_code
        self.disease_name = disease_name
        self.rules = rules

    def to_dict(self):
        return {
            'disease_code': self.disease_code,
            'disease_name': self.disease_name,
            'rules': [rule.to_dict() for rule in self.rules]
        }

class Database:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_disease(self, disease):
        existing_disease = self.collection.find_one({'disease_code': disease.disease_code})
        if existing_disease:
            return 'Error: A disease with this code already exists!'
        
        try:
            self.collection.insert_one(disease.to_dict())
            return 'Data submitted successfully!'
        except Exception as e:
            return f'Error inserting data: {e}'

app = Flask(__name__)

# MongoDB connection
db = Database('mongodb://localhost:27017/', 'rulebase', 'RuleBase')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    parameters = request.form.getlist('parameter')
    operators = request.form.getlist('operator')
    values = request.form.getlist('value')
    units = request.form.getlist('unit')
    age_ranges = request.form.getlist('age_range')
    genders = request.form.getlist('gender')
    valid_until_numbers = request.form.getlist('valid_until_number')
    valid_until_units = request.form.getlist('valid_until_unit')
    first_conditions = request.form.getlist('first_condition')

    # Ensure all lists have the same length
    list_lengths = [len(parameters), len(operators), len(values), len(units), len(age_ranges), len(genders), len(valid_until_numbers), len(valid_until_units)]
    if len(set(list_lengths)) != 1:
        return 'Error: Mismatched input lengths!'

    rules = []
    for i in range(len(parameters)):
        valid_until = f"{valid_until_numbers[i]} {valid_until_units[i]}"
        rule = Rule(parameters[i], operators[i], values[i], units[i], age_ranges[i], genders[i], valid_until, first_conditions[i] if i < len(first_conditions) else None)
        rules.append(rule)

    disease_code = request.form['disease_code']
    disease_name = request.form['disease_name']
    disease = Disease(disease_code, disease_name, rules)

    result = db.insert_disease(disease)
    return result

if __name__ == '__main__':
    app.run(debug=True)
