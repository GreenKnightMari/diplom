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
# ПАЛИТРА — белый фон, тёмный текст, яркие акценты
# =====================================================================
st.markdown("""
    <style>
    /* ВЕРХНИЙ HEADER STREAMLIT — голубой/синий градиент */
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
        font-size: 22px;
    }
    
    /* БЕЛЫЕ ПОЛЯ ВВОДА (фикс чёрных полос) */
    input, input[type="number"], input[type="text"],
    .stNumberInput input, .stTextInput input,
    div[data-baseweb="input"], div[data-baseweb="input"] input,
    div[data-baseweb="base-input"], div[data-baseweb="base-input"] input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        border: 1.5px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-size: 18px !important;
    }
    [data-testid="stNumberInputContainer"],
    [data-testid="stNumberInput"] > div {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    [data-testid="stNumberInput"] button {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
    }
    input:focus, .stNumberInput input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        outline: none !important;
    }
    
    /* СЛАЙДЕРЫ */
    .stSlider [data-baseweb="slider"] > div > div > div {
        background-color: #2563EB !important;
    }
    .stSlider [role="slider"] {
        background-color: #2563EB !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.5) !important;
        width: 22px !important;
        height: 22px !important;
    }
    .stSlider [data-baseweb="slider"] div div span {
        font-size: 18px !important;
        color: #2563EB !important;
        font-weight: bold !important;
    }
    
    /* САЙДБАР — КРУПНЫЕ ШРИФТЫ */
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
        border-right: 2px solid #E5E7EB;
    }
    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 32px !important;
        color: #1E40AF !important;
        font-weight: bold !important;
    }
    
    /* ЗАГОЛОВКИ */
    h1 {
        color: #1E40AF !important;
        font-size: 46px !important;
        font-weight: bold !important;
        text-align: center;
        padding: 18px 0;
        border-bottom: 4px solid #2563EB;
        margin-bottom: 35px !important;
    }
    h2 {
        color: #1E40AF !important;
        font-size: 36px !important;
        font-weight: bold !important;
        margin-top: 30px !important;
    }
    h3 {
        color: #2563EB !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        margin-top: 25px !important;
    }
    
    /* ОСНОВНОЙ ТЕКСТ */
    .stMarkdown p, .stMarkdown li {
        font-size: 22px !important;
        line-height: 1.8 !important;
        color: #1F2937 !important;
    }
    .stMarkdown strong, .stMarkdown b {
        color: #1E40AF !important;
        font-weight: bold !important;
    }
    
    /* Таблицы из markdown */
    .stMarkdown table {
        font-size: 20px !important;
    }
    .stMarkdown table th {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-size: 20px !important;
        padding: 14px !important;
    }
    .stMarkdown table td {
        padding: 12px !important;
        font-size: 19px !important;
    }
    
    /* ВКЛАДКИ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F3F4F6;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 21px !important;
        font-weight: 600 !important;
        padding: 18px 28px !important;
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
        padding: 32px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }
    .metric-box-m2 {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 10px solid #DC2626;
        padding: 32px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.15);
    }
    .metric-box-m1 p, .metric-box-m2 p {
        font-size: 22px !important;
        margin: 10px 0 !important;
        color: #1F2937 !important;
    }
    
    /* ИНФО-БЛОКИ */
    .info-block {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        padding: 28px;
        border-radius: 14px;
        border-left: 8px solid #F59E0B;
        margin: 28px 0;
        font-size: 22px !important;
        color: #1F2937;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.15);
    }
    .description-block {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        padding: 26px;
        border-radius: 14px;
        border-left: 6px solid #7C3AED;
        margin: 20px 0;
        font-size: 21px !important;
        line-height: 1.75 !important;
        color: #1F2937;
    }
    
    /* КНОПКИ */
    .stDownloadButton button, .stButton button {
        font-size: 25px !important;
        padding: 20px 40px !important;
        width: 100% !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 14px !important;
        border: none !important;
        transition: all 0.25s ease;
        margin: 20px 0 !important;
        min-height: 80px !important;
        letter-spacing: 0.5px;
    }
    .stDownloadButton button {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    .stDownloadButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.5);
    }
    
    /* LATEX И ПРОЧЕЕ */
    .katex {
        font-size: 1.4em !important;
        color: #111827 !important;
    }
    .stSlider label, .stNumberInput label {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# MATPLOTLIB — белая тема, яркие линии
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
    'axes.labelsize':   20,
    'xtick.labelsize':  17,
    'ytick.labelsize':  17,
    'legend.fontsize':  17,
    'axes.titlesize':   22,
    'axes.titleweight': 'bold',
    'axes.edgecolor':   '#9CA3AF',
    'axes.linewidth':   1.5,
    'axes.titlecolor':  '#1E40AF',
    'figure.dpi':       110,
})

COLOR_M1     = '#2563EB'   # синий (Модель 1)
COLOR_M2     = '#DC2626'   # красный (Модель 2)
COLOR_REF    = '#F59E0B'   # янтарный (уровень надёжности)
COLOR_ACCENT = '#7C3AED'   # фиолетовый (график по δ)
COLOR_GREEN  = '#10B981'   # зелёный (акцент)

# =====================================================================
# ЗАГОЛОВОК
# =====================================================================
st.markdown(
    "<h1>🛡️ Программный комплекс актуарного анализа катастрофических рисков</h1>",
    unsafe_allow_html=True
)

# =====================================================================
# БОКОВАЯ ПАНЕЛЬ — ВХОДНЫЕ ПАРАМЕТРЫ
# =====================================================================
st.sidebar.markdown("## ⚙️ Параметры портфеля")

N = st.sidebar.number_input("Число застрахованных объектов N, ед.", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность наступления рисков λ", value=0.01, format="%.3f")
T = st.sidebar.slider("Период накопления резерва T, лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Максимальный ущерб S_max, руб.", value=100_000_000, step=1_000_000)
P_gamma = st.sidebar.slider("Уровень надёжности фонда P", 0.800, 0.999, 0.950, step=0.005)
f = st.sidebar.slider("Доля страховой нагрузки f, %", 0, 50, 20) / 100
delta = st.sidebar.slider("Норма дисконтирования δ", 0.0, 0.20, 0.05, step=0.01)

# =====================================================================
# МАТЕМАТИЧЕСКОЕ ЯДРО
# =====================================================================
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

# =====================================================================
# ВКЛАДКИ
# =====================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Сводный расчёт",
    "📈 Анализ чувствительности",
    "🌌 Поверхность тарифных решений",
    "📚 Методология",
    "📥 Отчёты и данные"
])

# ---------------------------------------------------------------------
# ВКЛАДКА 1
# ---------------------------------------------------------------------
with tab1:
    st.markdown("## Результаты сопоставления актуарных моделей")
    st.markdown(
        "В блоке ниже представлены итоговые значения требуемых страховых резервов "
        "и расчётных тарифных ставок, полученные по двум альтернативным актуарным "
        "моделям при заданных параметрах портфеля."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-box-m1">
            <h3 style="color:#1E40AF; margin-top:0;">Модель 1 — без учёта временной стоимости денег</h3>
            <p>Требуемый размер резервного фонда:<br>
            <b style="font-size:30px; color:#2563EB;">{r1[0]:,.0f} ₽</b></p>
            <p>Расчётный брутто-тариф:<br>
            <b style="font-size:30px; color:#2563EB;">{r1[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box-m2">
            <h3 style="color:#991B1B; margin-top:0;">Модель 2 — с учётом инвестиционного дохода</h3>
            <p>Требуемый размер резервного фонда:<br>
            <b style="font-size:30px; color:#DC2626;">{r2[0]:,.0f} ₽</b></p>
            <p>Расчётный брутто-тариф:<br>
            <b style="font-size:30px; color:#DC2626;">{r2[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)

    savings = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    st.markdown(f"""
    <div class="info-block">
        💡 <b>Экономическая interpretation результата.</b><br><br>
        Учёт временной стоимости капитала в Модели 2 позволяет снизить тарифную нагрузку
        на страхователей на <b style="font-size:26px; color:#10B981;">{savings:.2f}%</b>
        при сохранении заданного уровня финансовой устойчивости фонда
        <b>{P_gamma*100:.1f}%</b>. Разница объясняется тем, что Модель 2 корректно
        учитывает доход страховщика от инвестирования временно свободных средств
        до момента наступления страховых событий.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Интегральная функция распределения совокупного ущерба")
    st.markdown(
        "Кривые ниже показывают вероятность того, что совокупный ущерб портфеля не "
        "превысит заданного уровня. Вертикальные пунктирные линии отмечают значения "
        "требуемого фонда, обеспечивающие заданный уровень надёжности."
    )

    x = np.linspace(0, max(r1[0], r2[0]) * 1.4, 500)
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(x/1e6, gamma.cdf(x, r1[3], scale=1/r1[4]),
             label="Модель 1 — без дисконтирования", color=COLOR_M1, lw=3)
    ax1.plot(x/1e6, gamma.cdf(x, r2[3], scale=1/r2[4]),
             label="Модель 2 — с дисконтированием", color=COLOR_M2, ls="--", lw=3)
    ax1.axhline(y=P_gamma, color=COLOR_REF, ls=":", lw=2.5,
                label=f"Уровень надёжности P = {P_gamma}")
    ax1.axvline(x=r1[0]/1e6, color=COLOR_M1, ls=":", lw=1.5, alpha=0.6)
    ax1.axvline(x=r2[0]/1e6, color=COLOR_M2, ls=":", lw=1.5, alpha=0.6)
    ax1.set_xlabel("Совокупный накопленный ущерб, млн руб.")
    ax1.set_ylabel("Вероятность покрытия R(x)")
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc='lower right', framealpha=0.95, facecolor='#FFFFFF', edgecolor='#E5E7EB')
    st.pyplot(fig1)

