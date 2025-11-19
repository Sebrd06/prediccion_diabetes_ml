from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuario con autenticación"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con predicciones
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hashing de contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Modelo de predicción de diabetes"""
    id = db.Column(db.Integer, primary_key=True)
    # Permitir predicciones anónimas (user_id nullable)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    
    # Datos del paciente
    pregnancies = db.Column(db.Float, nullable=False)
    glucose = db.Column(db.Float, nullable=False)
    bloodpressure = db.Column(db.Float, nullable=False)
    skinthickness = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    pedigree = db.Column(db.Float, nullable=False)
    age = db.Column(db.Float, nullable=False)
    
    # Resultado
    result = db.Column(db.String(3), nullable=False)  # 'Sí' o 'No'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convertir a diccionario para exportar"""
        return {
            'Pregnancies': self.pregnancies,
            'Glucose': self.glucose,
            'BloodPressure': self.bloodpressure,
            'SkinThickness': self.skinthickness,
            'Insulin': self.insulin,
            'BMI': self.bmi,
            'DiabetesPedigree': self.pedigree,
            'Age': self.age,
            'Resultado': self.result,
            'Fecha': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Prediction user_id={self.user_id} result={self.result}>'
