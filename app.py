import streamlit as st
import pandas as pd

# =====================================================================
# 1. CONFIGURACIÓN VISUAL: DISEÑO DE ALTO CONTRASTE INSTITUTIONAL
# =====================================================================
st.set_page_config(page_title="UltraCred - Dashboard de Cobranzas", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* Fondo general de la app (Gris claro premium) */
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    
    /* Títulos y textos en color azul oscuro/pizarra */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #0f172a !important;
    }
    
    /* Contenedores de secciones para agrupar visualmente */
    .seccion-bloque {
        background-color: #ffffff !important;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Tarjetas de Métricas Internas (Estilo UltraCred) */
    div[data-testid="stMetric"] {
        background-color: #f1f5f9 !important;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #cbd5e1 !important;
    }
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
    }
    
    /* Bloque Especial de Créditos a Cobrar */
    .card-detalle-credito-nueva {
        background-color: #f1f5f9 !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #cbd5e1 !important;
    }
    .linea-credito {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #cbd5e1 !important;
    }
    .linea-credito:last-child {
        border-bottom: none !important;
    }
    .lbl-credito {
        color: #475569 !important;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .val-credito {
        color: #0f172a !important;
        font-size: 1rem;
        font-weight: 800;
    }
    
    /* Tarjetas de Caja Activa */
    .card-caja {
        background-color: #ffffff !important;
        padding: 16px;
        border-radius: 12px;
        border-left: 5px solid #f59e0b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Tarjetas de Compensaciones */
    .card-compensacion {
        background-color: #ffffff !important;
        padding: 14px;
        border-radius: 10px;
        border-top: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        text-align: center;
        border-left: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Panel de Control Operativo — UltraCred")
st.markdown("---")

# =====================================================================
# 2. VINCULACIÓN CON LA NUBE
# =====================================================================
URL_GOOGLE_SHEETS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYzZVnpesIun4fZkyvu2G1wOytYnrMJYn7rv9B87Ko3kxzhN1XGw3VLmvGrUNveg/pub?output=csv"

@st.cache_data(ttl=2) 
def cargar_datos_desde_nube(url):
    try:
        df = pd.read_csv(url, header=None, engine="python")
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        st.stop()

df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)

# =====================================================================
# 3. PROCESAMIENTO DE NÚMEROS
# =====================================================================
def forzar_numero(val):
    if not val: return 0.0
    s = str(val).strip().upper().replace("$", "").replace("%", "").replace(" ", "")
    if not s: return 0.0
    try:
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."): s = s.replace(".", "").replace(",", ".")
            else: s = s.replace(",", "")
        elif "," in s:
            if s.count(",") == 1 and len(s.split(",")[1]) <= 2: s = s.replace(",", ".")
            else: s = s.replace(",", "")
        elif "." in s and s.count(".") > 1: s = s.replace(".", "")
        elif "." in s and len(s.split(".")[1]) == 3: s = s.replace(".", "")
        return float(s)
    except:
        return 0.0

def obtener_valor_kpi(lista_claves):
    for fila_idx, fila in df_real.iterrows():
        fila_texto = " ".join(fila.astype(str)).upper()
        if any(clave.upper() in fila_texto for clave in lista_claves):
            for celda in fila:
                celda_str = str(celda).strip().upper()
                if any(clave.upper() in celda_str for clave in lista_claves): continue
                num = forzar_numero(celda)
                if num != 0.0: return num
    return 0.0

# =====================================================================
# 4. EXTRACCIÓN MAESTRA DE DATOS
# =====================================================================
try:
    fecha_referencia = str(df_real.iloc[0, 1]).strip()
except:
    fecha_referencia = "Falta Fecha"

# Métricas del bloque superior (Fila 1 a 4 del Excel)
try: capital_vendido = forzar_numero(df_real.iloc[1, 1])
except: capital_vendido = 0.0
if capital_vendido == 0.0:
    capital_vendido = obtener_valor_kpi(["VENTA (K)", "VENTA (K) DEL DÍA"])

intereses_convenios = obtener_valor_kpi(["INTERESES CONVENIOS", "CONVENIOS"])
total_cobrado_dia_anterior = obtener_valor_kpi(["TOTAL COBRADO", "COBRADO"]) 

# Resto de indicadores
morosidad_total = obtener_valor_kpi(["MORA TOTAL", "% EN MORA"])     
efectivo = obtener_valor_kpi(["EFECTIVO"])
macro_fci = obtener_valor_kpi(["MACRO"])
debito_suarez = obtener_valor_kpi(["SUAREZ", "DÉBITO"])
total_caja = obtener_valor_kpi(["TOTAL CAJA", "CAJA TOTAL"])

if 0 < morosidad_total < 1.0: 
    morosidad_total = morosidad_total * 100.0

try:
    monto_vencido_lbl = str(df_real.iloc[90, 0]).strip() 
    monto_vencido_val = forzar_numero(df_real.iloc[90, 1])
    cobrado_lbl = str(df_real.iloc[91, 0]).strip()       
    cobrado_val = forzar_numero(df_real.iloc[91, 1])
    monto_total_a_cobrar_val = forzar_numero(df_real.iloc[92, 1]) 
except:
    monto_vencido_lbl, monto_vencido_val = "MONTO VENCIDO", 0.0
    cobrado_lbl, cobrado_val = "COBRADO", 0.0
    monto_total_a_cobrar_val = 0.0

# =====================================================================
# RENDIMIENTO DE LA FECHA (NUEVO BLOQUE VISUAL UNIFICADO)
# =====================================================================
st.markdown(f"### 📅 Rendimiento Operativo del Día — Ref: {fecha_referencia}")
with st.container():
    st.markdown("<div class='seccion-bloque'>", unsafe_allow_html=True)
    col_v, col_c, col_i = st.columns(3)
    with col_v:
        st.metric(label="📉 Capital Vendido (K)", value=f"$ {capital_vendido:,.2f}")
    with col_c:
        st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
    with col_i:
        st.metric(label="🤝 Intereses Convenios", value=f"$ {intereses_convenios:,.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# RIESGO Y CARTERA TOTAL
# =====================================================================
st.markdown("### 📊 Estado de Riesgo & Carteras Activas")
with st.container():
    st.markdown("<div class='seccion-bloque'>", unsafe_allow_html=True)
    col_mora, col_creditos = st.columns([1, 1])
    with col_mora:
        st.metric(label="🚨 Porcentaje Morosidad Total", value=f"{morosidad_total:.2f}%")
    with col_creditos:
        st.markdown(f"""
            <div class='card-detalle-credito-nueva'>
                <label style='color: #475569; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;'>💼 MONTO TOTAL A COBRAR</label>
                <div style='color: #0f172a; font-size: 1.8rem; font-weight: 800; margin-bottom: 10px;'>$ {monto_total_a_cobrar_val:,.2f}</div>
                <div style='border-top: 1px solid #cbd5e1; padding-top: 5px;'>
                    <div class='linea-credito'>
                        <span class='lbl-credito'>🔹 {monto_vencido_lbl}</span>
                        <span class='val-credito'>$ {monto_vencido_val:,.2f}</span>
                    </div>
                    <div class='linea-credito'>
                        <span class='lbl-credito'>🔹 {cobrado_lbl}</span>
                        <span class='val-credito'>$ {cobrado_val:,.2f}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# DISPONIBILIDAD DE CAJA
# =====================================================================
st.markdown("### 🏦 Composición y Disponibilidad de Caja")
with st.container():
    st.markdown("<div class='seccion-bloque'>", unsafe_allow_html=True)
    col_caja1, col_caja2, col_caja3, col_caja4 = st.columns(4)
    with col_caja1:
        st.markdown(f"<div class='card-caja' style='border-left-color: #10b981;'><span style='color:#475569; font-size:0.8rem; font-weight:700;'>💵 EFECTIVO</span><br><span style='font-size:1.4rem; font-weight:800; color:#059669;'>$ {efectivo:,.2f}</span></div>", unsafe_allow_html=True)
    with col_caja2:
        st.markdown(f"<div class='card-caja' style='border-left-color: #3b82f6;'><span style='color:#475569; font-size:0.8rem; font-weight:700;'>🏛️ BANCOS (MACRO + FCI)</span><br><span style='font-size:1.4rem; font-weight:800; color:#2563eb;'>$ {macro_fci:,.2f}</span></div>", unsafe_allow_html=True)
    with col_caja3:
        st.markdown(f"<div class='card-caja' style='border-left-color: #8b5cf6;'><span style='color:#475569; font-size:0.8rem; font-weight:700;'>💳 DÉBITO + CNEL. SUAREZ</span><br><span style='font-size:1.4rem; font-weight:800; color:#7c3aed;'>$ {debito_suarez:,.2f}</span></div>", unsafe_allow_html=True)
    with col_caja4:
        st.markdown(f"<div class='card-caja' style='border-left-color: #475569;'><span style='color:#475569; font-size:0.8rem; font-weight:700;'>📈 TOTAL GENERAL EN CAJA</span><br><span style='font-size:1.4rem; font-weight:800; color:#1e293b;'>$ {total_caja:,.2f}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# PRÓXIMAS COMPENSACIONES
# =====================================================================
st.markdown("### 📅 Próximas Compensaciones")
with st.container():
    st.markdown("<div class='seccion-bloque'>", unsafe_allow_html=True)
    try:
        comp_datos = [
            {"fecha": str(df_real.iloc[118, 0]).strip(), "monto": forzar_numero(df_real.iloc[118, 1])},
            {"fecha": str(df_real.iloc[119, 0]).strip(), "monto": forzar_numero(df_real.iloc[119, 1])},
            {"fecha": str(df_real.iloc[120, 0]).strip(), "monto": forzar_numero(df_real.iloc[120, 1])},
            {"fecha": str(df_real.iloc[121, 0]).strip(), "monto": forzar_numero(df_real.iloc[121, 1])},
        ]
        col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
        columnas_lista = [col_comp1, col_comp2, col_comp3, col_comp4]
        for i, item in enumerate(comp_datos):
            with columnas_lista[i]:
                if item["fecha"] and item["monto"] > 0:
                    st.markdown(f"<div class='card-compensacion'> <span style='color:#475569; font-size:0.8rem; font-weight:700; text-transform:uppercase;'>⏳ {item['fecha']}</span><br><span style='font-size:1.25rem; font-weight:800; color:#1d4ed8;'>$ {item['monto']:,.2f}</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='card-compensacion' style='border-top-color: #cbd5e1;'><span style='color:#64748b; font-size:0.8rem;'>Sin vencimientos</span></div>", unsafe_allow_html=True)
    except:
        st.warning("⚠️ Error al cargar compensaciones.")
    st.markdown("</div>", unsafe_allow_html=True)

# (Se mantiene el código de Mora Histórica igual debajo)
