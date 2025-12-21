"""
Dashboard para Andrés - Gestión de Leads del Diagnóstico AI Readiness
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from integrations.sheets_connector import SheetsConnector
from core.models import Tier

# Configuración de página
st.set_page_config(
    page_title="Dashboard - AI Readiness",
    page_icon="📊",
    layout="wide"
)

# Autenticación simple
def check_password():
    """Autenticación básica"""
    def password_entered():
        if st.session_state["password"] == st.secrets.get("dashboard_password", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrecto")
        return False
    else:
        return True

def load_data():
    """Cargar datos desde Google Sheets"""
    try:
        connector = SheetsConnector()
        diagnostics = connector.get_all_diagnostics()
        analytics = connector.get_analytics_summary()
        return diagnostics, analytics
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return [], {}

def show_kpi_cards(analytics):
    """Mostrar tarjetas de KPIs principales"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = analytics.get("Total Diagnósticos", 0)
        st.metric("Total Diagnósticos", total)

    with col2:
        tier_a = analytics.get("Tier A", 0)
        st.metric("Tier A (Ideal)", tier_a, delta=f"{tier_a} leads calientes")

    with col3:
        score_prom = analytics.get("Score Promedio", "0")
        st.metric("Score Promedio", score_prom)

    with col4:
        pipeline = analytics.get("Pipeline Value Estimado", "$0")
        st.metric("Pipeline Estimado", pipeline)

