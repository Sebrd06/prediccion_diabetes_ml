# Predicción del Riesgo de Diabetes con Extra Trees Classifier

Este proyecto es una aplicación web desarrollada con Flask que permite predecir el riesgo de diabetes en pacientes, usando un modelo de clasificación binaria entrenado con el dataset **Pima Indians Diabetes Dataset**. El modelo fue construido con el algoritmo **Extra Trees Classifier** y permite realizar predicciones a partir de datos médicos ingresados manualmente.

## Tecnologías utilizadas

- Python 3.x
- Flask
- Scikit-learn
- Pandas
- Numpy
- Jinja2 (plantillas HTML)
- Joblib (para guardar el modelo)
- Openpyxl (para exportar a Excel)
- HTML/CSS (frontend básico)

## Modelo de Machine Learning

- **Algoritmo**: Extra Trees Classifier
- **Dataset**: Pima Indians Diabetes Dataset (Kaggle)
- **Variables**:
  - Número de embarazos
  - Glucosa
  - Presión arterial
  - Espesor de piel
  - Insulina
  - Índice de Masa Corporal (IMC)
  - Herencia genética (Diabetes pedigree function)
  - Edad

## Funcionalidades actuales

- Formulario HTML para ingresar de médicos.
- Predicción del riesgo de diabetes (resultado binario: Sí / No).
- Historial de predicciones con todos los datos ingresados.
- Exportación del historial a archivo Excel.
- Visualización del historial en una tabla web.

## Estructura del proyecto

/data/ # Contiene el dataset original y archivos auxiliares
/models/ # Archivo del modelo entrenado (modelo_entrenado.pkl)
/templates/ # Archivos HTML (formulario, tabla de historial)
app.py # Script principal de la aplicación Flask
README.md # Este archivo
requirements.txt # Lista de dependencias


## Cómo ejecutar el proyecto

1. Clona este repositorio:

```bash
git clone https://github.com/tu_usuario/diabetes-prediction-app.git
cd diabetes-prediction-app
```

2. Instala las dependencias (recomendado: usar Python 3.11 en Windows):

Opción recomendada (recrear virtualenv con Python 3.11):

```powershell
# Asegúrate de tener Python 3.11 instalado y accesible como `py -3.11`.
cd <ruta-del-proyecto>
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
# Ejecutar la app
python app.py
```

Notas:
- Si `Activate.ps1` falla por la política de ejecución, ejecuta en PowerShell como administrador:
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y luego vuelve a activar.

Opción alternativa (si NO puedes cambiar la versión de Python):

- Instala las "Microsoft C++ Build Tools" (requerido para compilar scikit-learn desde fuente en Windows):
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Después de instalar las build tools, activa tu venv y ejecuta:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Aviso: la opción alternativa es más lenta y puede ser compleja; la opción recomendada es usar Python 3.11.

3. Ejecuta la app:
```powershell
python app.py  # usa el python del venv activado
# o
py -3.11 app.py
```

4. Abre el enlace en el navegador.