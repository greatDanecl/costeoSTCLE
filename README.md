# 📊 Modelo Costo Contrato Colectivo · STCLE / LAN Express

App Streamlit para modelar y sensibilizar el costo del Contrato Colectivo firmado el 01/09/2023 entre el **Sindicato de Tripulantes de Cabina LAN Express (STCLE)** y **Transporte Aéreo S.A.**, con vigencia hasta el 31/08/2026.

---

## 🚀 Despliegue rápido (Streamlit Community Cloud — **gratuito**)

### 1. Sube el repo a GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/stcle-costeo.git
git push -u origin main
```

### 2. Despliega en Streamlit Cloud
1. Ve a **[share.streamlit.io](https://share.streamlit.io)**
2. Haz clic en **"New app"**
3. Selecciona tu repositorio y rama `main`
4. En **"Main file path"** escribe: `app.py`
5. Clic en **"Deploy"** — listo en ~2 minutos ✅

> El archivo `logo.png` debe estar en la raíz del repositorio junto a `app.py`.

---

## 💻 Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🗂 Estructura del modelo

```
stcle_app/
├── app.py              ← App principal
├── logo.png            ← Logo STCLE (incluir en el repo)
├── requirements.txt    ← Dependencias Python
└── README.md
```

---

## 📋 Funcionalidades

### Tab 1 — Costeo por Beneficio
- **25+ conceptos remuneracionales** extraídos del contrato colectivo
- Para cada beneficio: valor unitario actual vs. nuevo, costo anual calculado automáticamente
- Organizados por categoría (remuneraciones directas, bonos, asignaciones, etc.)
- Badge "Recurrente" vs "One-Time"

### Tab 2 — Evolución Anual & CAGR
- Proyección punta a punta (hasta 3 años)
- Gráfico de barras actual vs. nuevo por año
- Gráfico waterfall de variación por categoría
- Donut de composición del costo
- **CAGR** del contrato actual y nuevo
- Tablas con valores en **CLP y USD**

### Tab 3 — Simulador Nuevo Contrato
- Sliders para incremento diferencial en HV, sueldo base y bonos
- Variación de dotación
- Adición de nuevos beneficios propuestos
- Trayectoria de costo simulada vs. actual

### Tab 4 — Resumen Ejecutivo
- Vista consolidada de todos los beneficios
- Totales en CLP y USD
- CAGR final e indicadores clave

---

## ⚙️ Sidebar — Parámetros Globales
- **Tipo de cambio** CLP/USD (default $980, promedio 2025)
- **Horizonte** 1–3 años
- **Incremento real** pactado (1%/año, configurable)
- **Dotación** por subcategoría (editable)
- **Horas de vuelo** promedio por subcategoría

---

## 📌 Supuestos del modelo
| Concepto | Supuesto |
|---|---|
| Bono asistencia | 85% trabajadores lo perciben |
| Hijos promedio | 0.8 hijos/trabajador (bonos con recargo por hijo) |
| Bono desempeño | Mix: 10% excepcional, 30% sobre esperado, 60% esperado |
| Viático nacional | 8 días/mes promedio |
| Viático internacional | 4 días/mes promedio (tarifa Sudamérica $50 USD) |
| Movilización | 60% opta por asignación en efectivo |
| PSVNC | 1.5 eventos/mes/persona promedio |
| IPC | **Excluido** (costo hundido, no modelado) |
| Indemnizaciones YOS | Declarado pero no costeado |

---

## 🎨 Paleta de colores
- **Azul marino** `#1B2A6B` — principal
- **Rojo** `#C8102E` — acento / alertas
- Basado en la identidad visual del logo STCLE

---

*Uso interno STCLE · Modelo de costeo CC · No distribuir*
