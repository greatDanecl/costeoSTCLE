import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Modelo Costo Contrato Colectivo · STCLE",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# PALETA Y ESTILOS
# ─────────────────────────────────────────────
ROJO   = "#C8102E"
AZUL   = "#1B2A6B"
AZUL_C = "#2E4BAD"
GRIS   = "#F4F5F7"
BLANCO = "#FFFFFF"
VERDE  = "#1A7A4A"
AMBAR  = "#D97706"

st.markdown(f"""
<style>
  /* Fondo general */
  .stApp {{ background-color: {GRIS}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{ background-color: {AZUL}; }}
  [data-testid="stSidebar"] * {{ color: white !important; }}
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stSlider label {{ color: #CBD5F5 !important; }}

  /* Títulos */
  h1 {{ color: {AZUL}; font-family: 'Segoe UI', sans-serif; }}
  h2, h3 {{ color: {AZUL}; }}

  /* Cards métricas */
  .metric-card {{
    background: {BLANCO};
    border-left: 5px solid {ROJO};
    border-radius: 8px;
    padding: 16px 20px;
    margin: 6px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}
  .metric-card .label {{ font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:.5px; }}
  .metric-card .value {{ font-size:22px; font-weight:700; color:{AZUL}; }}
  .metric-card .delta {{ font-size:13px; margin-top:2px; }}
  .delta-pos {{ color:{VERDE}; }}
  .delta-neg {{ color:{ROJO}; }}

  /* Header banner */
  .header-banner {{
    background: linear-gradient(135deg, {AZUL} 0%, {AZUL_C} 100%);
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 18px;
    color: white;
  }}
  .header-banner h1 {{ color: white !important; margin:0; font-size:22px; }}
  .header-banner p  {{ color: #CBD5F5; margin:0; font-size:13px; }}

  /* Tabla */
  .stDataFrame {{ border-radius: 8px; }}

  /* Expander */
  .streamlit-expanderHeader {{ background: {BLANCO}; border-radius:8px; color:{AZUL} !important; }}

  /* Section divider */
  .section-title {{
    font-size:15px; font-weight:700; color:{AZUL};
    border-bottom: 2px solid {ROJO};
    padding-bottom: 4px; margin: 16px 0 10px 0;
    text-transform: uppercase; letter-spacing:.5px;
  }}

  /* Badge */
  .badge {{
    display:inline-block; padding:2px 10px;
    border-radius:12px; font-size:11px; font-weight:600;
  }}
  .badge-recurrente {{ background:#DBEAFE; color:#1E40AF; }}
  .badge-onetime    {{ background:#FEE2E2; color:#991B1B; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOGO
# ─────────────────────────────────────────────
def img_to_b64(path):
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except:
        return ""

logo_b64 = img_to_b64("logo.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:56px;border-radius:50%;">' if logo_b64 else "✈️"

st.markdown(f"""
<div class="header-banner">
  {logo_html}
  <div>
    <h1>Modelo de Costeo · Contrato Colectivo STCLE</h1>
    <p>Sindicato de Tripulantes de Cabina LAN Express · Vigencia 01/09/2023 – 31/08/2026</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — PARÁMETROS GLOBALES
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Parámetros Globales")

    st.markdown("### 💱 Tipo de Cambio")
    tc_usd = st.number_input("CLP / USD", value=980, step=5, min_value=700, max_value=1500)

    st.markdown("### 📅 Horizonte de Análisis")
    anios = st.slider("Años del contrato", 1, 3, 3)

    st.markdown("### 📈 Incremento Real (% anual)")
    st.caption("Aplica sobre conceptos definidos por contrato (excluye IPC)")
    inc_real_pct = st.number_input("Incremento real %", value=1.0, step=0.5, min_value=0.0, max_value=10.0)

    st.markdown("### 👥 Dotación por Subcategoría")
    st.caption("Número de trabajadores por categoría")

    n_trainee  = st.number_input("TC Trainee",       value=10, min_value=0, step=1)
    n_tcj      = st.number_input("TC Junior",         value=25, min_value=0, step=1)
    n_tc       = st.number_input("TC Senior (TC)",    value=60, min_value=0, step=1)
    n_tcs      = st.number_input("TC Senior (TCs)",   value=45, min_value=0, step=1)
    n_jsab     = st.number_input("Jefe Servicio AB",  value=35, min_value=0, step=1)
    n_jsabs    = st.number_input("Jefe SA Bordo Sr",  value=18, min_value=0, step=1)

    total_dot  = n_trainee + n_tcj + n_tc + n_tcs + n_jsab + n_jsabs
    st.metric("Total dotación", total_dot)

    st.markdown("### ✈️ Productividad (hrs vuelo/mes promedio)")
    hv_trainee = st.number_input("HV/mes TC Trainee",  value=55.0, step=1.0)
    hv_tcj     = st.number_input("HV/mes TC Junior",   value=57.0, step=1.0)
    hv_tc      = st.number_input("HV/mes TC",          value=60.0, step=1.0)
    hv_tcs     = st.number_input("HV/mes TCs",         value=62.0, step=1.0)
    hv_jsab    = st.number_input("HV/mes JSAB",        value=60.0, step=1.0)
    hv_jsabs   = st.number_input("HV/mes JSABs",       value=60.0, step=1.0)

# ─────────────────────────────────────────────
# DATOS BASE DEL CONTRATO (valores a la firma, sep-2023)
# ─────────────────────────────────────────────

# Valores hora de vuelo (brutos CLP, referencia firma)
HV = {
    "TC Trainee": 3579,
    "TC Junior":  3937,
    "TC":         7119,
    "TCs":        11051,
    "JSAB":       16018,
    "JSABs":      19871,
}

# Sueldo base mensual (brutos CLP)
SB = {
    "TC Trainee": 500000,   # aprox. IMM 2023
    "TC Junior":  460000,
    "TC":         460000,
    "TCs":        460000,
    "JSAB":       483575,
    "JSABs":      559136,
}

# Dotaciones del sidebar
dotacion = {
    "TC Trainee": n_trainee,
    "TC Junior":  n_tcj,
    "TC":         n_tc,
    "TCs":        n_tcs,
    "JSAB":       n_jsab,
    "JSABs":      n_jsabs,
}

hv_mes = {
    "TC Trainee": hv_trainee,
    "TC Junior":  hv_tcj,
    "TC":         hv_tc,
    "TCs":        hv_tcs,
    "JSAB":       hv_jsab,
    "JSABs":      hv_jsabs,
}

subcat_list = list(HV.keys())

# ─────────────────────────────────────────────
# HELPER: aplicar incremento real acumulado por año
# ─────────────────────────────────────────────
def factor_inc(anio, pct):
    """Factor multiplicador con incremento real anual. Año 0 = base."""
    return (1 + pct/100) ** anio

# ─────────────────────────────────────────────
# DEFINICIÓN DE BENEFICIOS
# Estructura: cada beneficio tiene:
#   nombre, cláusula, tipo (recurrente/one-time),
#   sujeto_incremento (bool), formula(params) -> CLP/año
# ─────────────────────────────────────────────

def costo_hora_vuelo_anual(hv_dict_nuevo=None):
    """Costo total anual por horas de vuelo (piso 55 hrs garantizado)."""
    hv_use = hv_dict_nuevo if hv_dict_nuevo else HV
    total = 0
    for sc in subcat_list:
        hv_real = max(hv_mes[sc], 55)
        total += hv_use[sc] * hv_real * 12 * dotacion[sc]
    return total

def costo_sueldo_base_anual(sb_dict_nuevo=None):
    sb_use = sb_dict_nuevo if sb_dict_nuevo else SB
    total = 0
    for sc in subcat_list:
        total += sb_use[sc] * 12 * dotacion[sc]
    return total

# ─────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Costeo por Beneficio",
    "📈 Evolución Anual & CAGR",
    "🔬 Simulador Nuevo Contrato",
    "📋 Resumen Ejecutivo"
])

