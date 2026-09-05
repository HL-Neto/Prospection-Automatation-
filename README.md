# 🤖 RH Currículo Analisador

Sistema de **automação e análise inteligente de currículos** utilizando Inteligência Artificial.

O projeto integra a **Gmail API**, processamento de arquivos PDF, **embeddings**, **Pinecone** e **Google Gemini** para automatizar parte do processo de triagem de candidatos.

A ideia principal é transformar currículos recebidos por e-mail em informações estruturadas que podem ser utilizadas para avaliar a compatibilidade do candidato com uma determinada vaga.

---

## 🚀 Como funciona

O fluxo principal do sistema é:

```text
📧 Gmail
   ↓
📎 Anexos dos e-mails
   ↓
📄 Download dos currículos em PDF
   ↓
📝 Extração do texto
   ↓
✂️ Divisão em chunks
   ↓
🧠 Embeddings
   ↓
🗄️ Pinecone
   ↓
🔎 Busca pelo ID do currículo
   ↓
🤖 Google Gemini
   ↓
📊 Análise do candidato
```

Cada currículo recebe um **ID associado ao seu arquivo/anexo**. Esse ID é armazenado como metadata junto aos vetores no Pinecone, permitindo recuperar especificamente os chunks pertencentes a determinado currículo.

---

## 🧠 Tecnologias utilizadas

* **Python**
* **Gmail API**
* **PyPDF**
* **LangChain**
* **Hugging Face Embeddings**
* **Pinecone**
* **Google Gemini**
* **python-dotenv**

### Modelo de Embeddings

O projeto utiliza:

```text
sentence-transformers/all-mpnet-base-v2
```

com embeddings normalizados:

```python
encode_kwargs={"normalize_embeddings": True}
```

O modelo gera vetores com **768 dimensões**, correspondendo à configuração do índice utilizado no Pinecone.

---

## 📂 Estrutura do processamento

### 1. Coleta dos currículos

A função `get_curriculum()` busca os anexos dos e-mails e realiza o download dos PDFs.

Cada currículo é armazenado com informações como:

```python
{
    "id": "...",
    "remetente": "...",
    "curriculo": "..."
}
```

O `id` funciona como identificador do currículo dentro do sistema.

---

### 2. Extração do texto

O projeto utiliza `PyPDF` para percorrer as páginas do currículo:

```python
for page in reader.pages:
    text = page.extract_text()
```

O texto de todas as páginas é reunido em uma única string.

---

### 3. Chunking

Como currículos podem possuir bastante conteúdo, o texto é dividido em partes menores utilizando:

```python
RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

Isso permite que o conteúdo seja transformado em pequenos documentos antes de ser convertido em embeddings.

Cada chunk recebe metadata:

```python
{
    "id": curriculo["id"],
    "remetente": curriculo["remetente"]
}
```

Dessa forma, mesmo depois de dividir um currículo em vários chunks, é possível identificar a qual currículo cada pedaço pertence.

---

## 🗄️ Pinecone

Os chunks são transformados em embeddings e armazenados em um índice vetorial do Pinecone.

Índice utilizado:

```text
rh-curriculo-analisador
```

Configuração:

```text
Dimension: 768
Metric: cosine
Cloud: AWS
Region: us-east-1
```

A similaridade por **cosine** é utilizada para encontrar conteúdos semanticamente relacionados.

---

## 🔎 Recuperação por currículo

Uma das partes importantes do projeto é a utilização do metadata para localizar um currículo específico.

Por exemplo:

```python
documentos = vector_store.similarity_search(
    "currículo experiência profissional CNH entrega",
    k=4,
    filter={
        "id": id_curriculo
    }
)
```

O filtro:

```python
filter={"id": id_curriculo}
```

garante que a busca seja realizada apenas entre os chunks daquele currículo.

Assim, o sistema pode ter centenas de currículos armazenados no Pinecone sem misturar os dados de candidatos diferentes durante a análise.

---

## 🤖 Análise com Gemini

Após recuperar os chunks relevantes do currículo, o conteúdo é reunido:

```python
contexto = "\n\n".join(
    doc.page_content for doc in documentos
)
```

Esse contexto é enviado ao modelo Gemini juntamente com as informações da vaga.

Atualmente, o projeto possui como exemplo a análise para:

**Assistente da Administração — MOTOMAR Honda**

O modelo avalia:

* Nome do candidato
* Experiências relevantes
* Pontos positivos
* Pontos de atenção
* Compatibilidade com a vaga de 0 a 100
* Classificação final

---

## 🎯 Objetivo do projeto

O objetivo é automatizar tarefas repetitivas do processo de triagem de currículos.

Em vez de analisar manualmente cada PDF recebido por e-mail, o sistema pode:

1. Identificar os currículos recebidos.
2. Baixar os arquivos.
3. Extrair o conteúdo.
4. Transformar os documentos em embeddings.
5. Armazenar os dados em um banco vetorial.
6. Recuperar informações relevantes de um candidato específico.
7. Utilizar IA para realizar uma análise inicial.

A proposta não é substituir completamente um profissional de RH, mas **reduzir o trabalho manual e acelerar a etapa inicial de triagem**.

---

## 🔐 Variáveis de ambiente

As credenciais não devem ser armazenadas diretamente no código.

Utilize um arquivo `.env`:

```env
PINECONE_API_KEY=sua_chave
GOOGLE_API_KEY=sua_chave
```

O arquivo `.env` **não deve ser enviado para o GitHub**.

Adicione ao `.gitignore`:

```gitignore
.env
credentials.json
token.json
__pycache__/
*.pdf
```

> Nunca publique chaves de API, tokens de autenticação ou credenciais do Gmail no repositório.

---

## ⚙️ Instalação

Clone o projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd rh-curriculo-analisador
```

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual no Windows:

