import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
import pandas as pd
import plotly.graph_objects as go

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Анализ катастрофических рисков", layout="wide", page_icon="🛡️")

# --- ГЛУБОКИЙ ТЕМНО-СИНИЙ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    /* Основной фон (очень глубокий синий) */
    .stApp {
        background-color: #031326;
        color: #E2E8F0;
    }
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background-color: #0B1E36;
        border-right: 1px solid #1E3A5F;
    }
    /* Заголовки */
    h1, h2, h3 {
        color: #38BDF8 !important;
    }
    /* Цифры метрик */
    [data-testid="stMetricValue"] {
        color: #38BDF8;
    }
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0B1E36;
        border-radius: 4px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Настройка matplotlib
plt.style.use('dark_background')
plt.rcParams.update({
    'axes.facecolor': '#031326',
    'figure.facecolor': '#031326',
    'grid.color': '#1E3A5F',
    'text.color': '#E2E8F0',
    'axes.labelcolor': '#E2E8F0',
    'xtick.color': '#E2E8F0',
    'ytick.color': '#E2E8F0'
})

st.title("🛡️ Платформа моделирования катастрофических рисков")

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Входные параметры")
N = st.sidebar.number_input("Число объектов (N)", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность риска (λ)", value=0.01, format="%.3f")
T = st.sidebar.slider("Период накопления (T), лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Макс. ущерб (S_max), руб", value=100000000, step=1000000)
P_gamma = st.sidebar.slider("Надежность (P)", 0.80, 0.999, 0.950, step=0.005)
f = st.sidebar.slider("Нагрузка (f), %", 0, 50, 20) / 100
delta = st.sidebar.slider("Ставка дисконтирования (δ)", 0.0, 0.20, 0.05, step=0.01)

# --- МАТЕМАТИКА ---
m0 = S_vos / 2
D0 = (S_vos**2) / 12

def calc_model(is_disc, temp_T=None, temp_delta=None):
    t_val = temp_T if temp_T is not None else T
    d_val = temp_delta if temp_delta is not None else delta
    
    if not is_disc:
        eta = N * lam * t_val
        c1, c2 = eta * m0, eta * (m0**2 + D0)
    else:
        if d_val == 0:
            c1, c2 = N * lam * t_val * m0, N * lam * t_val * (m0**2 + D0)
        else:
            c1 = N * lam * m0 * (1 - np.exp(-d_val * t_val)) / d_val
            c2 = N * lam * (m0**2 + D0) * (1 - np.exp(-2 * d_val * t_val)) / (2 * d_val)
    
    b = c1 / c2 if c2 != 0 else 1e-10
    a = c1 * b if b != 0 else 1e-10
    
    Pr = gamma.ppf(P_gamma, a=a, scale=1/b) if a > 0 else 0
    Trn = (Pr * 100) / (N * S_vos * t_val) if t_val > 0 else 0
    Trbr = (Trn / (1 - f)) * (np.exp(d_val * t_val) if not is_disc else 1)
        
    return Pr, Trn, Trbr, a, b

r1 = calc_model(False)
r2 = calc_model(True)

# --- ВКЛАДКИ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Сводный расчет", 
    "📈 2D Аналитика", 
    "🌌 3D Поверхность",
    "📚 Методология",
    "📥 Данные"
])

# --- ВКЛАДКА 1: БАЗОВЫЙ РАСЧЕТ ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"### Модель 1 (Без дисконта)\n**Начальный капитал:** {r1[0]:,.0f} ₽\n\n**Брутто-тариф:** {r1[2]:.4f} %")
    with col2:
        st.success(f"### Модель 2 (С дисконтом)\n**Начальный капитал:** {r2[0]:,.0f} ₽\n\n**Брутто-тариф:** {r2[2]:.4f} %")

    savings = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    st.warning(f"💡 Экономический эффект: применение дисконтирования экономит **{savings:.2f}%** стоимости полиса.")

    st.markdown("### Интегральное распределение ущерба")
    x = np.linspace(0, max(r1[0], r2[0]) * 1.3, 500)
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(x/1e6, gamma.cdf(x, r1[3], scale=1/r1[4]), label="Модель 1", color="#38BDF8", lw=2)
    ax1.plot(x/1e6, gamma.cdf(x, r2[3], scale=1/r2[4]), label="Модель 2", color="#F87171", ls="--", lw=2)
    ax1.axhline(y=P_gamma, color="#94A3B8", ls=":", label="Надежность")
    ax1.set_xlabel("Ущерб (млн. руб.)")
    ax1.set_ylabel("Вероятность R(x)")
    ax1.grid(True, alpha=0.2)
    ax1.legend()
    st.pyplot(fig1)

