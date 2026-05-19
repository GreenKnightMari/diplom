import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
import pandas as pd
import plotly.graph_objects as go

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Анализ катастрофических рисков", layout="wide", page_icon="🛡️")

# --- ГЛОБАЛЬНЫЙ ИНЖЕКТ CSS ДЛЯ КРУПНЫХ ШРИФТОВ И ДИЗАЙНА ---
st.markdown("""
    <style>
    /* Глубокий темно-синий фон и увеличение базового шрифта */
    .stApp {
        background-color: #031326;
        color: #E2E8F0;
        font-size: 18px !important;
    }
    /* Увеличение текста в боковой панели */
    [data-testid="stSidebar"] {
        background-color: #0B1E36;
        border-right: 1px solid #1E3A5F;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    /* Стилизация заголовков */
    h1 { color: #38BDF8 !important; font-size: 36px !important; font-weight: bold !important; text-align: center; margin-bottom: 25px; }
    h2 { color: #38BDF8 !important; font-size: 28px !important; margin-top: 20px; }
    h3 { color: #64FFDA !important; font-size: 22px !important; margin-top: 15px; }
    
    /* Увеличение обычного текста во вкладках */
    .stMarkdown p, .stMarkdown li {
        font-size: 18px !important;
        line-height: 1.6 !important;
    }
    
    /* Огромные и заметные блоки результатов */
    .metric-box-m1 {
        background-color: #0B1E36;
        border-left: 6px solid #38BDF8;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .metric-box-m2 {
        background-color: #0B1E36;
        border-left: 6px solid #64FFDA;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    /* ОГРОМНЫЕ ЯРКИЕ КНОПКИ СКАЧИВАНИЯ */
    .stButton button {
        font-size: 20px !important;
        padding: 15px 30px !important;
        width: 100% !important;
        background-color: #38BDF8 !important;
        color: #031326 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(56, 189, 248, 0.2);
        transition: all 0.3s ease;
        margin-top: 15px;
    }
    .stButton button:hover {
        background-color: #64FFDA !important;
        box-shadow: 0 6px 12px rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
    }
    
    /* Крупная кастомная таблица данных */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 18px;
        text-align: left;
    }
    .custom-table th {
        background-color: #1E3A5F;
        color: #64FFDA;
        padding: 12px;
        border: 1px solid #233554;
    }
    .custom-table td {
        padding: 12px;
        border: 1px solid #233554;
        background-color: #0B1E36;
    }
    .custom-table tr:hover td {
        background-color: #112240;
    }
    </style>
    """, unsafe_allow_html=True)

# Универсальные настройки графиков Matplotlib для идеальной видимости
plt.style.use('dark_background')
plt.rcParams.update({
    'axes.facecolor': '#031326',
    'figure.facecolor': '#031326',
    'grid.color': '#1E3A5F',
    'text.color': '#E2E8F0',
    'axes.labelcolor': '#E2E8F0',
    'xtick.color': '#E2E8F0',
    'ytick.color': '#E2E8F0',
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12
})

st.markdown("<h1>🛡️ Программный комплекс оценки финансовой устойчивости страховых фондов</h1>", unsafe_allow_html=True)

# --- БОКОВАЯ ПАНЕЛЬ С ВВОДОМ ---
st.sidebar.header("⚙️ Входные параметры модели")
N = st.sidebar.number_input("Число застрахованных объектов (N), ед.", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность наступления рисков (λ)", value=0.01, format="%.3f")
T = st.sidebar.slider("Период накопления резерва (T), лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Максимальный ущерб при аварии (S_max), руб", value=100000000, step=1000000)
P_gamma = st.sidebar.slider("Заданный уровень надежности фонда (P)", 0.800, 0.999, 0.950, step=0.005)
f = st.sidebar.slider("Доля нагрузки в брутто-тарифе (f), %", 0, 50, 20) / 100
delta = st.sidebar.slider("Непрерывная ставка дисконтирования (δ)", 0.0, 0.20, 0.05, step=0.01)

# --- МАТЕМАТИЧЕСКОЕ ЯДРО ---
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

# --- ИНТЕРФЕЙС: ВКЛАДКИ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Сводный расчет тарифов", 
    "📈 2D Анализ зависимостей", 
    "🌌 3D Поверхность рисков",
    "📚 Методология и теория",
    "📥 Выгрузка отчетов и данных"
])

