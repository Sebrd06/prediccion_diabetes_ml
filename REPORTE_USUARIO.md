# 📊 Reporte de Seguimiento de Usuario - Predicción de Diabetes

## Descripción General
El sistema ahora incluye un reporte detallado de seguimiento para cada usuario registrado que permite visualizar el historial completo de predicciones realizadas.

---

## 📋 Información del Reporte

### 1. **Estadísticas Generales**
El reporte muestra 4 tarjetas principales con datos resumidos:

- **Total de Predicciones**: Número total de exámenes realizados
- **Con Riesgo**: Cuántas predicciones indicaron riesgo de diabetes (Sí)
- **Sin Riesgo**: Cuántas predicciones indicaron ausencia de riesgo (No)
- **% de Riesgo**: Porcentaje calculado de predicciones positivas

### 2. **Reporte Detallado**
Una tarjeta de reporte que incluye:

```
📋 Reporte de Seguimiento
├─ Exámenes Realizados: [Número total]
├─ Predicciones Positivas (Riesgo): [Cantidad] 
├─ Predicciones Negativas (Sin Riesgo): [Cantidad]
├─ Porcentaje de Riesgo: [Porcentaje]%
├─ Primer Examen: [Fecha y hora del primer examen]
└─ Último Examen: [Fecha y hora del último examen]
```

### 3. **Historial Detallado de Predicciones**
Una tabla interactiva con todas las predicciones realizadas, mostrando:

| # | Fecha y Hora | Edad | Glucosa (mg/dL) | Presión Arterial | IMC | Resultado |
|---|---|---|---|---|---|---|
| 1 | 18/11/2025 22:23:38 | 45 | 125 | 80 | 27.5 | ⚠ RIESGO DETECTADO |
| 2 | 18/11/2025 22:25:10 | 32 | 95 | 75 | 24.2 | ✓ SIN RIESGO |

---

## 🎯 Características del Reporte

### ✓ Campos Mostrados
1. **Número de Examen** (#): Ordenamiento secuencial
2. **Fecha y Hora**: Cuándo se realizó el examen
3. **Edad**: Edad del paciente al momento del examen
4. **Glucosa**: Nivel de glucosa en sangre (mg/dL)
5. **Presión Arterial**: Medida en mmHg
6. **IMC**: Índice de Masa Corporal
7. **Resultado**: 
   - ⚠️ **RIESGO DETECTADO** (badge rojo)
   - ✓ **SIN RIESGO** (badge verde)

### 🎨 Estilos Visuales
- **Badges de Riesgo**: Fondo rojo con texto oscuro
- **Badges Seguros**: Fondo verde con texto oscuro
- **Tabla Interactiva**: Filas con hover effect
- **Estadísticas en Tarjetas**: Colores diferenciados por tipo

---

## 📍 Ubicación en la Aplicación

Para acceder al reporte:
1. Inicia sesión con tus credenciales
2. Haz clic en "Mi Perfil" en la barra de navegación
3. Verás el reporte completo con todas tus predicciones

### Ruta URL
```
http://127.0.0.1:10000/perfil
```

---

## 🔐 Acceso Restringido

- **Solo usuarios autenticados** pueden ver su propio reporte
- Cada usuario solo ve su historial personal
- Los administradores pueden ver reportes de todos los usuarios en `/admin/predicciones`

---

## 📥 Exportar Datos

El reporte incluye un botón para descargar los datos en formato Excel:
- Botón: **📥 Descargar Excel**
- Incluye todas las predicciones del usuario
- Formato: `.xlsx` con múltiples columnas

---

## 📊 Datos de Ejemplo

Si un usuario ha realizado múltiples predicciones:

```
Usuario: admin
Total Predicciones: 5
Con Riesgo: 2 (40%)
Sin Riesgo: 3 (60%)
Primer Examen: 18/11/2025 20:15:00
Último Examen: 18/11/2025 22:30:45
```

---

## 🛠️ Funcionalidades Incluidas

✅ Seguimiento de cuántas veces ha hecho el examen
✅ Visualización de tendencias (riesgo vs sin riesgo)
✅ Historial completo y detallado
✅ Información de fechas y horas
✅ Valores médicos completos
✅ Exportación a Excel
✅ Interfaz responsive y accesible

---

## 📝 Notas Técnicas

- Los exámenes se ordenan de forma **inversa** (más recientes primero)
- El cálculo del porcentaje se realiza automáticamente
- Los datos se guardan en SQLite y se sincronizan en tiempo real
- La tabla es completamente responsive en dispositivos móviles

---

**Versión**: 1.0  
**Última Actualización**: 18/11/2025  
**Estado**: ✅ Activo y Funcional
