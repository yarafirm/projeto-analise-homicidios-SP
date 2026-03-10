# Análise de Séries Temporais: Homicídios em São Paulo (1989–2022)

## Resumo 
Este repositório apresenta uma investigação empírica sobre a evolução dos homicídios no Estado de São Paulo ao longo de três décadas. O projeto, migrado de **Stata** para **Python**, utiliza modelos autorregressivos (ARIMA) para decompor a série histórica, testar a estabilidade dos dados e validar as tendências de queda observadas na segurança pública paulista.

## Variáveis
A investigação fundamenta-se na análise univariada de séries temporais, cujo comportamento da variável é explicado pela:

* **Variável Dependente ($Y$):** Volume anual de **Homicídios**. Representa o indicador de letalidade violenta.
* **Variável Independente ($X$):** O **Eixo Temporal (Ano)**. Atua como o suporte onde os choques estruturais e as mudanças de políticas públicas são registrados.

---

## Hipóteses de Literatura
Ao confrontar os dados com a literatura de segurança pública, estabeleci as seguintes **assumptions** (suposições) sobre a trajetória da série:

1.  **Crise (1989–2001):** Os dados revelam uma ascensão parabólica que culmina em um pico superior a 15.000 ocorrências no início dos anos 2000. Assume-se que este período reflete a expansão do crime organizado e a ausência de mecanismos de inteligência integrada.
2.  **Reformas Estruturais (Pós-2003):** Observa-se uma redução drástica e consistente na série. A hipótese central da literatura atribui este fenômeno a marcos como o **Estatuto do Desarmamento** e a implementação de sistemas de georreferenciamento criminal (Infocrim).
3.  **Memória do Fenômeno:** A modelagem estatística busca validar a "memória" do crime, assumindo que a violência de hoje é, em parte, um reflexo condicionado dos eventos do período anterior.

---

## Metodologia de Modelagem Passo a Passo

### 1. Diagnóstico de Estacionaridade (Augmented Dickey-Fuller)
A primeira etapa consistiu em verificar se a série possui média e variância constantes.

>![Texto Alt]((https://github.com/yarafirm/projeto-analise-homicidios-SP/blob/main/data/processed/Homicidios_por_ano.png)

* **Evidência:** O teste ADF em nível (com drift) apresentou um **p-valor de 0.7222**, falhando em rejeitar a hipótese de raiz unitária.
* **Conclusão:** A série é **Não-Estacionária**, o que exige transformações matemáticas para evitar regressões espúrias.

### 2. Estabilização da Série via Diferenciação
Para neutralizar a tendência e estabilizar a variância, aplicou-se a **primeira diferença** ($\Delta Y_t$).

> **[INSERIR AQUI O GRÁFICO DA PÁGINA 9 - SÉRIE VS PRIMEIRA DIFERENÇA]**
[Image of original time series versus its first difference]

* **Resultado:** Após a transformação, o teste ADF resultou em um **p-valor de 0.0175**.
* **Decisão Técnica:** A série tornou-se estacionária, classificando-se como integrada de ordem 1, ou **$I(1)$**.

### 3. Seleção e Validação do Modelo ARIMA(1, 1, 0)
Através da análise das funções de autocorrelação (ACF) e autocorrelação parcial (PACF), identificou-se uma forte dependência do passado imediato (Lag 1).

| Critério de Informação | ARIMA(0, 1, 0) | ARIMA(1, 1, 0) |
| :--- | :---: | :---: |
| **AIC** | 550.44 | **545.35** |
| **BIC** | 551.93 | **548.35** |

* **Análise:** O modelo **ARIMA(1, 1, 0)** apresentou os menores valores de AIC e BIC, sendo o mais equilibrado estatisticamente.
* **Coeficiente AR(1):** O valor de **0.3482** ($p=0.002$) confirma que aproximadamente 34,8% da variação residual do ano anterior persiste no ano atual.

### 4. Ruído Branco
Para garantir que o modelo extraiu toda a informação disponível, testei os resíduos.

* **Teste ARIMA:** Obtivemos um **p-valor de 0.73**.
* **Conclusão Acadêmica:** Como o p-valor é superior a 0.05, os resíduos são classificados como **Ruído Branco**. O modelo é estatisticamente válido e livre de autocorrelação residual.

---

## Conclusão e ajuste do modelo
O ajuste final demonstra que a queda dos homicídios em São Paulo segue um padrão matemático robusto. A investigação valida que as mudanças estruturais nas últimas décadas criaram uma nova dinâmica de segurança, capturada com precisão pelo modelo ARIMA.

> **[INSERIR AQUI O GRÁFICO DA PÁGINA 10 - AJUSTE FINAL ARIMA]**
[Image of ARIMA model fit plotted against observed homicide data]

---

## 📂 Organização do Repositório
* `notebooks/`: Implementação completa em Python (SARIMAX).
* `data/`: Base histórica processada (1989-2022).
* `outputs/`: Relatórios detalhados em Excel.
