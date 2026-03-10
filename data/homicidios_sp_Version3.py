# =============================================================================
# Análise de Séries Temporais - Homicídios em São Paulo
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# clear
# import excel "...\Homícidios - SP.xlsx", sheet("Página1") firstrow
# =============================================================================
df = pd.read_csv("homicidios.csv", sep=";")

# Filtrar apenas São Paulo (cod 35)
df = df[df["cod"] == 35].copy()

# Renomear colunas para o padrão esperado: "período" -> "Ano", "valor" -> "Homicídios"
df = df.rename(columns={"período": "Ano", "valor": "Homicídios"})
df = df[["Ano", "Homicídios"]].sort_values("Ano").reset_index(drop=True)

print("=== Dados Importados (SP) ===")
print(df)

# =============================================================================
# tsset Ano
# =============================================================================
df = df.set_index("Ano")
df.index = pd.PeriodIndex(df.index, freq="Y")
df = df.sort_index()

# =============================================================================
# label variable Homicídios "Homicídios"
# rename Homicídios y1
# =============================================================================
df = df.rename(columns={"Homicídios": "y1"})

# =============================================================================
# twoway scatter y1 Ano
# =============================================================================
plt.figure(figsize=(10, 5))
plt.scatter(df.index.year, df["y1"], color="steelblue", edgecolors="black")
plt.title("Homicídios por Ano")
plt.xlabel("Ano")
plt.ylabel("Homicídios")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# =============================================================================
# tsline y1
# =============================================================================
plt.figure(figsize=(10, 5))
plt.plot(df.index.year, df["y1"], color="steelblue", linewidth=1.5, marker="o", markersize=4)
plt.title("Homicídios")
plt.xlabel("Ano")
plt.ylabel("Homicídios")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# =============================================================================
# * Here the conclusion is non-stationary
# dfuller y1
# dfuller y1, drift
# dfuller y1, trend
# =============================================================================
def teste_adf(serie, nome, regression="c"):
    resultado = adfuller(serie.dropna(), regression=regression, autolag="AIC")
    mapa = {"n": "Sem constante", "c": "Com constante (drift)", "ct": "Com constante e tendência (trend)"}
    print(f"\nTeste ADF: {nome} [{mapa[regression]}]")
    print(f"  Estatística ADF: {resultado[0]:.4f}")
    print(f"  p-valor:         {resultado[1]:.4f}")
    print(f"  Lags:            {resultado[2]}")
    print(f"  Valores críticos:")
    for k, v in resultado[4].items():
        print(f"    {k}: {v:.4f}")
    if resultado[1] < 0.05:
        print(f"  >>> ESTACIONÁRIA (p={resultado[1]:.4f})")
    else:
        print(f"  >>> NÃO-ESTACIONÁRIA (p={resultado[1]:.4f})")
    return resultado

print("# Here the conclusion is non-stationary")
adf_y1_n = teste_adf(df["y1"], "y1", regression="n")
adf_y1_c = teste_adf(df["y1"], "y1", regression="c")
adf_y1_ct = teste_adf(df["y1"], "y1", regression="ct")

# =============================================================================
# * With the difference y1 is stationary
# gen diff_y1 = d.y1
# dfuller diff_y1
# label variable diff_y1 "Homicídios,d"
# =============================================================================
print("\n# With the difference y1 is stationary")
df["diff_y1"] = df["y1"].diff()
adf_diff = teste_adf(df["diff_y1"], "diff_y1", regression="c")

