import os
import sys
import subprocess
import socket
import io
import textwrap
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mis Consumos",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (MODO OSCURO Y BLOQUEO DE TECLADO)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        [data-testid="stHeader"] { background-color: rgba(0, 0, 0, 0) !important; }
        .block-container { padding: 1.2rem 0.8rem 2rem 0.8rem; max-width: 740px; }

        /* 🚫 BLOQUEO DEFINITIVO DEL TECLADO EN MÓVILES 🚫 */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            user-select: none !important;
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
        }
        
        div[data-testid="stRadio"] input {
             pointer-events: auto !important;
        }

        /* Bloquea la captura táctil de Plotly para permitir scroll de página fluido */
        .js-plotly-plot, .plotly, .plot-container, .main-svg {
            touch-action: pan-y !important;
            user-select: none !important;
            -webkit-user-select: none !important;
            -webkit-touch-callout: none !important;
        }

        h1, h2, h3, h4, h5, h6, 
        [data-testid="stMarkdownContainer"] h1, 
        [data-testid="stMarkdownContainer"] h2, 
        [data-testid="stMarkdownContainer"] h3, 
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6 {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        [data-testid="stExpander"] summary p {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            background-color: transparent !important;
            border-bottom-color: #2D323E !important;
            opacity: 1 !important;
        }
        div[data-testid="stTabs"] button[role="tab"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {
            color: #00D1B2 !important;
            -webkit-text-fill-color: #00D1B2 !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            border-bottom-color: #00D1B2 !important;
        }

        div[data-testid="stRadio"] *, div[data-testid="stSelectbox"] label * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: bold !important;
            opacity: 1 !important;
        }

        div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button, div[data-testid="stPopover"] > button {
            background-color: #1E222B !important;
            border: 1.5px solid #107C41 !important;
            border-radius: 8px !important;
            padding: 0.4rem 0.8rem !important;
            margin-top: 6px;
            width: 100% !important; 
        }
        div[data-testid="stButton"] > button *, div[data-testid="stDownloadButton"] > button *, div[data-testid="stPopover"] > button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover, div[data-testid="stPopover"] > button:hover {
            background-color: #107C41 !important;
            border-color: #107C41 !important;
        }
        div[data-testid="stButton"] > button:hover *, div[data-testid="stDownloadButton"] > button:hover *, div[data-testid="stPopover"] > button:hover * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        .credit-card-box { background-color: #1E222B; border: 1px solid #2D323E; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px;}
        .total-card-box { background: linear-gradient(135deg, #132433 0%, #1E222B 100%); border: 1.8px solid #00D1B2; border-radius: 12px; padding: 14px 16px; margin-top: 6px; margin-bottom: 14px; }
        .card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .card-name-title { font-size: 1rem; font-weight: 700; margin: 0; color: #FFFFFF !important; }
        .card-time-badge { font-size: 0.72rem; color: #A0AEC0; background: #2D323E; padding: 3px 8px; border-radius: 6px; font-weight: 500; }
        .card-metrics-grid { display: grid; grid-template-columns: 1.15fr 1fr 0.85fr; gap: 6px; text-align: center; }
        .submetric-box { background-color: #14171E; border: 1px solid #252A36; padding: 8px 4px; border-radius: 8px; }
        .submetric-lbl { font-size: 0.64rem; text-transform: uppercase; color: #94A3B8; font-weight: 600; margin-bottom: 3px; }
        .val-total { font-size: 1.05rem; font-weight: 700; color: #00E676; }
        .val-daily { font-size: 1.05rem; font-weight: 700; color: #38BDF8; }
        .val-payments { font-size: 1.05rem; font-weight: 700; color: #FBBF24; }
        .val-total-tot { font-size: 1.15rem; font-weight: 700; color: #00D1B2; }
        .val-daily-tot { font-size: 1.15rem; font-weight: 700; color: #38BDF8; }
        .val-payments-tot { font-size: 1.15rem; font-weight: 700; color: #FBBF24; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# HELPER: GENERADOR DE TABLAS ESTILO EXCEL
# ---------------------------------------------------------
def render_excel_table(df, currency_cols=None):
    if currency_cols is None:
        currency_cols = ["Suma de Valor", "Valor"]
    html = """
    <div style="overflow-x: auto; border-radius: 10px; border: 1.5px solid #107C41; margin-top: 8px; margin-bottom: 12px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);">
    <table style="width:100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 0.93rem; color: #FAFAFA;">
        <thead><tr style="background: linear-gradient(135deg, #107C41 0%, #0D5C30 100%); color: #FFFFFF;">
    """
    for col in df.columns:
        align = "right" if col in currency_cols or "Suma" in col or "Valor" in col else "left"
        html += f'<th style="padding: 11px 14px; border-bottom: 2px solid #1B9E52; text-align: {align}; font-weight: 700;">{col}</th>'
    html += '</tr></thead><tbody>'

    total_rows = len(df)
    for idx, row in df.iterrows():
        is_total_row = (idx == total_rows - 1) and any(str(v).upper().startswith("TOTAL") for v in row.values)
        if is_total_row:
            row_style = "background-color: #133322; font-weight: bold; border-top: 2px solid #107C41; color: #00E676;"
        else:
            row_bg = "#1A1D24" if idx % 2 == 0 else "#222733"
            row_style = f"background-color: {row_bg}; color: #FAFAFA;"

        html += f'<tr style="{row_style}">'
        for col in df.columns:
            val = row[col]
            align = "right" if col in currency_cols or "Suma" in col or "Valor" in col or isinstance(val, (int, float)) else "left"
            if isinstance(val, (int, float)):
                val_str = f"${val:,.2f}" if col in currency_cols or "Suma" in col or "Valor" in col else f"{val:,}"
            else:
                val_str = str(val)
            html += f'<td style="padding: 9px 14px; border-bottom: 1px solid #2A323D; text-align: {align};">{val_str}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    return html

# ---------------------------------------------------------
# CONEXIÓN GOOGLE DRIVE & CARGA DE DATOS
# ---------------------------------------------------------
EXCEL_URL = "https://drive.google.com/uc?export=download&id=1UpW_wHsvth7zf-vSHfRmqvVpqqHWJukG"

@st.cache_data(ttl=300)
def load_credit_card_data():
    response = requests.get(EXCEL_URL, timeout=30)
    response.raise_for_status()
    df = pd.read_excel(io.BytesIO(response.content), sheet_name="Todas las Tarjetas", usecols="A:E")
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {}
    for col in df.columns:
        if "Establecimiento" in col: rename_map[col] = "Establecimiento"
        elif "Terminada" in col: rename_map[col] = "Tarjeta Terminada en"
    df = df.rename(columns=rename_map)

    for text_col in ["Tarjeta", "Establecimiento"]:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).str.replace(r"[\r\n]|_x000D_", "", regex=True).str.strip()

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0.0)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"]).copy()
    df["Año"] = df["Fecha"].dt.year.astype(int)
    return df.sort_values(by="Fecha", ascending=False).reset_index(drop=True)

try:
    with st.spinner("Cargando consumos desde Google Drive..."):
        df_raw = load_credit_card_data()
except Exception as e:
    st.error(f"Error al conectar con Google Drive: {e}")
    st.stop()

# ---------------------------------------------------------
# CABECERA & BOTÓN REFRESCAR
# ---------------------------------------------------------
header_col1, header_col2 = st.columns([2.5, 1.5], vertical_alignment="center")
with header_col1:
    st.markdown("<h3 style='margin: 0; color: #FFFFFF !important;'>💳 Mis Consumos</h3>", unsafe_allow_html=True)
with header_col2:
    if st.button("🔄 Refrescar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------------
# FILTROS GLOBALES
# ---------------------------------------------------------
with st.expander("🔍 **Filtros Generales**", expanded=False):
    anios_disponibles = ["Todos"] + sorted(list(df_raw["Año"].unique()), reverse=True)
    f_anio = st.selectbox("Año General:", anios_disponibles, index=0)
    tarjetas_disponibles = ["Todas"] + sorted(list(df_raw["Tarjeta"].unique()))
    f_tarjeta = st.selectbox("Tarjeta General:", tarjetas_disponibles, index=0)

df_filtrado = df_raw.copy()
if f_anio != "Todos": df_filtrado = df_filtrado[df_filtrado["Año"] == f_anio]
if f_tarjeta != "Todas": df_filtrado = df_filtrado[df_filtrado["Tarjeta"] == f_tarjeta]

# ---------------------------------------------------------
# TARJETAS DE RESUMEN (KPIs)
# ---------------------------------------------------------
st.markdown("<h4 style='color: #FFFFFF !important; margin-top: 15px;'>💳 Resumen de Consumos</h4>", unsafe_allow_html=True)
if df_filtrado.empty:
    st.info("No se encontraron consumos con los filtros seleccionados.")
else:
    for tarjeta, g in df_filtrado.groupby("Tarjeta"):
        c_total = g["Valor"].sum()
        f_min, f_max = g["Fecha"].min(), g["Fecha"].max()
        n_dias = (f_max - f_min).days + 1
        gasto_dia = c_total / n_dias if n_dias > 0 else 0.0
        st.markdown(
            f"""
            <div class="credit-card-box">
                <div class="card-header-flex">
                    <span class="card-name-title">💳 {tarjeta}</span>
                    <span class="card-time-badge">⏱️ {n_dias:,} días</span>
                </div>
                <div class="card-metrics-grid">
                    <div class="submetric-box"><div class="submetric-lbl">Total</div><div class="val-total">${c_total:,.2f}</div></div>
                    <div class="submetric-box"><div class="submetric-lbl">/ Día</div><div class="val-daily">${gasto_dia:,.2f}</div></div>
                    <div class="submetric-box"><div class="submetric-lbl">Pagos</div><div class="val-payments">{len(g):,}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    tot_consumo = df_filtrado["Valor"].sum()
    tot_dias = (df_filtrado["Fecha"].max() - df_filtrado["Fecha"].min()).days + 1 if not df_filtrado.empty else 0
    tot_gasto_dia = tot_consumo / tot_dias if tot_dias > 0 else 0.0
    st.markdown(
        f"""
        <div class="total-card-box">
            <div class="card-header-flex">
                <span class="card-name-title" style="color: #00D1B2 !important;">⭐ TOTAL GENERAL</span>
                <span class="card-time-badge" style="background: rgba(0,209,178,0.15); color: #00D1B2;">⏱️ {tot_dias:,} días</span>
            </div>
            <div class="card-metrics-grid">
                <div class="submetric-box"><div class="submetric-lbl" style="color: #00D1B2;">Total</div><div class="val-total-tot">${tot_consumo:,.2f}</div></div>
                <div class="submetric-box"><div class="submetric-lbl" style="color: #38BDF8;">/ Día</div><div class="val-daily-tot">${tot_gasto_dia:,.2f}</div></div>
                <div class="submetric-box"><div class="submetric-lbl" style="color: #FBBF24;">Pagos</div><div class="val-payments-tot">{len(df_filtrado):,}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

# =========================================================
# SECCIÓN 1: SOLO TABLAS (ESTILO EXCEL)
# =========================================================
st.markdown("---")
st.markdown("<h3 style='color: #FFFFFF !important;'>📋 Tablas de Detalles</h3>", unsafe_allow_html=True)

tab_anio, tab_cat_anio, tab_tarjeta, tab_categoria = st.tabs(["Año \\ Valor", "Categoría \\ Año", "Tarjeta \\ Año", "Categoría \\ Valor"])

with tab_anio:
    if not df_filtrado.empty:
        tabla_anio = df_filtrado.groupby("Año", as_index=False)["Valor"].sum().rename(columns={"Año": "Etiquetas de fila", "Valor": "Suma de Valor"}).sort_values(by="Suma de Valor", ascending=False)
        tabla_anio["Etiquetas de fila"] = tabla_anio["Etiquetas de fila"].astype(str)
        fila_total = pd.DataFrame([{"Etiquetas de fila": "Total general", "Suma de Valor": tabla_anio["Suma de Valor"].sum()}])
        tabla_anio_final = pd.concat([tabla_anio, fila_total], ignore_index=True)
        st.markdown(render_excel_table(tabla_anio_final), unsafe_allow_html=True)

with tab_cat_anio:
    if not df_filtrado.empty:
        tabla_dinamica = df_filtrado.groupby(["Establecimiento", "Año"], as_index=False)["Valor"].sum().rename(columns={"Establecimiento": "Categoría", "Valor": "Suma de Valor"}).sort_values(by=["Categoría", "Año"])
        tabla_dinamica["Año"] = tabla_dinamica["Año"].astype(str) 
        st.markdown(render_excel_table(tabla_dinamica), unsafe_allow_html=True)

with tab_tarjeta:
    if not df_filtrado.empty:
        tabla_tarjeta = df_filtrado.groupby(["Tarjeta", "Año"], as_index=False)["Valor"].sum().rename(columns={"Valor": "Suma de Valor"}).sort_values(by=["Tarjeta", "Año"])
        tabla_tarjeta["Año"] = tabla_tarjeta["Año"].astype(str)
        fila_tot = pd.DataFrame([{"Tarjeta": "TOTAL GENERAL", "Año": "-", "Suma de Valor": tabla_tarjeta["Suma de Valor"].sum()}])
        tabla_tarjeta_final = pd.concat([tabla_tarjeta, fila_tot], ignore_index=True)
        st.markdown(render_excel_table(tabla_tarjeta_final), unsafe_allow_html=True)

with tab_categoria:
    if not df_filtrado.empty:
        tabla_cat = df_filtrado.groupby("Establecimiento", as_index=False)["Valor"].sum().rename(columns={"Establecimiento": "Etiquetas de fila", "Valor": "Suma de Valor"}).sort_values(by="Etiquetas de fila")
        fila_tot_cat = pd.DataFrame([{"Etiquetas de fila": "Total general", "Suma de Valor": tabla_cat["Suma de Valor"].sum()}])
        tabla_cat_final = pd.concat([tabla_cat, fila_tot_cat], ignore_index=True)
        st.markdown(render_excel_table(tabla_cat_final), unsafe_allow_html=True)


# =========================================================
# SECCIÓN 2: GRÁFICOS OPTIMIZADOS (ZOOM Y TECLADO BLOQUEADOS)
# =========================================================
st.markdown("---")
st.markdown("<h3 style='color: #FFFFFF !important;'>📊 Gráficos Dinámicos</h3>", unsafe_allow_html=True)

plotly_config = {
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': False,
    'showAxisDragHandles': False,
    'showAxisRangeEntryBoxes': False,
    'staticPlot': True
}

def wrap_labels(text, width=18):
    return '<br>'.join(textwrap.wrap(str(text), width=width))

tab_grafico_evolucion_anual, tab_grafico_flujo, tab_grafico_top = st.tabs([
    "📅 Evolución Anual",
    "📊 Flujo por Categoría", 
    "📈 Top 10 Gastos"
])

with tab_grafico_evolucion_anual:
    if not df_filtrado.empty:
        establecimientos = ["Todos"] + sorted(list(df_filtrado["Establecimiento"].dropna().unique()))
        
        # OPCIÓN 1: POPOVER + RADIO BUTTONS (CERO TECLADO EN MÓVILES)
        if "est_seleccionado" not in st.session_state:
            st.session_state.est_seleccionado = "Todos"
            
        with st.popover(f"📍 Filtro: {st.session_state.est_seleccionado}"):
            # st.radio es puramente táctil, jamás levanta teclado
            est_seleccionado = st.radio("Selecciona Establecimiento:", options=establecimientos, index=establecimientos.index(st.session_state.est_seleccionado), key="radio_est")
            if est_seleccionado != st.session_state.est_seleccionado:
                st.session_state.est_seleccionado = est_seleccionado
                st.rerun()
        
        df_chart_evo = df_filtrado.copy()
        if st.session_state.est_seleccionado != "Todos":
            df_chart_evo = df_chart_evo[df_chart_evo["Establecimiento"] == st.session_state.est_seleccionado]

        if not df_chart_evo.empty:
            df_evo_anual = df_chart_evo.groupby("Año")["Valor"].sum().reset_index()
            df_evo_anual = df_evo_anual.sort_values(by="Año", ascending=False)
            df_evo_anual["Año"] = df_evo_anual["Año"].astype(str)
            max_evo = df_evo_anual["Valor"].max() if not df_evo_anual.empty else 100
            
            st.markdown(f"<h5 style='color: #38BDF8; text-align: center;'>Evolución del Gasto: {st.session_state.est_seleccionado}</h5>", unsafe_allow_html=True)

            fig_evo_anual = px.bar(df_evo_anual, x="Valor", y="Año", orientation="h", template="plotly_dark", text="Valor")
            
            fig_evo_anual.update_traces(
                marker_color="#38BDF8", texttemplate="$%{x:,.2f}", textposition="outside", 
                cliponaxis=False, textfont=dict(color="#FFFFFF", size=11, family="sans-serif")
            )
            fig_evo_anual.update_xaxes(fixedrange=True)
            fig_evo_anual.update_yaxes(fixedrange=True)
            fig_evo_anual.update_layout(
                dragmode=False,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="", showticklabels=False, range=[0, max_evo * 1.35]),
                yaxis=dict(title="", type='category', tickfont=dict(color="#FFFFFF", size=12)), 
                margin=dict(l=45, r=40, t=10, b=10),
                height=250,
            )
            st.plotly_chart(fig_evo_anual, use_container_width=True, theme=None, config=plotly_config)
        else:
            st.info(f"No hay registros para '{st.session_state.est_seleccionado}'.")

with tab_grafico_flujo:
    if not df_filtrado.empty:
        anios_grafico = ["Todos"] + sorted(list(df_filtrado["Año"].unique()), reverse=True)
        anio_seleccionado = st.radio("Filtro de Año:", options=anios_grafico, horizontal=True)
        
        df_chart_flujo = df_filtrado.copy()
        if anio_seleccionado != "Todos":
            df_chart_flujo = df_chart_flujo[df_chart_flujo["Año"] == anio_seleccionado]

        if not df_chart_flujo.empty:
            df_flujo = df_chart_flujo.groupby("Establecimiento")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=True)
            df_flujo["Establecimiento_Corto"] = df_flujo["Establecimiento"].apply(lambda x: wrap_labels(x, 18))
            
            max_flujo = df_flujo["Valor"].max() if not df_flujo.empty else 100
            
            st.markdown(f"<h5 style='color: #00D1B2; text-align: center;'>Flujo por Establecimiento: {anio_seleccionado}</h5>", unsafe_allow_html=True)

            fig_flujo = px.bar(df_flujo, x="Valor", y="Establecimiento_Corto", orientation="h", template="plotly_dark", text="Valor")
            fig_flujo.update_traces(
                marker_color="#00D1B2", texttemplate="$%{x:,.2f}", textposition="outside", 
                cliponaxis=False, textfont=dict(color="#FFFFFF", size=11)
            )
            fig_flujo.update_xaxes(fixedrange=True)
            fig_flujo.update_yaxes(fixedrange=True)
            fig_flujo.update_layout(
                dragmode=False,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="", showticklabels=False, range=[0, max_flujo * 1.35]),
                yaxis=dict(title="", tickfont=dict(color="#FFFFFF", size=10)),
                margin=dict(l=70, r=40, t=10, b=10),
                height=max(350, len(df_flujo) * 45), 
            )
            st.plotly_chart(fig_flujo, use_container_width=True, theme=None, config=plotly_config)
        else:
            st.info(f"No hay registros para el año {anio_seleccionado}.")

with tab_grafico_top:
    if not df_filtrado.empty:
        top_est = df_filtrado.groupby("Establecimiento")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False).head(10)
        top_est["Establecimiento_Corto"] = top_est["Establecimiento"].apply(lambda x: wrap_labels(x, 18))
        
        max_valor = top_est["Valor"].max() if not top_est.empty else 100
        
        st.markdown("<h5 style='color: #FBBF24; text-align: center;'>Top 10 Categorías de Gasto</h5>", unsafe_allow_html=True)

        fig_top = px.bar(top_est, x="Valor", y="Establecimiento_Corto", orientation="h", text="Valor", template="plotly_dark")
        fig_top.update_traces(
            marker_color="#FBBF24", texttemplate="$%{x:,.2f}", textposition="outside", 
            cliponaxis=False, textfont=dict(color="#FFFFFF", size=11)
        )
        fig_top.update_xaxes(fixedrange=True)
        fig_top.update_yaxes(fixedrange=True)
        fig_top.update_layout(
            dragmode=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(categoryorder="total ascending", title="", tickfont=dict(color="#FFFFFF", size=10)),
            xaxis=dict(range=[0, max_valor * 1.35], showticklabels=False, title=""),
            margin=dict(l=70, r=40, t=10, b=10),
            height=420,
        )
        st.plotly_chart(fig_top, use_container_width=True, theme=None, config=plotly_config)

# =========================================================
# AUTO-EJECUCIÓN AL HACER DOBLE CLIC EN EL ARCHIVO .PY
# =========================================================
if __name__ == "__main__":
    if not os.environ.get("STREAMLIT_RUNNING"):
        os.environ["STREAMLIT_RUNNING"] = "true"
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
            
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("  DASHBOARD INICIADO CORRECTAMENTE")
        print("="*60)
        print("\n  PARA VER EL DASHBOARD EN TU CELULAR, ABRE CHROME Y ESCRIBE ESTA DIRECCION:\n")
        print(f"  👉  http://{IP}:8501  👈\n")
        print("="*60)
        print("  (Deja esta ventana negra abierta mientras usas el celular)")
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", sys.argv[0], "--server.address=0.0.0.0"])