# ---------------------------------------------------------------------
# ВКЛАДКА 2
# ---------------------------------------------------------------------
with tab2:
    st.markdown("## Анализ чувствительности тарифа к ключевым параметрам")
    st.markdown(
        "Графики ниже показывают, как изменяется итоговая величина брутто-тарифа "
        "при варьировании одного из определяющих параметров с сохранением остальных "
        "входных значений."
    )

    st.markdown("### График 1. Зависимость брутто-тарифа от срока накопления T")
    st.markdown(f"""
    <div class="description-block">
    <b>Что показывает график.</b> По горизонтальной оси отложен срок действия программы
    страхования — период, в течение которого формируется резервный фонд. По вертикальной
    оси — значение брутто-тарифа, выраженное в процентах от страховой суммы.<br><br>
    <b>Как интерпретировать.</b> Каждая точка кривой отвечает на вопрос: «какой тариф нужен,
    чтобы покрыть катастрофические убытки за заданное число лет с требуемой надёжностью?».
    Модель 1 (без учёта инвестиций) демонстрирует практически линейный рост тарифа
    со временем, поскольку каждый дополнительный год добавляет в портфель новые риски,
    никак не компенсируемые доходом от размещения средств. Модель 2, напротив, выходит
    на стабильное плато: сложный процент от инвестирования резервов уравновешивает рост
    накопленных рисков, обеспечивая стабильность тарифа на длинном горизонте.<br><br>
    <b>Практический вывод.</b> Чем длиннее срок накопления, тем сильнее расхождение
    моделей и тем существеннее экономия для страхователя при использовании Модели 2.
    </div>
    """, unsafe_allow_html=True)

    t_array = np.arange(1, 31)
    trbr_m1 = [calc_model(False, temp_T=t)[2] for t in t_array]
    trbr_m2 = [calc_model(True,  temp_T=t)[2] for t in t_array]
    fig2, ax2 = plt.subplots(figsize=(12, 5.5))
    ax2.plot(t_array, trbr_m1, label="Модель 1 — без дисконтирования",
             color=COLOR_M1, lw=3, marker='o', markersize=6, markerfacecolor='#FFFFFF')
    ax2.plot(t_array, trbr_m2, label="Модель 2 — с дисконтированием",
             color=COLOR_M2, lw=3, marker='s', markersize=6, markerfacecolor='#FFFFFF')
    ax2.set_xlabel("Срок накопления резерва T, лет")
    ax2.set_ylabel("Брутто-тариф, %")
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc='best', framealpha=0.95, facecolor='#FFFFFF', edgecolor='#E5E7EB')
    st.pyplot(fig2)

    st.markdown("---")
    st.markdown("### График 2. Зависимость брутто-тарифа от нормы дисконтирования δ")
    st.markdown(f"""
    <div class="description-block">
    <b>Что такое δ в этом контексте.</b> Параметр δ — это норма доходности, под которую
    страховщик размещает временно свободные средства резервного фонда (банковские
    депозиты, государственные облигации, инвестиционный портфель). Чем выше δ, тем
    больший доход получает страховщик за время до наступления страховых событий.<br><br>
    <b>Что показывает график.</b> По горизонтальной оси — значение нормы дисконтирования
    в процентах годовых (от 0 % до 18 %). По вертикальной оси — соответствующее значение
    брутто-тарифа Модели 2 при сроке T = {T} лет.<br><br>
    <b>Как интерпретировать.</b> Кривая монотонно убывает: чем выше доходность размещения
    резервов, тем ниже может быть тарифный взнос для обеспечения той же финансовой
    устойчивости фонда. Это происходит потому, что часть будущих страховых выплат
    «оплачивается» инвестиционным доходом, а не премиями страхователей.<br><br>
    <b>Практический вывод.</b> График позволяет страховой компании оценить, какой объём
    инвестиционного дохода необходим для предложения конкурентоспособного тарифа
    на рынке, и показывает чувствительность тарифа к колебаниям рыночных ставок —
    параметр, важный для стресс-тестирования портфеля.
    </div>
    """, unsafe_allow_html=True)

    d_array = np.linspace(0, 0.18, 30)
    trbr_d2 = [calc_model(True, temp_delta=d)[2] for d in d_array]
    fig3, ax3 = plt.subplots(figsize=(12, 5.5))
    ax3.plot(d_array * 100, trbr_d2, color=COLOR_ACCENT, lw=3.5,
             marker='o', markersize=7, markerfacecolor='#FFFFFF',
             label="Модель 2 — с дисконтированием")
    ax3.fill_between(d_array * 100, trbr_d2, alpha=0.2, color=COLOR_ACCENT)
    ax3.set_xlabel("Норма дисконтирования δ, % годовых")
    ax3.set_ylabel("Брутто-тариф, %")
    ax3.grid(True, alpha=0.4)
    ax3.legend(loc='best', framealpha=0.95, facecolor='#FFFFFF', edgecolor='#E5E7EB')
    st.pyplot(fig3)

