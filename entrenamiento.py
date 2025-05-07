import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
import joblib
import os

# Ruta del dataset
DATA_PATH = 'datos/diabetes.csv'

# Cargar el dataset
df = pd.read_csv(DATA_PATH)

# Reemplazar ceros por NaN en columnas que no pueden tener 0
columnas_a_corregir = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
df[columnas_a_corregir] = df[columnas_a_corregir].replace(0, np.nan)

# Opcional: llenar NaN con la media
df[columnas_a_corregir] = df[columnas_a_corregir].fillna(df[columnas_a_corregir].mean())

# Separar variables independientes (X) y objetivo (y)
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inicializar y entrenar el modelo
modelo = ExtraTreesClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Evaluación
y_pred = modelo.predict(X_test)

print("=== Evaluación del Modelo ===")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.2f}")
print(f"Precision: {precision_score(y_test, y_pred):.2f}")
print(f"Recall:    {recall_score(y_test, y_pred):.2f}")
print("\nMatriz de Confusión:")
print(confusion_matrix(y_test, y_pred))
print("\nReporte de Clasificación:")
print(classification_report(y_test, y_pred))

# Crear carpeta para guardar el modelo
os.makedirs('models', exist_ok=True)
joblib.dump(modelo, 'models/modelo_entrenado.pkl')
print("\n Modelo guardado como 'models/modelo_entrenado.pkl'")