```bash
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure as variáveis de ambiente no `.env`.

Depois, execute o projeto:

```bash
python main.py
```

---

## 🔑 APIs necessárias

Para executar o projeto, é necessário configurar:

### Gmail API

Utilizada para acessar os e-mails e seus anexos.

É necessário configurar as credenciais da API do Google e realizar a autenticação da conta.

### Pinecone

Utilizado como banco de dados vetorial para armazenar os embeddings dos currículos.

### Google Gemini

Utilizado para realizar a análise dos currículos utilizando o contexto recuperado do banco vetorial.

---

## 📌 Exemplo do resultado

A IA pode retornar uma análise semelhante a:

```text
Nome:
Vinicius Emanoel dos Santos de Andrade

Experiências relevantes:
Experiência profissional relacionada às atividades da vaga.

Pontos positivos:
- Possui CNH A/B
- Possui experiência profissional relevante
- Disponibilidade para atividades externas

Pontos de atenção:
- Experiência específica com entrega pode ser limitada

Compatibilidade:
85/100

Classificação final:
Candidato compatível com a vaga.
```

---

## 🛠️ Próximas melhorias

O projeto ainda está em desenvolvimento e algumas melhorias planejadas incluem:

* [ ] Evitar reindexação de currículos já processados
* [ ] Criar identificação automática de novos currículos
* [ ] Melhorar o sistema de recuperação dos chunks
* [ ] Retornar respostas em JSON estruturado
* [ ] Criar uma interface web para visualizar os candidatos
* [ ] Criar ranking automático dos candidatos
* [ ] Permitir diferentes vagas e critérios de avaliação
* [ ] Armazenar histórico das análises
* [ ] Melhorar tratamento de currículos sem texto extraível
* [ ] Adicionar logs e tratamento de erros
* [ ] Implementar processamento assíncrono
* [ ] Criar testes automatizados

---

## 📚 Conceitos utilizados

Este projeto foi desenvolvido utilizando conceitos de:

* **LLM (Large Language Models)**
* **RAG (Retrieval-Augmented Generation)**
* **Vector Database**
* **Embeddings**
* **Semantic Search**
* **Metadata Filtering**
* **Document Chunking**
* **Prompt Engineering**
* **API Integration**
* **Automação de processos**
* **Processamento de documentos**

---

## 👨‍💻 Sobre o projeto

Projeto desenvolvido como estudo prático de **Inteligência Artificial, automação e desenvolvimento de aplicações utilizando LLMs**.

A aplicação combina APIs externas, processamento de documentos, banco vetorial e modelos de linguagem em um único fluxo automatizado.

O projeto também serve como experimento para entender, na prática, como construir aplicações utilizando **RAG e LLMs em um cenário real de negócio**.