# ══════════════════════════════════════════════
# TAB 1 — COSTEO POR BENEFICIO
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Variables Remuneracionales — Contrato Colectivo STCLE · LanExpress</div>', unsafe_allow_html=True)
    st.caption("Ajusta los valores actuales y nuevos para cada beneficio. El costo anual se calcula automáticamente.")

    # ── Construir tabla de beneficios editable ──
    # Definimos todos los beneficios extraídos del contrato

    beneficios_def = [
        # (id, nombre, cláusula, recurrente, unidad, cant_actual, val_unit_actual, cant_nueva, val_unit_nueva, sujeto_inc_real, notas)
        # REMUNERACIONES DIRECTAS
        ("hv",        "Horas de Vuelo",                     "Cláusula 26",  True,  "HV×dotación×12", None, None, None, None, True,  "Calculado desde dotación y HV/mes por subcategoría"),
        ("sb",        "Sueldo Base",                         "Cláusula 26",  True,  "SB×dotación×12", None, None, None, None, True,  "Sueldo base fijo mensual × dotación"),
        ("gratif",    "Gratificación Legal (25% rem.)",      "Cláusula 4",   True,  "% rem.",         None, None, None, None, True,  "25% remuneración mensual legal, tope 4.75 IMM"),
        # BONOS RECURRENTES
        ("asist",     "Bono 100% Asistencia",                "Cláusula 28a", True,  "CLP/mes/persona",169349, None, 169349, None, False, "Se asume 85% de trabajadores lo perciben"),
        ("fiestas",   "Bono Fiestas Patrias",                "Cláusula 28b", True,  "CLP/persona",   138983, None, 138983, None, False, "Pago septiembre. Incluye 30% por hijo (prom. 0.8 hijos)"),
        ("navidad",   "Bono Navidad",                        "Cláusula 28c", True,  "CLP/persona",   169872, None, 169872, None, False, "Pago diciembre. Incluye 30% por hijo (prom. 0.8 hijos)"),
        ("bono_des",  "Bono Desempeño (TC promedio)",        "Cláusula 37",  True,  "CLP/persona",   405337, None, 405337, None, False, "Pago julio. Se asume 60% 'cumple esperado', 30% 'sobre esperado'"),
        ("bono_prod", "Bono Productividad (factor 1.0)",     "Cláusula 37",  True,  "CLP/persona",   674602, None, 674602, None, False, "Pago marzo. JSAB: $1.180.556. Asume 100% cumplimiento."),
        # BONOS OPERACIONALES (por evento)
        ("psvnc",     "Bono Noche Consecutiva (PSVNC)",      "Cláusula 17/1.5", True,  "CLP/evento",  52094, None,  52094, None, False, "Máx. 2 eventos/mes programados. Estimado: 1.5 eventos/mes/persona"),
        ("ext_psv",   "Bono Extensión PSV 12→14h (1er evt)", "Cláusula 23",  True,  "CLP/evento",   79029, None,  79029, None, False, "Estimado: 0.5 eventos/mes/persona"),
        ("cambio_v",  "Bono Cambio de Vuelo",                "Cláusula 13d", True,  "CLP/evento",  119819, None, 119819, None, False, "Estimado: 0.3 eventos/mes/persona"),
        ("cancel_v",  "Bono Cancelación Vuelo (espera>3h)",  "Cláusula 13b", True,  "CLP/evento",  200469, None, 200469, None, False, "Estimado: 0.2 eventos/mes/persona"),
        ("turno5",    "Bono 5° Turno en adelante",           "Cláusula 17/4",True,  "CLP/turno",    58608, None,  58608, None, False, "TC: $58.608 | JSAB: $97.678. Estimado: 15% trabajadores/mes"),
        ("turno_atp", "Bono Turno Aeropuerto (1er turno)",   "Cláusula 17/4.2", True,"CLP/turno",   54700, None,  54700, None, False, "Estimado: 1 turno ATO/mes promedio por trabajador"),
        ("pre_libre", "Bono PSV previo a día libre >22:00",  "Cláusula 17/1.6",True, "CLP/evento",  64196, None,  64196, None, False, "Estimado: 0.4 eventos/mes/persona"),
        ("high_rank", "Diferencial High Rank Programado",    "Cláusula 16",  True,  "CLP/HV diff",  None,  None,  None,  None, False, "Diferencia HV TCs vs JSABs. Estimado 5% vuelos con HR."),
        # ASIGNACIONES
        ("escolar",   "Asignación Escolaridad (prom.)",      "Cláusula 29a", True,  "CLP/hijo/año", 164532, None, 164532, None, False, "EM promedio. Se asume prom. 0.8 hijos/trabajador"),
        ("matrimon",  "Asignación Matrimonio/AUC",           "Cláusula 29b", True,  "CLP/evento",  189211, None, 189211, None, False, "Estimado: 3% dotación/año"),
        ("nacim",     "Asignación Nacimiento/Adopción",      "Cláusula 29d", True,  "CLP/hijo",    189211, None, 189211, None, False, "Estimado: 5% dotación/año"),
        ("fallec",    "Asignación Fallecimiento familiar",   "Cláusula 29c", True,  "CLP/evento", 1681904,None, 1681904,None, False, "Estimado: 2% dotación/año"),
        # BENEFICIOS ESPECIALES
        ("viatico_n", "Viáticos Nacionales (CLP/día)",       "Cláusula 8",   True,  "CLP/día/vuelo",35000,None,  35000, None, False, "Estimado: 8 días viático nacional/mes por persona"),
        ("viatico_i", "Viáticos Internacionales (USD/día)",  "Cláusula 8",   True,  "USD/día",        50, None,     50, None, False, "Estimado: 4 días viático internacional/mes (Sudamérica)"),
        ("moviliz",   "Movilización (asignación mensual)",   "Cláusula 18",  True,  "CLP/mes/persona",264528,None,264528,None,False, "Quienes optan por movilización propia. Estimado 60% dotación"),
        ("bono_ant",  "Bono Antigüedad (promedio anual)",    "Cláusula 32",  True,  "% rem. al cumplir años", None, None, None, None, False, "Estimado según distribución de antigüedad de dotación"),
        ("apv",       "APV Empresa (matching)",              "Cláusula 39",  True,  "CLP/mes/persona",10000,None,  10000, None, False, "Tope $10.000/mes. Estimado 70% adhesión"),
        ("seguro_v",  "Seguros de Vida + Accidentes",        "Cláusula 38",  True,  "CLP/persona/año",None,None,  None,  None, False, "Prima estimada mercado: ~$80.000/año/persona"),
        # INCREMENTO REAL (sólo aplica sobre HV y SB según contrato)
        ("inc_real",  "Incremento Real Pactado (HV + SB)",   "Cláusula 43",  True,  "% sobre HV+SB",  1.0, None,    1.0, None, True,  "1% anual acumulativo sobre HV y Sueldo Base"),
        # ONE-TIME
        ("bono_term", "Bono Término Negociación Colectiva",  "Cláusula 42",  False, "CLP/persona",4200000,None,4200000,None,False, "Pago único sep-2023. NO recurrente."),
    ]

    # Convertimos a lista editable
    # Precalculamos costos actuales
    def calcular_costo_anual_base(bid, val_unit, dotacion_total=total_dot):
        """Calcula costo anual base según el tipo de beneficio."""
        d = dotacion

        if bid == "hv":
            return costo_hora_vuelo_anual()
        elif bid == "sb":
            return costo_sueldo_base_anual()
        elif bid == "gratif":
            # 25% rem. mensual, tope 4.75 IMM (~$500k × 4.75 = $2.375M/año)
            # Aprox: 8.33% del costo HV + SB (equivale a 1 mes de gratif)
            hv_total = costo_hora_vuelo_anual()
            sb_total = costo_sueldo_base_anual()
            return (hv_total + sb_total) * 0.0833
        elif bid == "asist":
            return val_unit * 12 * 0.85 * dotacion_total
        elif bid == "fiestas":
            factor_hijos = 1 + 0.30 * 0.8
            return val_unit * factor_hijos * dotacion_total
        elif bid == "navidad":
            factor_hijos = 1 + 0.30 * 0.8
            return val_unit * factor_hijos * dotacion_total
        elif bid == "bono_des":
            # Mix: 10% excepcional ($765k TC), 30% sobre esperado ($530k), 60% esperado ($405k)
            val_tc   = 0.1*765750 + 0.3*530920 + 0.6*405337
            val_jsab = 0.1*918900 + 0.3*612600 + 0.6*510500
            tc_tot   = d["TC Trainee"] + d["TC Junior"] + d["TC"] + d["TCs"]
            jsab_tot = d["JSAB"] + d["JSABs"]
            return val_tc * tc_tot + val_jsab * jsab_tot
        elif bid == "bono_prod":
            val_tc   = 674602
            val_jsab = 1180556
            tc_tot   = d["TC Trainee"] + d["TC Junior"] + d["TC"] + d["TCs"]
            jsab_tot = d["JSAB"] + d["JSABs"]
            return val_tc * tc_tot + val_jsab * jsab_tot
        elif bid == "psvnc":
            return val_unit * 1.5 * 12 * dotacion_total
        elif bid == "ext_psv":
            return val_unit * 0.5 * 12 * dotacion_total
        elif bid == "cambio_v":
            return val_unit * 0.3 * 12 * dotacion_total
        elif bid == "cancel_v":
            return val_unit * 0.2 * 12 * dotacion_total
        elif bid == "turno5":
            # TC: $58.608, JSAB: $97.678, 15% dotación/mes
            val_mix = (58608 * (d["TC Trainee"]+d["TC Junior"]+d["TC"]+d["TCs"]) +
                       97678 * (d["JSAB"]+d["JSABs"])) / max(dotacion_total,1)
            return val_mix * 0.15 * 12 * dotacion_total
        elif bid == "turno_atp":
            return val_unit * 12 * dotacion_total
        elif bid == "pre_libre":
            return val_unit * 0.4 * 12 * dotacion_total
        elif bid == "high_rank":
            # 5% vuelos con HR: diferencia HV TCs→JSABs × 5% HV mensual
            diff_hv = HV["JSABs"] - HV["TCs"]
            return diff_hv * 0.05 * 60 * 12 * (d["TCs"])
        elif bid == "escolar":
            return val_unit * 0.8 * dotacion_total
        elif bid == "matrimon":
            return val_unit * 0.03 * dotacion_total
        elif bid == "nacim":
            return val_unit * 0.05 * dotacion_total
        elif bid == "fallec":
            return val_unit * 0.02 * dotacion_total
        elif bid == "viatico_n":
            return val_unit * 8 * 12 * dotacion_total
        elif bid == "viatico_i":
            return val_unit * tc_usd * 4 * 12 * dotacion_total
        elif bid == "moviliz":
            return val_unit * 12 * 0.6 * dotacion_total
        elif bid == "bono_ant":
            # Estimado: promedio 8% remuneración para quienes cumplen años (prom. 10% dot/año)
            rem_prom = (costo_hora_vuelo_anual() + costo_sueldo_base_anual()) / max(dotacion_total,1) / 12
            return rem_prom * 0.50 * 0.10 * dotacion_total  # 50% prom × 10% dot
        elif bid == "apv":
            return val_unit * 12 * 0.70 * dotacion_total
        elif bid == "seguro_v":
            return 80000 * dotacion_total
        elif bid == "inc_real":
            # Costeamos el delta del incremento real (no el costo base)
            hv_sb = costo_hora_vuelo_anual() + costo_sueldo_base_anual()
            return hv_sb * (inc_real_pct / 100)  # 1er año
        elif bid == "bono_term":
            return val_unit * dotacion_total
        return 0

    # ── UI: tabla de beneficios con inputs ──
    st.markdown("#### 💰 Ajuste de Beneficios")

    filas = []
    for item in beneficios_def:
        bid, nombre, clausula, recurrente, unidad, cant_act, val_act, cant_new, val_new, suj_inc, notas = item
        costo_actual = calcular_costo_anual_base(bid, val_act if val_act else 0)
        filas.append({
            "id": bid,
            "Beneficio": nombre,
            "Cláusula": clausula,
            "Tipo": "Recurrente" if recurrente else "One-Time",
            "Unidad": unidad,
            "Costo Actual (CLP/año)": int(costo_actual),
            "Inc. Real?": "✓" if suj_inc else "—",
            "Notas": notas,
        })

    df_base = pd.DataFrame(filas)

    # ── Tabla con expanders por categoría ──
    categorias = {
        "💼 Remuneraciones Directas": ["hv", "sb", "gratif"],
        "🎁 Bonos Recurrentes": ["asist", "fiestas", "navidad", "bono_des", "bono_prod"],
        "✈️ Bonos Operacionales": ["psvnc", "ext_psv", "cambio_v", "cancel_v", "turno5", "turno_atp", "pre_libre", "high_rank"],
        "👨‍👩‍👧 Asignaciones": ["escolar", "matrimon", "nacim", "fallec"],
        "🏨 Beneficios en Especie": ["viatico_n", "viatico_i", "moviliz", "bono_ant", "apv", "seguro_v"],
        "📈 Incremento Real": ["inc_real"],
        "⚡ One-Time": ["bono_term"],
    }

    nuevos_valores = {}  # almacenaremos overrides del usuario

    for cat_nombre, cat_ids in categorias.items():
        with st.expander(cat_nombre, expanded=(cat_nombre in ["💼 Remuneraciones Directas", "🎁 Bonos Recurrentes"])):
            for item in beneficios_def:
                bid = item[0]
                if bid not in cat_ids:
                    continue
                nombre, clausula, recurrente, unidad, cant_act, val_act, cant_new, val_new, suj_inc, notas = item[1:]
                costo_act = calcular_costo_anual_base(bid, val_act if val_act else 0)

                st.markdown(f"**{nombre}** &nbsp; `{clausula}`")
                badge = '<span class="badge badge-recurrente">Recurrente</span>' if recurrente else '<span class="badge badge-onetime">One-Time</span>'
                st.markdown(badge, unsafe_allow_html=True)
                st.caption(notas)

                cols = st.columns([2, 2, 2, 1])

                with cols[0]:
                    # Valor unit actual (si aplica)
                    if val_act is not None:
                        v_act = st.number_input(
                            f"Valor unitario actual (CLP)", value=int(val_act),
                            step=1000, key=f"va_{bid}", label_visibility="visible"
                        )
                    else:
                        v_act = None
                        st.markdown(f"**Costo actual:** `${costo_act:,.0f}`")

                with cols[1]:
                    if val_act is not None:
                        v_new = st.number_input(
                            f"Valor unitario nuevo (CLP)", value=int(val_act),
                            step=1000, key=f"vn_{bid}", label_visibility="visible"
                        )
                    else:
                        v_new = None
                        st.markdown("*(calculado automáticamente)*")

                with cols[2]:
                    costo_new = calcular_costo_anual_base(bid, v_new if v_new else 0)
                    delta = costo_new - costo_act
                    color_d = VERDE if delta <= 0 else ROJO
                    sign = "+" if delta > 0 else ""
                    st.markdown(f"""
                    <div style="background:{BLANCO};border-left:4px solid {AZUL};border-radius:6px;padding:8px 12px;margin-top:4px">
                      <div style="font-size:11px;color:#6B7280">Costo anual actual</div>
                      <div style="font-weight:700;color:{AZUL}">${costo_act:,.0f}</div>
                      <div style="font-size:11px;color:{color_d};margin-top:2px">{sign}${delta:,.0f} vs nuevo</div>
                    </div>""", unsafe_allow_html=True)

                with cols[3]:
                    st.markdown(f"<div style='margin-top:18px;font-size:12px;color:#6B7280'>Inc. Real:<br><b>{'✓' if suj_inc else '—'}</b></div>", unsafe_allow_html=True)

                nuevos_valores[bid] = {
                    "nombre": nombre,
                    "clausula": clausula,
                    "recurrente": recurrente,
                    "costo_actual": costo_act,
                    "costo_nuevo": costo_new,
                    "suj_inc": suj_inc,
                }
                st.markdown("---")

    # ── Totales ──
    st.markdown('<div class="section-title">📊 Resumen de Costos</div>', unsafe_allow_html=True)

    total_act_rec  = sum(v["costo_actual"] for v in nuevos_valores.values() if v["recurrente"] and v["nombre"] != "Bono Término Negociación Colectiva")
    total_new_rec  = sum(v["costo_nuevo"]  for v in nuevos_valores.values() if v["recurrente"] and v["nombre"] != "Bono Término Negociación Colectiva")
    total_onetime  = sum(v["costo_actual"] for v in nuevos_valores.values() if not v["recurrente"])

    delta_rec = total_new_rec - total_act_rec

    c1, c2, c3, c4 = st.columns(4)
    def metric_card(col, label, value_clp, delta_clp=None, usd=True):
        val_usd = value_clp / tc_usd
        delta_html = ""
        if delta_clp is not None:
            sign = "+" if delta_clp > 0 else ""
            color = ROJO if delta_clp > 0 else VERDE
            delta_html = f'<div class="delta" style="color:{color}">{sign}${delta_clp/1e6:.2f}M vs. actual</div>'
        col.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">${value_clp/1e6:.1f}M CLP</div>
          <div style="font-size:13px;color:#6B7280">${val_usd/1e6:.2f}M USD</div>
          {delta_html}
        </div>""", unsafe_allow_html=True)

    metric_card(c1, "Costo Recurrente Actual / Año", total_act_rec)
    metric_card(c2, "Costo Recurrente Nuevo / Año",  total_new_rec, delta_rec)
    metric_card(c3, "Costo por Trabajador / Año (actual)", total_act_rec/max(total_dot,1))
    metric_card(c4, "One-Time (Bono Firma)", total_onetime)

    # Guardar en session state para otros tabs
    st.session_state["nuevos_valores"] = nuevos_valores
    st.session_state["total_act_rec"]  = total_act_rec
    st.session_state["total_new_rec"]  = total_new_rec
    st.session_state["total_onetime"]  = total_onetime
    st.session_state["total_dot"]      = total_dot

# ══════════════════════════════════════════════
# TAB 2 — EVOLUCIÓN ANUAL & CAGR
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Evolución del Costo Total — Punta a Punta (3 años)</div>', unsafe_allow_html=True)

    nv   = st.session_state.get("nuevos_valores", {})
    t_act = st.session_state.get("total_act_rec", 0)
    t_new = st.session_state.get("total_new_rec", 0)
    t_dot = st.session_state.get("total_dot", total_dot)

    if not nv:
        st.info("Ajusta los parámetros en la Tab 1 primero.")
    else:
        años_labels = [f"Año {i}" for i in range(anios + 1)]

        # Costo actual proyectado con incremento real
        costos_actuales = []
        costos_nuevos   = []

        for yr in range(anios + 1):
            f = factor_inc(yr, inc_real_pct)
            c_act = 0
            c_new = 0
            for bid, v in nv.items():
                if not v["recurrente"]:
                    continue
                base_act = v["costo_actual"]
                base_new = v["costo_nuevo"]
                if v["suj_inc"]:
                    c_act += base_act * f
                    c_new += base_new * f
                else:
                    c_act += base_act
                    c_new += base_new
            costos_actuales.append(c_act)
            costos_nuevos.append(c_new)

        # CAGR
        def cagr(inicio, fin, n):
            if inicio <= 0 or n == 0:
                return 0
            return ((fin / inicio) ** (1/n) - 1) * 100

        cagr_act = cagr(costos_actuales[0], costos_actuales[-1], anios)
        cagr_new = cagr(costos_nuevos[0],   costos_nuevos[-1],   anios)
        cagr_rel = cagr(costos_actuales[-1], costos_nuevos[-1],  1) if anios > 0 else 0

        # Variación punta a punta
        delta_punta = costos_nuevos[-1] - costos_actuales[-1]
        delta_punta_pct = delta_punta / costos_actuales[-1] * 100 if costos_actuales[-1] else 0

        c1, c2, c3, c4 = st.columns(4)
        def kpi(col, label, val, suffix="", color=AZUL):
            col.markdown(f"""
            <div class="metric-card">
              <div class="label">{label}</div>
              <div class="value" style="color:{color}">{val:.2f}{suffix}</div>
            </div>""", unsafe_allow_html=True)

        kpi(c1, "CAGR Contrato Actual (3a)", cagr_act, "%")
        kpi(c2, "CAGR Contrato Nuevo (3a)",  cagr_new, "%")
        kpi(c3, "Δ Costo Año 3 (nuevo vs actual)", delta_punta_pct, "%", ROJO if delta_punta_pct>0 else VERDE)
        kpi(c4, "Δ Absoluto Año 3", delta_punta/1e6, "M CLP", ROJO if delta_punta>0 else VERDE)

        # Gráfico de barras agrupadas + líneas
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Contrato Actual",
            x=años_labels,
            y=[c/1e6 for c in costos_actuales],
            marker_color=AZUL,
            opacity=0.85,
        ))
        fig.add_trace(go.Bar(
            name="Contrato Nuevo",
            x=años_labels,
            y=[c/1e6 for c in costos_nuevos],
            marker_color=ROJO,
            opacity=0.85,
        ))
        fig.add_trace(go.Scatter(
            name="Δ incremental",
            x=años_labels,
            y=[(n-a)/1e6 for n,a in zip(costos_nuevos, costos_actuales)],
            mode="lines+markers",
            line=dict(color=AMBAR, width=2, dash="dot"),
            yaxis="y2"
        ))
        fig.update_layout(
            title="Costo Recurrente Anual — Actual vs. Nuevo Contrato",
            barmode="group",
            yaxis=dict(title="CLP Millones"),
            yaxis2=dict(title="Δ CLP Millones", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.08),
            plot_bgcolor=BLANCO,
            paper_bgcolor=GRIS,
            font=dict(color=AZUL),
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla punta a punta
        df_pp = pd.DataFrame({
            "Año": años_labels,
            "Costo Actual (CLP M)": [f"${c/1e6:.2f}M" for c in costos_actuales],
            "Costo Nuevo (CLP M)":  [f"${c/1e6:.2f}M" for c in costos_nuevos],
            "Δ (CLP M)":           [f"${(n-a)/1e6:+.2f}M" for n,a in zip(costos_nuevos,costos_actuales)],
            "Costo Actual (USD M)": [f"${c/tc_usd/1e6:.2f}M" for c in costos_actuales],
            "Costo Nuevo (USD M)":  [f"${c/tc_usd/1e6:.2f}M" for c in costos_nuevos],
        })
        st.dataframe(df_pp, use_container_width=True, hide_index=True)

        # Gráfico waterfall por categoría
        st.markdown("#### Variación por Categoría de Beneficio (Año 1 vs Año 3)")
        cat_names, cat_deltas = [], []
        cat_map = {
            "Rem. Directas":    ["hv","sb","gratif"],
            "Bonos Recurrentes":["asist","fiestas","navidad","bono_des","bono_prod"],
            "Bonos Operac.":    ["psvnc","ext_psv","cambio_v","cancel_v","turno5","turno_atp","pre_libre","high_rank"],
            "Asignaciones":     ["escolar","matrimon","nacim","fallec"],
            "Benef. Especie":   ["viatico_n","viatico_i","moviliz","bono_ant","apv","seguro_v"],
            "Inc. Real":        ["inc_real"],
        }
        for cname, cids in cat_map.items():
            delta_cat = sum(
                (nv[bid]["costo_nuevo"] - nv[bid]["costo_actual"])
                for bid in cids if bid in nv
            )
            cat_names.append(cname)
            cat_deltas.append(delta_cat / 1e6)

        colors_wf = [ROJO if d > 0 else VERDE for d in cat_deltas]
        fig2 = go.Figure(go.Bar(
            x=cat_names, y=cat_deltas,
            marker_color=colors_wf,
            text=[f"${d:+.1f}M" for d in cat_deltas],
            textposition="outside"
        ))
        fig2.update_layout(
            title="Variación de Costo Nuevo vs. Actual por Categoría (CLP M)",
            yaxis_title="CLP Millones",
            plot_bgcolor=BLANCO, paper_bgcolor=GRIS,
            font=dict(color=AZUL), height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Composición del costo en donut
        st.markdown("#### Composición del Costo Anual Actual")
        pie_labels, pie_values = [], []
        for cname, cids in cat_map.items():
            val = sum(nv[bid]["costo_actual"] for bid in cids if bid in nv)
            if val > 0:
                pie_labels.append(cname)
                pie_values.append(val)

        colors_pie = [AZUL, ROJO, "#4B6FD4", "#E05C6E", "#7B93D9", AMBAR]
        fig3 = go.Figure(go.Pie(
            labels=pie_labels, values=pie_values,
            hole=0.5,
            marker_colors=colors_pie,
            textinfo="label+percent",
            insidetextorientation="radial"
        ))
        fig3.update_layout(
            title="Composición Costo Recurrente Actual",
            paper_bgcolor=GRIS, font=dict(color=AZUL),
            height=380,
            annotations=[dict(text=f"${sum(pie_values)/1e6:.0f}M", x=0.5, y=0.5,
                               font_size=16, font_color=AZUL, showarrow=False)]
        )
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — SIMULADOR NUEVO CONTRATO
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Simulador de Propuesta — Nuevo Contrato</div>', unsafe_allow_html=True)
    st.caption("Modifica los parámetros clave para simular el costo de un contrato nuevo. Los valores 'nuevo' se toman del Tab 1.")

    nv = st.session_state.get("nuevos_valores", {})
    if not nv:
        st.info("Completa el Tab 1 primero.")
    else:
        col_sim1, col_sim2 = st.columns([2,1])

        with col_sim1:
            st.markdown("#### Parámetros de Negociación")

            # Incremento adicional sobre HV
            inc_hv = st.slider("Incremento adicional sobre Hora de Vuelo (%)", 0.0, 20.0, 0.0, 0.5)
            inc_sb = st.slider("Incremento adicional sobre Sueldo Base (%)",   0.0, 20.0, 0.0, 0.5)
            inc_bonos = st.slider("Incremento general sobre bonos fijos (%)",  0.0, 20.0, 0.0, 0.5)
            nueva_dot = st.slider("Variación de dotación (%)", -20, 30, 0, 1)

            # Nuevos beneficios propuestos
            st.markdown("#### Nuevos Beneficios Propuestos")
            nuevo_ben1_nombre = st.text_input("Nombre beneficio nuevo 1", "Bono Bienestar")
            nuevo_ben1_valor  = st.number_input("Valor anual total (CLP)", value=0, step=100000, key="nb1")
            nuevo_ben2_nombre = st.text_input("Nombre beneficio nuevo 2", "")
            nuevo_ben2_valor  = st.number_input("Valor anual total (CLP)", value=0, step=100000, key="nb2")

        with col_sim2:
            st.markdown("#### Resultado Simulación")

            # Calculamos el costo nuevo simulado
            dot_factor = 1 + nueva_dot / 100
            hv_base  = nv.get("hv", {}).get("costo_actual", 0) * (1 + inc_hv/100) * dot_factor
            sb_base  = nv.get("sb", {}).get("costo_actual", 0) * (1 + inc_sb/100) * dot_factor
            grat_sim = (hv_base + sb_base) * 0.0833

            costo_sim = hv_base + sb_base + grat_sim
            for bid, v in nv.items():
                if bid in ["hv","sb","gratif"]:
                    continue
                if not v["recurrente"]:
                    continue
                if bid in ["bono_des","bono_prod","asist"]:
                    costo_sim += v["costo_actual"] * (1 + inc_bonos/100) * dot_factor
                else:
                    costo_sim += v["costo_actual"] * dot_factor

            costo_sim += nuevo_ben1_valor + nuevo_ben2_valor

            t_act = st.session_state.get("total_act_rec", 1)
            delta_sim = costo_sim - t_act
            delta_sim_pct = delta_sim / t_act * 100

            cagr_sim = cagr(t_act, costo_sim * (factor_inc(anios, inc_real_pct)), anios) if anios > 0 else 0

            def kpi_sim(label, val_clp, suffix="CLP"):
                val_usd = val_clp / tc_usd
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{label}</div>
                  <div class="value">${val_clp/1e6:.2f}M CLP</div>
                  <div style="font-size:12px;color:#6B7280">${val_usd/1e6:.2f}M USD</div>
                </div>""", unsafe_allow_html=True)

            kpi_sim("Costo Actual Recurrente", t_act)
            kpi_sim("Costo Simulado Nuevo", costo_sim)

            sign = "+" if delta_sim > 0 else ""
            color_d = ROJO if delta_sim > 0 else VERDE
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Variación vs. Actual</div>
              <div class="value" style="color:{color_d}">{sign}{delta_sim_pct:.2f}%</div>
              <div style="font-size:13px;color:{color_d}">{sign}${delta_sim/1e6:.2f}M CLP/año</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card">
              <div class="label">CAGR Simulado ({anios}a)</div>
              <div class="value">{cagr_sim:.2f}%</div>
              <div style="font-size:12px;color:#6B7280">Incluye inc. real {inc_real_pct}%/a</div>
            </div>""", unsafe_allow_html=True)

            costo_punta_sim = costo_sim * factor_inc(anios, inc_real_pct)
            costo_punta_act = t_act    * factor_inc(anios, inc_real_pct)
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Costo Año {anios} (punta)</div>
              <div class="value">${costo_punta_sim/1e6:.2f}M CLP</div>
              <div style="font-size:13px;color:{ROJO}">${(costo_punta_sim - costo_punta_act)/1e6:+.2f}M vs. actual</div>
            </div>""", unsafe_allow_html=True)

        # Gráfico comparativo simulación
        años_l = [f"Año {i}" for i in range(anios+1)]
        c_act_yr = [t_act   * factor_inc(yr, inc_real_pct) for yr in range(anios+1)]
        c_sim_yr = [costo_sim * factor_inc(yr, inc_real_pct) for yr in range(anios+1)]

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=años_l, y=[c/1e6 for c in c_act_yr],
            name="Contrato Actual", mode="lines+markers",
            line=dict(color=AZUL, width=3), marker=dict(size=8)))
        fig_sim.add_trace(go.Scatter(x=años_l, y=[c/1e6 for c in c_sim_yr],
            name="Contrato Simulado", mode="lines+markers",
            line=dict(color=ROJO, width=3, dash="dash"), marker=dict(size=8)))
        fig_sim.update_layout(
            title="Trayectoria de Costo — Actual vs. Propuesta Simulada",
            yaxis_title="CLP Millones",
            plot_bgcolor=BLANCO, paper_bgcolor=GRIS,
            font=dict(color=AZUL), height=380,
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig_sim, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Resumen Ejecutivo</div>', unsafe_allow_html=True)

    nv    = st.session_state.get("nuevos_valores", {})
    t_act = st.session_state.get("total_act_rec", 0)
    t_new = st.session_state.get("total_new_rec", 0)
    t_one = st.session_state.get("total_onetime", 0)
    t_dot = st.session_state.get("total_dot", total_dot)

    if not nv:
        st.info("Completa los parámetros en la Tab 1.")
    else:
        st.markdown(f"""
        <div style="background:{BLANCO};border-radius:10px;padding:20px 28px;box-shadow:0 1px 6px rgba(0,0,0,0.07);margin-bottom:16px">
          <h3 style="color:{AZUL};margin-top:0">Contrato Colectivo · STCLE / Transporte Aéreo S.A.</h3>
          <p style="color:#4B5563">Período: 01/09/2023 – 31/08/2026 &nbsp;|&nbsp; Trabajadores: <b>{t_dot}</b> &nbsp;|&nbsp; TC: $980 CLP/USD</p>
          <hr style="border-color:#E5E7EB">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:12px">
            <div>
              <div style="font-size:12px;color:#6B7280;text-transform:uppercase">Costo recurrente anual actual</div>
              <div style="font-size:24px;font-weight:700;color:{AZUL}">${t_act/1e6:.1f}M CLP</div>
              <div style="font-size:13px;color:#6B7280">${t_act/tc_usd/1e6:.2f}M USD</div>
            </div>
            <div>
              <div style="font-size:12px;color:#6B7280;text-transform:uppercase">Costo por trabajador/año</div>
              <div style="font-size:24px;font-weight:700;color:{AZUL}">${t_act/max(t_dot,1)/1e6:.2f}M CLP</div>
              <div style="font-size:13px;color:#6B7280">${t_act/max(t_dot,1)/tc_usd/1e3:.0f}K USD</div>
            </div>
            <div>
              <div style="font-size:12px;color:#6B7280;text-transform:uppercase">One-Time (bono firma)</div>
              <div style="font-size:24px;font-weight:700;color:{ROJO}">${t_one/1e6:.1f}M CLP</div>
              <div style="font-size:13px;color:#6B7280">${t_one/tc_usd/1e6:.2f}M USD</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabla resumen por beneficio
        filas_res = []
        for bid, v in nv.items():
            delta = v["costo_nuevo"] - v["costo_actual"]
            filas_res.append({
                "Beneficio":           v["nombre"],
                "Cláusula":            v["clausula"],
                "Tipo":                "Recurrente" if v["recurrente"] else "One-Time",
                "Costo Actual CLP/año":f"${v['costo_actual']:,.0f}",
                "Costo Nuevo CLP/año": f"${v['costo_nuevo']:,.0f}",
                "Δ CLP/año":           f"${delta:+,.0f}",
                "Δ %":                 f"{delta/v['costo_actual']*100:+.1f}%" if v["costo_actual"] else "N/A",
                "Inc. Real":           "✓" if v["suj_inc"] else "—",
            })

        df_res = pd.DataFrame(filas_res)
        st.dataframe(df_res, use_container_width=True, hide_index=True, height=500)

        # Totales finales
        st.markdown("---")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Total recurrente actual / año</div>
              <div class="value">${t_act/1e6:.2f}M CLP &nbsp;|&nbsp; ${t_act/tc_usd/1e6:.2f}M USD</div>
              <div class="delta">Costo por trabajador: ${t_act/max(t_dot,1)/1e3:,.0f}K CLP</div>
            </div>""", unsafe_allow_html=True)
        with col_f2:
            delta_tot = t_new - t_act
            sign = "+" if delta_tot > 0 else ""
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Total recurrente nuevo / año</div>
              <div class="value">${t_new/1e6:.2f}M CLP &nbsp;|&nbsp; ${t_new/tc_usd/1e6:.2f}M USD</div>
              <div class="delta {'delta-neg' if delta_tot>0 else 'delta-pos'}">{sign}${delta_tot/1e6:.2f}M CLP vs. actual</div>
            </div>""", unsafe_allow_html=True)

        # CAGR final
        cagr_final = cagr(t_act, t_act * factor_inc(anios, inc_real_pct), anios)
        st.markdown(f"""
        <div style="background:{AZUL};color:white;border-radius:10px;padding:16px 24px;margin-top:12px;display:flex;gap:40px;align-items:center">
          <div><div style="font-size:11px;opacity:.75">CAGR Contrato Actual ({anios}a)</div>
               <div style="font-size:22px;font-weight:700">{cagr_final:.2f}%</div></div>
          <div><div style="font-size:11px;opacity:.75">Inc. Real pactado/año</div>
               <div style="font-size:22px;font-weight:700">{inc_real_pct:.1f}%</div></div>
          <div><div style="font-size:11px;opacity:.75">Período contrato</div>
               <div style="font-size:22px;font-weight:700">36 meses</div></div>
          <div><div style="font-size:11px;opacity:.75">TC USD/CLP (promedio 2025)</div>
               <div style="font-size:22px;font-weight:700">${tc_usd:,}</div></div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown(f"""
<div style="margin-top:40px;padding:12px 0;border-top:2px solid #E5E7EB;text-align:center;font-size:11px;color:#9CA3AF">
  STCLE · Sindicato Tripulantes de Cabina LAN Express &nbsp;|&nbsp;
  Modelo de costeo CC · Uso interno · {anios} años de vigencia proyectados
</div>
""", unsafe_allow_html=True)