def show_tier_distribution(df):
    """Mostrar distribución de Tiers"""
    st.subheader("📊 Distribución por Tier")

    tier_counts = df['tier'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=tier_counts.index,
        values=tier_counts.values,
        marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
        hole=0.4
    )])

    fig.update_layout(
        title="Distribución de Prospectos",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

def show_score_distribution(df):
    """Mostrar distribución de scores"""
    st.subheader("📈 Distribución de Scores")

    fig = px.histogram(
        df,
        x='score_final',
        nbins=20,
        color='tier',
        color_discrete_map={'A': '#10b981', 'B': '#f59e0b', 'C': '#ef4444'},
        title="Distribución de Scores Finales"
    )

    fig.add_vline(x=70, line_dash="dash", line_color="green", annotation_text="Tier A")
    fig.add_vline(x=40, line_dash="dash", line_color="orange", annotation_text="Tier B")

    st.plotly_chart(fig, use_container_width=True)

def show_tier_a_table(df):
    """Mostrar tabla de prospectos Tier A"""
    st.subheader("🌟 Prospectos Tier A - ACCIÓN INMEDIATA")

    tier_a = df[df['tier'] == 'A'].sort_values('timestamp', ascending=False)

    if len(tier_a) == 0:
        st.info("No hay prospectos Tier A aún")
        return

    # Preparar datos para tabla
    display_df = tier_a[[
        'timestamp', 'nombre_empresa', 'contacto_email', 'score_final',
        'arquetipo_nombre', 'servicio_sugerido', 'probabilidad_cierre'
    ]].copy()

    display_df['monto_estimado'] = tier_a.apply(
        lambda row: f"${(row['monto_min'] + row['monto_max'])/2/1000000:.1f}M",
        axis=1
    )

    display_df.columns = [
        'Fecha', 'Empresa', 'Email', 'Score', 'Arquetipo',
        'Servicio', 'Prob. Cierre', 'Monto Est.'
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )

    # Botón para ver detalles
    selected_empresa = st.selectbox(
        "Ver detalles de:",
        options=tier_a['nombre_empresa'].tolist()
    )

    if selected_empresa:
        show_prospect_detail(tier_a[tier_a['nombre_empresa'] == selected_empresa].iloc[0])

def show_prospect_detail(row):
    """Mostrar detalles completos de un prospecto"""

    with st.expander(f"📋 Detalles completos - {row['nombre_empresa']}", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Análisis de Scores")

            scores_data = {
                'Dimensión': ['Madurez Digital', 'Capacidad Inversión', 'Viabilidad Comercial'],
                'Score': [
                    row['madurez_digital_total'],
                    row['capacidad_inversion_total'],
                    row['viabilidad_total']
                ],
                'Máximo': [40, 30, 30]
            }

            scores_df = pd.DataFrame(scores_data)
            scores_df['Porcentaje'] = (scores_df['Score'] / scores_df['Máximo'] * 100).round(1)

            st.dataframe(scores_df, use_container_width=True)

            # Gráfico radar
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=[
                    row['madurez_digital_total']/40*100,
                    row['capacidad_inversion_total']/30*100,
                    row['viabilidad_total']/30*100
                ],
                theta=['Madurez Digital', 'Capacidad Inversión', 'Viabilidad'],
                fill='toself',
                name=row['nombre_empresa']
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=300
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🎯 Recomendación Estratégica")

            st.info(f"""
            **Arquetipo:** {row['arquetipo_nombre']}

            **Servicio Sugerido:** {row['servicio_sugerido']}

            **Rango de Inversión:** ${row['monto_min']/1000000:.1f}M - ${row['monto_max']/1000000:.1f}M COP

            **Probabilidad de Cierre:** {row['probabilidad_cierre']}%
            """)

            st.markdown("### 📞 Contacto")
            st.markdown(f"""
            - **Email:** {row['contacto_email']}
            - **Empresa:** {row['nombre_empresa']}
            - **Score Final:** {row['score_final']}/100
            """)

            st.markdown("### ⚡ Quick Wins Sugeridos")
            st.markdown(f"Se identificaron {row['quick_wins_count']} oportunidades de quick wins")

            if row['red_flags_count'] > 0:
                st.warning(f"⚠️ {row['red_flags_count']} red flags identificados")

def main():
    if not check_password():
        return

    st.title("📊 Dashboard AI Readiness - Gestión de Leads")

    # Cargar datos
    with st.spinner("Cargando datos..."):
        diagnostics, analytics = load_data()

    if not diagnostics:
        st.warning("No hay datos disponibles aún")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(diagnostics)

    # KPIs principales
    show_kpi_cards(analytics)

    st.markdown("---")

    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 Tier A (Acción Inmediata)",
        "📊 Análisis General",
        "🔍 Todos los Prospectos",
        "📈 Tendencias"
    ])

    with tab1:
        show_tier_a_table(df)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            show_tier_distribution(df)

        with col2:
            show_score_distribution(df)

        # Distribución por arquetipo
        st.subheader("🎭 Distribución por Arquetipo")
        arquetipo_counts = df['arquetipo_tipo'].value_counts()

        fig = px.bar(
            x=arquetipo_counts.index,
            y=arquetipo_counts.values,
            labels={'x': 'Arquetipo', 'y': 'Cantidad'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("📋 Todos los Prospectos")

        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            tier_filter = st.multiselect(
                "Filtrar por Tier",
                options=['A', 'B', 'C'],
                default=['A', 'B', 'C']
            )

        with col2:
            arquetipos = df['arquetipo_tipo'].unique().tolist()
            arquetipo_filter = st.multiselect(
                "Filtrar por Arquetipo",
                options=arquetipos,
                default=arquetipos
            )

        # Aplicar filtros
        filtered_df = df[
            (df['tier'].isin(tier_filter)) &
            (df['arquetipo_tipo'].isin(arquetipo_filter))
        ]

        # Mostrar tabla
        display_cols = [
            'timestamp', 'nombre_empresa', 'contacto_email', 'tier',
            'score_final', 'arquetipo_nombre', 'probabilidad_cierre'
        ]

        st.dataframe(
            filtered_df[display_cols].sort_values('timestamp', ascending=False),
            use_container_width=True,
            height=500
        )

    with tab4:
        st.subheader("📈 Tendencias Temporales")

        # Convertir timestamp a datetime
        df['date'] = pd.to_datetime(df['timestamp'])
        df['week'] = df['date'].dt.to_period('W').astype(str)

        # Diagnósticos por semana
        weekly_counts = df.groupby('week').size().reset_index(name='count')

        fig = px.line(
            weekly_counts,
            x='week',
            y='count',
            title="Diagnósticos por Semana",
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Score promedio por semana
        weekly_scores = df.groupby('week')['score_final'].mean().reset_index()

        fig = px.line(
            weekly_scores,
            x='week',
            y='score_final',
            title="Score Promedio por Semana",
            markers=True
        )

        fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Tier A threshold")
        fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Tier B threshold")

        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
