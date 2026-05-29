import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

ROJO   = "#C8102E"
AZUL   = "#1B2A6B"
AZUL_C = "#2E4BAD"
GRIS   = "#F4F5F7"
BLANCO = "#FFFFFF"
VERDE  = "#1A7A4A"
AMBAR  = "#D97706"

# ─────────────────────────────────────────────
# CSS — fix sidebar: solo labels blancos, inputs con fondo blanco/texto oscuro
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {GRIS}; }}

  /* Sidebar fondo */
  [data-testid="stSidebar"] {{ background-color: {AZUL}; }}

  /* Solo los LABELS del sidebar en blanco */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] h4,
  [data-testid="stSidebar"] .stCaption,
  [data-testid="stSidebar"] .stMetricLabel,
  [data-testid="stSidebar"] .stMetricValue
    {{ color: #E8ECF8 !important; }}

  /* Inputs del sidebar: fondo blanco, texto oscuro */
  [data-testid="stSidebar"] input[type="number"],
  [data-testid="stSidebar"] input[type="text"] {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #6B80C4 !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {{
    background-color: #FFFFFF !important;
  }}
  /* Slider track */
  [data-testid="stSidebar"] .stSlider {{ filter: brightness(1.3); }}

  /* Títulos área principal */
  h1 {{ color: {AZUL}; font-family: 'Segoe UI', sans-serif; }}
  h2, h3, h4 {{ color: {AZUL}; }}

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

  /* Section divider */
  .section-title {{
    font-size:15px; font-weight:700; color:{AZUL};
    border-bottom: 2px solid {ROJO};
    padding-bottom: 4px; margin: 16px 0 10px 0;
    text-transform: uppercase; letter-spacing:.5px;
  }}

  /* Badge */
  .badge {{ display:inline-block; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; }}
  .badge-rec {{ background:#DBEAFE; color:#1E40AF; }}
  .badge-one {{ background:#FEE2E2; color:#991B1B; }}

  /* Caja beneficio */
  .ben-box {{
    background:{BLANCO};
    border-radius:10px;
    padding:14px 18px;
    margin-bottom:10px;
    box-shadow:0 1px 3px rgba(0,0,0,0.07);
    border-top: 3px solid {AZUL};
  }}
  .ben-title {{ font-weight:700; color:{AZUL}; font-size:14px; }}
  .ben-nota  {{ font-size:11px; color:#6B7280; margin-top:2px; }}

  /* Costo card inline */
  .cost-display {{
    background: {GRIS};
    border-radius:8px;
    padding:10px 14px;
    border-left:4px solid {AZUL};
  }}
  .cost-display .lbl {{ font-size:11px; color:#6B7280; }}
  .cost-display .val {{ font-size:18px; font-weight:700; color:{AZUL}; }}
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
    <p>Sindicato de Tripulantes de Cabina LAN Express &nbsp;·&nbsp; Vigencia 01/09/2023 – 31/08/2026</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Parámetros Globales")
    st.markdown("---")

    st.markdown("#### 💱 Tipo de Cambio")
    tc_usd = st.number_input("CLP / USD", value=980, step=5, min_value=700, max_value=1500)

    st.markdown("#### 📅 Horizonte")
    anios = st.slider("Años del contrato", 1, 3, 3)

    st.markdown("#### 📈 Incremento Real (% anual)")
    st.caption("Sobre HV y SB según contrato. Excluye IPC.")
    inc_real_pct = st.number_input("Incremento real %", value=1.0, step=0.5,
                                    min_value=0.0, max_value=10.0)

    st.markdown("---")
    st.markdown("#### 👥 Dotación por Subcategoría")
    n_trainee = st.number_input("TC Trainee",      value=10,  min_value=0, step=1)
    n_tcj     = st.number_input("TC Junior",        value=25,  min_value=0, step=1)
    n_tc      = st.number_input("TC (Senior)",      value=60,  min_value=0, step=1)
    n_tcs     = st.number_input("TC Senior (TCs)",  value=45,  min_value=0, step=1)
    n_jsab    = st.number_input("Jefe SAB",         value=35,  min_value=0, step=1)
    n_jsabs   = st.number_input("Jefe SAB Senior",  value=18,  min_value=0, step=1)
    total_dot = n_trainee + n_tcj + n_tc + n_tcs + n_jsab + n_jsabs
    st.metric("Total dotación", total_dot)

    st.markdown("---")
    st.markdown("#### ✈️ Productividad (HV/mes promedio)")
    hv_trainee = st.number_input("HV/mes Trainee",  value=55.0, step=1.0)
    hv_tcj     = st.number_input("HV/mes TCj",      value=57.0, step=1.0)
    hv_tc      = st.number_input("HV/mes TC",       value=60.0, step=1.0)
    hv_tcs     = st.number_input("HV/mes TCs",      value=62.0, step=1.0)
    hv_jsab    = st.number_input("HV/mes JSAB",     value=60.0, step=1.0)
    hv_jsabs   = st.number_input("HV/mes JSABs",    value=60.0, step=1.0)

# ─────────────────────────────────────────────
# DATOS BASE
# ─────────────────────────────────────────────
HV_BASE = {"TC Trainee": 3579, "TC Junior": 3937, "TC": 7119,
           "TCs": 11051, "JSAB": 16018, "JSABs": 19871}
SB_BASE = {"TC Trainee": 500000, "TC Junior": 460000, "TC": 460000,
           "TCs": 460000, "JSAB": 483575, "JSABs": 559136}

dotacion = {"TC Trainee": n_trainee, "TC Junior": n_tcj, "TC": n_tc,
            "TCs": n_tcs, "JSAB": n_jsab, "JSABs": n_jsabs}
hv_mes   = {"TC Trainee": hv_trainee, "TC Junior": hv_tcj, "TC": hv_tc,
            "TCs": hv_tcs, "JSAB": hv_jsab, "JSABs": hv_jsabs}
subcat   = list(HV_BASE.keys())

def factor_inc(yr, pct): return (1 + pct/100) ** yr

def cagr(ini, fin, n):
    if ini <= 0 or n == 0: return 0.0
    return ((fin/ini)**(1/n) - 1) * 100

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Costeo por Beneficio",
    "📈 Evolución Anual & CAGR",
    "🔬 Simulador Nuevo Contrato",
    "📋 Resumen Ejecutivo",
])

# ══════════════════════════════════════════════
# TAB 1 — COSTEO POR BENEFICIO
# Cada beneficio tiene inputs editables:
#   - Valor unitario actual / nuevo  (CLP o USD)
#   - Cantidad / frecuencia actual / nueva  (ej. eventos/mes, % personas, nº hijos)
# El costo = f(valor, cantidad, dotación)
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Variables Remuneracionales — Ajuste Actual vs. Nuevo</div>',
                unsafe_allow_html=True)
    st.caption("Cada beneficio expone sus parámetros editables. "
               "Columna **Actual** = contrato vigente · Columna **Nuevo** = propuesta. "
               "El costo anual se recalcula en tiempo real.")

    nuevos_valores = {}  # {bid: {nombre, clausula, recurrente, costo_actual, costo_nuevo, suj_inc}}

    # ── Helpers de renderizado ──────────────────
    def costo_card(label_act, c_act, label_new, c_new, suj_inc):
        delta = c_new - c_act
        sign  = "+" if delta >= 0 else ""
        col_d = ROJO if delta > 0 else (VERDE if delta < 0 else "#6B7280")
        c_act_usd = c_act / tc_usd
        c_new_usd = c_new / tc_usd
        st.markdown(f"""
        <div class="cost-display" style="margin-top:6px">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            <div>
              <div class="lbl">{label_act}</div>
              <div class="val">${c_act/1e6:.3f}M CLP</div>
              <div style="font-size:11px;color:#9CA3AF">${c_act_usd/1e3:.1f}K USD</div>
            </div>
            <div>
              <div class="lbl">{label_new}</div>
              <div class="val" style="color:{ROJO if delta>0 else AZUL}">${c_new/1e6:.3f}M CLP</div>
              <div style="font-size:11px;color:#9CA3AF">${c_new_usd/1e3:.1f}K USD</div>
            </div>
          </div>
          <div style="margin-top:6px;font-size:12px;color:{col_d};font-weight:600">
            Δ {sign}${delta/1e3:,.1f}K CLP/año &nbsp;·&nbsp;
            Inc. Real aplicable: {"✅ Sí" if suj_inc else "❌ No"}
          </div>
        </div>""", unsafe_allow_html=True)

    def ben_header(nombre, clausula, recurrente, notas):
        badge = ('<span class="badge badge-rec">Recurrente</span>'
                 if recurrente else '<span class="badge badge-one">One-Time</span>')
        st.markdown(f"""
        <div style="margin-bottom:4px">
          <span class="ben-title">{nombre}</span>
          &nbsp;<code style="font-size:11px;background:#EEF2FF;color:{AZUL};
                 padding:1px 6px;border-radius:4px">{clausula}</code>
          &nbsp;{badge}
        </div>
        <div class="ben-nota">{notas}</div>""", unsafe_allow_html=True)

    # ════════════════════════════════════
    # CATEGORÍA: REMUNERACIONES DIRECTAS
    # ════════════════════════════════════
    with st.expander("💼 Remuneraciones Directas", expanded=True):

        # ── Horas de Vuelo ──────────────────────────────────
        ben_header("Horas de Vuelo", "Cláusula 26", True,
                   "Valor HV × max(HV_mes, 55 piso) × 12 meses × dotación por subcategoría")
        st.markdown("**Valores de Hora de Vuelo por subcategoría (CLP bruto)**")
        col_hdr = st.columns([2,1,1,1,1,1,1])
        col_hdr[0].markdown("**Subcategoría**")
        col_hdr[1].markdown("**Dotación**")
        col_hdr[2].markdown("**HV actual**")
        col_hdr[3].markdown("**HV nuevo**")
        col_hdr[4].markdown("**HV/mes**")
        col_hdr[5].markdown("**C. actual (M)**")
        col_hdr[6].markdown("**C. nuevo (M)**")

        hv_act_vals, hv_new_vals = {}, {}
        c_hv_act = c_hv_new = 0
        for sc in subcat:
            cols_hv = st.columns([2,1,1,1,1,1,1])
            cols_hv[0].markdown(f"`{sc}`")
            cols_hv[1].markdown(f"{dotacion[sc]}")
            hv_a = cols_hv[2].number_input("", value=HV_BASE[sc], step=100,
                                            key=f"hv_a_{sc}", label_visibility="collapsed")
            hv_n = cols_hv[3].number_input("", value=HV_BASE[sc], step=100,
                                            key=f"hv_n_{sc}", label_visibility="collapsed")
            hv_real = max(hv_mes[sc], 55)
            ca = hv_a * hv_real * 12 * dotacion[sc]
            cn = hv_n * hv_real * 12 * dotacion[sc]
            cols_hv[4].markdown(f"{hv_real:.0f}")
            cols_hv[5].markdown(f"${ca/1e6:.3f}")
            cols_hv[6].markdown(f"${cn/1e6:.3f}")
            hv_act_vals[sc] = hv_a; hv_new_vals[sc] = hv_n
            c_hv_act += ca; c_hv_new += cn

        costo_card("Costo HV Actual/año", c_hv_act, "Costo HV Nuevo/año", c_hv_new, True)
        nuevos_valores["hv"] = dict(nombre="Horas de Vuelo", clausula="Cláusula 26",
            recurrente=True, costo_actual=c_hv_act, costo_nuevo=c_hv_new, suj_inc=True)
        st.markdown("---")

        # ── Sueldo Base ────────────────────────────────────
        ben_header("Sueldo Base Mensual", "Cláusula 26", True,
                   "Sueldo base fijo × 12 meses × dotación por subcategoría")
        col_hdr2 = st.columns([2,1,1,1,1,1])
        col_hdr2[0].markdown("**Subcategoría**"); col_hdr2[1].markdown("**Dotación**")
        col_hdr2[2].markdown("**SB actual**");    col_hdr2[3].markdown("**SB nuevo**")
        col_hdr2[4].markdown("**C.Act (M)**");    col_hdr2[5].markdown("**C.Nvo (M)**")

        c_sb_act = c_sb_new = 0
        for sc in subcat:
            cols_sb = st.columns([2,1,1,1,1,1])
            cols_sb[0].markdown(f"`{sc}`"); cols_sb[1].markdown(f"{dotacion[sc]}")
            sb_a = cols_sb[2].number_input("", value=SB_BASE[sc], step=5000,
                                            key=f"sb_a_{sc}", label_visibility="collapsed")
            sb_n = cols_sb[3].number_input("", value=SB_BASE[sc], step=5000,
                                            key=f"sb_n_{sc}", label_visibility="collapsed")
            ca = sb_a * 12 * dotacion[sc]; cn = sb_n * 12 * dotacion[sc]
            cols_sb[4].markdown(f"${ca/1e6:.3f}"); cols_sb[5].markdown(f"${cn/1e6:.3f}")
            c_sb_act += ca; c_sb_new += cn

        costo_card("Costo SB Actual/año", c_sb_act, "Costo SB Nuevo/año", c_sb_new, True)
        nuevos_valores["sb"] = dict(nombre="Sueldo Base", clausula="Cláusula 26",
            recurrente=True, costo_actual=c_sb_act, costo_nuevo=c_sb_new, suj_inc=True)
        st.markdown("---")

        # ── Gratificación ──────────────────────────────────
        ben_header("Gratificación Legal 25%", "Cláusula 4", True,
                   "25% remuneración mensual legal. Aprox. 1/12 del total HV+SB anual.")
        c1g, c2g, c3g, c4g = st.columns(4)
        pct_grat_a = c1g.number_input("% Gratif. actual", value=8.33, step=0.1,
                                       min_value=0.0, max_value=25.0, key="grat_a")
        pct_grat_n = c2g.number_input("% Gratif. nuevo",  value=8.33, step=0.1,
                                       min_value=0.0, max_value=25.0, key="grat_n")
        c_grat_act = (c_hv_act + c_sb_act) * pct_grat_a / 100
        c_grat_new = (c_hv_new + c_sb_new) * pct_grat_n / 100
        costo_card("Costo Gratif. Actual/año", c_grat_act, "Costo Gratif. Nuevo/año", c_grat_new, True)
        nuevos_valores["gratif"] = dict(nombre="Gratificación Legal 25%", clausula="Cláusula 4",
            recurrente=True, costo_actual=c_grat_act, costo_nuevo=c_grat_new, suj_inc=True)

    # ════════════════════════════════════
    # CATEGORÍA: BONOS RECURRENTES
    # ════════════════════════════════════
    with st.expander("🎁 Bonos Recurrentes", expanded=True):

        bonos_rec = [
            ("asist",    "Bono 100% Asistencia",           "Cláusula 28a",
             "Mensual. % trabajadores que lo perciben × valor × 12.",
             169349, 169349, 0.85, 0.85, "% personas que perciben", True),
            ("fiestas",  "Bono Fiestas Patrias",            "Cláusula 28b",
             "Pago sep. Valor base + 30% por hijo. Promedio 0.8 hijos/trabajador.",
             138983, 138983, 0.8, 0.8, "Nº hijos promedio/trabajador", False),
            ("navidad",  "Bono Navidad",                    "Cláusula 28c",
             "Pago dic. Valor base + 30% por hijo. Promedio 0.8 hijos/trabajador.",
             169872, 169872, 0.8, 0.8, "Nº hijos promedio/trabajador", False),
            ("bono_des", "Bono Desempeño TC (mix ponderado)","Cláusula 37",
             "Pago julio. Mix: 10% excepcional, 30% sobre esperado, 60% esperado.",
             int(0.1*765750 + 0.3*530920 + 0.6*405337),
             int(0.1*765750 + 0.3*530920 + 0.6*405337),
             1.0, 1.0, "Factor cobertura (1=100% dotación TC)", False),
            ("bono_prod","Bono Productividad TC (factor 1.0)","Cláusula 37",
             "Pago mar. Factor 1.0 (100% cumplimiento presupuesto). TC: $674.602, JSAB: $1.180.556.",
             674602, 674602, 1.0, 1.0, "Factor de cumplimiento (0–1.2)", False),
        ]

        for bid, nombre, clausula, notas, val_a_def, val_n_def, cant_a_def, cant_n_def, cant_lbl, suj_inc in bonos_rec:
            ben_header(nombre, clausula, True, notas)
            b1, b2, b3, b4 = st.columns(4)

            val_a = b1.number_input(f"Valor unit. actual (CLP)", value=val_a_def,
                                     step=1000, key=f"va_{bid}")
            val_n = b2.number_input(f"Valor unit. nuevo (CLP)",  value=val_n_def,
                                     step=1000, key=f"vn_{bid}")

            if bid in ("asist",):
                cant_a = b3.number_input(f"% personas (actual, 0–1)", value=cant_a_def,
                                          step=0.05, min_value=0.0, max_value=1.0, key=f"ca_{bid}")
                cant_n = b4.number_input(f"% personas (nuevo, 0–1)",  value=cant_n_def,
                                          step=0.05, min_value=0.0, max_value=1.0, key=f"cn_{bid}")
                c_act = val_a * 12 * cant_a * total_dot
                c_new = val_n * 12 * cant_n * total_dot
            elif bid in ("fiestas","navidad"):
                cant_a = b3.number_input(f"Hijos prom. actual",  value=cant_a_def,
                                          step=0.1, min_value=0.0, key=f"ca_{bid}")
                cant_n = b4.number_input(f"Hijos prom. nuevo",   value=cant_n_def,
                                          step=0.1, min_value=0.0, key=f"cn_{bid}")
                c_act = val_a * (1 + 0.30*cant_a) * total_dot
                c_new = val_n * (1 + 0.30*cant_n) * total_dot
            elif bid == "bono_des":
                # Para JSAB el valor es diferente
                val_a_jsab = b3.number_input("Valor JSAB actual (CLP)",
                    value=int(0.1*918900+0.3*612600+0.6*510500), step=1000, key=f"va_jsab_{bid}")
                val_n_jsab = b4.number_input("Valor JSAB nuevo (CLP)",
                    value=int(0.1*918900+0.3*612600+0.6*510500), step=1000, key=f"vn_jsab_{bid}")
                tc_tot = n_trainee+n_tcj+n_tc+n_tcs
                jsab_tot = n_jsab+n_jsabs
                c_act = val_a*tc_tot + val_a_jsab*jsab_tot
                c_new = val_n*tc_tot + val_n_jsab*jsab_tot
            elif bid == "bono_prod":
                val_a_jsab2 = b3.number_input("Valor JSAB actual (CLP)",
                    value=1180556, step=1000, key=f"va_jsab_{bid}")
                val_n_jsab2 = b4.number_input("Valor JSAB nuevo (CLP)",
                    value=1180556, step=1000, key=f"vn_jsab_{bid}")
                tc_tot = n_trainee+n_tcj+n_tc+n_tcs
                jsab_tot = n_jsab+n_jsabs
                c_act = val_a*tc_tot + val_a_jsab2*jsab_tot
                c_new = val_n*tc_tot + val_n_jsab2*jsab_tot
            else:
                c_act = val_a * cant_a * total_dot
                c_new = val_n * cant_n * total_dot

            costo_card("Costo Actual/año", c_act, "Costo Nuevo/año", c_new, suj_inc)
            nuevos_valores[bid] = dict(nombre=nombre, clausula=clausula,
                recurrente=True, costo_actual=c_act, costo_nuevo=c_new, suj_inc=suj_inc)
            st.markdown("---")

    # ════════════════════════════════════
    # CATEGORÍA: BONOS OPERACIONALES
    # ════════════════════════════════════
    with st.expander("✈️ Bonos Operacionales (por evento)", expanded=False):

        bonos_op = [
            ("psvnc",    "Bono Noche Consecutiva (PSVNC)", "Cláusula 17/1.5",
             "Por cada evento PSVNC. Estimado: frecuencia eventos/mes/persona.",
             52094, 52094, 1.5, 1.5, "Eventos/mes/persona", False),
            ("ext_psv",  "Bono Extensión PSV 12→14h",      "Cláusula 23",
             "1er evento: $79.029; 2do: $39.516; 3ro+: $69.149. Se usa valor 1er evento como base.",
             79029, 79029, 0.5, 0.5, "Eventos/mes/persona", False),
            ("cambio_v", "Bono Cambio de Vuelo",            "Cláusula 13d",
             "Al cambiar vuelo estando en aeropuerto, móvil o posta.",
             119819, 119819, 0.3, 0.3, "Eventos/mes/persona", False),
            ("cancel_v", "Bono Cancelación (espera >3h)",   "Cláusula 13b",
             "Cuando se cancela el primer tramo y espera supera 3 horas.",
             200469, 200469, 0.2, 0.2, "Eventos/mes/persona", False),
            ("turno_atp","Bono Turno Aeropuerto (1er turno)","Cláusula 17/4.2",
             "1er turno mes: $54.700 | desde 2do: $68.377. Se usa valor 1er turno.",
             54700, 54700, 1.0, 1.0, "Turnos ATO/mes/persona", False),
            ("pre_libre","Bono PSV previo libre >22:00",    "Cláusula 17/1.6",
             "Cuando PSV termina entre 22:00 y 23:59 previo a días libres.",
             64196, 64196, 0.4, 0.4, "Eventos/mes/persona", False),
        ]

        for bid, nombre, clausula, notas, val_a_def, val_n_def, frec_a, frec_n, frec_lbl, suj_inc in bonos_op:
            ben_header(nombre, clausula, True, notas)
            o1, o2, o3, o4 = st.columns(4)
            val_a  = o1.number_input("Valor unitario actual (CLP)", value=val_a_def,
                                      step=500, key=f"va_{bid}")
            val_n  = o2.number_input("Valor unitario nuevo (CLP)",  value=val_n_def,
                                      step=500, key=f"vn_{bid}")
            freq_a = o3.number_input(f"{frec_lbl} (actual)", value=frec_a,
                                      step=0.1, min_value=0.0, key=f"fa_{bid}")
            freq_n = o4.number_input(f"{frec_lbl} (nuevo)",  value=frec_n,
                                      step=0.1, min_value=0.0, key=f"fn_{bid}")
            c_act = val_a * freq_a * 12 * total_dot
            c_new = val_n * freq_n * 12 * total_dot
            costo_card("Costo Actual/año", c_act, "Costo Nuevo/año", c_new, suj_inc)
            nuevos_valores[bid] = dict(nombre=nombre, clausula=clausula,
                recurrente=True, costo_actual=c_act, costo_nuevo=c_new, suj_inc=suj_inc)
            st.markdown("---")

        # Bono 5° turno — separado porque TC y JSAB tienen valores distintos
        ben_header("Bono 5° Turno en adelante", "Cláusula 17/4", True,
                   "TC: $58.608 | JSAB: $97.678. % de trabajadores que lo activan en el mes.")
        t1,t2,t3,t4,t5,t6 = st.columns(6)
        vt_tc_a  = t1.number_input("Valor TC actual",   value=58608,  step=500, key="vt_tc_a")
        vt_tc_n  = t2.number_input("Valor TC nuevo",    value=58608,  step=500, key="vt_tc_n")
        vt_j_a   = t3.number_input("Valor JSAB actual", value=97678,  step=500, key="vt_j_a")
        vt_j_n   = t4.number_input("Valor JSAB nuevo",  value=97678,  step=500, key="vt_j_n")
        pct_t5_a = t5.number_input("% trabaj. activan (actual)", value=0.15,
                                    step=0.01, min_value=0.0, max_value=1.0, key="pct_t5_a")
        pct_t5_n = t6.number_input("% trabaj. activan (nuevo)",  value=0.15,
                                    step=0.01, min_value=0.0, max_value=1.0, key="pct_t5_n")
        tc_tot  = n_trainee+n_tcj+n_tc+n_tcs
        jsab_tot= n_jsab+n_jsabs
        c_t5_a  = (vt_tc_a*tc_tot + vt_j_a*jsab_tot) * pct_t5_a * 12
        c_t5_n  = (vt_tc_n*tc_tot + vt_j_n*jsab_tot) * pct_t5_n * 12
        costo_card("Costo Actual/año", c_t5_a, "Costo Nuevo/año", c_t5_n, False)
        nuevos_valores["turno5"] = dict(nombre="Bono 5° Turno", clausula="Cláusula 17/4",
            recurrente=True, costo_actual=c_t5_a, costo_nuevo=c_t5_n, suj_inc=False)
        st.markdown("---")

        # High Rank
        ben_header("Diferencial High Rank Programado", "Cláusula 16", True,
                   "Diferencia entre HV de TCs y JSABs × HV/mes × % vuelos con HR.")
        hr1,hr2,hr3,hr4 = st.columns(4)
        diff_hv_a = hr1.number_input("Diferencia HV TCs→JSAB actual (CLP)",
                                      value=HV_BASE["JSABs"]-HV_BASE["TCs"], step=100, key="hr_diff_a")
        diff_hv_n = hr2.number_input("Diferencia HV TCs→JSAB nuevo (CLP)",
                                      value=HV_BASE["JSABs"]-HV_BASE["TCs"], step=100, key="hr_diff_n")
        pct_hr_a  = hr3.number_input("% vuelos con HR (actual)", value=0.05,
                                      step=0.01, min_value=0.0, max_value=1.0, key="hr_pct_a")
        pct_hr_n  = hr4.number_input("% vuelos con HR (nuevo)",  value=0.05,
                                      step=0.01, min_value=0.0, max_value=1.0, key="hr_pct_n")
        hv_prom_tcs = hv_mes["TCs"]
        c_hr_a = diff_hv_a * pct_hr_a * hv_prom_tcs * 12 * n_tcs
        c_hr_n = diff_hv_n * pct_hr_n * hv_prom_tcs * 12 * n_tcs
        costo_card("Costo Actual/año", c_hr_a, "Costo Nuevo/año", c_hr_n, False)
        nuevos_valores["high_rank"] = dict(nombre="High Rank Programado", clausula="Cláusula 16",
            recurrente=True, costo_actual=c_hr_a, costo_nuevo=c_hr_n, suj_inc=False)

    # ════════════════════════════════════
    # CATEGORÍA: ASIGNACIONES
    # ════════════════════════════════════
    with st.expander("👨‍👩‍👧 Asignaciones", expanded=False):

        asignaciones = [
            ("escolar",  "Asignación Escolaridad", "Cláusula 29a",
             "Por hijo estudiante. Valor promedio EM ($164.532). Nº hijos promedio por trabajador.",
             164532, 164532, 0.8, 0.8, "Hijos estudiantes promedio/trabajador"),
            ("matrimon", "Asignación Matrimonio / AUC", "Cláusula 29b",
             "Por evento. % de la dotación que contrae matrimonio o AUC al año.",
             189211, 189211, 0.03, 0.03, "% dotación que se casa/AUC (por año)"),
            ("nacim",    "Asignación Nacimiento / Adopción", "Cláusula 29d",
             "Por hijo nacido o adoptado. % dotación con hijo al año.",
             189211, 189211, 0.05, 0.05, "% dotación con nacimiento (por año)"),
            ("fallec",   "Asignación Fallecimiento Familiar", "Cláusula 29c",
             "Por evento de fallecimiento de familiar directo.",
             1681904, 1681904, 0.02, 0.02, "% dotación afectada (por año)"),
        ]

        for bid, nombre, clausula, notas, va_d, vn_d, ca_d, cn_d, cant_lbl in asignaciones:
            ben_header(nombre, clausula, True, notas)
            a1,a2,a3,a4 = st.columns(4)
            va = a1.number_input("Valor unit. actual (CLP)", value=va_d, step=1000, key=f"va_{bid}")
            vn = a2.number_input("Valor unit. nuevo (CLP)",  value=vn_d, step=1000, key=f"vn_{bid}")
            ca = a3.number_input(f"{cant_lbl} (actual)", value=ca_d, step=0.01,
                                  min_value=0.0, key=f"ca_{bid}")
            cn = a4.number_input(f"{cant_lbl} (nuevo)",  value=cn_d, step=0.01,
                                  min_value=0.0, key=f"cn_{bid}")
            c_act = va * ca * total_dot
            c_new = vn * cn * total_dot
            costo_card("Costo Actual/año", c_act, "Costo Nuevo/año", c_new, False)
            nuevos_valores[bid] = dict(nombre=nombre, clausula=clausula,
                recurrente=True, costo_actual=c_act, costo_nuevo=c_new, suj_inc=False)
            st.markdown("---")

    # ════════════════════════════════════
    # CATEGORÍA: BENEFICIOS EN ESPECIE / OTROS
    # ════════════════════════════════════
    with st.expander("🏨 Beneficios en Especie y Otros", expanded=False):

        # Viáticos nacionales
        ben_header("Viáticos Nacionales", "Cláusula 8", True,
                   "CLP/día × días/mes × 12 meses × dotación.")
        vn1,vn2,vn3,vn4 = st.columns(4)
        viatn_va = vn1.number_input("CLP/día actual",  value=35000, step=500,  key="viatn_va")
        viatn_vn = vn2.number_input("CLP/día nuevo",   value=35000, step=500,  key="viatn_vn")
        viatn_da = vn3.number_input("Días/mes actual", value=8.0, step=0.5, min_value=0.0, key="viatn_da")
        viatn_dn = vn4.number_input("Días/mes nuevo",  value=8.0, step=0.5, min_value=0.0, key="viatn_dn")
        c_vn_a = viatn_va * viatn_da * 12 * total_dot
        c_vn_n = viatn_vn * viatn_dn * 12 * total_dot
        costo_card("Costo Actual/año", c_vn_a, "Costo Nuevo/año", c_vn_n, False)
        nuevos_valores["viatico_n"] = dict(nombre="Viáticos Nacionales", clausula="Cláusula 8",
            recurrente=True, costo_actual=c_vn_a, costo_nuevo=c_vn_n, suj_inc=False)
        st.markdown("---")

        # Viáticos internacionales
        ben_header("Viáticos Internacionales", "Cláusula 8", True,
                   "USD/día × TC × días/mes × 12 meses × dotación. Tarifa Sudamérica = USD 50.")
        vi1,vi2,vi3,vi4 = st.columns(4)
        viati_va = vi1.number_input("USD/día actual",  value=50.0, step=1.0, key="viati_va")
        viati_vn = vi2.number_input("USD/día nuevo",   value=50.0, step=1.0, key="viati_vn")
        viati_da = vi3.number_input("Días/mes actual", value=4.0,  step=0.5, min_value=0.0, key="viati_da")
        viati_dn = vi4.number_input("Días/mes nuevo",  value=4.0,  step=0.5, min_value=0.0, key="viati_dn")
        c_vi_a = viati_va * tc_usd * viati_da * 12 * total_dot
        c_vi_n = viati_vn * tc_usd * viati_dn * 12 * total_dot
        costo_card("Costo Actual/año", c_vi_a, "Costo Nuevo/año", c_vi_n, False)
        nuevos_valores["viatico_i"] = dict(nombre="Viáticos Internacionales", clausula="Cláusula 8",
            recurrente=True, costo_actual=c_vi_a, costo_nuevo=c_vi_n, suj_inc=False)
        st.markdown("---")

        # Movilización
        ben_header("Movilización (asignación en efectivo)", "Cláusula 18", True,
                   "Para quienes optan por movilización propia. Monto mensual líquido.")
        m1,m2,m3,m4 = st.columns(4)
        mov_va = m1.number_input("CLP/mes actual", value=264528, step=1000, key="mov_va")
        mov_vn = m2.number_input("CLP/mes nuevo",  value=264528, step=1000, key="mov_vn")
        mov_pa = m3.number_input("% dotación que opta (actual)", value=0.60,
                                  step=0.05, min_value=0.0, max_value=1.0, key="mov_pa")
        mov_pn = m4.number_input("% dotación que opta (nuevo)",  value=0.60,
                                  step=0.05, min_value=0.0, max_value=1.0, key="mov_pn")
        c_mov_a = mov_va * 12 * mov_pa * total_dot
        c_mov_n = mov_vn * 12 * mov_pn * total_dot
        costo_card("Costo Actual/año", c_mov_a, "Costo Nuevo/año", c_mov_n, False)
        nuevos_valores["moviliz"] = dict(nombre="Movilización", clausula="Cláusula 18",
            recurrente=True, costo_actual=c_mov_a, costo_nuevo=c_mov_n, suj_inc=False)
        st.markdown("---")

        # Bono Antigüedad
        ben_header("Bono Antigüedad", "Cláusula 32", True,
                   "% remuneración bruta al cumplir años de servicio. Se modela como % de rem. mensual × % dotación que cumple años.")
        ba1,ba2,ba3,ba4 = st.columns(4)
        ba_pct_a = ba1.number_input("% rem. promedio (actual)", value=50.0, step=5.0,
                                     min_value=0.0, key="ba_pct_a",
                                     help="50% corresponde a trabajadores que cumplen 10 años")
        ba_pct_n = ba2.number_input("% rem. promedio (nuevo)",  value=50.0, step=5.0,
                                     min_value=0.0, key="ba_pct_n")
        ba_cob_a = ba3.number_input("% dotación que cumple años (actual)", value=0.10,
                                     step=0.01, min_value=0.0, max_value=1.0, key="ba_cob_a")
        ba_cob_n = ba4.number_input("% dotación que cumple años (nuevo)",  value=0.10,
                                     step=0.01, min_value=0.0, max_value=1.0, key="ba_cob_n")
        rem_prom = (c_hv_act + c_sb_act) / max(total_dot, 1) / 12
        c_ba_a = rem_prom * (ba_pct_a/100) * ba_cob_a * total_dot
        c_ba_n = rem_prom * (ba_pct_n/100) * ba_cob_n * total_dot
        costo_card("Costo Actual/año", c_ba_a, "Costo Nuevo/año", c_ba_n, False)
        nuevos_valores["bono_ant"] = dict(nombre="Bono Antigüedad", clausula="Cláusula 32",
            recurrente=True, costo_actual=c_ba_a, costo_nuevo=c_ba_n, suj_inc=False)
        st.markdown("---")

        # APV
        ben_header("APV Empresa (matching)", "Cláusula 39", True,
                   "La empresa iguala el aporte del trabajador. Tope $10.000/mes.")
        ap1,ap2,ap3,ap4 = st.columns(4)
        apv_va = ap1.number_input("Aporte máx/mes actual (CLP)", value=10000, step=500, key="apv_va")
        apv_vn = ap2.number_input("Aporte máx/mes nuevo (CLP)",  value=10000, step=500, key="apv_vn")
        apv_pa = ap3.number_input("% adhesión actual", value=0.70, step=0.05,
                                   min_value=0.0, max_value=1.0, key="apv_pa")
        apv_pn = ap4.number_input("% adhesión nuevo",  value=0.70, step=0.05,
                                   min_value=0.0, max_value=1.0, key="apv_pn")
        c_apv_a = apv_va * 12 * apv_pa * total_dot
        c_apv_n = apv_vn * 12 * apv_pn * total_dot
        costo_card("Costo Actual/año", c_apv_a, "Costo Nuevo/año", c_apv_n, False)
        nuevos_valores["apv"] = dict(nombre="APV Empresa", clausula="Cláusula 39",
            recurrente=True, costo_actual=c_apv_a, costo_nuevo=c_apv_n, suj_inc=False)
        st.markdown("---")

        # Seguros
        ben_header("Seguros de Vida y Accidentes", "Cláusula 38", True,
                   "Prima estimada de mercado por persona/año (vida + accidentes personales).")
        sg1,sg2 = st.columns(2)
        seg_va = sg1.number_input("Prima anual/persona actual (CLP)", value=80000, step=5000, key="seg_va")
        seg_vn = sg2.number_input("Prima anual/persona nueva (CLP)",  value=80000, step=5000, key="seg_vn")
        c_seg_a = seg_va * total_dot
        c_seg_n = seg_vn * total_dot
        costo_card("Costo Actual/año", c_seg_a, "Costo Nuevo/año", c_seg_n, False)
        nuevos_valores["seguro_v"] = dict(nombre="Seguros Vida+Accidentes", clausula="Cláusula 38",
            recurrente=True, costo_actual=c_seg_a, costo_nuevo=c_seg_n, suj_inc=False)

    # ════════════════════════════════════
    # CATEGORÍA: INCREMENTO REAL
    # ════════════════════════════════════
    with st.expander("📈 Incremento Real Pactado", expanded=False):
        ben_header("Incremento Real HV + SB", "Cláusula 43", True,
                   "1% anual sobre HV y SB según contrato (excluye IPC). Se costea como el delta del 1° año.")
        ir1, ir2 = st.columns(2)
        pct_ir_a = ir1.number_input("% incremento actual/año", value=inc_real_pct,
                                     step=0.5, min_value=0.0, key="ir_pct_a")
        pct_ir_n = ir2.number_input("% incremento nuevo/año",  value=inc_real_pct,
                                     step=0.5, min_value=0.0, key="ir_pct_n")
        c_ir_a = (c_hv_act + c_sb_act) * pct_ir_a / 100
        c_ir_n = (c_hv_new + c_sb_new) * pct_ir_n / 100
        costo_card("Delta Inc. Real Actual (año 1)", c_ir_a,
                   "Delta Inc. Real Nuevo (año 1)", c_ir_n, True)
        nuevos_valores["inc_real"] = dict(nombre="Incremento Real (HV+SB)", clausula="Cláusula 43",
            recurrente=True, costo_actual=c_ir_a, costo_nuevo=c_ir_n, suj_inc=True)

    # ════════════════════════════════════
    # CATEGORÍA: ONE-TIME
    # ════════════════════════════════════
    with st.expander("⚡ Pagos One-Time (no recurrentes)", expanded=False):
        ben_header("Bono Término Negociación Colectiva", "Cláusula 42", False,
                   "Pago único sep-2023. $4.200.000 brutos/persona. NO forma parte del piso del próximo contrato.")
        bt1, bt2 = st.columns(2)
        bono_t_va = bt1.number_input("Valor actual/persona (CLP)", value=4200000, step=100000, key="bt_va")
        bono_t_vn = bt2.number_input("Valor nuevo/persona (CLP)",  value=4200000, step=100000, key="bt_vn")
        c_bt_a = bono_t_va * total_dot
        c_bt_n = bono_t_vn * total_dot
        costo_card("Costo One-Time Actual", c_bt_a, "Costo One-Time Nuevo", c_bt_n, False)
        nuevos_valores["bono_term"] = dict(nombre="Bono Término NC", clausula="Cláusula 42",
            recurrente=False, costo_actual=c_bt_a, costo_nuevo=c_bt_n, suj_inc=False)

    # ════════════════════════════════════
    # TOTALES TAB 1
    # ════════════════════════════════════
    st.markdown('<div class="section-title">📊 Resumen de Costos</div>', unsafe_allow_html=True)

    total_act_rec = sum(v["costo_actual"] for v in nuevos_valores.values() if v["recurrente"])
    total_new_rec = sum(v["costo_nuevo"]  for v in nuevos_valores.values() if v["recurrente"])
    total_onetime = sum(v["costo_actual"] for v in nuevos_valores.values() if not v["recurrente"])
    delta_rec     = total_new_rec - total_act_rec

    tc1, tc2, tc3, tc4 = st.columns(4)
    def big_metric(col, label, val_clp, delta_clp=None):
        val_usd = val_clp / tc_usd
        d_html = ""
        if delta_clp is not None:
            sign  = "+" if delta_clp >= 0 else ""
            color = ROJO if delta_clp > 0 else VERDE
            d_html = f'<div class="delta" style="color:{color}">{sign}${delta_clp/1e6:.2f}M vs. actual</div>'
        col.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">${val_clp/1e6:.1f}M CLP</div>
          <div style="font-size:12px;color:#6B7280">${val_usd/1e6:.2f}M USD</div>
          {d_html}
        </div>""", unsafe_allow_html=True)

    big_metric(tc1, "Costo Recurrente Actual / Año", total_act_rec)
    big_metric(tc2, "Costo Recurrente Nuevo / Año",  total_new_rec, delta_rec)
    big_metric(tc3, "Costo x Trabajador / Año (actual)", total_act_rec / max(total_dot, 1))
    big_metric(tc4, "Bono Firma (One-Time)", total_onetime)

    # Guardar en session_state para otros tabs
    st.session_state.update({
        "nv": nuevos_valores,
        "t_act_rec": total_act_rec,
        "t_new_rec": total_new_rec,
        "t_onetime": total_onetime,
        "t_dot":     total_dot,
        "c_hv_act":  c_hv_act,
        "c_sb_act":  c_sb_act,
    })

# ══════════════════════════════════════════════
# TAB 2 — EVOLUCIÓN ANUAL & CAGR
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Evolución del Costo — Punta a Punta (hasta 3 años)</div>',
                unsafe_allow_html=True)

    nv    = st.session_state.get("nv", {})
    t_act = st.session_state.get("t_act_rec", 0)
    t_new = st.session_state.get("t_new_rec", 0)

    if not nv:
        st.info("Primero ajusta los parámetros en la Tab 1.")
    else:
        años_l = [f"Año {i}" for i in range(anios + 1)]
        costos_act, costos_new = [], []

        for yr in range(anios + 1):
            f = factor_inc(yr, inc_real_pct)
            ca = cn = 0
            for v in nv.values():
                if not v["recurrente"]: continue
                ca += v["costo_actual"] * f if v["suj_inc"] else v["costo_actual"]
                cn += v["costo_nuevo"]  * f if v["suj_inc"] else v["costo_nuevo"]
            costos_act.append(ca)
            costos_new.append(cn)

        cagr_act = cagr(costos_act[0], costos_act[-1], anios)
        cagr_new = cagr(costos_new[0], costos_new[-1], anios)
        delta_pp  = costos_new[-1] - costos_act[-1]
        delta_pp_pct = delta_pp / costos_act[-1] * 100 if costos_act[-1] else 0

        k1,k2,k3,k4 = st.columns(4)
        for col, lbl, val, suf in [
            (k1,"CAGR Contrato Actual",  cagr_act,    "%"),
            (k2,"CAGR Contrato Nuevo",   cagr_new,    "%"),
            (k3,f"Δ Costo Año {anios} (%)", delta_pp_pct,"%"),
            (k4,f"Δ Absoluto Año {anios}", delta_pp/1e6,"M CLP"),
        ]:
            color = ROJO if val > 0 and "Δ" in lbl else AZUL
            col.markdown(f"""
            <div class="metric-card">
              <div class="label">{lbl}</div>
              <div class="value" style="color:{color}">{val:.2f}{suf}</div>
            </div>""", unsafe_allow_html=True)

        # Gráfico barras + línea delta
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Contrato Actual", x=años_l,
                             y=[c/1e6 for c in costos_act],
                             marker_color=AZUL, opacity=0.85))
        fig.add_trace(go.Bar(name="Contrato Nuevo", x=años_l,
                             y=[c/1e6 for c in costos_new],
                             marker_color=ROJO, opacity=0.85))
        fig.add_trace(go.Scatter(name="Δ (nuevo–actual)", x=años_l,
                                  y=[(n-a)/1e6 for n,a in zip(costos_new,costos_act)],
                                  mode="lines+markers",
                                  line=dict(color=AMBAR, width=2, dash="dot"),
                                  yaxis="y2"))
        fig.update_layout(barmode="group",
                          title="Costo Recurrente Anual — Actual vs. Nuevo",
                          yaxis=dict(title="CLP Millones"),
                          yaxis2=dict(title="Δ CLP M", overlaying="y",
                                      side="right", showgrid=False),
                          legend=dict(orientation="h", y=1.08),
                          plot_bgcolor=BLANCO, paper_bgcolor=GRIS,
                          font=dict(color=AZUL), height=430)
        st.plotly_chart(fig, use_container_width=True)

        # Tabla punta a punta
        df_pp = pd.DataFrame({
            "Año": años_l,
            "Costo Actual (CLP M)": [f"${c/1e6:.2f}M" for c in costos_act],
            "Costo Nuevo (CLP M)":  [f"${c/1e6:.2f}M" for c in costos_new],
            "Δ (CLP M)":            [f"${(n-a)/1e6:+.2f}M" for n,a in zip(costos_new,costos_act)],
            "Δ %":                  [f"{(n-a)/a*100:+.2f}%" for n,a in zip(costos_new,costos_act)],
            "Costo Act (USD M)":    [f"${c/tc_usd/1e6:.2f}M" for c in costos_act],
            "Costo Nvo (USD M)":    [f"${c/tc_usd/1e6:.2f}M" for c in costos_new],
        })
        st.dataframe(df_pp, use_container_width=True, hide_index=True)

        # Waterfall por categoría
        st.markdown("#### Variación por Categoría (Nuevo vs. Actual)")
        cat_map = {
            "Rem. Directas":     ["hv","sb","gratif"],
            "Bonos Recurrentes": ["asist","fiestas","navidad","bono_des","bono_prod"],
            "Bonos Operac.":     ["psvnc","ext_psv","cambio_v","cancel_v","turno5","turno_atp","pre_libre","high_rank"],
            "Asignaciones":      ["escolar","matrimon","nacim","fallec"],
            "Benef. Especie":    ["viatico_n","viatico_i","moviliz","bono_ant","apv","seguro_v"],
            "Inc. Real":         ["inc_real"],
        }
        cat_names = list(cat_map.keys())
        cat_deltas = [sum((nv[b]["costo_nuevo"]-nv[b]["costo_actual"])
                         for b in ids if b in nv) / 1e6
                      for ids in cat_map.values()]
        fig2 = go.Figure(go.Bar(
            x=cat_names, y=cat_deltas,
            marker_color=[ROJO if d>0 else VERDE for d in cat_deltas],
            text=[f"${d:+.1f}M" for d in cat_deltas],
            textposition="outside"
        ))
        fig2.update_layout(title="Δ Costo Nuevo vs. Actual por Categoría (CLP M)",
                           yaxis_title="CLP M", plot_bgcolor=BLANCO,
                           paper_bgcolor=GRIS, font=dict(color=AZUL), height=360)
        st.plotly_chart(fig2, use_container_width=True)

        # Donut composición actual
        st.markdown("#### Composición Costo Recurrente Actual")
        pie_l, pie_v = [], []
        for cname, cids in cat_map.items():
            v = sum(nv[b]["costo_actual"] for b in cids if b in nv)
            if v > 0: pie_l.append(cname); pie_v.append(v)
        colors_pie = [AZUL, ROJO, "#4B6FD4","#E05C6E","#7B93D9",AMBAR]
        fig3 = go.Figure(go.Pie(labels=pie_l, values=pie_v, hole=0.5,
                                 marker_colors=colors_pie,
                                 textinfo="label+percent"))
        fig3.update_layout(title="Composición Costo Anual Actual",
                           paper_bgcolor=GRIS, font=dict(color=AZUL), height=380,
                           annotations=[dict(text=f"${sum(pie_v)/1e6:.0f}M",
                                             x=0.5, y=0.5, font_size=16,
                                             font_color=AZUL, showarrow=False)])
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — SIMULADOR NUEVO CONTRATO
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Simulador de Propuesta — Nuevo Contrato</div>',
                unsafe_allow_html=True)

    nv    = st.session_state.get("nv", {})
    t_act = st.session_state.get("t_act_rec", 0)

    if not nv:
        st.info("Completa primero el Tab 1.")
    else:
        cs1, cs2 = st.columns([2, 1])
        with cs1:
            st.markdown("#### Parámetros de Negociación")
            inc_hv    = st.slider("Incremento adicional HV (%)",    0.0, 25.0, 0.0, 0.5)
            inc_sb    = st.slider("Incremento adicional SB (%)",    0.0, 25.0, 0.0, 0.5)
            inc_bonos = st.slider("Incremento bonos recurrentes (%)",0.0, 25.0, 0.0, 0.5)
            inc_dot   = st.slider("Variación dotación (%)",        -20,  30,   0,   1)
            st.markdown("#### Nuevos Beneficios Propuestos")
            nb1_n = st.text_input("Nombre beneficio nuevo 1", "Bono Bienestar")
            nb1_v = st.number_input("Valor anual total (CLP)", value=0, step=100000, key="nb1")
            nb2_n = st.text_input("Nombre beneficio nuevo 2", "")
            nb2_v = st.number_input("Valor anual total (CLP)", value=0, step=100000, key="nb2")

        with cs2:
            st.markdown("#### Resultado Simulación")
            dot_f = 1 + inc_dot / 100
            hv_s  = nv.get("hv",{}).get("costo_actual",0) * (1+inc_hv/100) * dot_f
            sb_s  = nv.get("sb",{}).get("costo_actual",0) * (1+inc_sb/100) * dot_f
            gr_s  = (hv_s + sb_s) * 0.0833
            c_sim = hv_s + sb_s + gr_s
            for bid, v in nv.items():
                if bid in ("hv","sb","gratif") or not v["recurrente"]: continue
                mult = (1+inc_bonos/100) if bid in ("asist","fiestas","navidad","bono_des","bono_prod") else 1
                c_sim += v["costo_actual"] * mult * dot_f
            c_sim += nb1_v + nb2_v

            delta_s = c_sim - t_act
            pct_s   = delta_s / t_act * 100 if t_act else 0
            cagr_s  = cagr(t_act, c_sim * factor_inc(anios, inc_real_pct), anios)

            for lbl, val, suf, extra in [
                ("Costo Actual Recurrente",  t_act,  None, None),
                ("Costo Simulado Nuevo",     c_sim,  None, None),
            ]:
                usd = val/tc_usd
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{lbl}</div>
                  <div class="value">${val/1e6:.2f}M CLP</div>
                  <div style="font-size:12px;color:#6B7280">${usd/1e6:.2f}M USD</div>
                </div>""", unsafe_allow_html=True)

            sign_s = "+" if delta_s >= 0 else ""
            col_s  = ROJO if delta_s > 0 else VERDE
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Variación vs. Actual</div>
              <div class="value" style="color:{col_s}">{sign_s}{pct_s:.2f}%</div>
              <div style="font-size:13px;color:{col_s}">{sign_s}${delta_s/1e6:.2f}M CLP/año</div>
            </div>
            <div class="metric-card">
              <div class="label">CAGR Simulado ({anios}a)</div>
              <div class="value">{cagr_s:.2f}%</div>
              <div style="font-size:12px;color:#6B7280">Inc. real {inc_real_pct:.1f}%/a incluido</div>
            </div>""", unsafe_allow_html=True)
            c_pp_s = c_sim * factor_inc(anios, inc_real_pct)
            c_pp_a = t_act  * factor_inc(anios, inc_real_pct)
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">Costo Año {anios} (punta)</div>
              <div class="value">${c_pp_s/1e6:.2f}M CLP</div>
              <div style="font-size:13px;color:{ROJO}">${(c_pp_s-c_pp_a)/1e6:+.2f}M vs. actual</div>
            </div>""", unsafe_allow_html=True)

        # Gráfico trayectoria
        años_l2 = [f"Año {i}" for i in range(anios+1)]
        c_a_yr  = [t_act  * factor_inc(yr, inc_real_pct) for yr in range(anios+1)]
        c_s_yr  = [c_sim  * factor_inc(yr, inc_real_pct) for yr in range(anios+1)]
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=años_l2, y=[c/1e6 for c in c_a_yr],
            name="Contrato Actual", mode="lines+markers",
            line=dict(color=AZUL, width=3), marker=dict(size=8)))
        fig_s.add_trace(go.Scatter(x=años_l2, y=[c/1e6 for c in c_s_yr],
            name="Contrato Simulado", mode="lines+markers",
            line=dict(color=ROJO, width=3, dash="dash"), marker=dict(size=8)))
        fig_s.update_layout(title="Trayectoria de Costo — Actual vs. Simulado",
                             yaxis_title="CLP Millones", plot_bgcolor=BLANCO,
                             paper_bgcolor=GRIS, font=dict(color=AZUL), height=380,
                             legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_s, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Resumen Ejecutivo</div>', unsafe_allow_html=True)

    nv    = st.session_state.get("nv", {})
    t_act = st.session_state.get("t_act_rec", 0)
    t_new = st.session_state.get("t_new_rec", 0)
    t_one = st.session_state.get("t_onetime", 0)
    t_dot = st.session_state.get("t_dot", total_dot)

    if not nv:
        st.info("Completa el Tab 1 primero.")
    else:
        st.markdown(f"""
        <div style="background:{BLANCO};border-radius:10px;padding:20px 28px;
                    box-shadow:0 1px 6px rgba(0,0,0,.07);margin-bottom:16px">
          <h3 style="color:{AZUL};margin-top:0">
            Contrato Colectivo · STCLE / Transporte Aéreo S.A.</h3>
          <p style="color:#4B5563">
            Período: 01/09/2023 – 31/08/2026 &nbsp;|&nbsp;
            Trabajadores: <b>{t_dot}</b> &nbsp;|&nbsp; TC: ${tc_usd:,} CLP/USD
          </p>
          <hr style="border-color:#E5E7EB">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:12px">
            <div>
              <div style="font-size:11px;color:#6B7280;text-transform:uppercase">Costo recurrente actual / año</div>
              <div style="font-size:24px;font-weight:700;color:{AZUL}">${t_act/1e6:.1f}M CLP</div>
              <div style="font-size:13px;color:#9CA3AF">${t_act/tc_usd/1e6:.2f}M USD</div>
            </div>
            <div>
              <div style="font-size:11px;color:#6B7280;text-transform:uppercase">Costo por trabajador / año</div>
              <div style="font-size:24px;font-weight:700;color:{AZUL}">${t_act/max(t_dot,1)/1e6:.3f}M CLP</div>
              <div style="font-size:13px;color:#9CA3AF">${t_act/max(t_dot,1)/tc_usd/1e3:.0f}K USD</div>
            </div>
            <div>
              <div style="font-size:11px;color:#6B7280;text-transform:uppercase">Bono firma (one-time)</div>
              <div style="font-size:24px;font-weight:700;color:{ROJO}">${t_one/1e6:.1f}M CLP</div>
              <div style="font-size:13px;color:#9CA3AF">${t_one/tc_usd/1e6:.2f}M USD</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Tabla detalle
        rows = []
        for v in nv.values():
            delta = v["costo_nuevo"] - v["costo_actual"]
            pct_d = f"{delta/v['costo_actual']*100:+.1f}%" if v["costo_actual"] else "N/A"
            rows.append({
                "Beneficio":          v["nombre"],
                "Cláusula":           v["clausula"],
                "Tipo":               "Recurrente" if v["recurrente"] else "One-Time",
                "Costo Actual (CLP)": f"${v['costo_actual']:,.0f}",
                "Costo Nuevo (CLP)":  f"${v['costo_nuevo']:,.0f}",
                "Δ CLP":              f"${delta:+,.0f}",
                "Δ %":                pct_d,
                "Inc.Real":           "✓" if v["suj_inc"] else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=520)

        st.markdown("---")
        rf1, rf2 = st.columns(2)
        delta_tot = t_new - t_act
        sign_tot  = "+" if delta_tot >= 0 else ""
        col_tot   = ROJO if delta_tot > 0 else VERDE
        rf1.markdown(f"""
        <div class="metric-card">
          <div class="label">Total recurrente actual / año</div>
          <div class="value">${t_act/1e6:.2f}M CLP &nbsp;|&nbsp; ${t_act/tc_usd/1e6:.2f}M USD</div>
          <div class="delta">Costo/trabajador: ${t_act/max(t_dot,1)/1e3:,.0f}K CLP</div>
        </div>""", unsafe_allow_html=True)
        rf2.markdown(f"""
        <div class="metric-card">
          <div class="label">Total recurrente nuevo / año</div>
          <div class="value">${t_new/1e6:.2f}M CLP &nbsp;|&nbsp; ${t_new/tc_usd/1e6:.2f}M USD</div>
          <div class="delta" style="color:{col_tot}">{sign_tot}${delta_tot/1e6:.2f}M vs. actual</div>
        </div>""", unsafe_allow_html=True)

        cagr_f = cagr(t_act, t_act * factor_inc(anios, inc_real_pct), anios)
        st.markdown(f"""
        <div style="background:{AZUL};color:white;border-radius:10px;
                    padding:16px 28px;margin-top:12px;
                    display:flex;gap:40px;align-items:center;flex-wrap:wrap">
          <div><div style="font-size:11px;opacity:.7">CAGR Contrato Actual ({anios}a)</div>
               <div style="font-size:22px;font-weight:700">{cagr_f:.2f}%</div></div>
          <div><div style="font-size:11px;opacity:.7">Inc. Real pactado / año</div>
               <div style="font-size:22px;font-weight:700">{inc_real_pct:.1f}%</div></div>
          <div><div style="font-size:11px;opacity:.7">Período contrato</div>
               <div style="font-size:22px;font-weight:700">36 meses</div></div>
          <div><div style="font-size:11px;opacity:.7">TC USD (prom. 2025)</div>
               <div style="font-size:22px;font-weight:700">${tc_usd:,}</div></div>
          <div><div style="font-size:11px;opacity:.7">Total dotación</div>
               <div style="font-size:22px;font-weight:700">{t_dot}</div></div>
        </div>""", unsafe_allow_html=True)

# ── Footer ──
st.markdown(f"""
<div style="margin-top:40px;padding:12px 0;border-top:2px solid #E5E7EB;
            text-align:center;font-size:11px;color:#9CA3AF">
  STCLE · Sindicato Tripulantes de Cabina LAN Express &nbsp;|&nbsp;
  Modelo de costeo CC · Uso interno · {anios} año(s) proyectados
</div>""", unsafe_allow_html=True)