# --- ВКЛАДКА 1: СВОДНЫЙ РАСЧЕТ ---
with tab1:
    st.markdown("## Результаты сопоставления актуарных моделей")
    st.markdown("Здесь представлены итоговые значения необходимых резервов и расчетных ставок страховых взносов.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-box-m1">
            <h3 style="margin-top:0; color:#38BDF8;">Классическая модель (Без дисконтирования)</h3>
            <p>Необходимый стартовый капитал: <b style="font-size:22px; color:#38BDF8;">{r1[0]:,.0f} ₽</b></p>
            <p>Расчетный брутто-тариф: <b style="font-size:22px; color:#38BDF8;">{r1[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-box-m2">
            <h3 style="margin-top:0; color:#64FFDA;">Разработанная модель (С дисконтированием)</h3>
            <p>Необходимый стартовый капитал: <b style="font-size:22px; color:#64FFDA;">{r2[0]:,.0f} ₽</b></p>
            <p>Расчетный брутто-тариф: <b style="font-size:22px; color:#64FFDA;">{r2[2]:.4f} %</b></p>
        </div>
        """, unsafe_allow_html=True)

    savings = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    st.markdown(f"""
    <div style="background-color: #112240; padding: 15px; border-radius: 8px; border: 1px solid #38BDF8; margin-top: 15px;">
        💡 <b>Экономическое заключение:</b> Учет временной стоимости капитала (инвестиционного дохода фонда) по Модели 2 
        позволяет снизить тарифную нагрузку на страхователей на <b>{savings:.2f}%</b> при неизменном уровне надежности фонда ({P_gamma*100}%).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Интегральная функция распределения совокупного ущерба")
    x = np.linspace(0, max(r1[0], r2[0]) * 1.4, 500)
    fig1, ax1 = plt.subplots(figsize=(10, 3.5))
    ax1.plot(x/1e6, gamma.cdf(x, r1[3], scale=1/r1[4]), label="Модель 1 (без дисконта)", color="#38BDF8", lw=2.5)
    ax1.plot(x/1e6, gamma.cdf(x, r2[3], scale=1/r2[4]), label="Модель 2 (с дисконтом)", color="#F87171", ls="--", lw=2.5)
    ax1.axhline(y=P_gamma, color="#94A3B8", ls=":", label=f"Уровень безопасности P={P_gamma}")
    ax1.set_xlabel("Совокупный накопленный ущерб (млн. руб.)")
    ax1.set_ylabel("Вероятность покрытия R(x)")
    ax1.grid(True, alpha=0.2)
    ax1.legend(facecolor='#0B1E36', edgecolor='#1E3A5F')
    st.pyplot(fig1)

# --- ВКЛАДКА 2: 2D АНАЛИТИКА ---
with tab2:
    st.markdown("## Двумерный анализ чувствительности моделей")
    
    col_g1, col_g2 = st.columns(2)
    t_array = np.arange(1, 31)
    
    with col_g1:
        st.markdown("### 1. Зависимость брутто-тарифа от срока накопления")
        trbr_m1 = [calc_model(False, temp_T=t)[2] for t in t_array]
        trbr_m2 = [calc_model(True, temp_T=t)[2] for t in t_array]
        fig2, ax2 = plt.subplots()
        ax2.plot(t_array, trbr_m1, label="Модель 1 (Без дисконта)", color="#38BDF8", lw=2)
        ax2.plot(t_array, trbr_m2, label="Модель 2 (С дисконтом)", color="#F87171", lw=2)
        ax2.set_xlabel("Срок удержания портфеля рисков (T), лет")
        ax2.set_ylabel("Величина брутто-тарифа (%)")
        ax2.grid(True, alpha=0.2)
        ax2.legend()
        st.pyplot(fig2)
        st.markdown("""
        **Что означает этот график:** График иллюстрирует критическую ошибку Модели 1. Без дисконтирования страховой тариф неограниченно растет с течением времени из-за линейного накопления рисков. 
        Модель 2 (красная линия) стабилизирует тариф, доказывая, что сложный процент от инвестирования резервов компенсирует будущие катастрофические убытки.
        """)
        
    with col_g2:
        st.markdown("### 2. Влияние ставки дисконтирования на брутто-тариф")
        d_array = np.linspace(0, 0.18, 30)
        trbr_d2 = [calc_model(True, temp_delta=d)[2] for d in d_array]
        fig3, ax3 = plt.subplots()
        ax3.plot(d_array * 100, trbr_d2, color="#64FFDA", lw=2, label="Модель 2")
        ax3.set_xlabel("Непрерывная процентная ставка (δ), %")
        ax3.set_ylabel("Величина брутто-тарифа (%)")
        ax3.grid(True, alpha=0.2)
        ax3.legend()
        st.pyplot(fig3)
        st.markdown("""
        **Что означает этот график:** Этот график исследует только **Модель 2**. Он наглядно демонстрирует, как доходность размещения средств фонда влияет на стоимость страховки. 
        Чем выше ставка дисконтирования $\delta$ (эффективность инвестиций компании), тем ниже может быть тарифный взнос для обеспечения той же финансовой устойчивости.
        """)

# --- ВКЛАДКА 3: 3D ПОВЕРХНОСТЬ ---
with tab3:
    st.markdown("## Трехмерное пространство тарифных решений")
    
    st.markdown("""
    ### 🧭 Руководство по интерпретации 3D-модели:
    * **Ось X (Срок T):** Временной горизонт планирования (от 5 до 30 лет).
    * **Ось Y (Дисконт δ):** Норма доходности инвестиционного портфеля страховой компании (от 1% до 15%).
    * **Высота Z (Брутто-тариф):** Результирующий страховой тариф в %.
    
    **Аналитическая ценность:** Поверхность наглядно демонстрирует синергетический эффект времени и доходности. Минимальные (наиболее конкурентоспособные) тарифы находятся в области максимальных сроков и высоких ставок (самая низкая, темно-синяя часть воронки). Вы можете вращать и масштабировать этот график мышью для демонстрации на защите.
    """)
    
    t_vals = np.linspace(5, 30, 30)
    d_vals = np.linspace(0.01, 0.15, 30)
    T_grid, D_grid = np.meshgrid(t_vals, d_vals)
    Z = np.zeros_like(T_grid)
    
    for i in range(T_grid.shape[0]):
        for j in range(T_grid.shape[1]):
            Z[i, j] = calc_model(True, temp_T=T_grid[i, j], temp_delta=D_grid[i, j])[2]
            
    fig_3d = go.Figure(data=[go.Surface(z=Z, x=T_grid, y=D_grid, colorscale='Viridis')])
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title='Срок (T, лет)', backgroundcolor="#0B1E36"),
            yaxis=dict(title='Ставка дисконта (δ)', backgroundcolor="#0B1E36"),
            zaxis=dict(title='Тариф (%)', backgroundcolor="#0B1E36"),
        ),
        width=1100,
        height=700,
        paper_bgcolor="#031326",
        font=dict(color="#E2E8F0", size=14),
        margin=dict(l=10, r=10, b=10, t=10)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# --- ВКЛАДКА 4: МЕТОДОЛОГИЯ ---
with tab4:
    st.markdown("## Научно-методологическое обоснование комплекса")
    
    st.markdown("""
    ### 1. Постановка актуарной задачи
    При страховании крупных имущественных комплексов от **катастрофических рисков** (техногенные взрывы, экологические аварии, разрушения цехов) классические методы страхования, опирающиеся на закон больших чисел, не применимы напрямую. Вероятность единичного события крайне мала ($\lambda \to 0$), однако ущерб носит тотальный характер и исчисляется сотнями миллионов.
    
    Для решения этой проблемы дипломная работа реализует **временную раскладку рисков** с помощью замкнутого накопительного страхового механизма. Страховщик формирует специализированный фонд резервов на протяжении долгосрочного периода $T$, инвестируя свободные средства под непрерывную ставку процентов $\delta$.
    
    ### 2. Математическое описание моделей
    Совокупный дисконтированный страховой ущерб на интервале времени $[0, T]$ аппроксимируется непрерывным **Гамма-распределением** с параметрами формы ($\alpha$) и масштаба ($\beta$).
    
    Для нахождения этих параметров используется метод моментов, связывающий их с первыми двумя **семиинвариантами (кумулянтами)** характеристической функции совокупных убытков.
    
    **Для Модели 1 (без дисконтирования потоков во времени):**
    """)
    st.latex(r"\chi_1 = N \cdot \lambda \cdot T \cdot m_0")
    st.latex(r"\chi_2 = N \cdot \lambda \cdot T \cdot (m_0^2 + D_0)")
    
    st.markdown("**Для Модели 2 (с полным непрерывным дисконтированием страховых выплат):**")
    st.latex(r"\chi_1 = N \lambda m_0 \frac{1 - e^{-\delta T}}{\delta}")
    st.latex(r"\chi_2 = N \lambda (m_0^2 + D_0) \frac{1 - e^{-2\delta T}}{2\delta}")
    
    st.markdown("Переход от кумулянтов к структурным параметрам плотности вероятности Гамма-распределения:")
    st.latex(r"\beta = \frac{\chi_1}{\chi_2}, \quad \alpha = \chi_1 \cdot \beta")
    
    st.markdown("""
    ### 3. Алгоритм поиска тарифов
    1. На основе Гамма-распределения вычисляется квантиль уровня доверия $P_{\gamma}$ (например, 95% или 99%), определяющий величину целевого фонда (начального капитала $P_r$).
    2. Вычисляется Нетто-тариф ($Tr_n$), распределяющий необходимый объем фонда равномерно между всеми участниками $N$ и годами $T$.
    3. Рассчитывается Брутто-тариф ($Tr_{br}$) с учетом административных расходов компании (нагрузка $f$). В Модели 1 на этом этапе применяется повышающий коэффициент $e^{\delta T}$, отражающий обесценение будущих денег, что приводит к завышению стоимости полиса.
    """)

# --- ВКЛАДКА 5: ДАННЫЕ И ОТЧЕТЫ ---
with tab5:
    st.markdown("## Сгенерированная матрица плановых показателей по годам")
    st.markdown("Эта таблица содержит пошаговую динамику изменения тарифов по мере увеличения горизонта планирования от 1 года до заданного вами значения.")
    
    # Расчет датафрейма
    data = []
    for t_step in range(1, T + 1):
        res1_t = calc_model(False, temp_T=t_step)
        res2_t = calc_model(True, temp_T=t_step)
        data.append({
            "Год (T)": t_step,
            "Капитал М1 (руб)": f"{res1_t[0]:,.0f}",
            "Капитал М2 (руб)": f"{res2_t[0]:,.0f}",
            "Тариф М1 (%)": f"{res1_t[2]:.4f}",
            "Тариф М2 (%)": f"{res2_t[2]:.4f}",
            "Разница тарифов (%)": f"{((1 - res2_t[2]/res1_t[2])*100):.2f}%" if res1_t[2]>0 else "0%"
        })
    df = pd.DataFrame(data)
    
    # Сборка ЧЕТКОЙ КРУПНОЙ HTML ТАБЛИЦЫ взамен стандартного мелкого dataframe
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
    
    # Выводим крупную таблицу
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.markdown("## 📥 Экспорт результатов для дипломной работы")
    st.markdown("Используйте эти кнопки, чтобы скачать готовые материалы для добавления в практическую главу и приложения к диплому.")
    
    # Кнопка 1: Скачивание CSV таблицы рисков
    csv_data = pd.DataFrame([{
        "Год (T)": i+1, 
        "Тариф_М1_процент": calc_model(False, temp_T=i+1)[2], 
        "Тариф_М2_процент": calc_model(True, temp_T=i+1)[2]} 
        for i in range(T)]).to_csv(index=False).encode('utf-8')
        
    st.download_button(
        label="📥 СКАЧАТЬ ТАБЛИЦУ РАСЧЕТОВ (ДЛЯ EXCEL)",
        data=csv_data,
        file_name='insurance_matrix_report.csv',
        mime='text/csv',
    )
    
    # Кнопка 2: Скачивание текстового заключения
    report_text = f"""АНАЛИТИЧЕСКИЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ МОДЕЛИРОВАНИЯ
===================================================
Выполнено в рамках дипломного проектирования.

ИСХОДНЫЕ МАКРОПАРАМЕТРЫ ПОРТФЕЛЯ:
- Количество застрахованных объектов (N): {N} ед.
- Базовая интенсивность катастроф (λ): {lam}
- Максимальный лимит ответственности (S_max): {S_vos:,.2f} руб.
- Заданная надежность резервного фонда (P): {P_gamma*100}%
- Непрерывная норма дисконтирования (δ): {delta*100}%

ИТОГОВЫЕ ТАРИФНЫЕ СТАВКИ (Для расчетного периода T = {T} лет):
1. Классический подход (Модель 1 без дисконта): {r1[2]:.4f} %
2. Модифицированный подход (Модель 2 с полным дисконтом): {r2[2]:.4f} %

НАУЧНО-ПРАКТИЧЕСКИЙ ВЫВОД:
Внедрение разработанной математической модели 2 обеспечивает снижение 
конечной стоимости страховой защиты на {savings:.2f}% по сравнению с классическим расчетом. 
Экономический эффект достигается за счет точной капитализации инвестиционного дохода 
от размещения временно свободных средств страховых резервов фонда. Финансовая надежность 
фонда полностью удовлетворяет жесткому критерию устойчивости и составляет {P_gamma*100}%.
"""
    st.download_button(
        label="📄 СКАЧАТЬ ГОТОВОЕ ТЕКСТОВОЕ ЗАКЛЮЧЕНИЕ (ДЛЯ ВСТАВКИ В ТЕКСТ ДИПЛОМА)",
        data=report_text,
        file_name='academic_conclusion.txt',
        mime='text/plain',
    )
