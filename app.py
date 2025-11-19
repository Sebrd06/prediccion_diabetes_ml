# Compatibilidad: en Python 3.14 `pkgutil.get_loader` puede no existir.
import pkgutil
import importlib
if not hasattr(pkgutil, 'get_loader'):
    def _compat_get_loader(name):
        try:
            spec = importlib.util.find_spec(name)
            return spec.loader if spec is not None else None
        except Exception:
            return None
    pkgutil.get_loader = _compat_get_loader

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from datetime import datetime
import io
import base64

from models import db, User, Prediction

import numpy as np
import pandas as pd
import joblib

# Matplotlib es opcional para gráficos - si no está disponible, mostramos solo tablas

app = Flask(__name__)

# Configuración BD
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "diabetes_app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_segura_cambiar_en_produccion'

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Cargar modelo ML
modelo = None
model_load_error = None
try:
    modelo = joblib.load('models/modelo_entrenado.pkl')
except Exception as e:
    modelo = None
    model_load_error = str(e)


def fallback_predict(entrada_numpy):
    """Predictor de reserva simple (heurístico) usado cuando no está disponible el modelo real.
    entrada_numpy: np.array de forma (1, 8) con los campos en el mismo orden que el dataset.
    Devuelve 1 (riesgo) o 0 (no riesgo).
    Reglas heurísticas (temporal):
    - Glucosa > 125 => riesgo
    - IMC >= 30 => riesgo
    - Edad >= 50 => riesgo
    - Pedigree >= 0.6 => riesgo
    - Si ninguna condición, no riesgo
    """
    try:
        arr = np.asarray(entrada_numpy).reshape(-1, 8)
    except Exception:
        return 0
    g = float(arr[0, 1])
    bmi = float(arr[0, 5])
    age = float(arr[0, 7])
    pedigree = float(arr[0, 6])

    if g > 125 or bmi >= 30 or age >= 50 or pedigree >= 0.6:
        return 1
    return 0

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Crear tablas al iniciar
with app.app_context():
    db.create_all()
    # Crear usuario admin si no existe
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@diabetes.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Usuario admin creado: admin / admin123")

# ============ RUTAS DE AUTENTICACIÓN ============

@app.route('/')
def index():
    """Página pública de inicio. No requiere login."""
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario de login"""
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('inicio'))
        else:
            flash('Usuario o contraseña inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Formulario de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validaciones
        if not username or not email or not password:
            flash('Todos los campos son requeridos', 'danger')
            return redirect(url_for('registro'))
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('registro'))
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('registro'))
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('registro'))
        
        # Crear usuario (estándar)
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # Auto-login después de registrarse para que el usuario estándar pueda predecir de inmediato
        login_user(user)
        flash('Cuenta registrada y sesión iniciada. Ya puedes realizar predicciones.', 'success')
        return redirect(url_for('formulario'))
    
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# ============ RUTAS PRINCIPALES ============

@app.route('/inicio')
def inicio():
    """Página de bienvenida pública"""
    return render_template('inicio.html')

@app.route('/formulario')
def formulario():
    """Formulario de predicción público. Si hay usuario autenticado, mostramos su historial."""
    historial = current_user.predictions if current_user.is_authenticated else []
    return render_template('index.html', resultado=None, historial=historial, modelo_disponible=(modelo is not None))

@app.route('/predecir', methods=['POST'])
def predecir():
    """Realizar predicción. Público: si hay usuario autenticado, se asocia la predicción a su cuenta."""
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
        # Usar modelo real si está disponible, si no usar predictor heurístico
        if modelo is not None:
            pred_val = int(modelo.predict(entrada)[0])
            used = 'modelo'
        else:
            pred_val = int(fallback_predict(entrada))
            used = 'heuristico'

        resultado = 'Sí' if pred_val == 1 else 'No'
        mensaje = ("⚠ Riesgo de diabetes detectado" if pred_val == 1 else "✓ No hay riesgo de diabetes")
        if used == 'heuristico':
            mensaje += ' (predicción heurística)'

        # Guardar predicción en BD; si el usuario no está autenticado, user_id será None
        user_id = current_user.id if current_user.is_authenticated else None
        pred = Prediction(
            user_id=user_id,
            pregnancies=datos[0],
            glucose=datos[1],
            bloodpressure=datos[2],
            skinthickness=datos[3],
            insulin=datos[4],
            bmi=datos[5],
            pedigree=datos[6],
            age=datos[7],
            result=resultado
        )
        db.session.add(pred)
        db.session.commit()

        flash(mensaje, 'info')
        historial = current_user.predictions if current_user.is_authenticated else []
        
        # Calcular estadísticas
        stats = None
        if current_user.is_authenticated:
            stats = {
                'total_predicciones': len(historial),
                'con_riesgo': sum(1 for p in historial if p.result == 'Sí'),
                'sin_riesgo': sum(1 for p in historial if p.result == 'No'),
            }
        
        return render_template('index.html', resultado=mensaje, historial=historial, stats=stats, modelo_disponible=(modelo is not None))

    except Exception as e:
        flash(f'Error en predicción: {str(e)}', 'danger')
        historial = current_user.predictions if current_user.is_authenticated else []
        
        # Calcular estadísticas incluso en caso de error
        stats = None
        if current_user.is_authenticated:
            stats = {
                'total_predicciones': len(historial),
                'con_riesgo': sum(1 for p in historial if p.result == 'Sí'),
                'sin_riesgo': sum(1 for p in historial if p.result == 'No'),
            }
        
        return render_template('index.html', resultado=None, historial=historial, stats=stats, modelo_disponible=(modelo is not None))
@app.route('/perfil')
@login_required
def perfil():
    """Perfil del usuario"""
    historial = current_user.predictions
    stats = {
        'total_predicciones': len(historial),
        'con_riesgo': sum(1 for p in historial if p.result == 'Sí'),
        'sin_riesgo': sum(1 for p in historial if p.result == 'No'),
    }
    return render_template('perfil.html', historial=historial, stats=stats)

@app.route('/descargar_historial')
@login_required
def descargar_historial():
    """Descargar historial del usuario en Excel"""
    predicciones = current_user.predictions
    if not predicciones:
        flash('No hay predicciones para exportar', 'warning')
        return redirect(url_for('perfil'))
    
    data = [p.to_dict() for p in predicciones]
    df = pd.DataFrame(data)
    
    os.makedirs('resultados', exist_ok=True)
    export_path = f'resultados/historial_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(export_path, index=False)
    
    return send_file(export_path, as_attachment=True)

# ============ RUTAS ADMIN ============

@app.route('/admin')
@login_required
def admin_panel():
    """Panel de administración"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))
    
    usuarios = User.query.all()
    total_predicciones = Prediction.query.count()
    total_usuarios = User.query.count()
    predicciones_con_riesgo = Prediction.query.filter_by(result='Sí').count()
    
    stats = {
        'total_usuarios': total_usuarios,
        'total_predicciones': total_predicciones,
        'con_riesgo': predicciones_con_riesgo,
        'sin_riesgo': total_predicciones - predicciones_con_riesgo,
    }
    
    return render_template('admin.html', usuarios=usuarios, stats=stats)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard con accesos rápidos"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))

    total_predicciones = Prediction.query.count()
    total_usuarios = User.query.count()
    predicciones_con_riesgo = Prediction.query.filter_by(result='Sí').count()

    stats = {
        'total_usuarios': total_usuarios,
        'total_predicciones': total_predicciones,
        'con_riesgo': predicciones_con_riesgo,
        'sin_riesgo': total_predicciones - predicciones_con_riesgo,
    }

    return render_template('dashboard_admin.html', stats=stats)


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard general: redirige a dashboard admin o muestra dashboard usuario"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    # Estadísticas del usuario
    historial = current_user.predictions
    stats = {
        'total_predicciones': len(historial),
        'con_riesgo': sum(1 for p in historial if p.result == 'Sí'),
        'sin_riesgo': sum(1 for p in historial if p.result == 'No'),
    }
    last_pred = historial[-1] if historial else None
    return render_template('dashboard_user.html', stats=stats, last_pred=last_pred, historial=historial)

