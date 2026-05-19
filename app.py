import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Актуарный анализ катастрофических рисков",
    layout="wide",
    page_icon="🛡️"
)

# =====================================================================
# ПАЛИТРА И ГЛОБАЛЬНЫЕ СТИЛИ (БЕЗОПАСНОЕ УВЕЛИЧЕНИЕ)
# =====================================================================
st.markdown("""
    <style>
    /* ВЕРХНИЙ HEADER STREAMLIT */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 50%, #06B6D4 100%) !important;
        height: 60px !important;
        border-bottom: 3px solid #1E40AF;
    }
    header[data-testid="stHeader"] *,
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    .main .block-container {
        padding-top: 3rem;
    }
    
    /* БАЗОВЫЙ ФОН */
    .stApp {
        background-color: #FFFFFF;
        color: #111827;
    }
    
    /* =========================================================
       ОСНОВНОЙ ТЕКСТ (СУПЕР-КРУПНЫЙ, НО БЕЗОПАСНЫЙ)
       ========================================================= */
    .stMarkdown p, .stMarkdown li {
        font-size: 30px !important;
        line-height: 1.8 !important;
        color: #1F2937 !important;
    }
    .stMarkdown strong, .stMarkdown b {
        color: #1E40AF !important;
        font-weight: bold !important;
    }
    
    /* БЕЛАЯ КЛИЕНТСКАЯ ЗОНА ДЛЯ ВВОДА */
    input, input[type="number"], input[type="text"],
    .stNumberInput input, .stTextInput input,
    div[data-baseweb="input"], div[data-baseweb="input"] input,
    div[data-baseweb="base-input"], div[data-baseweb="base-input"] input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        border: 1.5px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-size: 26px !important;
    }
    [data-testid="stNumberInputContainer"],
    [data-testid="stNumberInput"] > div {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* ПОДПИСИ ЭЛЕМЕНТОВ ВВОДА И ПОЛЗУНКОВ */
    .stSlider label, .stNumberInput label {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    
    /* СЛАЙДЕРЫ */
    .stSlider [data-baseweb="slider"] > div > div > div {
        background-color: #2563EB !important;
    }
    .stSlider [role="slider"] {
        background-color: #2563EB !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.5) !important;
        width: 28px !important;
        height: 28px !important;
    }
    .stSlider [data-baseweb="slider"] div div span {
        font-size: 26px !important;
        color: #2563EB !important;
        font-weight: bold !important;
    }
    
    /* САЙДБАР */
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
        border-right: 2px solid #E5E7EB;
    }
    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 42px !important;
        color: #1E40AF !important;
        font-weight: bold !important;
    }
    
    /* ЗАГОЛОВКИ */
    h1 {
        color: #1E40AF !important;
        font-size: 60px !important;
        font-weight: bold !important;
        text-align: center;
        padding: 18px 0;
        border-bottom: 4px solid #2563EB;
        margin-bottom: 35px !important;
    }
    h2 {
        color: #1E40AF !important;
        font-size: 48px !important;
        font-weight: bold !important;
        margin-top: 40px !important;
    }
    h3 {
        color: #2563EB !important;
        font-size: 38px !important;
        font-weight: 600 !important;
        margin-top: 30px !important;
    }
    
    /* ВКЛАДКИ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #F3F4F6;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        padding: 20px 32px !important;
        background-color: #FFFFFF !important;
        color: #4B5563 !important;
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    /* КАРТОЧКИ РЕЗУЛЬТАТОВ */
    .metric-box-m1 {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 10px solid #2563EB;
        padding: 36px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }
    .metric-box-m2 {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 10px solid #DC2626;
        padding: 36px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.15);
    }
    .metric-box-m1 p, .metric-box-m2 p {
        font-size: 30px !important;
        margin: 12px 0 !important;
        color: #1F2937 !important;
    }
    
    /* ИНФО-БЛОКИ */
    .info-block {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        padding: 32px;
        border-radius: 14px;
        border-left: 8px solid #F59E0B;
        margin: 32px 0;
        font-size: 30px !important;
        color: #1F2937;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.15);
    }
    .description-block {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        padding: 30px;
        border-radius: 14px;
        border-left: 6px solid #7C3AED;
        margin: 24px 0;
        font-size: 28px !important;
        line-height: 1.8 !important;
        color: #1F2937;
    }
    
    /* КНОПКИ */
    .stDownloadButton button, .stButton button {
        font-size: 32px !important;
        padding: 30px 40px !important;
        width: 100% !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 14px !important;
        border: none !important;
        transition: all 0.25s ease;
        margin: 20px 0 !important;
        min-height: 110px !important;
        letter-spacing: 0.5px;
    }
    .stDownloadButton:nth-of-type(1) button {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    .stDownloadButton:nth-of-type(2) button {
        background: linear-gradient(135deg, #F59E0B 0%, #DC2626 100%) !important;
        box-shadow: 0 6px 16px rgba(220, 38, 38, 0.35);
    }
    .stButton button {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
    }
    
    /* ТАБЛИЦА */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 28px 0;
        font-size: 26px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }
    .custom-table th {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        color: #FFFFFF !important;
        padding: 24px 18px;
        font-size: 28px !important;
        font-weight: bold;
    }
    .custom-table td {
        padding: 20px 16px;
        border: 1px solid #E5E7EB;
        background-color: #FFFFFF;
        color: #111827 !important;
        font-size: 25px !important;
    }
    .custom-table tr:nth-child(even) td {
        background-color: #F9FAFB;
    }
    
    /* LATEX КЛАССЫ */
    .katex {
        font-size: 1.6em !important;
        color: #111827 !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# MATPLOTLIB — УМЕНЬШЕННЫЕ ШРИФТЫ ДЛЯ АККУРАТНОСТИ ГРАФИКОВ
# =====================================================================
plt.rcParams.update({
    'axes.facecolor':   '#FFFFFF',
    'figure.facecolor': '#FFFFFF',
    'grid.color':       '#E5E7EB',
    'grid.alpha':       0.7,
    'text.color':       '#111827',
    'axes.labelcolor':  '#111827',
    'xtick.color':      '#111827',
    'ytick.color':      '#111827',
    'axes.labelsize':   13,      
    'xtick.labelsize':  11,      
    'ytick.labelsize':  11,      
    'legend.fontsize':  11,      
    'axes.titlesize':   15,      
    'axes.titleweight': 'bold',
    'axes.edgecolor':   '#9CA3AF',
    'axes.linewidth':   1.5,
    'figure.dpi':       110,     
})

COLOR_M1     = '#2563EB'
COLOR_M2     = '#DC2626'
COLOR_REF    = '#F59E0B'
COLOR_ACCENT = '#7C3AED'

# =====================================================================
# ЗАГОЛОВОК И СБОР ДАННЫХ
# =====================================================================
st.markdown("<h1>🛡️ Программный комплекс актуарного анализа катастрофических рисков</h1>", unsafe_allow_html=True)

st.sidebar.markdown("## ⚙️ Параметры портфеля")
N = st.sidebar.number_input("Число застрахованных объектов N, ед.", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность наступления рисков λ", value=0.01, format="%.3f")
T = st.sidebar.slider("Период накопления резерва T, лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Максимальный ущерб S_max, руб.", value=100_000_000, step=1_000_000)
P_gamma = st.sidebar.slider("Уровень надёжности фонда P", 0.800, 0.999, 0.950, step=0.005)
f = st.sidebar.slider("Доля страховой нагрузки f, %", 0, 50, 20) / 100
delta = st.sidebar.slider("Норма дисконтирования δ", 0.0, 0.20, 0.05, step=0.01)

m0 = S_vos / 2
D0 = (S_vos ** 2) / 12

def calc_model(is_disc, temp_T=None, temp_delta=None):
    t_val = temp_T if temp_T is not None else T
    d_val = temp_delta if temp_delta is not None else delta
    if not is_disc:
        eta = N * lam * t_val
        c1, c2 = eta * m0, eta * (m0**2 + D0)
    else:
        if d_val == 0:
            c1 = N * lam * t_val * m0
            c2 = N * lam * t_val * (m0**2 + D0)
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

# ВКЛАДКИ
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Сводный расчёт", "📈 Анализ чувствительности", "🌌 Поверхность решений", "📚 Методология", "📥 Отчёты"
])

# ---------------------------------------------------------------------
# ВКЛАДКА 1
# ---------------------------------------------------------------------
with tab1:
    st.markdown("## Результаты сопоставления актуарных моделей")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-box-m1">
            <h3 style="color:#1E40AF; margin-top:0;">Модель 1 — без учёта временной стоимости денег</h3>
            <p>Требуемый размер резервного фонда:<br><b style="font-size:52px; color:#2563EB;">{r1[0]:,.0f} ₽</b></p>
            <p>Расчётный брутто-тариф:<br><b style="font-size:52px; color:#2563EB;">{r1[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box-m2">
            <h3 style="color:#991B1B; margin-top:0;">Модель 2 — с учётом инвестиционного дохода</h3>
            <p>Требуемый размер резервного фонда:<br><b style="font-size:52px; color:#DC2626;">{r2[0]:,.0f} ₽</b></p>
            <p>Расчётный брутто-тариф:<br><b style="font-size:52px; color:#DC2626;">{r2[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)

    savings = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    st.markdown(f"""
    <div class="info-block">
        💡 <b>Экономическая интерпретация результата.</b><br>
        Учёт временной стоимости капитала в Модели 2 позволяет снизить тарифную нагрузку на страхователей на 
        <b style="font-size:40px; color:#10B981;">{savings:.2f}%</b> при сохранении заданного уровня надёжности фонда.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Интегральная функция распределения совокупного ущерба")
    x = np.linspace(0, max(r1[0], r2[0]) * 1.4, 500)
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(x/1e6, gamma.cdf(x, r1[3], scale=1/r1[4]), label="Модель 1 — без дисконтирования", color=COLOR_M1, lw=3)
    ax1.plot(x/1e6, gamma.cdf(x, r2[3], scale=1/r2[4]), label="Модель 2 — с дисконтированием", color=COLOR_M2, ls="--", lw=3)
    ax1.axhline(y=P_gamma, color=COLOR_REF, ls=":", lw=2.5, label=f"Уровень надёжности P = {P_gamma}")
    ax1.axvline(x=r1[0]/1e6, color=COLOR_M1, ls=":", lw=1.5, alpha=0.6)
    ax1.axvline(x=r2[0]/1e6, color=COLOR_M2, ls=":", lw=1.5, alpha=0.6)
    ax1.set_xlabel("Совокупный накопленный ущерб, млн руб.")
    ax1.set_ylabel("Вероятность покрытия R(x)")
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc='lower right', framealpha=0.95)
    st.pyplot(fig1)