# --- ВКЛАДКА 2: АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ ---
with tab2:
    col_g1, col_g2 = st.columns(2)
    t_array = np.arange(1, 31)
    
    with col_g1:
        trbr_m1 = [calc_model(False, temp_T=t)[2] for t in t_array]
        trbr_m2 = [calc_model(True, temp_T=t)[2] for t in t_array]
        fig2, ax2 = plt.subplots()
        ax2.plot(t_array, trbr_m1, label="Модель 1", color="#38BDF8")
        ax2.plot(t_array, trbr_m2, label="Модель 2", color="#F87171")
        ax2.set_xlabel("Срок накопления T")
        ax2.set_ylabel("Тариф %")
        ax2.grid(True, alpha=0.2)
        ax2.legend()
        st.pyplot(fig2)
        
    with col_g2:
        d_array = np.linspace(0, 0.15, 30)
        trbr_d2 = [calc_model(True, temp_delta=d)[2] for d in d_array]
        fig3, ax3 = plt.subplots()
        ax3.plot(d_array, trbr_d2, color="#F87171")
        ax3.set_xlabel("Ставка дисконтирования δ")
        ax3.set_ylabel("Тариф (Модель 2) %")
        ax3.grid(True, alpha=0.2)
        st.pyplot(fig3)

# --- ВКЛАДКА 3: 3D ГРАФИК (WOW-ЭФФЕКТ) ---
with tab3:
    st.markdown("### Интерактивная 3D-модель тарифа")
    st.markdown("Вращайте график мышкой, чтобы оценить влияние срока и ставки на брутто-тариф (Модель 2).")
    
    t_vals = np.linspace(5, 30, 25)
    d_vals = np.linspace(0.01, 0.15, 25)
    T_grid, D_grid = np.meshgrid(t_vals, d_vals)
    Z = np.zeros_like(T_grid)
    
    for i in range(T_grid.shape[0]):
        for j in range(T_grid.shape[1]):
            Z[i, j] = calc_model(True, temp_T=T_grid[i, j], temp_delta=D_grid[i, j])[2]
            
    fig_3d = go.Figure(data=[go.Surface(z=Z, x=T_grid, y=D_grid, colorscale='Viridis')])
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Срок (T)',
            yaxis_title='Дисконт (δ)',
            zaxis_title='Тариф %',
            bgcolor="#031326"
        ),
        paper_bgcolor="#031326",
        font=dict(color="#E2E8F0"),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# --- ВКЛАДКА 4: МЕТОДОЛОГИЯ ---
with tab4:
    st.markdown("### Математическое обеспечение")
    st.markdown("""
    В основе расчетов лежит аппроксимация функции распределения совокупного страхового ущерба с помощью Гамма-распределения. 
    Поскольку мы имеем дело с накопительным механизмом, необходимо учитывать разновесомость финансовых потоков во времени.
    """)
    st.info("Семиинварианты характеристической функции дисконтированного ущерба:")
    st.latex(r"\chi_1 = N \lambda m_0 \frac{1 - e^{-\delta T}}{\delta}")
    st.latex(r"\chi_2 = N \lambda (m_0^2 + D_0) \frac{1 - e^{-2\delta T}}{2\delta}")
    st.markdown("Параметры Гамма-распределения $\alpha$ и $\beta$ определяются как:")
    st.latex(r"\alpha = \chi_1 \cdot \beta, \quad \beta = \frac{\chi_1}{\chi_2}")

# --- ВКЛАДКА 5: ДАННЫЕ ---
with tab5:
    st.markdown("### Экспорт расчетных данных")
    data = []
    for t_step in range(1, T + 1):
        res1_t = calc_model(False, temp_T=t_step)
        res2_t = calc_model(True, temp_T=t_step)
        data.append({
            "Срок (T)": t_step,
            "Тариф М1 (%)": round(res1_t[2], 4),
            "Тариф М2 (%)": round(res2_t[2], 4),
            "Дельта (%)": round((1 - res2_t[2]/res1_t[2])*100, 2) if res1_t[2]>0 else 0
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
