from flask import Flask, request, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['rulebase']
collection = db['RuleBase']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    rule_data = []
    parameters = request.form.getlist('parameter')
    operators = request.form.getlist('operator')
    values = request.form.getlist('value')
    units = request.form.getlist('unit')
    age_ranges = request.form.getlist('age_range')
    genders = request.form.getlist('gender')
    valid_until_numbers = request.form.getlist('valid_until_number')
    valid_until_units = request.form.getlist('valid_until_unit')
    first_conditions = request.form.getlist('first_condition')

    for i in range(len(parameters)):
        rule_data.append({
            'parameter': parameters[i],
            'operator': operators[i],
            'value': values[i],
            'unit': units[i],
            'age_range': age_ranges[i],
            'gender': genders[i],
            'valid_until': f"{valid_until_numbers[i]} {valid_until_units[i]}",
            'first_condition': first_conditions[i] if i < len(first_conditions) else None
        })

    disease_code = request.form['disease_code']
    disease_data = {
        'disease_code': disease_code,
        'disease_name': request.form['disease_name'],
        'rules': rule_data
    }

    # Check if a disease with the same code already exists
    existing_disease = collection.find_one({'disease_code': disease_code})
    if existing_disease:
        return 'Error: A disease with this code already exists!'

    print("Captured Data:", disease_data)  # Debugging statement to print the data being inserted

    try:
        collection.insert_one(disease_data)
        print("Data inserted successfully")
    except Exception as e:
        print("Error inserting data:", e)

    return 'Data submitted successfully!'

if __name__ == '__main__':
    app.run(debug=True)
