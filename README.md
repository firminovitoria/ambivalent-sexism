# 🧠 Detecção de Sexismo Ambivalente

Este repositório apresenta um estudo experimental sobre **detecção de sexismo ambivalente** em textos, explorando o desempenho de **11 modelos de aprendizado de máquina e deep learning**. O objetivo é avaliar quais algoritmos são mais eficazes para identificar discursos sexistas em diferentes nuances, considerando aspectos linguísticos, sociais e culturais.

---

## 📌 Contexto

O **sexismo ambivalente** é caracterizado pela coexistência de discursos **hostis** (explícitos, negativos) e **benevolentes** (sutis, aparentemente positivos, mas que reforçam estereótipos). Detectar essas formas é um desafio em PLN (Processamento de Linguagem Natural), pois exige sensibilidade para distinguir expressões implícitas e explícitas.

---

## 🚀 Objetivos do Projeto

- Implementar e comparar **11 modelos distintos** para detecção de sexismo ambivalente.  
- Explorar diferentes técnicas de **representação de texto** (TF-IDF, embeddings, BERT, etc.).  
- Avaliar métricas como **Acurácia, F1-score, AUC-ROC**, além de métricas de justiça algorítmica.  
- Contribuir para a discussão sobre **ética e viés social em modelos de linguagem**.  

---

## ⚙️ Modelos Utilizados

Os modelos implementados neste repositório são:

1. **Albertina 100M** (`albertina_100m.py`)  
2. **Bernice** (`bernice.py`)  
3. **BERT Multilingual (Uncased)** (`bert_multilingual.py`)  
4. **BERTaPóru Base** (`bertabaporu_base.py`)  
5. **BERTaPóru Large** (`bertabaporu_large.py`)  
6. **BERTimbau Base** (`bertimbau_base.py`)  
7. **BERTimbau Large** (`bertimbau_large.py`)  
8. **BERTweetBR** (`bertweetbr.py`)  
9. **DistilBERT Base Multilingual Cased** (`distilbert_base_multilingual_cased.py`)  
10. **XLM-RoBERTa Base** (`xlm_roberta_base.py`)  
11. **BERT Multilingual (Ilustração)** (`bert-multilingual-uncased.png`) 

---

## 📊 Resultados Esperados

- Comparação quantitativa entre os 11 modelos.  
- Identificação de quais técnicas lidam melhor com as **sutilezas do sexismo ambivalente**.  
- Discussão sobre **trade-offs entre performance e interpretabilidade**.  

---

