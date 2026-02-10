import json, os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Condição que pega o caminho atual
caminho = os.path.dirname(os.path.abspath(__file__))

# Função para carregar credenciais de um arquivo JSON
def carregar_credenciais(arquivo_json):
    with open(arquivo_json, 'r') as f:
        credenciais = json.load(f)
    return credenciais

credenciais = carregar_credenciais(os.path.join(caminho, "credenciais.json"))

# --- CONFIGURAÇÃO DA CONEXÃO COM O BANCO ---
# IMPORTANTE: Substitua os dados abaixo pelas suas credenciais reais do PostgreSQL
DB_USER = credenciais['capstone']['username']
DB_PASS = credenciais['capstone']['password']
DB_HOST = credenciais['capstone']['host']
DB_PORT = credenciais['capstone']['port']
DB_NAME = credenciais['capstone']['database']

# String de conexão (SQLAlchemy)
DB_CONNECTION_STR = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Acadêmico Pro", layout="wide", page_icon="🎓")
st.title("📊 Monitoramento Estratégico de Engajamento")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=600)
def load_data():
    try:
        engine = create_engine(DB_CONNECTION_STR)
        
        # Carregando tabelas
        df_fac = pd.read_sql("SELECT * FROM gold_video_views_dia_faculdade", engine)
        df_rede = pd.read_sql("SELECT * FROM gold_video_views_dia_rede_social", engine)
        
        # Conversão de datas
        df_fac['data_postagem'] = pd.to_datetime(df_fac['data_postagem'])
        df_rede['data_postagem'] = pd.to_datetime(df_rede['data_postagem'])
        
        return df_fac, df_rede
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_faculdade, df_rede_social = load_data()

