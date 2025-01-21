# -*- coding: utf-8 -*-
"""bertabaporu-large.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ih6YYVTkFOvzXp7_b8GihSNxQ7ZEAU9t

# Fine Tuning

## Preparação dos Dados
"""

import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

caminho_arquivo = '/content/drive/MyDrive/JBCS/Anotações/anotadores-sexismo - anotadores-sexismo.csv'
df = pd.read_csv(caminho_arquivo)

df.head()

df.shape

df = df[df['Resultado'].notna()]

categoria_counts = df['Resultado'].value_counts()
print(categoria_counts)

X = df['Frase'].values  # Frases
y = df['Resultado'].values  # Rótulos

from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['Resultado'])

classes_mapeadas = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
print(classes_mapeadas)

from imblearn.over_sampling import RandomOverSampler

def balance_classes(X, y):
    ros = RandomOverSampler(random_state=42)
    X, y = ros.fit_resample(X.reshape(-1, 1), y)
    return X.flatten(), y

from sklearn.model_selection import StratifiedKFold
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW

class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

"""## Treinamento"""

# treinamento
def train_model(model, data_loader, optimizer):
    model = model.train()
    total_loss = 0
    for batch in data_loader:
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()

    return total_loss / len(data_loader)

"""## Avaliação"""

# avaliação
from sklearn.metrics import classification_report

def evaluate_model(model, data_loader):
    model = model.eval()
    total_correct = 0
    total_samples = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            _, preds = torch.max(logits, dim=1)

            total_correct += torch.sum(preds == labels)
            total_samples += labels.size(0)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='weighted')
    recall = recall_score(all_labels, all_preds, average='weighted')
    f1 = f1_score(all_labels, all_preds, average='weighted')

    # Gera o classification report
    class_report = classification_report(all_labels, all_preds, target_names=label_encoder.classes_)

    return accuracy, precision, recall, f1, class_report, all_preds

# tokenizer e o modelo BERTimbau
tokenizer = BertTokenizer.from_pretrained('pablocosta/bertabaporu-large-uncased')
model = BertForSequenceClassification.from_pretrained('pablocosta/bertabaporu-large-uncased', num_labels=3)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

"""Validação Cruzada Estratificada

"""

# Definir o número de folds para validação cruzada
n_splits = 10 #10 é o mais comum, mas pode aumentar o número de folds desde que contenha no minimo 30 exemplos em cada fold, ex: 100 exemplos anotados, deve ter no maximo 3 folds / Deve-se saber tbm, que quanto maior o número de folds, maior o custo computacional
skf = StratifiedKFold(n_splits=n_splits)

# Otimizador
optimizer = AdamW(model.parameters(), lr=1e-5)

all_fold_metrics = {
    'accuracy': [],
    'precision': [],
    'recall': [],
    'f1': []
}

all_true_labels = []
all_pred_labels = []

"""## Treinamento e Avaliação de Modelo com Validação Cruzada Estratificada e Balanceamento de Classes"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

for fold, (train_index, test_index) in enumerate(skf.split(X, y)):
    print(f"Fold {fold+1}/{n_splits}")

    # Dividir os dados em treino e teste
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # Balancear as classes no conjunto de treino
    X_train_balanced, y_train_balanced = balance_classes(X_train, y_train)

    # Criar datasets e dataloaders
    train_dataset = TextDataset(X_train_balanced, y_train_balanced, tokenizer)
    test_dataset = TextDataset(X_test, y_test, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)  # mini-batch de tamanho 16 e shuffle para pegar amostras aleatórias
    test_loader = DataLoader(test_dataset, batch_size=16) # mini-batch de tamanho 16

    # Treinar o modelo no fold atual
    train_loss = train_model(model, train_loader, optimizer)
    print(f"Loss de treino no Fold {fold+1}: {train_loss}") #quanto menor a loss em cada fold significa que o modelo está aprendendo

    # Avaliar o modelo no fold atual
    accuracy, precision, recall, f1, class_report, all_preds = evaluate_model(model, test_loader)

    # Armazenar métricas para cada fold
    all_fold_metrics['accuracy'].append(accuracy)
    all_fold_metrics['precision'].append(precision)
    all_fold_metrics['recall'].append(recall)
    all_fold_metrics['f1'].append(f1)

    all_true_labels.extend(y_test)
    all_pred_labels.extend(all_preds)

# Cálculo das métricas finais (médias)
final_accuracy = np.mean(all_fold_metrics['accuracy'])
final_precision = np.mean(all_fold_metrics['precision'])
final_recall = np.mean(all_fold_metrics['recall'])
final_f1 = np.mean(all_fold_metrics['f1'])


print(f"\nDesempenho Final:")
print(f"Accuracy Média: {final_accuracy}")
print(f"Precision Média: {final_precision}")
print(f"Recall Médio: {final_recall}")
print(f"F1-score Médio: {final_f1}")

# Geração do Classification Report geral
final_class_report = classification_report(all_true_labels, all_pred_labels, target_names=label_encoder.classes_)
print("\nClassification Report:")
print(final_class_report)

"""# Sem Fine Tuning"""

from transformers import BertTokenizer, BertModel
import numpy as np

tokenizer = BertTokenizer.from_pretrained('pablocosta/bertabaporu-large-uncased')
model = BertModel.from_pretrained('pablocosta/bertabaporu-large-uncased')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def get_embeddings(texts, tokenizer, model, max_length=128):
    model.eval()  # Colocar o modelo em modo de avaliação
    embeddings = []
    with torch.no_grad():  # Não calcular gradientes
        for text in texts:
            # Tokenização da frase
            inputs = tokenizer(
                text,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            inputs = {key: value.to(device) for key, value in inputs.items()}

            # Obter as representações da última camada
            outputs = model(**inputs)
            embeddings.append(outputs.last_hidden_state[:, 0, :].cpu().numpy())  # Pooling [CLS]
    return np.vstack(embeddings)  # Retorna um array 2D

X_train_embeddings = get_embeddings(X_train, tokenizer, model)
X_test_embeddings = get_embeddings(X_test, tokenizer, model)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# Treinar um classificador
clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train_embeddings, y_train)

# Fazer previsões
y_pred = clf.predict(X_test_embeddings)

# Calcular métricas
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
class_report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-score: {f1}")
print("\nClassification Report:\n", class_report)

"""# Comparação"""

import pandas as pd

comparison = {
    "Métrica": ["Accuracy", "Precision", "Recall", "F1-score"],
    "Sem Fine-Tuning": [accuracy, precision, recall, f1],
    "Com Fine-Tuning": [final_accuracy, final_precision, final_recall, final_f1]  # Valores do modelo com fine-tuning
}

df_comparison = pd.DataFrame(comparison)
print(df_comparison)

import matplotlib.pyplot as plt

labels = ["Accuracy", "Precision", "Recall", "F1-score"]
no_tuning = [accuracy, precision, recall, f1]
tuned = [final_accuracy, final_precision, final_recall, final_f1]

x = range(len(labels))
plt.bar(x, no_tuning, width=0.4, label='Without Fine-Tuning', align='center', color='skyblue')
plt.bar([p + 0.4 for p in x], tuned, width=0.4, label='With Fine-Tuning', align='center', color='salmon')
plt.xticks([p + 0.2 for p in x], labels)
plt.xlabel("Metrics")
plt.ylabel("Scores")
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.show()