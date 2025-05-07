from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)

modelo = joblib.load('models/modelo_entrenado.pkl')

@app.route('/')
def index():
    return render_template('index.html', resultado=None)

@app.route('/predecir', methods=['POST'])
def predecir():
    try:
        datos = [
            float(request.form['pregnancies']),
            float(request.form['glucose']),
            float(request.form['bloodpressure']),
            float(request.form['skinthickness']),
            float(request.form['insulin']),
            float(request.form['bmi']),
            float(request.form['pedigree']),
            float(request.form['age'])
        ]

        entrada = np.array([datos])
        prediccion = modelo.predict(entrada)[0]

        if prediccion == 1:
            mensaje = "Riesgo de diabetes detectado"
        else:
            mensaje = "No hay riesgo de diabetes"

        return render_template('index.html', resultado=mensaje)

    except Exception as e:
        return render_template('index.html', resultado=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
