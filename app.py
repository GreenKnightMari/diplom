import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
import pandas as pd
import io

# --- НАСТРОЙКИ СТРАНИЦЫ И СТИЛЬ ---
st.set_page_config(page_title="Анализ катастрофических рисков", layout="wide", page_icon="🛡️")

# Настройка цвета фона через CSS (светло-сине-серый деловой стиль)
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f7f6;
    }
    .main-header {
        color: #1f3b4d;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🛡️ Система моделирования тарифов при катастрофических рисках</h1>", unsafe_allow_html=True)

# --- БОКОВАЯ ПАНЕЛЬ С ВВОДОМ ---
st.sidebar.header("⚙️ Входные параметры")
N = st.sidebar.number_input("Число объектов (N)", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность λ", value=0.01, format="%.3f")
T = st.sidebar.slider("Период накопления (T), лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Макс. ущерб (S_max), руб", value=100_000_000, step=1000000)
P_gamma = st.sidebar.slider("Надежность (P)", 0.80, 0.99, 0.95, step=0.01)
f = st.sidebar.slider("Нагрузка (f), %", 0, 50, 20) / 100
delta = st.sidebar.slider("Ставка дисконтирования (δ)", 0.0, 0.20, 0.05, step=0.01)

# --- БАЗОВАЯ МАТЕМАТИКА ---
m0 = S_vos / 2
D0 = (S_vos**2) / 12

def calc_model(is_disc, temp_T=None, temp_P=None):
    """Универсальная функция расчета (позволяет подменять T и P для графиков)"""
    t_val = temp_T if temp_T is not None else T
    p_val = temp_P if temp_P is not None else P_gamma
    
    if not is_disc:
        eta = N * lam * t_val
        c1, c2 = eta * m0, eta * (m0**2 + D0)
    else:
        c1 = N * lam * m0 * (1 - np.exp(-delta * t_val)) / delta
        c2 = N * lam * (m0**2 + D0) * (1 - np.exp(-2 * delta * t_val)) / (2 * delta)
    
    b = c1 / c2 if c2 != 0 else 1e-10
    a = c1 * b if b != 0 else 1e-10
    
    Pr = gamma.ppf(p_val, a=a, scale=1/b) if a > 0 else 0
    Trn = (Pr * 100) / (N * S_vos * t_val) if t_val > 0 else 0
    Trbr = (Trn / (1 - f)) * (np.exp(delta * t_val) if not is_disc else 1)
    
    return Pr, Trn, Trbr, a, b

# Основные расчеты
r1 = calc_model(False)
r2 = calc_model(True)

# --- РАЗДЕЛЕНИЕ НА ВКЛАДКИ (ДЛЯ ДИПЛОМА ЭТО ТОП) ---
tab1, tab2, tab3 = st.tabs(["📊 Основной расчет", "📈 Анализ чувствительности", "📑 Отчеты и данные"])

# --- ВКЛАДКА 1: ОСНОВНОЙ РАСЧЕТ ---
with tab1:
    st.markdown("### Сравнение моделей при заданных параметрах")
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.info(f"**Модель 1 (без дисконта)**\n\nНачальный резерв: **{r1[0]:,.0f} ₽**\n\nБрутто-тариф: **{r1[2]:.4f} %**")
    with c_res2:
        st.success(f"**Модель 2 (с дисконтом)**\n\nНачальный резерв: **{r2[0]:,.0f} ₽**\n\nБрутто-тариф: **{r2[2]:.4f} %**")

    savings = (1 - r2[2]/r1[2]) * 100 if r1[2] > 0 else 0
    st.warning(f"💡 **Эффективность:** Модель 2 позволяет снизить тариф на **{savings:.2f}%**.")

    # График функции распределения
    st.markdown("### Интегральная функция распределения ущерба")
    x = np.linspace(0, max(r1[0], r2[0]) * 1.3, 400)
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(x/1e6, gamma.cdf(x, r1[3], scale=1/r1[4]), label="Модель 1", color="#1f77b4", linewidth=2)
    ax1.plot(x/1e6, gamma.cdf(x, r2[3], scale=1/r2[4]), label="Модель 2", color="#d62728", linestyle="--", linewidth=2)
    ax1.axhline(y=P_gamma, color="gray", linestyle=":", label="Требуемая надежность")
    ax1.set_xlabel("Ущерб (млн. руб.)")
    ax1.set_ylabel("Вероятность R(x)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)

# --- ВКЛАДКА 2: АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ ---
with tab2:
    st.markdown("### Исследование влияния параметров на тариф")
    st.markdown("Эти графики показывают, как поведут себя модели при изменении срока страхования или уровня надежности.")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # График 2: Тариф от времени T
        t_array = np.arange(1, 31)
        trbr_m1 = [calc_model(False, temp_T=t)[2] for t in t_array]
        trbr_m2 = [calc_model(True, temp_T=t)[2] for t in t_array]
        
        fig2, ax2 = plt.subplots()
        ax2.plot(t_array, trbr_m1, label="Модель 1", color="blue")
        ax2.plot(t_array, trbr_m2, label="Модель 2", color="red")
        ax2.set_xlabel("Срок накопления (T), лет")
        ax2.set_ylabel("Брутто-тариф (%)")
        ax2.set_title("Динамика тарифа от срока")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        st.pyplot(fig2)
        
    with col_g2:
        # График 3: Резерв от надежности P
        p_array = np.linspace(0.8, 0.999, 20)
        cap_m1 = [calc_model(False, temp_P=p)[0]/1e6 for p in p_array]
        cap_m2 = [calc_model(True, temp_P=p)[0]/1e6 for p in p_array]
        
        fig3, ax3 = plt.subplots()
        ax3.plot(p_array, cap_m1, label="Модель 1", color="blue")
        ax3.plot(p_array, cap_m2, label="Модель 2", color="red")
        ax3.set_xlabel("Надежность (P)")
        ax3.set_ylabel("Требуемый резерв (млн. руб)")
        ax3.set_title("Влияние надежности на капитал")
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        st.pyplot(fig3)

# --- ВКЛАДКА 3: ОТЧЕТЫ И ВЫГРУЗКА ---
with tab3:
    st.markdown("### Сводная таблица расчетов")
    
    # Формируем таблицу (Dataframe)
    data = []
    for t_step in range(1, T + 1):
        res1_t = calc_model(False, temp_T=t_step)
        res2_t = calc_model(True, temp_T=t_step)
        data.append({
            "Год (T)": t_step,
            "Капитал (М1), руб": round(res1_t[0], 2),
            "Капитал (М2), руб": round(res2_t[0], 2),
            "Тариф (М1), %": round(res1_t[2], 4),
            "Тариф (М2), %": round(res2_t[2], 4),
            "Экономия (Δ), %": round((1 - res2_t[2]/res1_t[2])*100, 2) if res1_t[2]>0 else 0
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Кнопка скачивания таблицы CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Скачать таблицу (CSV / Excel)",
        data=csv,
        file_name='insurance_analysis.csv',
        mime='text/csv',
    )
    
    # Кнопка генерации текстового заключения
    report_text = f"""
    АКАДЕМИЧЕСКИЙ ОТЧЕТ О РАСЧЕТЕ СТРАХОВЫХ ТАРИФОВ
    ===============================================
    Входные параметры:
    - Предприятий (N): {N}
    - Срок удержания риска (T): {T} лет
    - Интенсивность риска (λ): {lam}
    - Ставка дисконтирования: {delta*100}%
    - Уровень надежности: {P_gamma*100}%
    
    РЕЗУЛЬТАТЫ:
    1. Упрощенная модель (без дисконта):
       Требуемый начальный резерв: {r1[0]:,.2f} руб.
       Итоговый брутто-тариф: {r1[2]:.4f}%
       
    2. Разработанная модель (с дисконтом):
       Требуемый начальный резерв: {r2[0]:,.2f} руб.
       Итоговый брутто-тариф: {r2[2]:.4f}%
       
    ЗАКЛЮЧЕНИЕ:
    Использование механизма дисконтирования на периоде {T} лет 
    позволяет снизить тарифную нагрузку на страхователей на {savings:.2f}%, 
    сохраняя при этом финансовую устойчивость страховщика на уровне {P_gamma*100}%.
    """
    
    st.download_button(
        label="📄 Скачать текстовое заключение",
        data=report_text,
        file_name='conclusion.txt',
        mime='text/plain',
    )