if not df_faculdade.empty and not df_rede_social.empty:

    # ==============================================================================
    # 🎯 SIDEBAR COM 3 FILTROS
    # ==============================================================================
    st.sidebar.header("🔍 Filtros de Análise")

    # 1. FILTRO DE DATA (Comum às duas tabelas)
    min_date = min(df_faculdade['data_postagem'].min(), df_rede_social['data_postagem'].min())
    max_date = max(df_faculdade['data_postagem'].max(), df_rede_social['data_postagem'].max())
    
    date_range = st.sidebar.date_input(
        "Período de Postagem",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 2. FILTRO DE FACULDADE (Afeta Tabela 1)
    all_faculdades = sorted(df_faculdade['faculdade'].unique())
    selected_faculdades = st.sidebar.multiselect(
        "Selecione as Faculdades",
        options=all_faculdades,
        default=all_faculdades
    )

    # 3. FILTRO DE REDE SOCIAL (Afeta Tabela 2)
    all_redes = sorted(df_rede_social['rede_social'].unique())
    selected_redes = st.sidebar.multiselect(
        "Selecione as Redes Sociais",
        options=all_redes,
        default=all_redes
    )

    # ==============================================================================
    # ⚙️ APLICAÇÃO DOS FILTROS
    # ==============================================================================
    
    # Filtrando datas (Válido para ambos)
    if len(date_range) == 2:
        start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask_date_fac = (df_faculdade['data_postagem'] >= start_d) & (df_faculdade['data_postagem'] <= end_d)
        mask_date_rede = (df_rede_social['data_postagem'] >= start_d) & (df_rede_social['data_postagem'] <= end_d)
    else:
        mask_date_fac = [True] * len(df_faculdade)
        mask_date_rede = [True] * len(df_rede_social)

    # Filtrando Dataframes Finais
    # DF 1: Filtro de Data + Filtro de Faculdade
    df_fac_final = df_faculdade[mask_date_fac & df_faculdade['faculdade'].isin(selected_faculdades)]
    
    # DF 2: Filtro de Data + Filtro de Rede Social
    df_rede_final = df_rede_social[mask_date_rede & df_rede_social['rede_social'].isin(selected_redes)]

    # Tratamento para divisão por zero (Engajamento)
    df_fac_final['taxa_engajamento'] = df_fac_final.apply(
        lambda x: ((x['total_likes'] + x['total_comentarios']) / x['total_views'] * 100) if x['total_views'] > 0 else 0, axis=1
    )

    # ==============================================================================
    # 📊 VISUALIZAÇÃO DO DASHBOARD
    # ==============================================================================

    # --- SEÇÃO 1: KPIS GERAIS (Baseado na seleção de faculdades) ---
    st.markdown("### 📈 Performance das Faculdades Selecionadas")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Views Totais", f"{df_fac_final['total_views'].sum():,.0f}".replace(",", "."))
    kpi2.metric("Likes Totais", f"{df_fac_final['total_likes'].sum():,.0f}".replace(",", "."))
    kpi3.metric("Comentários", f"{df_fac_final['total_comentarios'].sum():,.0f}".replace(",", "."))
    kpi4.metric("Engajamento Médio", f"{df_fac_final['taxa_engajamento'].mean():.2f}%")
    
    st.divider()

    # --- SEÇÃO 2: ANÁLISE COMPETITIVA (Afetado pelo filtro de Faculdade) ---
    col_g1, col_g2 = st.columns([2, 1])
    
    with col_g1:
        st.subheader("Evolução Temporal")
        if not df_fac_final.empty:
            fig_line = px.line(
                df_fac_final, 
                x='data_postagem', 
                y='total_views', 
                color='faculdade',
                title='Comparativo de Views por Dia',
                labels={'total_views': 'Visualizações', 'data_postagem': 'Data'}
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Nenhum dado para as faculdades selecionadas.")

    with col_g2:
        st.subheader("Divisão de Audiência")
        if not df_fac_final.empty:
            fig_pie = px.pie(
                df_fac_final.groupby('faculdade')['total_views'].sum().reset_index(), 
                values='total_views', 
                names='faculdade', 
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # --- SEÇÃO 3: ANÁLISE DE MERCADO/REDES (Afetado pelo filtro de Rede Social) ---
    st.subheader("📱 Inteligência de Redes Sociais")
    st.caption("Esta seção responde onde você deve investir, baseando-se nas redes selecionadas no filtro lateral.")
    
    if not df_rede_final.empty:
        def fmt_short(n: float) -> str:
            n = float(n or 0)
            absn = abs(n)
            if absn >= 1_000_000:
                return f"{n/1_000_000:.1f}M".replace(".", ",")
            if absn >= 1_000:
                return f"{n/1_000:.0f}k".replace(".", ",")
            return f"{n:.0f}".replace(".", ",")

        df = df_rede_final.copy()
        df["data_postagem"] = pd.to_datetime(df["data_postagem"]).dt.normalize()

        # =========================
        # Cards do topo (3)
        # =========================
        # Share de views (líder em alcance)
        views_por_rede = df.groupby("rede_social")["total_views"].sum().sort_values(ascending=False)
        total_views_all = float(views_por_rede.sum() or 1)
        lider_rede = views_por_rede.index[0] if len(views_por_rede) else "-"
        lider_share = (views_por_rede.iloc[0] / total_views_all) * 100 if len(views_por_rede) else 0

        # Engagement rate (melhor qualidade) = (likes + comentarios) / views
        df["eng_rate"] = np.where(
            df["total_views"] > 0,
            (df["total_likes"] + df["total_comentarios"]) / df["total_views"] * 100,
            0.0
        )
        eng_por_rede = df.groupby("rede_social")["eng_rate"].mean().sort_values(ascending=False)
        melhor_eng_rede = eng_por_rede.index[0] if len(eng_por_rede) else "-"
        melhor_eng = float(eng_por_rede.iloc[0] if len(eng_por_rede) else 0)

        # Estabilidade (menor volatilidade) via coeficiente de variação do volume diário
        daily = df.groupby(["rede_social", "data_postagem"])["total_views"].sum().reset_index()
        cv = (
            daily.groupby("rede_social")["total_views"]
            .apply(lambda s: (s.std(ddof=0) / s.mean()) if s.mean() else np.nan)
            .sort_values()
        )
        estavel_rede = cv.index[0] if len(cv.dropna()) else "-"
        cv_min = float(cv.iloc[0]) if len(cv.dropna()) else np.nan
        # label simples
        if np.isnan(cv_min):
            estab_label = "-"
        elif cv_min <= 0.25:
            estab_label = "High"
        elif cv_min <= 0.50:
            estab_label = "Medium"
        else:
            estab_label = "Low"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**{lider_rede.upper()}**")
            st.metric("Share de Views", f"{lider_share:.0f}%")
            st.caption("Líder em alcance")
        with c2:
            st.markdown(f"**{melhor_eng_rede.upper()}**")
            st.metric("Engagement Rate", f"{melhor_eng:.1f}%")
            st.caption("Melhor qualidade")
        with c3:
            st.markdown(f"**{estavel_rede.upper()}**")
            st.metric("Estabilidade", estab_label)
            st.caption("Menor volatilidade")

        st.divider()

        # ==========================================
        # Barras: Volume Diário de Views (Média)
        # ==========================================
        media_diaria = (
            daily.groupby("rede_social")["total_views"].mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_barh = go.Figure()
        for _, r in media_diaria.iterrows():
            rede = str(r["rede_social"])
            v = float(r["total_views"])
            fig_barh.add_trace(
                go.Bar(
                    y=[rede.upper()],
                    x=[v],
                    orientation="h",
                    text=[fmt_short(v)],
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate=f"{rede}<br>Média diária: {fmt_short(v)}<extra></extra>",
                )
            )

        fig_barh.update_layout(
            title="Volume Diário de Views (Média)",
            barmode="stack",
            showlegend=False,
            xaxis_title="Views",
            yaxis_title="",
            height=260,
        )
        fig_barh.update_xaxes(showgrid=False)

        st.plotly_chart(fig_barh, use_container_width=True)

        # ==================================
        # Linhas: Tendência (últimos 3 dias)
        # ==================================
        last_dates = sorted(daily["data_postagem"].unique())[-3:]
        trend = daily[daily["data_postagem"].isin(last_dates)].copy()
        trend["dia_label"] = trend["data_postagem"].rank(method="dense").astype(int).apply(lambda x: f"Day {x}")

        fig_trend = go.Figure()
        for rede in trend["rede_social"].dropna().unique():
            dfr = trend[trend["rede_social"] == rede].sort_values("data_postagem")
            fig_trend.add_trace(
                go.Scatter(
                    x=dfr["dia_label"],
                    y=dfr["total_views"],
                    mode="lines+markers",
                    name=str(rede).upper(),
                    line=dict(width=3),
                    marker=dict(size=8),
                    hovertemplate=f"{rede}<br>%{{x}}: %{{y:,.0f}}<extra></extra>".replace(",", "."),
                )
            )

        fig_trend.update_layout(
            title="Tendência de Views (Últimos 3 Dias)",
            xaxis_title="",
            yaxis_title="Views",
            height=340,
            legend=dict(orientation="h", y=1.02, x=0),
        )
        fig_trend.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")

        st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.info("Conectando ao banco de dados... Se demorar, verifique as credenciais.")