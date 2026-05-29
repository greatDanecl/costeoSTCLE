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
    page_title="Modelo Costo CC · STCLE",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROJO  = "#C8102E"
AZUL  = "#1B2A6B"
AZULC = "#2E4BAD"
GRIS  = "#F4F5F7"
BLANC = "#FFFFFF"
VERDE = "#1A7A4A"
AMBAR = "#D97706"

st.markdown(f"""
<style>
  .stApp {{ background-color:{GRIS}; }}

  /* ── Sidebar: fondo azul, labels blancos, inputs con texto oscuro ── */
  [data-testid="stSidebar"] {{ background-color:{AZUL}; }}
  [data-testid="stSidebar"] label                    {{ color:#CBD5F5 !important; }}
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color:#E8ECF8 !important; }}
  [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] h4                       {{ color:#FFFFFF !important; }}
  [data-testid="stSidebar"] .stMetricValue           {{ color:#FFFFFF !important; }}
  [data-testid="stSidebar"] .stMetricLabel           {{ color:#CBD5F5 !important; }}
  /* Inputs numéricos: fondo blanco, texto negro */
  [data-testid="stSidebar"] input                    {{ background:#fff !important; color:#111 !important; }}
  [data-testid="stSidebar"] [data-baseweb="input"]   {{ background:#fff !important; }}

  /* ── Header ── */
  .header-banner {{
    background:linear-gradient(135deg,{AZUL} 0%,{AZULC} 100%);
    border-radius:12px; padding:18px 26px; margin-bottom:16px;
    display:flex; align-items:center; gap:16px;
  }}
  .header-banner h1 {{ color:#fff !important; margin:0; font-size:20px; }}
  .header-banner p  {{ color:#CBD5F5; margin:0; font-size:12px; }}

  /* ── Section title ── */
  .sec {{ font-size:14px; font-weight:700; color:{AZUL};
          border-bottom:2px solid {ROJO}; padding-bottom:4px;
          margin:18px 0 10px; text-transform:uppercase; letter-spacing:.5px; }}

  /* ── Metric card ── */
  .mc {{ background:{BLANC}; border-left:5px solid {ROJO}; border-radius:8px;
         padding:14px 18px; margin:4px 0; box-shadow:0 1px 4px rgba(0,0,0,.07); }}
  .mc .lbl {{ font-size:11px; color:#6B7280; text-transform:uppercase; letter-spacing:.4px; }}
  .mc .val {{ font-size:20px; font-weight:700; color:{AZUL}; }}
  .mc .sub {{ font-size:12px; color:#9CA3AF; margin-top:2px; }}

  /* ── Benefit row ── */
  .brow {{ background:{BLANC}; border-radius:10px; padding:16px 20px;
           margin-bottom:12px; border-top:3px solid {AZUL};
           box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  .btitle {{ font-weight:700; color:{AZUL}; font-size:14px; }}
  .bnota  {{ font-size:11px; color:#6B7280; margin-top:2px; margin-bottom:8px; }}

  /* ── Cost result box ── */
  .cbox {{ background:{GRIS}; border-radius:8px; padding:10px 14px;
           border-left:4px solid {AZUL}; margin-top:6px; }}
  .cbox .cl {{ font-size:11px; color:#6B7280; }}
  .cbox .cv {{ font-size:17px; font-weight:700; color:{AZUL}; }}

  /* ── Badges ── */
  .brec {{ display:inline-block; padding:1px 9px; border-radius:10px;
           font-size:11px; font-weight:600; background:#DBEAFE; color:#1E40AF; }}
  .bone {{ display:inline-block; padding:1px 9px; border-radius:10px;
           font-size:11px; font-weight:600; background:#FEE2E2; color:#991B1B; }}

  h1,h2,h3,h4 {{ color:{AZUL}; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOGO
# ─────────────────────────────────────────────
def img_b64(p):
    try: return base64.b64encode(Path(p).read_bytes()).decode()
    except: return ""

logo = img_b64("logo.png")
logo_tag = f'<img src="data:image/png;base64,{logo}" style="height:52px;border-radius:50%;">' if logo else "✈️"
st.markdown(f"""
<div class="header-banner">
  {logo_tag}
  <div>
    <h1>Modelo de Costeo · Contrato Colectivo STCLE</h1>
    <p>Sindicato de Tripulantes de Cabina LAN Express &nbsp;·&nbsp; Vigencia 01/09/2023 – 31/08/2026</p>
  </div>
</div>""", unsafe_allow_html=True)

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
    st.markdown("#### 📈 Incremento Real % anual")
    st.caption("Aplica sobre HV y SB. Excluye IPC.")
    inc_r = st.number_input("Inc. real %", value=1.0, step=0.5, min_value=0.0, max_value=10.0)
    st.markdown("---")
    st.markdown("#### 👥 Dotación por Subcategoría")
    n_tr  = st.number_input("TC Trainee",      value=10,  min_value=0, step=1)
    n_tcj = st.number_input("TC Junior",        value=25,  min_value=0, step=1)
    n_tc  = st.number_input("TC (Senior)",      value=60,  min_value=0, step=1)
    n_tcs = st.number_input("TC Senior (TCs)",  value=45,  min_value=0, step=1)
    n_j   = st.number_input("Jefe SAB",         value=35,  min_value=0, step=1)
    n_js  = st.number_input("Jefe SAB Senior",  value=18,  min_value=0, step=1)
    N = n_tr+n_tcj+n_tc+n_tcs+n_j+n_js
    st.metric("Total dotación", N)
    st.markdown("---")
    st.markdown("#### ✈️ Productividad HV/mes promedio")
    hv_tr  = st.number_input("HV Trainee", value=55.0, step=1.0)
    hv_tcj = st.number_input("HV TCj",     value=57.0, step=1.0)
    hv_tc  = st.number_input("HV TC",      value=60.0, step=1.0)
    hv_tcs = st.number_input("HV TCs",     value=62.0, step=1.0)
    hv_j   = st.number_input("HV JSAB",    value=60.0, step=1.0)
    hv_js  = st.number_input("HV JSABs",   value=60.0, step=1.0)

# ─────────────────────────────────────────────
# DATOS BASE
# ─────────────────────────────────────────────
SUBCAT = ["TC Trainee","TC Junior","TC","TCs","JSAB","JSABs"]
HV0 = dict(zip(SUBCAT,[3579,3937,7119,11051,16018,19871]))
SB0 = dict(zip(SUBCAT,[500000,460000,460000,460000,483575,559136]))
DOT = dict(zip(SUBCAT,[n_tr,n_tcj,n_tc,n_tcs,n_j,n_js]))
HVM = dict(zip(SUBCAT,[hv_tr,hv_tcj,hv_tc,hv_tcs,hv_j,hv_js]))

def fi(yr,pct): return (1+pct/100)**yr
def cagr(a,b,n): return ((b/a)**(1/n)-1)*100 if a>0 and n>0 else 0.0

# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────
def mc(col, label, clp, delta=None):
    """Render metric card."""
    usd = clp/tc_usd
    dh = ""
    if delta is not None:
        s = "+" if delta>=0 else ""
        c = ROJO if delta>0 else VERDE
        dh = f'<div style="font-size:12px;color:{c};margin-top:2px">{s}${delta/1e6:.2f}M vs actual</div>'
    col.markdown(f"""
    <div class="mc">
      <div class="lbl">{label}</div>
      <div class="val">${clp/1e6:.2f}M CLP</div>
      <div class="sub">${usd/1e6:.3f}M USD</div>
      {dh}
    </div>""", unsafe_allow_html=True)

def cost_box(c_act, c_new, suj_inc):
    """Render inline cost comparison."""
    delta = c_new - c_act
    s = "+" if delta>=0 else ""
    cd = ROJO if delta>0 else (VERDE if delta<0 else "#6B7280")
    st.markdown(f"""
    <div class="cbox">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;align-items:end">
        <div><div class="cl">Costo Actual / año</div>
             <div class="cv">${c_act/1e6:.3f}M CLP</div>
             <div style="font-size:11px;color:#9CA3AF">${c_act/tc_usd/1e3:.1f}K USD</div></div>
        <div><div class="cl">Costo Nuevo / año</div>
             <div class="cv" style="color:{ROJO if delta>0 else AZUL}">${c_new/1e6:.3f}M CLP</div>
             <div style="font-size:11px;color:#9CA3AF">${c_new/tc_usd/1e3:.1f}K USD</div></div>
        <div><div class="cl">Variación</div>
             <div style="font-size:16px;font-weight:700;color:{cd}">{s}${delta/1e3:,.0f}K</div>
             <div style="font-size:11px;color:#9CA3AF">Inc.Real: {"✅" if suj_inc else "❌"}</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

def bhead(nombre, clausula, rec, nota):
    badge = f'<span class="{"brec" if rec else "bone"}">{"Recurrente" if rec else "One-Time"}</span>'
    st.markdown(f"""
    <div class="btitle">{nombre} &nbsp;
      <code style="font-size:10px;background:#EEF2FF;color:{AZUL};padding:1px 5px;border-radius:3px">{clausula}</code>
      &nbsp;{badge}
    </div>
    <div class="bnota">{nota}</div>""", unsafe_allow_html=True)

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
# TAB 1
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec">Variables Remuneracionales — Ajuste Actual vs. Nuevo</div>', unsafe_allow_html=True)
    st.info("💡 Edita los campos **Actual** y **Nuevo** de cada beneficio. El costo se recalcula automáticamente. "
            "Los resultados alimentan los gráficos de los demás tabs.")

    NV = {}   # {bid: {nombre, clausula, recurrente, costo_actual, costo_nuevo, suj_inc}}

    # ════════════════════════════════════════
    # 1. REMUNERACIONES DIRECTAS
    # ════════════════════════════════════════
    with st.expander("💼 Remuneraciones Directas", expanded=True):

        # ── Horas de Vuelo ──
        st.markdown('<div class="brow">', unsafe_allow_html=True)
        bhead("Horas de Vuelo","Cláusula 26",True,
              "Valor HV × max(HV_mes_sidebar, 55 piso) × 12 meses × dotación. Edita valor por subcategoría.")
        st.markdown("</div>", unsafe_allow_html=True)

        hdr = st.columns([2,1,1,1,1,1,1])
        for h,t in zip(hdr,["Subcategoría","Dotación","HV Actual (CLP)","HV Nuevo (CLP)","HV/mes","Costo Act (M CLP)","Costo Nvo (M CLP)"]):
            h.markdown(f"**{t}**")

        c_hv_a = c_hv_n = 0
        for sc in SUBCAT:
            r = st.columns([2,1,1,1,1,1,1])
            r[0].write(sc)
            r[1].write(str(DOT[sc]))
            hv_a = r[2].number_input(f"HVa {sc}", value=int(HV0[sc]), step=100,
                                      label_visibility="collapsed", key=f"hva_{sc}")
            hv_n = r[3].number_input(f"HVn {sc}", value=int(HV0[sc]), step=100,
                                      label_visibility="collapsed", key=f"hvn_{sc}")
            hvm  = max(float(HVM[sc]), 55.0)
            ca   = hv_a * hvm * 12 * DOT[sc]
            cn   = hv_n * hvm * 12 * DOT[sc]
            r[4].write(f"{hvm:.0f}")
            r[5].write(f"${ca/1e6:.3f}")
            r[6].write(f"${cn/1e6:.3f}")
            c_hv_a += ca; c_hv_n += cn

        cost_box(c_hv_a, c_hv_n, True)
        NV["hv"] = dict(nombre="Horas de Vuelo", clausula="Cláusula 26",
                        recurrente=True, costo_actual=c_hv_a, costo_nuevo=c_hv_n, suj_inc=True)
        st.markdown("---")

        # ── Sueldo Base ──
        st.markdown('<div class="brow">', unsafe_allow_html=True)
        bhead("Sueldo Base","Cláusula 26",True,
              "Sueldo base mensual bruto × 12 × dotación. Edita por subcategoría.")
        st.markdown("</div>", unsafe_allow_html=True)

        hdr2 = st.columns([2,1,1,1,1,1])
        for h,t in zip(hdr2,["Subcategoría","Dotación","SB Actual (CLP)","SB Nuevo (CLP)","Costo Act (M)","Costo Nvo (M)"]):
            h.markdown(f"**{t}**")

        c_sb_a = c_sb_n = 0
        for sc in SUBCAT:
            r = st.columns([2,1,1,1,1,1])
            r[0].write(sc)
            r[1].write(str(DOT[sc]))
            sb_a = r[2].number_input(f"SBa {sc}", value=int(SB0[sc]), step=5000,
                                      label_visibility="collapsed", key=f"sba_{sc}")
            sb_n = r[3].number_input(f"SBn {sc}", value=int(SB0[sc]), step=5000,
                                      label_visibility="collapsed", key=f"sbn_{sc}")
            ca = sb_a * 12 * DOT[sc]; cn = sb_n * 12 * DOT[sc]
            r[4].write(f"${ca/1e6:.3f}"); r[5].write(f"${cn/1e6:.3f}")
            c_sb_a += ca; c_sb_n += cn

        cost_box(c_sb_a, c_sb_n, True)
        NV["sb"] = dict(nombre="Sueldo Base", clausula="Cláusula 26",
                        recurrente=True, costo_actual=c_sb_a, costo_nuevo=c_sb_n, suj_inc=True)
        st.markdown("---")

        # ── Gratificación ──
        st.markdown('<div class="brow">', unsafe_allow_html=True)
        bhead("Gratificación Legal 25%","Cláusula 4",True,
              "25% de remuneración mensual legal (HV+SB). Se modela como % del costo HV+SB anual ÷ 12.")
        st.markdown("</div>", unsafe_allow_html=True)
        g1,g2,_,_ = st.columns(4)
        pg_a = g1.number_input("% Gratif. Actual", value=8.33, step=0.1, min_value=0.0, max_value=25.0, key="gra")
        pg_n = g2.number_input("% Gratif. Nuevo",  value=8.33, step=0.1, min_value=0.0, max_value=25.0, key="grn")
        c_gr_a = (c_hv_a+c_sb_a)*pg_a/100
        c_gr_n = (c_hv_n+c_sb_n)*pg_n/100
        cost_box(c_gr_a, c_gr_n, True)
        NV["gratif"] = dict(nombre="Gratificación Legal", clausula="Cláusula 4",
                            recurrente=True, costo_actual=c_gr_a, costo_nuevo=c_gr_n, suj_inc=True)

    # ════════════════════════════════════════
    # 2. BONOS RECURRENTES
    # ════════════════════════════════════════
    with st.expander("🎁 Bonos Recurrentes", expanded=True):

        # Bono Asistencia
        bhead("Bono 100% Asistencia","Cláusula 28a",True,
              "Mensual por trabajador. Multiplica por % que lo percibe (85% por defecto) × 12 meses.")
        a1,a2,a3,a4 = st.columns(4)
        bas_va = a1.number_input("Valor actual (CLP/mes)", value=169349, step=1000, key="bas_va")
        bas_vn = a2.number_input("Valor nuevo (CLP/mes)",  value=169349, step=1000, key="bas_vn")
        bas_pa = a3.number_input("% personas actual (0-1)", value=0.85, step=0.05, min_value=0.0, max_value=1.0, key="bas_pa")
        bas_pn = a4.number_input("% personas nuevo (0-1)",  value=0.85, step=0.05, min_value=0.0, max_value=1.0, key="bas_pn")
        c_bas_a = bas_va * 12 * bas_pa * N
        c_bas_n = bas_vn * 12 * bas_pn * N
        cost_box(c_bas_a, c_bas_n, False)
        NV["asist"] = dict(nombre="Bono Asistencia", clausula="Cláusula 28a",
                           recurrente=True, costo_actual=c_bas_a, costo_nuevo=c_bas_n, suj_inc=False)
        st.markdown("---")

        # Bono Fiestas Patrias
        bhead("Bono Fiestas Patrias","Cláusula 28b",True,
              "Pago sep. Valor base + 30% por cada hijo. Factor hijos = nº hijos prom/trabajador.")
        f1,f2,f3,f4 = st.columns(4)
        bfp_va = f1.number_input("Valor base actual (CLP)", value=138983, step=1000, key="bfp_va")
        bfp_vn = f2.number_input("Valor base nuevo (CLP)",  value=138983, step=1000, key="bfp_vn")
        bfp_ha = f3.number_input("Nº hijos prom. actual",   value=0.8, step=0.1, min_value=0.0, key="bfp_ha")
        bfp_hn = f4.number_input("Nº hijos prom. nuevo",    value=0.8, step=0.1, min_value=0.0, key="bfp_hn")
        c_bfp_a = bfp_va*(1+0.30*bfp_ha)*N
        c_bfp_n = bfp_vn*(1+0.30*bfp_hn)*N
        cost_box(c_bfp_a, c_bfp_n, False)
        NV["fiestas"] = dict(nombre="Bono Fiestas Patrias", clausula="Cláusula 28b",
                             recurrente=True, costo_actual=c_bfp_a, costo_nuevo=c_bfp_n, suj_inc=False)
        st.markdown("---")

        # Bono Navidad
        bhead("Bono Navidad","Cláusula 28c",True,
              "Pago dic. Valor base + 30% por cada hijo.")
        n1,n2,n3,n4 = st.columns(4)
        bnv_va = n1.number_input("Valor base actual (CLP)", value=169872, step=1000, key="bnv_va")
        bnv_vn = n2.number_input("Valor base nuevo (CLP)",  value=169872, step=1000, key="bnv_vn")
        bnv_ha = n3.number_input("Nº hijos prom. actual",   value=0.8, step=0.1, min_value=0.0, key="bnv_ha")
        bnv_hn = n4.number_input("Nº hijos prom. nuevo",    value=0.8, step=0.1, min_value=0.0, key="bnv_hn")
        c_bnv_a = bnv_va*(1+0.30*bnv_ha)*N
        c_bnv_n = bnv_vn*(1+0.30*bnv_hn)*N
        cost_box(c_bnv_a, c_bnv_n, False)
        NV["navidad"] = dict(nombre="Bono Navidad", clausula="Cláusula 28c",
                             recurrente=True, costo_actual=c_bnv_a, costo_nuevo=c_bnv_n, suj_inc=False)
        st.markdown("---")

        # Bono Desempeño
        bhead("Bono Desempeño","Cláusula 37",True,
              "Pago julio. Valores diferenciados TC/JSAB. Mix de desempeño ponderado.")
        st.caption("TC ponderado por defecto: 10% excepcional + 30% sobre esperado + 60% esperado = $481,586")
        bd1,bd2,bd3,bd4 = st.columns(4)
        bdes_tc_a  = bd1.number_input("TC valor prom. actual (CLP)",   value=int(0.1*765750+0.3*530920+0.6*405337), step=1000, key="bdes_tc_a")
        bdes_tc_n  = bd2.number_input("TC valor prom. nuevo (CLP)",    value=int(0.1*765750+0.3*530920+0.6*405337), step=1000, key="bdes_tc_n")
        bdes_jsab_a= bd3.number_input("JSAB valor prom. actual (CLP)", value=int(0.1*918900+0.3*612600+0.6*510500), step=1000, key="bdes_jsab_a")
        bdes_jsab_n= bd4.number_input("JSAB valor prom. nuevo (CLP)",  value=int(0.1*918900+0.3*612600+0.6*510500), step=1000, key="bdes_jsab_n")
        tc_tot = n_tr+n_tcj+n_tc+n_tcs; jsab_tot = n_j+n_js
        c_bdes_a = bdes_tc_a*tc_tot + bdes_jsab_a*jsab_tot
        c_bdes_n = bdes_tc_n*tc_tot + bdes_jsab_n*jsab_tot
        cost_box(c_bdes_a, c_bdes_n, False)
        NV["bono_des"] = dict(nombre="Bono Desempeño", clausula="Cláusula 37",
                              recurrente=True, costo_actual=c_bdes_a, costo_nuevo=c_bdes_n, suj_inc=False)
        st.markdown("---")

        # Bono Productividad
        bhead("Bono Productividad","Cláusula 37",True,
              "Pago marzo. Factor cumplimiento presupuesto. TC: $674.602 | JSAB: $1.180.556 (factor 1.0).")
        bp1,bp2,bp3,bp4 = st.columns(4)
        bprod_tc_a  = bp1.number_input("TC valor actual (CLP)",   value=674602,  step=1000, key="bprod_tc_a")
        bprod_tc_n  = bp2.number_input("TC valor nuevo (CLP)",    value=674602,  step=1000, key="bprod_tc_n")
        bprod_jsab_a= bp3.number_input("JSAB valor actual (CLP)", value=1180556, step=1000, key="bprod_jsab_a")
        bprod_jsab_n= bp4.number_input("JSAB valor nuevo (CLP)",  value=1180556, step=1000, key="bprod_jsab_n")
        c_bprod_a = bprod_tc_a*tc_tot + bprod_jsab_a*jsab_tot
        c_bprod_n = bprod_tc_n*tc_tot + bprod_jsab_n*jsab_tot
        cost_box(c_bprod_a, c_bprod_n, False)
        NV["bono_prod"] = dict(nombre="Bono Productividad", clausula="Cláusula 37",
                               recurrente=True, costo_actual=c_bprod_a, costo_nuevo=c_bprod_n, suj_inc=False)

    # ════════════════════════════════════════
    # 3. BONOS OPERACIONALES
    # ════════════════════════════════════════
    with st.expander("✈️ Bonos Operacionales (por evento)", expanded=False):

        ops = [
            ("psvnc",    "Bono Noche Consecutiva (PSVNC)",  "Cláusula 17/1.5",
             "Por evento PSVNC. Valor × eventos/mes/persona × 12 × dotación.",
             52094, 1.5, False),
            ("ext_psv",  "Bono Extensión PSV 12→14h",        "Cláusula 23",
             "Valor 1er evento ($79.029). Estimado eventos/mes/persona.",
             79029, 0.5, False),
            ("cambio_v", "Bono Cambio de Vuelo",              "Cláusula 13d",
             "Al cambiar vuelo en aeropuerto/móvil. Valor × eventos/mes/persona × 12 × dotación.",
             119819, 0.3, False),
            ("cancel_v", "Bono Cancelación (espera > 3h)",    "Cláusula 13b",
             "Cancelación 1er tramo con espera mayor a 3 horas.",
             200469, 0.2, False),
            ("turno_atp","Bono Turno Aeropuerto (1er turno)", "Cláusula 17/4.2",
             "1er turno del mes: $54.700. Desde 2do: $68.377. Se usa valor 1er turno.",
             54700, 1.0, False),
            ("pre_libre","Bono PSV previo libre > 22:00",     "Cláusula 17/1.6",
             "Cuando PSV termina entre 22:00 y 23:59 previo a días libres.",
             64196, 0.4, False),
        ]

        for bid, nombre, clausula, nota, val_def, freq_def, suj in ops:
            bhead(nombre, clausula, True, nota)
            o1,o2,o3,o4 = st.columns(4)
            va = o1.number_input("Valor unit. actual (CLP)", value=val_def,  step=500,  key=f"ova_{bid}")
            vn = o2.number_input("Valor unit. nuevo (CLP)",  value=val_def,  step=500,  key=f"ovn_{bid}")
            fa = o3.number_input("Frec. actual (eventos/mes/persona)", value=freq_def, step=0.1, min_value=0.0, key=f"ofa_{bid}")
            fn = o4.number_input("Frec. nueva  (eventos/mes/persona)", value=freq_def, step=0.1, min_value=0.0, key=f"ofn_{bid}")
            c_a = va*fa*12*N;  c_n = vn*fn*12*N
            cost_box(c_a, c_n, suj)
            NV[bid] = dict(nombre=nombre, clausula=clausula, recurrente=True,
                           costo_actual=c_a, costo_nuevo=c_n, suj_inc=suj)
            st.markdown("---")

        # 5° Turno (TC ≠ JSAB)
        bhead("Bono 5° Turno en adelante","Cláusula 17/4",True,
              "TC: $58.608 | JSAB: $97.678. % de trabajadores que lo activan mensualmente.")
        t1,t2,t3,t4,t5,t6 = st.columns(6)
        vt_tc_a = t1.number_input("TC val. actual",    value=58608, step=500, key="vt_tca")
        vt_tc_n = t2.number_input("TC val. nuevo",     value=58608, step=500, key="vt_tcn")
        vt_j_a  = t3.number_input("JSAB val. actual",  value=97678, step=500, key="vt_ja")
        vt_j_n  = t4.number_input("JSAB val. nuevo",   value=97678, step=500, key="vt_jn")
        pt5_a   = t5.number_input("% trabaj. actual (0-1)", value=0.15, step=0.01, min_value=0.0, max_value=1.0, key="pt5a")
        pt5_n   = t6.number_input("% trabaj. nuevo  (0-1)", value=0.15, step=0.01, min_value=0.0, max_value=1.0, key="pt5n")
        c_t5_a = (vt_tc_a*tc_tot + vt_j_a*jsab_tot)*pt5_a*12
        c_t5_n = (vt_tc_n*tc_tot + vt_j_n*jsab_tot)*pt5_n*12
        cost_box(c_t5_a, c_t5_n, False)
        NV["turno5"] = dict(nombre="Bono 5° Turno", clausula="Cláusula 17/4",
                            recurrente=True, costo_actual=c_t5_a, costo_nuevo=c_t5_n, suj_inc=False)
        st.markdown("---")

        # High Rank
        bhead("Diferencial High Rank Programado","Cláusula 16",True,
              "Diferencia HV entre TCs y JSABs × HV/mes TCs × % vuelos con HR × dotación TCs × 12.")
        hr1,hr2,hr3,hr4 = st.columns(4)
        diff_a = hr1.number_input("Dif. HV TCs→JSAB actual", value=HV0["JSABs"]-HV0["TCs"], step=100, key="hr_da")
        diff_n = hr2.number_input("Dif. HV TCs→JSAB nuevo",  value=HV0["JSABs"]-HV0["TCs"], step=100, key="hr_dn")
        phr_a  = hr3.number_input("% vuelos con HR actual (0-1)", value=0.05, step=0.01, min_value=0.0, max_value=1.0, key="hr_pa")
        phr_n  = hr4.number_input("% vuelos con HR nuevo  (0-1)", value=0.05, step=0.01, min_value=0.0, max_value=1.0, key="hr_pn")
        c_hr_a = diff_a * phr_a * float(HVM["TCs"]) * 12 * n_tcs
        c_hr_n = diff_n * phr_n * float(HVM["TCs"]) * 12 * n_tcs
        cost_box(c_hr_a, c_hr_n, False)
        NV["high_rank"] = dict(nombre="High Rank Programado", clausula="Cláusula 16",
                               recurrente=True, costo_actual=c_hr_a, costo_nuevo=c_hr_n, suj_inc=False)

    # ════════════════════════════════════════
    # 4. ASIGNACIONES
    # ════════════════════════════════════════
    with st.expander("👨‍👩‍👧 Asignaciones", expanded=False):

        asigs = [
            ("escolar", "Asignación Escolaridad","Cláusula 29a",
             "Por hijo estudiante. Valor promedio EM. Nº hijos estudiantes prom. por trabajador.",
             164532, 0.8, "Hijos estud. prom./trabajador"),
            ("matrimon","Asignación Matrimonio / AUC","Cláusula 29b",
             "Por evento matrimonio o AUC. % dotación que lo impetran al año.",
             189211, 0.03, "% dotación anual"),
            ("nacim",   "Asignación Nacimiento / Adopción","Cláusula 29d",
             "Por hijo nacido o adoptado. % dotación con nacimiento al año.",
             189211, 0.05, "% dotación anual"),
            ("fallec",  "Asignación Fallecimiento Familiar","Cláusula 29c",
             "Por fallecimiento de familiar directo. % dotación afectada al año.",
             1681904, 0.02, "% dotación anual"),
        ]

        for bid, nombre, clausula, nota, vdef, cdef, clbl in asigs:
            bhead(nombre, clausula, True, nota)
            a1,a2,a3,a4 = st.columns(4)
            va = a1.number_input(f"Valor unit. actual (CLP)", value=vdef, step=1000, key=f"asva_{bid}")
            vn = a2.number_input(f"Valor unit. nuevo (CLP)",  value=vdef, step=1000, key=f"asvn_{bid}")
            ca = a3.number_input(f"{clbl} actual", value=cdef, step=0.01, min_value=0.0, key=f"asca_{bid}")
            cn = a4.number_input(f"{clbl} nuevo",  value=cdef, step=0.01, min_value=0.0, key=f"ascn_{bid}")
            c_a = va*ca*N; c_n = vn*cn*N
            cost_box(c_a, c_n, False)
            NV[bid] = dict(nombre=nombre, clausula=clausula, recurrente=True,
                           costo_actual=c_a, costo_nuevo=c_n, suj_inc=False)
            st.markdown("---")

    # ════════════════════════════════════════
    # 5. BENEFICIOS EN ESPECIE / OTROS
    # ════════════════════════════════════════
    with st.expander("🏨 Viáticos, Movilización y Otros", expanded=False):

        # Viáticos nacionales
        bhead("Viáticos Nacionales","Cláusula 8",True,
              "CLP/día × días/mes × 12 × dotación.")
        vn1,vn2,vn3,vn4 = st.columns(4)
        vtn_va = vn1.number_input("CLP/día actual",  value=35000, step=500,  key="vtn_va")
        vtn_vn = vn2.number_input("CLP/día nuevo",   value=35000, step=500,  key="vtn_vn")
        vtn_da = vn3.number_input("Días/mes actual",  value=8.0,  step=0.5, min_value=0.0, key="vtn_da")
        vtn_dn = vn4.number_input("Días/mes nuevo",   value=8.0,  step=0.5, min_value=0.0, key="vtn_dn")
        c_vtn_a = vtn_va*vtn_da*12*N; c_vtn_n = vtn_vn*vtn_dn*12*N
        cost_box(c_vtn_a, c_vtn_n, False)
        NV["viatico_n"] = dict(nombre="Viáticos Nacionales", clausula="Cláusula 8",
                               recurrente=True, costo_actual=c_vtn_a, costo_nuevo=c_vtn_n, suj_inc=False)
        st.markdown("---")

        # Viáticos internacionales
        bhead("Viáticos Internacionales","Cláusula 8",True,
              "USD/día × TC CLP/USD × días/mes × 12 × dotación. Tarifa Sudamérica: USD 50.")
        vi1,vi2,vi3,vi4 = st.columns(4)
        vti_va = vi1.number_input("USD/día actual",  value=50.0, step=1.0, key="vti_va")
        vti_vn = vi2.number_input("USD/día nuevo",   value=50.0, step=1.0, key="vti_vn")
        vti_da = vi3.number_input("Días/mes actual", value=4.0,  step=0.5, min_value=0.0, key="vti_da")
        vti_dn = vi4.number_input("Días/mes nuevo",  value=4.0,  step=0.5, min_value=0.0, key="vti_dn")
        c_vti_a = vti_va*tc_usd*vti_da*12*N; c_vti_n = vti_vn*tc_usd*vti_dn*12*N
        cost_box(c_vti_a, c_vti_n, False)
        NV["viatico_i"] = dict(nombre="Viáticos Internacionales", clausula="Cláusula 8",
                               recurrente=True, costo_actual=c_vti_a, costo_nuevo=c_vti_n, suj_inc=False)
        st.markdown("---")

        # Movilización
        bhead("Movilización (asignación efectivo)","Cláusula 18",True,
              "Para quienes optan por movilizarse por cuenta propia. CLP/mes × % que opta × 12.")
        m1,m2,m3,m4 = st.columns(4)
        mov_va = m1.number_input("CLP/mes actual", value=264528, step=1000, key="mov_va")
        mov_vn = m2.number_input("CLP/mes nuevo",  value=264528, step=1000, key="mov_vn")
        mov_pa = m3.number_input("% opta actual (0-1)", value=0.60, step=0.05, min_value=0.0, max_value=1.0, key="mov_pa")
        mov_pn = m4.number_input("% opta nuevo  (0-1)", value=0.60, step=0.05, min_value=0.0, max_value=1.0, key="mov_pn")
        c_mov_a = mov_va*12*mov_pa*N; c_mov_n = mov_vn*12*mov_pn*N
        cost_box(c_mov_a, c_mov_n, False)
        NV["moviliz"] = dict(nombre="Movilización", clausula="Cláusula 18",
                             recurrente=True, costo_actual=c_mov_a, costo_nuevo=c_mov_n, suj_inc=False)
        st.markdown("---")

        # Bono Antigüedad
        bhead("Bono Antigüedad","Cláusula 32",True,
              "% de remuneración bruta al cumplir años clave. Se modela como % rem. mensual × % dotación que cumple años.")
        ba1,ba2,ba3,ba4 = st.columns(4)
        ba_pa = ba1.number_input("% rem. prom. actual", value=50.0, step=5.0, min_value=0.0, key="ba_pa",
                                  help="50% = trabajadores que cumplen 10 años")
        ba_pn = ba2.number_input("% rem. prom. nuevo",  value=50.0, step=5.0, min_value=0.0, key="ba_pn")
        ba_ca = ba3.number_input("% dot. que cumple años actual (0-1)", value=0.10, step=0.01, min_value=0.0, max_value=1.0, key="ba_ca")
        ba_cn = ba4.number_input("% dot. que cumple años nuevo  (0-1)", value=0.10, step=0.01, min_value=0.0, max_value=1.0, key="ba_cn")
        rem_m = (c_hv_a+c_sb_a)/max(N,1)/12
        c_ba_a = rem_m*(ba_pa/100)*ba_ca*N; c_ba_n = rem_m*(ba_pn/100)*ba_cn*N
        cost_box(c_ba_a, c_ba_n, False)
        NV["bono_ant"] = dict(nombre="Bono Antigüedad", clausula="Cláusula 32",
                              recurrente=True, costo_actual=c_ba_a, costo_nuevo=c_ba_n, suj_inc=False)
        st.markdown("---")

        # APV
        bhead("APV Empresa (matching)","Cláusula 39",True,
              "Empresa iguala el aporte del trabajador. Tope $10.000/mes por persona.")
        ap1,ap2,ap3,ap4 = st.columns(4)
        apv_va = ap1.number_input("Aporte máx/mes actual (CLP)", value=10000, step=500, key="apv_va")
        apv_vn = ap2.number_input("Aporte máx/mes nuevo (CLP)",  value=10000, step=500, key="apv_vn")
        apv_pa = ap3.number_input("% adhesión actual (0-1)", value=0.70, step=0.05, min_value=0.0, max_value=1.0, key="apv_pa")
        apv_pn = ap4.number_input("% adhesión nuevo  (0-1)", value=0.70, step=0.05, min_value=0.0, max_value=1.0, key="apv_pn")
        c_apv_a = apv_va*12*apv_pa*N; c_apv_n = apv_vn*12*apv_pn*N
        cost_box(c_apv_a, c_apv_n, False)
        NV["apv"] = dict(nombre="APV Empresa", clausula="Cláusula 39",
                         recurrente=True, costo_actual=c_apv_a, costo_nuevo=c_apv_n, suj_inc=False)
        st.markdown("---")

        # Seguros
        bhead("Seguros de Vida y Accidentes","Cláusula 38",True,
              "Prima estimada por persona/año (vida UF2.000 + accidentes personales UF130).")
        sg1,sg2,_,_ = st.columns(4)
        seg_va = sg1.number_input("Prima anual/persona actual (CLP)", value=80000, step=5000, key="seg_va")
        seg_vn = sg2.number_input("Prima anual/persona nueva (CLP)",  value=80000, step=5000, key="seg_vn")
        c_seg_a = seg_va*N; c_seg_n = seg_vn*N
        cost_box(c_seg_a, c_seg_n, False)
        NV["seguro_v"] = dict(nombre="Seguros Vida+Accidentes", clausula="Cláusula 38",
                              recurrente=True, costo_actual=c_seg_a, costo_nuevo=c_seg_n, suj_inc=False)

    # ════════════════════════════════════════
    # 6. INCREMENTO REAL
    # ════════════════════════════════════════
    with st.expander("📈 Incremento Real Pactado (HV + SB)", expanded=False):
        bhead("Incremento Real","Cláusula 43",True,
              "1% anual acumulativo sobre HV y SB. Se costea como el delta incremental del año 1.")
        ir1,ir2,_,_ = st.columns(4)
        ir_pa = ir1.number_input("% anual actual", value=inc_r, step=0.5, min_value=0.0, key="ir_pa")
        ir_pn = ir2.number_input("% anual nuevo",  value=inc_r, step=0.5, min_value=0.0, key="ir_pn")
        c_ir_a = (c_hv_a+c_sb_a)*ir_pa/100
        c_ir_n = (c_hv_n+c_sb_n)*ir_pn/100
        cost_box(c_ir_a, c_ir_n, True)
        NV["inc_real"] = dict(nombre="Incremento Real HV+SB", clausula="Cláusula 43",
                              recurrente=True, costo_actual=c_ir_a, costo_nuevo=c_ir_n, suj_inc=True)

    # ════════════════════════════════════════
    # 7. ONE-TIME
    # ════════════════════════════════════════
    with st.expander("⚡ Pagos One-Time", expanded=False):
        bhead("Bono Término Negociación Colectiva","Cláusula 42",False,
              "Pago único sep-2023. NO forma parte del piso del próximo contrato.")
        bt1,bt2,_,_ = st.columns(4)
        bt_va = bt1.number_input("Valor actual/persona (CLP)", value=4200000, step=100000, key="bt_va")
        bt_vn = bt2.number_input("Valor nuevo/persona (CLP)",  value=4200000, step=100000, key="bt_vn")
        c_bt_a = bt_va*N; c_bt_n = bt_vn*N
        cost_box(c_bt_a, c_bt_n, False)
        NV["bono_term"] = dict(nombre="Bono Término NC", clausula="Cláusula 42",
                               recurrente=False, costo_actual=c_bt_a, costo_nuevo=c_bt_n, suj_inc=False)

    # ════════════════════════════════════════
    # TOTALES TAB 1
    # ════════════════════════════════════════
    st.markdown('<div class="sec">📊 Resumen Consolidado</div>', unsafe_allow_html=True)

    T_ACT = sum(v["costo_actual"] for v in NV.values() if v["recurrente"])
    T_NEW = sum(v["costo_nuevo"]  for v in NV.values() if v["recurrente"])
    T_ONE = sum(v["costo_actual"] for v in NV.values() if not v["recurrente"])
    DELTA = T_NEW - T_ACT

    r1,r2,r3,r4 = st.columns(4)
    mc(r1, "Costo Recurrente Actual / Año", T_ACT)
    mc(r2, "Costo Recurrente Nuevo / Año",  T_NEW, DELTA)
    mc(r3, "Costo x Trabajador / Año (actual)", T_ACT/max(N,1))
    mc(r4, "Bono Firma One-Time", T_ONE)

    # Guardar estado para otros tabs
    st.session_state.update(dict(NV=NV, T_ACT=T_ACT, T_NEW=T_NEW, T_ONE=T_ONE, N=N,
                                 c_hv_a=c_hv_a, c_sb_a=c_sb_a))

# ══════════════════════════════════════════════
# TAB 2 — EVOLUCIÓN & CAGR
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec">Evolución del Costo — Punta a Punta</div>', unsafe_allow_html=True)
    NV    = st.session_state.get("NV",{})
    T_ACT = st.session_state.get("T_ACT",0)
    T_NEW = st.session_state.get("T_NEW",0)

    if not NV:
        st.info("Ajusta los parámetros en el Tab 1 primero.")
    else:
        yrs = list(range(anios+1))
        labs = [f"Año {y}" for y in yrs]
        c_acts, c_news = [], []
        for yr in yrs:
            f = fi(yr, inc_r)
            ca = cn = 0
            for v in NV.values():
                if not v["recurrente"]: continue
                ca += v["costo_actual"]*f if v["suj_inc"] else v["costo_actual"]
                cn += v["costo_nuevo"] *f if v["suj_inc"] else v["costo_nuevo"]
            c_acts.append(ca); c_news.append(cn)

        cg_a = cagr(c_acts[0],c_acts[-1],anios)
        cg_n = cagr(c_news[0],c_news[-1],anios)
        dp   = c_news[-1]-c_acts[-1]
        dpp  = dp/c_acts[-1]*100 if c_acts[-1] else 0

        k1,k2,k3,k4 = st.columns(4)
        for col,lbl,val,suf in [(k1,"CAGR Actual",cg_a,"%"),(k2,"CAGR Nuevo",cg_n,"%"),
                                 (k3,f"Δ% Año {anios}",dpp,"%"),(k4,f"Δ Abs Año {anios}",dp/1e6,"M CLP")]:
            col_v = ROJO if "Δ" in lbl and val>0 else AZUL
            col.markdown(f"""
            <div class="mc"><div class="lbl">{lbl}</div>
            <div class="val" style="color:{col_v}">{val:.2f}{suf}</div></div>""",
            unsafe_allow_html=True)

        fig=go.Figure()
        fig.add_trace(go.Bar(name="Actual",x=labs,y=[c/1e6 for c in c_acts],marker_color=AZUL,opacity=.85))
        fig.add_trace(go.Bar(name="Nuevo", x=labs,y=[c/1e6 for c in c_news],marker_color=ROJO,opacity=.85))
        fig.add_trace(go.Scatter(name="Δ",x=labs,y=[(n-a)/1e6 for n,a in zip(c_news,c_acts)],
                                  mode="lines+markers",line=dict(color=AMBAR,width=2,dash="dot"),yaxis="y2"))
        fig.update_layout(barmode="group",title="Costo Recurrente Anual — Actual vs. Nuevo",
                          yaxis=dict(title="CLP M"),
                          yaxis2=dict(title="Δ CLP M",overlaying="y",side="right",showgrid=False),
                          legend=dict(orientation="h",y=1.08),
                          plot_bgcolor=BLANC,paper_bgcolor=GRIS,font=dict(color=AZUL),height=420)
        st.plotly_chart(fig,use_container_width=True)

        df_pp = pd.DataFrame({"Año":labs,
            "Actual (CLP M)":[f"${c/1e6:.2f}" for c in c_acts],
            "Nuevo (CLP M)": [f"${c/1e6:.2f}" for c in c_news],
            "Δ CLP M":       [f"${(n-a)/1e6:+.2f}" for n,a in zip(c_news,c_acts)],
            "Δ %":           [f"{(n-a)/a*100:+.2f}%" for n,a in zip(c_news,c_acts)],
            "Actual (USD M)":[f"${c/tc_usd/1e6:.2f}" for c in c_acts],
            "Nuevo (USD M)": [f"${c/tc_usd/1e6:.2f}" for c in c_news]})
        st.dataframe(df_pp,use_container_width=True,hide_index=True)

        cat_map = {
            "Rem. Directas":["hv","sb","gratif"],
            "Bonos Recur.": ["asist","fiestas","navidad","bono_des","bono_prod"],
            "Bonos Oper.":  ["psvnc","ext_psv","cambio_v","cancel_v","turno5","turno_atp","pre_libre","high_rank"],
            "Asignaciones": ["escolar","matrimon","nacim","fallec"],
            "Especie/Otros":["viatico_n","viatico_i","moviliz","bono_ant","apv","seguro_v"],
            "Inc. Real":    ["inc_real"],
        }
        cnames=[]; cdels=[]
        for cn2,ids in cat_map.items():
            d=sum((NV[b]["costo_nuevo"]-NV[b]["costo_actual"]) for b in ids if b in NV)/1e6
            cnames.append(cn2); cdels.append(d)

        fig2=go.Figure(go.Bar(x=cnames,y=cdels,
            marker_color=[ROJO if d>0 else VERDE for d in cdels],
            text=[f"${d:+.1f}M" for d in cdels],textposition="outside"))
        fig2.update_layout(title="Δ Nuevo vs. Actual por Categoría",
                           yaxis_title="CLP M",plot_bgcolor=BLANC,paper_bgcolor=GRIS,
                           font=dict(color=AZUL),height=360)
        st.plotly_chart(fig2,use_container_width=True)

        pie_l=[]; pie_v=[]
        for cn2,ids in cat_map.items():
            v=sum(NV[b]["costo_actual"] for b in ids if b in NV)
            if v>0: pie_l.append(cn2); pie_v.append(v)
        fig3=go.Figure(go.Pie(labels=pie_l,values=pie_v,hole=.5,
                               marker_colors=[AZUL,ROJO,"#4B6FD4","#E05C6E","#7B93D9",AMBAR],
                               textinfo="label+percent"))
        fig3.update_layout(title="Composición Costo Actual",paper_bgcolor=GRIS,
                           font=dict(color=AZUL),height=360,
                           annotations=[dict(text=f"${sum(pie_v)/1e6:.0f}M",
                                             x=.5,y=.5,font_size=16,font_color=AZUL,showarrow=False)])
        st.plotly_chart(fig3,use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — SIMULADOR
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec">Simulador de Propuesta — Nuevo Contrato</div>', unsafe_allow_html=True)
    NV    = st.session_state.get("NV",{})
    T_ACT = st.session_state.get("T_ACT",0)

    if not NV:
        st.info("Completa el Tab 1 primero.")
    else:
        s1,s2 = st.columns([2,1])
        with s1:
            st.markdown("#### Palancas de Negociación")
            i_hv  = st.slider("Incremento adicional HV (%)",     0.0,25.0,0.0,.5)
            i_sb  = st.slider("Incremento adicional SB (%)",     0.0,25.0,0.0,.5)
            i_bon = st.slider("Incremento bonos recurrentes (%)",0.0,25.0,0.0,.5)
            i_dot = st.slider("Variación dotación (%)",         -20, 30,  0,  1)
            st.markdown("#### Nuevos Beneficios")
            nb1n = st.text_input("Nombre beneficio nuevo 1","Bono Bienestar")
            nb1v = st.number_input("Valor anual total (CLP)",value=0,step=100000,key="nb1")
            nb2n = st.text_input("Nombre beneficio nuevo 2","")
            nb2v = st.number_input("Valor anual total (CLP)",value=0,step=100000,key="nb2")

        with s2:
            df = 1+i_dot/100
            hv_s = NV.get("hv",{}).get("costo_actual",0)*(1+i_hv/100)*df
            sb_s = NV.get("sb",{}).get("costo_actual",0)*(1+i_sb/100)*df
            gr_s = (hv_s+sb_s)*0.0833
            c_sim = hv_s+sb_s+gr_s
            for bid,v in NV.items():
                if bid in ("hv","sb","gratif") or not v["recurrente"]: continue
                m = (1+i_bon/100) if bid in ("asist","fiestas","navidad","bono_des","bono_prod") else 1
                c_sim += v["costo_actual"]*m*df
            c_sim += nb1v+nb2v

            delta_s = c_sim-T_ACT
            pct_s   = delta_s/T_ACT*100 if T_ACT else 0
            cagr_s  = cagr(T_ACT, c_sim*fi(anios,inc_r), anios)
            cs_col  = ROJO if delta_s>0 else VERDE
            sign_s  = "+" if delta_s>=0 else ""

            for lbl,val in [("Costo Actual Recurrente",T_ACT),("Costo Simulado Nuevo",c_sim)]:
                st.markdown(f"""
                <div class="mc"><div class="lbl">{lbl}</div>
                <div class="val">${val/1e6:.2f}M CLP</div>
                <div class="sub">${val/tc_usd/1e6:.2f}M USD</div></div>""",unsafe_allow_html=True)

            st.markdown(f"""
            <div class="mc"><div class="lbl">Variación vs. Actual</div>
            <div class="val" style="color:{cs_col}">{sign_s}{pct_s:.2f}%</div>
            <div class="sub">{sign_s}${delta_s/1e6:.2f}M CLP/año</div></div>
            <div class="mc"><div class="lbl">CAGR Simulado ({anios}a)</div>
            <div class="val">{cagr_s:.2f}%</div>
            <div class="sub">Inc. real {inc_r:.1f}%/a incluido</div></div>""",unsafe_allow_html=True)

            cpp_s = c_sim*fi(anios,inc_r); cpp_a = T_ACT*fi(anios,inc_r)
            st.markdown(f"""
            <div class="mc"><div class="lbl">Costo Año {anios} (punta)</div>
            <div class="val">${cpp_s/1e6:.2f}M CLP</div>
            <div class="sub" style="color:{ROJO}">${(cpp_s-cpp_a)/1e6:+.2f}M vs. actual</div>
            </div>""",unsafe_allow_html=True)

        yl2=[f"Año {y}" for y in range(anios+1)]
        ca_y=[T_ACT*fi(y,inc_r) for y in range(anios+1)]
        cs_y=[c_sim*fi(y,inc_r) for y in range(anios+1)]
        fs=go.Figure()
        fs.add_trace(go.Scatter(x=yl2,y=[c/1e6 for c in ca_y],name="Actual",
                                mode="lines+markers",line=dict(color=AZUL,width=3),marker=dict(size=8)))
        fs.add_trace(go.Scatter(x=yl2,y=[c/1e6 for c in cs_y],name="Simulado",
                                mode="lines+markers",line=dict(color=ROJO,width=3,dash="dash"),marker=dict(size=8)))
        fs.update_layout(title="Trayectoria Actual vs. Simulado",yaxis_title="CLP M",
                         plot_bgcolor=BLANC,paper_bgcolor=GRIS,font=dict(color=AZUL),height=380,
                         legend=dict(orientation="h",y=1.08))
        st.plotly_chart(fs,use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec">Resumen Ejecutivo</div>', unsafe_allow_html=True)
    NV    = st.session_state.get("NV",{})
    T_ACT = st.session_state.get("T_ACT",0)
    T_NEW = st.session_state.get("T_NEW",0)
    T_ONE = st.session_state.get("T_ONE",0)
    NN    = st.session_state.get("N",N)

    if not NV:
        st.info("Completa el Tab 1 primero.")
    else:
        st.markdown(f"""
        <div style="background:{BLANC};border-radius:10px;padding:18px 24px;
                    box-shadow:0 1px 6px rgba(0,0,0,.07);margin-bottom:14px">
          <h3 style="color:{AZUL};margin-top:0">Contrato Colectivo · STCLE / Transporte Aéreo S.A.</h3>
          <p style="color:#4B5563;margin:0">
            01/09/2023 – 31/08/2026 &nbsp;|&nbsp; Dotación: <b>{NN}</b> &nbsp;|&nbsp; TC: ${tc_usd:,} CLP/USD
          </p><hr style="border-color:#E5E7EB;margin:10px 0">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px">
            <div><div style="font-size:11px;color:#6B7280;text-transform:uppercase">Costo recurrente actual/año</div>
                 <div style="font-size:22px;font-weight:700;color:{AZUL}">${T_ACT/1e6:.1f}M CLP</div>
                 <div style="font-size:12px;color:#9CA3AF">${T_ACT/tc_usd/1e6:.2f}M USD</div></div>
            <div><div style="font-size:11px;color:#6B7280;text-transform:uppercase">Costo x trabajador/año</div>
                 <div style="font-size:22px;font-weight:700;color:{AZUL}">${T_ACT/max(NN,1)/1e3:,.0f}K CLP</div>
                 <div style="font-size:12px;color:#9CA3AF">${T_ACT/max(NN,1)/tc_usd/1e3:.1f}K USD</div></div>
            <div><div style="font-size:11px;color:#6B7280;text-transform:uppercase">Bono firma one-time</div>
                 <div style="font-size:22px;font-weight:700;color:{ROJO}">${T_ONE/1e6:.1f}M CLP</div>
                 <div style="font-size:12px;color:#9CA3AF">${T_ONE/tc_usd/1e6:.2f}M USD</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        rows=[]
        for v in NV.values():
            d=v["costo_nuevo"]-v["costo_actual"]
            rows.append({"Beneficio":v["nombre"],"Cláusula":v["clausula"],
                "Tipo":"Recurrente" if v["recurrente"] else "One-Time",
                "Costo Actual CLP":f"${v['costo_actual']:,.0f}",
                "Costo Nuevo CLP": f"${v['costo_nuevo']:,.0f}",
                "Δ CLP":f"${d:+,.0f}",
                "Δ %":f"{d/v['costo_actual']*100:+.1f}%" if v["costo_actual"] else "N/A",
                "Inc.Real":"✓" if v["suj_inc"] else "—"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,height=520)

        st.markdown("---")
        d_tot=T_NEW-T_ACT; s_t="+" if d_tot>=0 else ""; c_t=ROJO if d_tot>0 else VERDE
        rf1,rf2=st.columns(2)
        rf1.markdown(f"""
        <div class="mc"><div class="lbl">Total recurrente actual / año</div>
        <div class="val">${T_ACT/1e6:.2f}M CLP · ${T_ACT/tc_usd/1e6:.2f}M USD</div>
        <div class="sub">Por trabajador: ${T_ACT/max(NN,1)/1e3:,.0f}K CLP</div></div>""",unsafe_allow_html=True)
        rf2.markdown(f"""
        <div class="mc"><div class="lbl">Total recurrente nuevo / año</div>
        <div class="val">${T_NEW/1e6:.2f}M CLP · ${T_NEW/tc_usd/1e6:.2f}M USD</div>
        <div class="sub" style="color:{c_t}">{s_t}${d_tot/1e6:.2f}M vs. actual</div></div>""",unsafe_allow_html=True)

        cg_f=cagr(T_ACT,T_ACT*fi(anios,inc_r),anios)
        st.markdown(f"""
        <div style="background:{AZUL};color:white;border-radius:10px;padding:14px 24px;
                    margin-top:12px;display:flex;gap:36px;align-items:center;flex-wrap:wrap">
          <div><div style="font-size:10px;opacity:.7">CAGR Actual ({anios}a)</div>
               <div style="font-size:20px;font-weight:700">{cg_f:.2f}%</div></div>
          <div><div style="font-size:10px;opacity:.7">Inc. Real / año</div>
               <div style="font-size:20px;font-weight:700">{inc_r:.1f}%</div></div>
          <div><div style="font-size:10px;opacity:.7">Período contrato</div>
               <div style="font-size:20px;font-weight:700">36 meses</div></div>
          <div><div style="font-size:10px;opacity:.7">TC USD</div>
               <div style="font-size:20px;font-weight:700">${tc_usd:,}</div></div>
          <div><div style="font-size:10px;opacity:.7">Dotación</div>
               <div style="font-size:20px;font-weight:700">{NN}</div></div>
        </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top:36px;padding:10px 0;border-top:2px solid #E5E7EB;
            text-align:center;font-size:11px;color:#9CA3AF">
  STCLE · Sindicato Tripulantes de Cabina LAN Express &nbsp;|&nbsp; Modelo de costeo CC · Uso interno
</div>""", unsafe_allow_html=True)