# ---------------------------------------------------------------------
# ВКЛАДКА 2
# ---------------------------------------------------------------------
with tab2:
    st.markdown("## Анализ чувствительности тарифа к ключевым параметрам")

    st.markdown("### Зависимость брутто-тарифа от срока накопления T")
    t_array = np.arange(1, 31)
    trbr_m1 = [calc_model(False, temp_T=t)[2] for t in t_array]
    trbr_m2 = [calc_model(True,  temp_T=t)[2] for t in t_array]
    
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    ax2.plot(t_array, trbr_m1, label="Модель 1 — без дисконтирования", color=COLOR_M1, lw=3, marker='o', markersize=5)
    ax2.plot(t_array, trbr_m2, label="Модель 2 — с дисконтированием", color=COLOR_M2, lw=3, marker='s', markersize=5)
    ax2.set_xlabel("Срок накопления резерва T, лет")
    ax2.set_ylabel("Брутто-тариф, %")
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc='best')
    st.pyplot(fig2)

    st.markdown("---")
    st.markdown("### Зависимость брутто-тарифа от нормы дисконтирования δ")
    d_array = np.linspace(0, 0.18, 30)
    trbr_d2 = [calc_model(True, temp_delta=d)[2] for d in d_array]
    
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    ax3.plot(d_array * 100, trbr_d2, color=COLOR_ACCENT, lw=3, marker='o', markersize=5, label="Модель 2 — с дисконтированием")
    ax3.fill_between(d_array * 100, trbr_d2, alpha=0.15, color=COLOR_ACCENT)
    ax3.set_xlabel("Норма дисконтирования δ, % годовых")
    ax3.set_ylabel("Брутто-тариф, %")
    ax3.grid(True, alpha=0.4)
    ax3.legend(loc='best')
    st.pyplot(fig3)