@app.route('/admin/predicciones')
@login_required
def admin_predicciones():
    """Ver todas las predicciones del sistema"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))
    
    predicciones = Prediction.query.order_by(Prediction.created_at.desc()).all()
    return render_template('admin_predicciones.html', predicciones=predicciones)


@app.route('/admin/eliminar_prediccion/<int:pred_id>', methods=['POST'])
@login_required
def eliminar_prediccion(pred_id):
    """Eliminar una predicción (solo admin)"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))
    
    prediccion = Prediction.query.get(pred_id)
    if prediccion:
        db.session.delete(prediccion)
        db.session.commit()
        flash('Predicción eliminada', 'success')
    else:
        flash('Predicción no encontrada', 'danger')
    
    return redirect(url_for('admin_predicciones'))

@app.route('/admin/eliminar_usuario/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    """Eliminar usuario (solo admin)"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))
    
    usuario = User.query.get(user_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
    elif usuario.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'danger')
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {usuario.username} eliminado', 'success')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/estadisticas')
@login_required
def admin_estadisticas():
    """Página de estadísticas sin gráficos (usando tablas de texto)"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('inicio'))
    
    predicciones = Prediction.query.all()
    
    if not predicciones:
        flash('No hay datos para mostrar', 'info')
        return redirect(url_for('admin_panel'))
    
    # Convertir a DataFrame
    data = [p.to_dict() for p in predicciones]
    df = pd.DataFrame(data)
    
    # Estadísticas descriptivas
    stats = {
        'edad_media': round(df['Age'].mean(), 2),
        'edad_min': int(df['Age'].min()),
        'edad_max': int(df['Age'].max()),
        'glucosa_media': round(df['Glucose'].mean(), 2),
        'bmi_media': round(df['BMI'].mean(), 2),
        'presion_media': round(df['BloodPressure'].mean(), 2),
        'total_registros': len(df),
    }
    
    # Distribuciones por categorías
    resultado_dist = df['Resultado'].value_counts().to_dict()
    
    return render_template('estadisticas.html', stats=stats, df_html=df.to_html(classes='table table-striped'), resultado_dist=resultado_dist)

# ============ RUTAS ESTÁTICAS ============

@app.route('/negocio_y_datos')
def negocio_y_datos():
    return render_template('negocio_y_datos.html')

@app.route('/ingenieria_datos')
def ingenieria_datos():
    return render_template('ingenieria_datos.html')

@app.route('/ingenieria_modelo')
def ingenieria_modelo():
    return render_template('ingenieria_modelo.html')

@app.route('/despliegue_modelo')
def despliegue_modelo():
    return render_template('despliegue_modelo.html')

@app.route('/evaluacion_modelo')
def evaluacion_modelo():
    return render_template('evaluacion_modelo.html')

@app.route('/monitoreo_mantenimiento')
def monitoreo_mantenimiento():
    return render_template('monitoreo_mantenimiento.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)