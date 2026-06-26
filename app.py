import streamlit as st
import pandas as pd

# =====================================================================
# 1. CONFIGURACIÓN VISUAL DASHBOARD PROFESIONAL
# =====================================================================
st.set_page_config(page_title="UltraCred - Dashboard de Cobranzas", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.8rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    .card-caja {
        background: linear-gradient(135deg, #ffffff 0%, #fffdf9 100%);
        padding: 18px;
        border-radius: 14px;
        border-left: 5px solid #f59e0b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 12px;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    .card-compensacion {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border-top: 4px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .card-detalle-credito {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .fecha-kpi {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        margin-top: -5px;
    }
    </style>
""", unsafe_allow_html=True)

# Cambio de Título Solicitado
st.title("📈 Reporte UltraCred")
st.caption("Conectado en tiempo real a Google Sheets (Nube)")
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
        st.error(f"❌ No se pudo conectar con el reporte en la nube. Error: {e}")
        st.stop()

df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)

# =====================================================================
# 3. PROCESAMIENTO Y PARSING DE NÚMEROS (BLINDADO REGIONAL ARGENTINA)
# =====================================================================
def forzar_numero(val):
    try:
        s = str(val).strip().replace("$", "").replace("%", "").replace(" ", "")
        if not s:
            return 0.0
        
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        
        if "." in s:
            if s.count(".") > 1:
                s = s.replace(".", "")
            else:
                partes = s.split(".")
                if len(partes[1]) == 3:
                    s = s.replace(".", "")
                    
        return float(s)
    except:
        return 0.0

def obtener_valor_kpi(lista_claves):
    for fila_idx, fila in df_real.iterrows():
        fila_texto = " ".join(fila.astype(str)).upper()
        if any(clave.upper() in fila_texto for clave in lista_claves):
            for celda in reversed(fila):
                num = forzar_numero(celda)
                if num is not None and num != 0.0:
                    return num
    return 0.0

# =====================================================================
# 4. EXTRACCIÓN DE DATOS DINÁMICOS
# =====================================================================
try:
    fecha_referencia = str(df_real.iloc[0, 1]).strip()
except:
    fecha_referencia = "Fecha no disponible"

# KPIs principales
total_cobrado_dia_anterior = obtener_valor_kpi(["COBRADO", "TOTAL COBRADO"]) 
capital_vendido = obtener_valor_kpi(["CAPITAL VENDIDO", "TOTAL VENDIDO", "CAPITAL VENDIDO (K)"])
morosidad_total = obtener_valor_kpi(["MORA TOTAL", "MOROSIDAD ACUMULADA", "% EN MORA"])     

# Composición de Caja
efectivo = obtener_valor_kpi(["EFECTIVO"])
macro_fci = obtener_valor_kpi(["MACRO"])
debito_suarez = obtener_valor_kpi(["SUAREZ", "DÉBITO"])
total_caja = obtener_valor_kpi(["TOTAL CAJA", "CAJA TOTAL"])

if 0 < morosidad_total < 1.0:
    morosidad_total = morosidad_total * 100.0

# =====================================================================
# JERARQUÍA 1 y 2: TOTAL COBRADO Y CAPITAL VENDIDO (LADO A LADO)
# =====================================================================
col_jer1, col_jer2 = st.columns(2)
with col_jer1:
    st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
    st.markdown(f"<p class='fecha-kpi'>📅 Ref: {fecha_referencia}</p>", unsafe_allow_html=True)
with col_jer2:
    st.metric(label="📉 Capital Vendido (K)", value=f"$ {capital_vendido:,.2f}")
    st.markdown(f"<p class='fecha-kpi'>📅 Ref: {fecha_referencia}</p>", unsafe_allow_html=True)

# =====================================================================
# JERARQUÍA 3: PORCENTAJE MOROSIDAD TOTAL + CRÉDITOS A COBRAR DETALLADO
# =====================================================================
st.markdown("---")
col_mora, col_creditos = st.columns([1, 1])

with col_mora:
    st.metric(label="📊 Porcentaje Morosidad Total", value=f"{morosidad_total:.2f}%")

with col_creditos:
    st.markdown("<div class='card-detalle-credito'>", unsafe_allow_html=True)
    st.markdown("<span style='color: #64748b; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;'>💼 Estado de Créditos a Cobrar (Filas 90-93)</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    try:
        # Extraemos dinámicamente las filas 90 a 93 (índices 89 a 93 en Pandas)
        for r_idx in range(89, 93):
            concepto = str(df_real.iloc[r_idx, 0]).strip()
            monto_raw = df_real.iloc[r_idx, 1]
            monto_num = forzar_numero(monto_raw)
            if concepto:
                st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed #f1f5f9;'>
                        <span style='color: #475569; font-size: 0.95rem; font-weight: 500;'>{concepto}</span>
                        <span style='color: #0f172a; font-size: 0.95rem; font-weight: 700;'>$ {monto_num:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
    except:
        st.caption("No se pudieron leer las filas 90-93 de créditos.")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# JERARQUÍA 4: COMPOSICIÓN Y DISPONIBILIDAD DE CAJA
# =====================================================================
st.markdown("---")
st.subheader("🏦 Composición y Disponibilidad de Caja")
col_caja1, col_caja2, col_caja3, col_caja4 = st.columns(4)

with col_caja1:
    st.markdown(f"<div class='card-caja' style='border-left-color: #10b981;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>💵 EFECTIVO</span><br><span style='font-size:1.5rem; font-weight:800; color:#059669;'>$ {efectivo:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja2:
    st.markdown(f"<div class='card-caja' style='border-left-color: #3b82f6;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>🏛️ BANCOS (MACRO + FCI)</span><br><span style='font-size:1.5rem; font-weight:800; color:#2563eb;'>$ {macro_fci:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja3:
    st.markdown(f"<div class='card-caja' style='border-left-color: #8b5cf6;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>💳 DÉBITO + CNEL. SUAREZ</span><br><span style='font-size:1.5rem; font-weight:800; color:#7c3aed;'>$ {debito_suarez:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja4:
    st.markdown(f"<div class='card-caja' style='border-left-color: #475569;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>📈 TOTAL GENERAL EN CAJA</span><br><span style='font-size:1.5rem; font-weight:800; color:#1e293b;'>$ {total_caja:,.2f}</span></div>", unsafe_allow_html=True)

# =====================================================================
# JERARQUÍA 5: PRÓXIMAS COMPENSACIONES
# =====================================================================
st.markdown("---")
st.subheader("📅 Próximas Compensaciones")

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
                st.markdown(f"""
                    <div class='card-compensacion'>
                        <span style='color:#4b5563; font-size:0.85rem; font-weight:700; text-transform:uppercase;'>⏳ {item['fecha']}</span><br>
                        <span style='font-size:1.4rem; font-weight:800; color:#1d4ed8;'>$ {item['monto']:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='card-compensacion' style='border-top-color: #e5e7eb;'>
                        <span style='color:#9ca3af; font-size:0.85rem;'>Sin compensaciones programadas</span>
                    </div>
                """, unsafe_allow_html=True)
except Exception as e:
    st.warning("⚠️ Nota: Ocurrió un inconveniente al cargar el rango de compensaciones.")

# =====================================================================
# JERARQUÍA 6: PANEL DE PORCENTAJE DE MORA HISTÓRICA (DESDE FILA 11)
# =====================================================================
st.markdown("---")
st.subheader("🚨 Panel de Control de Mora Histórica")

dic_meses = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

registros_mora = []
# Leemos de manera segura todo el histórico desde la fila 11 (índice 10 en adelante)
for idx, fila in df_real.iloc[10:].iterrows():
    fila_str = " ".join(fila.astype(str)).upper()
    
    # Buscamos patrones de meses y años dentro del texto de la fila completa
    if any(m in fila_str for m in dic_meses.keys()):
        periodo = ""
        mes_num = 1
        anio_detectado = "2025"
        
        # Encontrar qué año y mes corresponden
        for m, n in dic_meses.items():
            if m in fila_str:
                if "2024" in fila_str: anio_detectado = "2024"
                elif "2026" in fila_str: anio_detectado = "2026"
                elif "2027" in fila_str: anio_detectado = "2027"
                else: anio_detectado = "2025"
                
                periodo = f"{m} {anio_detectado}"
                mes_num = n
                break
        
        # Obtenemos la métrica numérica de morosidad buscando desde atrás
        for celda in reversed(fila):
            num = forzar_numero(celda)
            if num is not None and 0.0 < num < 100.0:
                val_mora = num * 100.0 if num < 1.0 else num
                registros_mora.append({
                    "Período Comercial": periodo, 
                    "% En Mora": val_mora,
                    "Año": anio_detectado,
                    "Orden_Fecha": int(anio_detectado) * 100 + mes_num
                })
                break

if registros_mora:
    df_mora = pd.DataFrame(registros_mora).drop_duplicates(subset=["Período Comercial"])
    df_mora = df_mora.sort_values(by="Orden_Fecha").reset_index(drop=True)

    # Obtenemos la lista única de años detectados para armar el filtro dinámico
    lista_anios = ["Todos los años"] + sorted(list(df_mora["Año"].unique()), reverse=True)

    # Controles de filtros paralelos
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_anio = st.selectbox("📅 Filtrar por Año Comercial:", lista_anios)
    with col_filtro2:
        filtro_mora = st.selectbox("🔍 Filtrar por Nivel de Criticidad:", 
                                   ["Todos los meses", "Mora Crítica (Mayor a 12%)", "Mora Alerta (10% a 12%)", "Mora Controlada (Menor a 10%)"])

    # Aplicar Filtro 1: Año
    if filtro_anio != "Todos los años":
        df_filtrado = df_mora[df_mora["Año"] == filtro_anio]
    else:
        df_filtrado = df_mora

    # Aplicar Filtro 2: Criticidad
    if filtro_mora == "Mora Crítica (Mayor a 12%)": 
        df_filtrado = df_filtrado[df_filtrado["% En Mora"] > 12.0]
    elif filtro_mora == "Mora Alerta (10% a 12%)": 
        df_filtrado = df_filtrado[(df_filtrado["% En Mora"] >= 10.0) & (df_filtrado["% En Mora"] <= 12.0)]
    elif filtro_mora == "Mora Controlada (Menor a 10%)": 
        df_filtrado = df_filtrado[df_filtrado["% En Mora"] < 10.0]

    def colorear_celda(val):
        if val > 12.0: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val > 10.0: return 'background-color: #fef3c7; color: #92400e;'
        return 'background-color: #e8f5e9; color: #1b5e20;'

    df_tabla_render = df_filtrado[["Período Comercial", "% En Mora"]]
    df_estilizado = (df_tabla_render.style.map(colorear_celda, subset=["% En Mora"]).format({"% En Mora": "{:.2f}%"}))

    col_tabla, col_grafico = st.columns([4, 5])
    with col_tabla:
        st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    with col_grafico:
        if not df_filtrado.empty:
            st.line_chart(df_filtrado.set_index("Período Comercial")["% En Mora"])
        else:
            st.info("No hay registros coincidentes para los filtros seleccionados.")

# =====================================================================
# 7. REVISIÓN DE ESTRUCTURA REAL (SOLO PARA DIAGNÓSTICO)
# =====================================================================
st.markdown("---")
with st.expander("🔍 PASO DE CONTROL: Ver cómo Streamlit está leyendo tu Planilla"):
    st.write("Acá abajo podés ver exactamente la matriz de datos que viene desde tu Google Sheets:")
    st.dataframe(df_real)