# ---------------------------------------------------------------------
# ВКЛАДКА 3
# ---------------------------------------------------------------------
with tab3:
    st.markdown("## Трёхмерная поверхность тарифных решений")

    t_vals = np.linspace(5, 30, 35)
    d_vals = np.linspace(0.01, 0.15, 35)
    T_grid, D_grid = np.meshgrid(t_vals, d_vals)
    Z = np.zeros_like(T_grid)
    for i in range(T_grid.shape[0]):
        for j in range(T_grid.shape[1]):
            Z[i, j] = calc_model(True, temp_T=T_grid[i, j], temp_delta=D_grid[i, j])[2]

    fig_3d = go.Figure(data=[
        go.Surface(
            z=Z, x=T_grid, y=D_grid,
            colorscale='Plasma',
            colorbar=dict(
                title=dict(text="Тариф, %", font=dict(size=13, color='#111827')),
                tickfont=dict(size=11, color='#111827'),
                thickness=22,
                len=0.75
            )
        )
    ])
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title=dict(text='Срок T, лет', font=dict(size=13)), tickfont=dict(size=11)),
            yaxis=dict(title=dict(text='Ставка δ', font=dict(size=13)), tickfont=dict(size=11)),
            zaxis=dict(title=dict(text='Тариф, %', font=dict(size=13)), tickfont=dict(size=11)),
        ),
        height=750,
        margin=dict(l=10, r=10, b=10, t=40)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# ---------------------------------------------------------------------
