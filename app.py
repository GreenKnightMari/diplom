import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma

# Настройка страницы
st.set_page_config(page_title="Калькулятор тарифов", layout="wide")

st.title("📊 Калькулятор страховых тарифов (Катастрофические риски)")
st.markdown("""
Это приложение рассчитывает страховые тарифы по двум моделям: 
**Модель 1** (упрощенная, из Mathcad) и **Модель 2** (с полным дисконтированием).
""")

# --- БОКОВАЯ ПАНЕЛЬ С ВВОДОМ ---
st.sidebar.header("📝 Исходные данные")

N = st.sidebar.number_input("Количество предприятий (N)", value=100, min_value=1)
lam = st.sidebar.number_input("Интенсивность ущерба (λ)", value=0.01, format="%.3f")
T = st.sidebar.slider("Срок накопления (T), лет", 1, 50, 10)
S_vos = st.sidebar.number_input("Макс. ответственность (S_max), руб", value=100_000_000)
P_gamma = st.sidebar.slider("Надежность (вероятность)", 0.80, 0.99, 0.95)
f = st.sidebar.slider("Нагрузка (расходы компании), %", 0, 50, 20) / 100
delta = st.sidebar.slider("Норма дисконтирования (δ)", 0.0, 0.20, 0.05)

# --- МАТЕМАТИЧЕСКАЯ ЛОГИКА ---
m0 = S_vos / 2
D0 = (S_vos**2) / 12

def calculate_results(is_discounted):
    if not is_discounted:
        # Модель 1
        eta = N * lam * T
        chi1 = eta * m0
        chi2 = eta * (m0**2 + D0)
    else:
        # Модель 2
        chi1 = N * lam * m0 * (1 - np.exp(-delta * T)) / delta
        chi2 = N * lam * (m0**2 + D0) * (1 - np.exp(-2 * delta * T)) / (2 * delta)
    
    beta_param = chi1 / chi2
    alpha_param = chi1 * beta_param
    
    # Начальный капитал
    Pr = gamma.ppf(P_gamma, a=alpha_param, scale=1/beta_param)
    # Нетто-тариф
    Tr_n = (Pr * 100) / (N * S_vos * T)
    # Брутто-тариф
    if not is_discounted:
        Tr_br = (Tr_n / (1 - f)) * np.exp(delta * T)
    else:
        Tr_br = Tr_n / (1 - f)
        
    return Pr, Tr_n, Tr_br, alpha_param, beta_param

# Выполняем расчеты для обеих моделей
res1 = calculate_results(False) # Модель 1
res2 = calculate_results(True)  # Модель 2

# --- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔹 Модель 1 (без дисконта)")
    st.metric("Начальный капитал", f"{res1[0]:,.0f} ₽")
    st.metric("Брутто-тариф", f"{res1[2]:.4f} %")

with col2:
    st.subheader("🔸 Модель 2 (с дисконтом)")
    st.metric("Начальный капитал", f"{res2[0]:,.0f} ₽")
    st.metric("Брутто-тариф", f"{res2[2]:.4f} %")

# Сравнение
st.divider()
savings = (1 - res2[2]/res1[2]) * 100
st.success(f"✅ **Вывод:** Использование Модели 2 позволяет снизить тариф на **{savings:.2f}%** при той же надежности.")

# --- ГРАФИКИ ---
st.subheader("📈 Функция распределения совокупного ущерба")

x_max = max(res1[0], res2[0]) * 1.5
x = np.linspace(0, x_max, 500)
y1 = gamma.cdf(x, a=res1[3], scale=1/res1[4])
y2 = gamma.cdf(x, a=res2[3], scale=1/res2[4])

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x / 1e6, y1, label="Модель 1 (Без дисконта)", color="blue", linewidth=2)
ax.plot(x / 1e6, y2, label="Модель 2 (С дисконтом)", color="red", linestyle="--", linewidth=2)
ax.axhline(y=P_gamma, color="gray", linestyle=":", label=f"Надежность {P_gamma}")
ax.set_xlabel("Суммарный ущерб (млн. руб.)")
ax.set_ylabel("Вероятность R(x)")
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)