# =============================================================================
# * Don't have any type of white noise, because all the values are 0
# corrgram y1
# =============================================================================
def correlograma(serie, nome, lags=20):
    serie_limpa = serie.dropna()
    nlags = min(lags, len(serie_limpa) // 2 - 1)
    valores_acf = acf(serie_limpa, nlags=nlags, fft=False)
    valores_pacf = pacf(serie_limpa, nlags=nlags)
    print(f"\nCorrelograma: {nome}")
    print(f"{'Lag':>5} {'AC':>10} {'PAC':>10}")
    for i in range(1, nlags + 1):
        print(f"{i:>5} {valores_acf[i]:>10.4f} {valores_pacf[i]:>10.4f}")
    lb = acorr_ljungbox(serie_limpa, lags=nlags, return_df=True)
    print(f"\nLjung-Box (H0: ruído branco):")
    print(lb.to_string())
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(serie_limpa, lags=nlags, ax=axes[0], title=f"ACF - {nome}")
    plot_pacf(serie_limpa, lags=nlags, ax=axes[1], title=f"PACF - {nome}")
    plt.tight_layout()
    plt.show()

print("\n# Don't have any type of white noise, because all the values are 0")
correlograma(df["y1"], "y1")

# =============================================================================
# * No white noise
# corrgram diff_y1
# =============================================================================
print("\n# No white noise")
correlograma(df["diff_y1"], "diff_y1")

# =============================================================================
# * Let's test with ARIMA
# arima y1, arima(0,1,0)
# est store ARIMA010
# predict y1010_res, residuals
# corrgram y1010_res
# =============================================================================
print("\n# Let's test with ARIMA")

modelo_010 = ARIMA(df["y1"].dropna(), order=(0, 1, 0)).fit()
print(modelo_010.summary())
y1010_res = modelo_010.resid
correlograma(y1010_res, "y1010_res")

# =============================================================================
# * Now we have white noise!
# arima y1, arima(1,1,0)
# est store ARIMA110
# predict y1110_res, residuals
# corrgram y1110_res
# =============================================================================
print("\n# Now we have white noise!")

modelo_110 = ARIMA(df["y1"].dropna(), order=(1, 1, 0)).fit()
print(modelo_110.summary())
y1110_res = modelo_110.resid
correlograma(y1110_res, "y1110_res")

# =============================================================================
# * Let's visualize
# est table ARIMA010 ARIMA110, stats(N aic bic)
# =============================================================================
print("\n# Let's visualize")
comparacao = pd.DataFrame({
    "ARIMA(0,1,0)": {
        "N": modelo_010.nobs,
        "AIC": modelo_010.aic,
        "BIC": modelo_010.bic,
    },
    "ARIMA(1,1,0)": {
        "N": modelo_110.nobs,
        "AIC": modelo_110.aic,
        "BIC": modelo_110.bic,
    }
})
print(comparacao.to_string())

# =============================================================================
# * Doing a doc
# asdoc dfuller y1 ... (todos os asdoc)
# =============================================================================
with pd.ExcelWriter("resultados_homicidios_sp.xlsx", engine="openpyxl") as writer:
    pd.DataFrame({
        "Teste": ["ADF y1 (none)", "ADF y1 (drift)", "ADF y1 (trend)", "ADF diff_y1 (drift)"],
        "Estatística": [adf_y1_n[0], adf_y1_c[0], adf_y1_ct[0], adf_diff[0]],
        "p-valor": [adf_y1_n[1], adf_y1_c[1], adf_y1_ct[1], adf_diff[1]],
        "Lags": [adf_y1_n[2], adf_y1_c[2], adf_y1_ct[2], adf_diff[2]],
    }).to_excel(writer, sheet_name="Testes ADF", index=False)
    comparacao.to_excel(writer, sheet_name="Comparação ARIMA")
    df.to_excel(writer, sheet_name="Dados")
print("\n>>> Arquivo 'resultados_homicidios_sp.xlsx' salvo.")

# =============================================================================
# tsline y1 diff_y1
# =============================================================================
fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df.index.year, df["y1"], color="steelblue", linewidth=1.5, label="Homicídios (y1)")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Homicídios (y1)", color="steelblue")
ax2 = ax1.twinx()
ax2.plot(df.index.year, df["diff_y1"], color="coral", linewidth=1.5, linestyle="--", label="Homicídios,d (diff_y1)")
ax2.set_ylabel("Homicídios,d (diff_y1)", color="coral")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.title("y1 e diff_y1")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# =============================================================================
# arima y1, arima(1,1,0)
# predict y1110_fit, xb
# =============================================================================
y1110_fit = modelo_110.fittedvalues

# =============================================================================
# twoway (tsline y1 ...) (tsline y1110_fit ...), legend(...)
# =============================================================================
plt.figure(figsize=(12, 6))
plt.plot(df.index.year, df["y1"], color="black", linewidth=1.8, linestyle="-", label="Homicídios Observados")
plt.plot(df.index.year[:len(y1110_fit)], y1110_fit, color="blue", linewidth=1.8, linestyle="--", label="Ajuste ARIMA(1,1,0)")
plt.title("Homicídios e Ajuste com ARIMA(1,1,0)")
plt.xlabel("Ano")
plt.ylabel("Homicídios")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()