# ВКЛАДКА 4
# ---------------------------------------------------------------------
with tab4:
    st.markdown("## Методологическое описание программного комплекса")
    st.markdown("### 1. Постановка актуарной задачи")
    st.markdown("Страхование промышленных объектов от катастрофических рисков характеризуется малой частотой и огромным ущербом.")
    
    st.markdown("**Модель 1 (Без дисконтирования):**")
    st.latex(r"\chi_1 = N \lambda T \, m_0")
    st.latex(r"\chi_2 = N \lambda T \, (m_0^2 + D_0)")

    st.markdown("**Модель 2 (С непрерывным дисконтированием):**")
    st.latex(r"\chi_1 = N \lambda m_0 \cdot \frac{1 - e^{-\delta T}}{\delta}")
    st.latex(r"\chi_2 = N \lambda (m_0^2 + D_0) \cdot \frac{1 - e^{-2\delta T}}{2\delta}")

# ---------------------------------------------------------------------
# ВКЛАДКА 5 — ОТЧЁТЫ И ЭКСПОРТ
# ---------------------------------------------------------------------
with tab5:
    st.markdown("## Матрица плановых показателей по годам")

    data = []
    for t_step in range(1, T + 1):
        res1_t = calc_model(False, temp_T=t_step)
        res2_t = calc_model(True,  temp_T=t_step)
        data.append({
            "Год (T)":        t_step,
            "Фонд М1, руб.":  f"{res1_t[0]:,.0f}",
            "Фонд М2, руб.":  f"{res2_t[0]:,.0f}",
            "Тариф М1, %":    f"{res1_t[2]:.4f}",
            "Тариф М2, %":    f"{res2_t[2]:.4f}",
            "Экономия, %":    f"{((1 - res2_t[2]/res1_t[2])*100):.2f}" if res1_t[2] > 0 else "0.00"
        })
    df = pd.DataFrame(data)

    html_table = "<table class='custom-table'><thead><tr>"
    for col in df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html_table += "<tr>"
        for val in row:
            html_table += f"<td>{val}</td>"
        html_table += "</tr>"
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📥 Экспорт результатов расчёта")

    csv_data = pd.DataFrame([{
        "Год_T": i+1,
        "Фонд_М1_руб": calc_model(False, temp_T=i+1)[0],
        "Фонд_М2_руб": calc_model(True, temp_T=i+1)[0],
        "Тариф_М1_процент": calc_model(False, temp_T=i+1)[2],
        "Тариф_М2_процент": calc_model(True, temp_T=i+1)[2]
    } for i in range(T)]).to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label="📊 СКАЧАТЬ ТАБЛИЦУ РАСЧЁТОВ (CSV ДЛЯ EXCEL)",
        data=csv_data,
        file_name='insurance_matrix_report.csv',
        mime='text/csv',
        use_container_width=True
    )

    savings_val = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    report_text = f"""АНАЛИТИЧЕСКИЙ ОТЧЁТ ПО РЕЗУЛЬТАТАМ АКТУАРНОГО МОДЕЛИРОВАНИЯ
================================================================

ИСХОДНЫЕ ПАРАМЕТРЫ ПОРТФЕЛЯ
----------------------------------------------------------------
Количество застрахованных объектов (N):       {N} ед.
Интенсивность катастрофических событий (λ):    {lam}
Максимальный лимит ответственности (S_max):    {S_vos:,.2f} руб.
Заданная надёжность резервного фонда (P):      {P_gamma*100:.1f}%
Норма дисконтирования (δ):                     {delta*100:.1f}% годовых
Период накопления (T):                         {T} лет
Доля страховой нагрузки (f):                   {f*100:.1f}%

РЕЗУЛЬТАТЫ РАСЧЁТА
----------------------------------------------------------------
Модель 1 (без учёта временной стоимости денег):
   — Требуемый размер фонда:    {r1[0]:,.2f} руб.
   — Брутто-тариф:               {r1[2]:.4f} %

Модель 2 (с учётом инвестиционного дохода):
   — Требуемый размер фонда:    {r2[0]:,.2f} руб.
   — Брутто-тариф:               {r2[2]:.4f} %

СРАВНИТЕЛЬНЫЙ АНАЛИЗ
----------------------------------------------------------------
Применение Модели 2 обеспечивает снижение тарифной нагрузки
на страхователей на {savings_val:.2f}% при сохранении заданного уровня
финансовой устойчивости фонда ({P_gamma*100:.1f}%).

================================================================
"""

    st.download_button(
        label="📄 СКАЧАТЬ ТЕКСТОВЫЙ ОТЧЁТ С ВЫВОДАМИ",
        data=report_text.encode('utf-8'),
        file_name='analytical_report.txt',
        mime='text/plain',
        use_container_width=True
    )
