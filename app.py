from flask import Flask, render_template, request, send_file, redirect, url_for
import numpy as np
import pandas as pd
import joblib
import os

app = Flask(__name__)

modelo = joblib.load('models/modelo_entrenado.pkl')

historial_resultados = []

# Redirección desde raíz "/" hacia /inicio
@app.route('/')
def redireccion_inicio():
    return redirect(url_for('inicio'))

# Ruta de bienvenida
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')  # Pantalla de bienvenida

# Ruta para formulario de predicción
@app.route('/formulario')
def formulario():
    return render_template('index.html', resultado=None, historial=historial_resultados)

# Ruta de predicción
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

        mensaje = " Riesgo de diabetes detectado" if prediccion == 1 else " No hay riesgo de diabetes"

        historial_resultados.append({
            'Pregnancies': datos[0],
            'Glucose': datos[1],
            'BloodPressure': datos[2],
            'SkinThickness': datos[3],
            'Insulin': datos[4],
            'BMI': datos[5],
            'DiabetesPedigree': datos[6],
            'Age': datos[7],
            'Resultado': 'Sí' if prediccion == 1 else 'No'
        })

        return render_template('index.html', resultado=mensaje, historial=historial_resultados)

    except Exception as e:
        return render_template('index.html', resultado=f"Error: {str(e)}", historial=None)

# Ruta para descargar Excel
@app.route('/descargar')
def descargar():
    if not historial_resultados:
        return "No hay datos para exportar"

    df = pd.DataFrame(historial_resultados)
    os.makedirs('resultados', exist_ok=True)
    export_path = 'resultados/resultado_diabetes.xlsx'
    df.to_excel(export_path, index=False)
    return send_file(export_path, as_attachment=True)

# Ejecutar aplicación
if __name__ == '__main__':
    app.run(debug=True)
