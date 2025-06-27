from flask import Flask,render_template, request, jsonify
import joblib
import numpy as np


app = Flask(__name__)

MODEL_PATH = "artifacts/models/model.pkl"
SCALER_PATH = "artifacts/processed/scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURES = [
                'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
                'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
                'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
                'Predictive_Maintenance_Score', 'Error_Rate_%','Year', 'Month', 'Day', 'Hour'
            ]

# Feature information with descriptions, ranges, and units
FEATURE_INFO = {
    'Operation_Mode': {
        'description': 'Machine Operation Mode',
        'type': 'select',
        'options': [('0', 'Idle'), ('1', 'Active'), ('2', 'Maintenance')],
        'placeholder': 'Select operation mode'
    },
    'Temperature_C': {
        'description': 'Operating Temperature',
        'type': 'number',
        'min': 20,
        'max': 100,
        'step': 0.1,
        'unit': '°C',
        'placeholder': 'e.g., 65.5'
    },
    'Vibration_Hz': {
        'description': 'Machine Vibration Frequency',
        'type': 'number',
        'min': 0,
        'max': 5,
        'step': 0.01,
        'unit': 'Hz',
        'placeholder': 'e.g., 2.5'
    },
    'Power_Consumption_kW': {
        'description': 'Power Consumption',
        'type': 'number',
        'min': 0,
        'max': 15,
        'step': 0.1,
        'unit': 'kW',
        'placeholder': 'e.g., 7.2'
    },
    'Network_Latency_ms': {
        'description': 'Network Communication Latency',
        'type': 'number',
        'min': 0,
        'max': 50,
        'step': 0.1,
        'unit': 'ms',
        'placeholder': 'e.g., 25.3'
    },
    'Packet_Loss_%': {
        'description': 'Network Packet Loss Rate',
        'type': 'number',
        'min': 0,
        'max': 5,
        'step': 0.01,
        'unit': '%',
        'placeholder': 'e.g., 1.5'
    },
    'Quality_Control_Defect_Rate_%': {
        'description': 'Product Defect Rate',
        'type': 'number',
        'min': 0,
        'max': 10,
        'step': 0.01,
        'unit': '%',
        'placeholder': 'e.g., 3.2'
    },
    'Production_Speed_units_per_hr': {
        'description': 'Production Speed',
        'type': 'number',
        'min': 50,
        'max': 500,
        'step': 1,
        'unit': 'units/hr',
        'placeholder': 'e.g., 350'
    },
    'Predictive_Maintenance_Score': {
        'description': 'Maintenance Prediction Score',
        'type': 'number',
        'min': 0,
        'max': 1,
        'step': 0.01,
        'unit': '',
        'placeholder': 'e.g., 0.75'
    },
    'Error_Rate_%': {
        'description': 'System Error Rate',
        'type': 'number',
        'min': 0,
        'max': 15,
        'step': 0.01,
        'unit': '%',
        'placeholder': 'e.g., 2.1'
    },
    'Year': {
        'description': 'Year',
        'type': 'number',
        'min': 2020,
        'max': 2030,
        'step': 1,
        'unit': '',
        'placeholder': 'e.g., 2024'
    },
    'Month': {
        'description': 'Month',
        'type': 'number',
        'min': 1,
        'max': 12,
        'step': 1,
        'unit': '',
        'placeholder': 'e.g., 6'
    },
    'Day': {
        'description': 'Day',
        'type': 'number',
        'min': 1,
        'max': 31,
        'step': 1,
        'unit': '',
        'placeholder': 'e.g., 15'
    },
    'Hour': {
        'description': 'Hour (24-hour format)',
        'type': 'number',
        'min': 0,
        'max': 23,
        'step': 1,
        'unit': '',
        'placeholder': 'e.g., 14'
    }
}

LABELS = {
    0:"High",
    1:"Low",
    2:"Medium"
}


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        
        # Convert Operation_Mode to numeric if it's a string
        input_data = []
        for feature in FEATURES:
            value = data.get(feature, '')
            if feature == 'Operation_Mode':
                # Convert string to numeric if needed
                if value in ['Idle', 'Active', 'Maintenance']:
                    value = {'Idle': 0, 'Active': 1, 'Maintenance': 2}[value]
            input_data.append(float(value))
        
        input_array = np.array(input_data).reshape(1,-1)
        scaled_array = scaler.transform(input_array)

        # Get prediction and confidence
        pred = model.predict(scaled_array)[0]
        prediction = LABELS.get(pred, "Unknown")
        
        # Get prediction probabilities if available
        prediction_confidence = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(scaled_array)[0]
            prediction_confidence = f"{max(proba)*100:.1f}%"

        return jsonify({
            'success': True,
            'prediction': prediction,
            'confidence': prediction_confidence
        })

    except ValueError:
        return jsonify({
            'success': False,
            'error': "Invalid input: Please check your values and try again."
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        })

@app.route("/" , methods=["GET" , "POST"])
def index():
    prediction = None
    prediction_confidence = None
    input_values = {}

    if request.method=="POST":
        try:
            # Store input values to repopulate form on error
            for feature in FEATURES:
                input_values[feature] = request.form.get(feature, '')
            
            # Convert Operation_Mode to numeric if it's a string
            input_data = []
            for feature in FEATURES:
                value = request.form[feature]
                if feature == 'Operation_Mode':
                    # Convert string to numeric if needed
                    if value in ['Idle', 'Active', 'Maintenance']:
                        value = {'Idle': 0, 'Active': 1, 'Maintenance': 2}[value]
                input_data.append(float(value))
            
            input_array = np.array(input_data).reshape(1,-1)
            scaled_array = scaler.transform(input_array)

            # Get prediction and confidence
            pred = model.predict(scaled_array)[0]
            prediction = LABELS.get(pred , "Unknown")
            
            # Get prediction probabilities if available
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(scaled_array)[0]
                prediction_confidence = f"{max(proba)*100:.1f}%"

        except ValueError:
            prediction = "Invalid input: Please check your values and try again."
        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html", 
                         prediction=prediction, 
                         prediction_confidence=prediction_confidence,
                         features=FEATURES, 
                         feature_info=FEATURE_INFO,
                         input_values=input_values)

if __name__=="__main__":
    app.run(debug=True , host="0.0.0.0" , port=5000)