# ---------------------------------------------------------------------
# ВКЛАДКА 3 — 3D
# ---------------------------------------------------------------------
with tab3:
    st.markdown("## Трёхмерная поверхность тарифных решений")
    st.markdown("""
    <div class="description-block">
    <b>Назначение графика.</b> Трёхмерная поверхность визуализирует одновременное влияние
    двух ключевых параметров — срока накопления T и нормы дисконтирования δ — на
    итоговую величину брутто-тарифа в Модели 2. Этот график является интегральным
    инструментом для актуария: он позволяет одним взглядом охватить пространство
    допустимых тарифных решений.<br><br>
    <b>Что отложено на осях:</b><br>
    • <b>Ось X (вглубь)</b> — срок накопления резерва T, от 5 до 30 лет.<br>
    • <b>Ось Y (вдоль)</b> — норма дисконтирования δ, от 1 % до 15 % годовых.<br>
    • <b>Ось Z (высота)</b> — итоговое значение брутто-тарифа в процентах.<br><br>
    <b>Как читать поверхность.</b> Цветовая шкала показывает величину тарифа: холодные
    оттенки (синий, фиолетовый) соответствуют низким тарифам, тёплые (жёлтый, красный) —
    высоким. Возвышенные участки — это области сочетания параметров, при которых
    страхование становится дорогим. Низменные участки — зоны конкурентоспособных тарифов.<br><br>
    <b>Управление графиком.</b> График интерактивный: вращайте мышью, приближайте колесом,
    выделяйте область для увеличения. Двойной щелчок возвращает исходный вид. При
    наведении курсора отображаются точные значения T, δ и тарифа.
    </div>
    """, unsafe_allow_html=True)

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
                title=dict(text="Тариф, %", font=dict(size=20, color='#111827')),
                tickfont=dict(size=16, color='#111827'),
                thickness=25,
                len=0.75
            ),
            contours={
                "z": {"show": True, "start": Z.min(), "end": Z.max(),
                      "size": (Z.max() - Z.min())/12, "color": "#1E40AF"}
            }
        )
    ])
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(
                title=dict(text='Срок T, лет', font=dict(size=22, color='#111827')),
                tickfont=dict(size=17, color='#111827'),
                backgroundcolor='#FFFFFF', gridcolor='#E5E7EB'
            ),
            yaxis=dict(
                title=dict(text='Ставка δ', font=dict(size=22, color='#111827')),
                tickfont=dict(size=17, color='#111827'),
                backgroundcolor='#FFFFFF', gridcolor='#E5E7EB'
            ),
            zaxis=dict(
                title=dict(text='Тариф, %', font=dict(size=22, color='#111827')),
                tickfont=dict(size=17, color='#111827'),
                backgroundcolor='#FFFFFF', gridcolor='#E5E7EB'
            ),
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0))
        ),
        height=900,
        paper_bgcolor='#FFFFFF',
        font=dict(color='#111827', size=18),
        margin=dict(l=10, r=10, b=10, t=40)
    )
    st.plotly_chart(fig_3d, use_container_width=True)
    
    z_min_idx = np.unravel_index(np.argmin(Z), Z.shape)
    z_max_idx = np.unravel_index(np.argmax(Z), Z.shape)
    st.markdown(f"""
    <div class="info-block">
    📍 <b>Экстремумы поверхности.</b><br><br>
    <b style="color:#10B981;">Минимальный тариф</b> на исследованной области:
    <b style="font-size:24px;">{Z.min():.4f}%</b><br>
    достигается при T = {T_grid[z_min_idx]:.1f} лет, δ = {D_grid[z_min_idx]*100:.1f}%<br><br>
    <b style="color:#DC2626;">Максимальный тариф</b> на исследованной области:
    <b style="font-size:24px;">{Z.max():.4f}%</b><br>
    достигается при T = {T_grid[z_max_idx]:.1f} лет, δ = {D_grid[z_max_idx]*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# ВКЛАДКА 4 — МЕТОДОЛОГИЯ
# ---------------------------------------------------------------------
with tab4:
    st.markdown("## Методологическое описание программного комплекса")

    st.markdown("### 1. Постановка актуарной задачи")
    st.markdown("""
    Страхование промышленных объектов от катастрофических рисков занимает особое место
    в актуарной практике. Объекты подобной группы — металлургические комбинаты,
    нефтеперегонные и химические заводы, объекты атомной энергетики, крупные транспортные
    узлы — характеризуются накоплением значительных масс пожаро- и взрывоопасных веществ,
    высокой капиталоёмкостью и протяжёнными технологическими циклами.

    Особенность данного вида страхования состоит в том, что страховые риски одновременно
    име **малую частоту наступления** (порядка одного события на десятки лет на объект)
    и **крайне высокую тяжесть последствий** — экономический ущерб от единичного события
    может достигать десятков и сотен миллионов рублей. Это делает неприменимыми
    классические методы массового страхования, опирающиеся на закон больших чисел.

    Решением задачи служит механизм **временной раскладки риска**: страховщик принимает
    на себя ответственность по группе объектов на длительном интервале времени T
    (15–30 лет), за который накапливает достаточный резервный фонд для покрытия
    возможных катастрофических убытков. Свободные средства фонда размещаются на
    финансовом рынке под непрерывную ставку δ, что обеспечивает дополнительный
    инвестиционный доход.
    """)

    st.markdown("### 2. Типология катастрофических рисков")
    st.markdown("""
    Программный комплекс ориентирован на работу с рисками следующих категорий:

    • **Природно-техногенные риски** — события, обусловленные воздействием природных
    факторов (землетрясения, наводнения, ураганы) на промышленную инфраструктуру.

    • **Техногенные риски** — аварии, обусловленные особенностями технологического
    процесса: взрывы, пожары, разрушения несущих конструкций, выбросы опасных веществ.

    • **Системные риски** — события, способные привести к каскадному отказу
    взаимосвязанных производственных систем и длительной остановке технологического
    процесса предприятия.

    Общим свойством этих рисков является то, что наступление одного страхового события
    влечёт гибель значительной массы оборудования и длительный простой, что отличает
    данные риски от обычных имущественных и переводит их в категорию катастрофических.
    """)

    st.markdown("### 3. Параметры модели и их интерпретация")
    st.markdown("""
    | Параметр | Обозначение | Содержательный смысл |
    |---|---|---|
    | Число застрахованных объектов | N | Количество однородных предприятий в портфеле |
    | Интенсивность рисков | λ | Среднее число событий на один объект в год |
    | Период накопления | T | Длительность интервала формирования фонда |
    | Максимальный ущерб | S_max | Восстановительная стоимость при полной гибели |
    | Уровень надёжности | P | Вероятность полного покрытия выплат |
    | Доля нагрузки | f | Доля брутто-премии на расходы страховщика |
    | Норма дисконтирования | δ | Ставка доходности размещения средств фонда |
    """)

    st.markdown("### 4. Математическая модель совокупного ущерба")
    st.markdown("""
    Совокупный страховой ущерб по группе застрахованных объектов на интервале (0, T)
    моделируется как сложный пуассоновский процесс. Число страховых событий описывается
    распределением Пуассона с параметром, зависящим от выбранной модели. Размер ущерба
    в единичном страховом событии аппроксимируется непрерывным **гамма-распределением**
    с параметрами формы α и масштаба β, идентифицируемыми по первым двум семиинвариантам
    (кумулянтам) характеристической функции совокупного ущерба.

    **Модель 1.** Финансовые потоки не приводятся к единому моменту времени;
    взносы и выплаты считаются равноценными независимо от их временной локализации.
    """)
    st.latex(r"\chi_1 = N \lambda T \, m_0")
    st.latex(r"\chi_2 = N \lambda T \, (m_0^2 + D_0)")

    st.markdown("""
    **Модель 2.** Финансовые потоки приводятся к начальному моменту времени операцией
    непрерывного дисконтирования с нормой δ. Это позволяет учесть инвестиционный
    доход от размещения временно свободных средств фонда.
    """)
    st.latex(r"\chi_1 = N \lambda m_0 \cdot \frac{1 - e^{-\delta T}}{\delta}")
    st.latex(r"\chi_2 = N \lambda (m_0^2 + D_0) \cdot \frac{1 - e^{-2\delta T}}{2\delta}")

# ---------------------------------------------------------------------
# ВКЛАДКА 5 — ОТЧЁТЫ И ДАННЫЕ (Реализовано с нуля)
# ---------------------------------------------------------------------
with tab5:
    st.markdown("## Экспорт результатов и табличные данные")
    st.markdown(
        "Ниже приведена сводная таблица параметров и ключевых индикаторов расчёта. "
        "Вы можете скачать эти данные в формате CSV для последующего анализа в Excel."
    )
    
    # Формируем датафрейм со всеми показателями
    report_data = {
        "Наименование метрики": [
            "Число застрахованных объектов (N)",
            "Интенсивность наступления рисков (λ)",
            "Период накопления фонда (T), лет",
            "Максимальный ущерб при полной гибели (S_max), руб",
            "Требуемый уровень надёжности (P)",
            "Норма дисконтирования (δ), годовых",
            "Доля страховой нагрузки (f)",
            "М1: Требуемый размер фонда, руб",
            "М1: Расчётный брутто-тариф, %",
            "М2: Требуемый размер фонда (с дисконтом), руб",
            "М2: Расчётный брутто-тариф (с дисконтом), %",
            "Экономия фонда за счёт инвест. дохода, руб",
            "Снижение тарифной ставки, %"
        ],
        "Значение": [
            f"{N}",
            f"{lam:.3f}",
            f"{T}",
            f"{S_vos:,.0f}",
            f"{P_gamma*100:.1f}%",
            f"{delta*100:.1f}%",
            f"{f*100:.0f}%",
            f"{r1[0]:,.0f}",
            f"{r1[2]:.4f}",
            f"{r2[0]:,.0f}",
            f"{r2[2]:.4f}",
            f"{r1[0] - r2[0]:,.0f}",
            f"{(1 - r2[2]/r1[2])*100:.2f}%" if r1[2] > 0 else "0.00%"
        ]
    }
    
    df = pd.DataFrame(report_data)
    
    # Отрисовываем таблицу через стилизованный HTML, подготовленный в CSS (.custom-table)
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
    
    # Кнопка экспорта в CSV
    csv = df.to_csv(index=False).encode('utf-8-sig') # кодировка utf-8-sig для корректного открытия кириллицы в Excel
    st.download_button(
        label="📥 Скачать сводный актуарный отчёт (CSV)",
        data=csv,
        file_name="actuarial_catastrophe_report.csv",
        mime="text/csv"
    )
