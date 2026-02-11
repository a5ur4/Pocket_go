# Pocket GO

Uma plataforma completa para recomendação e avaliação de hotéis, com API REST, bot do Telegram e integração geoespacial.

## 📋 Sobre o Projeto

O **Pocket GO** é uma aplicação desenvolvida para fins educacionais que oferece:

- **API REST** completa para gerenciamento de hotéis, cidades, avaliações e usuários
- **Bot do Telegram** interativo para busca e avaliação de hotéis
- **Banco de dados PostgreSQL** com extensão PostGIS para funcionalidades geoespaciais
- **Sistema de logging** detalhado para rastreamento de operações
- **Testes automatizados** com pytest para garantir qualidade do código

O projeto permite que usuários busquem hotéis por localização, visualizem detalhes, deixem avaliações e interajam através de um bot do Telegram.

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido para construir APIs REST
- **SQLAlchemy** - ORM (Object-Relational Mapping) para interação com banco de dados
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic** - Validação de dados e serialização

### Banco de Dados
- **PostgreSQL** - Banco de dados relacional robusto
- **PostGIS** - Extensão para queries geoespaciais (busca por localização)
- **psycopg2** - Driver PostgreSQL para Python

### Bot e Comunicação
- **python-telegram-bot** - Biblioteca para integração com API do Telegram
- **httpx** - Cliente HTTP assíncrono para requisições

### Processamento de Dados
- **Pandas** - Manipulação e análise de dados
- **OpenPyXL** - Trabalho com arquivos Excel

### Testes e Qualidade
- **pytest** - Framework de testes
- **pytest-asyncio** - Suporte para testes assíncronos
- **pytest-sugar** - Melhor visualização dos resultados de testes

### Containerização
- **Docker & Docker Compose** - Containerização e orquestração

## 📁 Estrutura do Projeto

```
.
├── bot/                      # Bot do Telegram
│   ├── telegram_bot.py      # Implementação principal do bot
│   └── lang_texts.py        # Textos e mensagens
├── database/                 # Camada de dados
│   ├── engine_db.py         # Configuração do banco
│   ├── script.sql           # Scripts SQL iniciais
│   └── schemas/             # Schemas SQLAlchemy
├── models/                   # Modelos de dados (SQLAlchemy)
├── routes/                   # Rotas da API (endpoints)
├── services/                 # Lógica de negócio
├── middleware/               # Middlewares (logging, etc)
├── utils/                    # Utilitários (logger, etc)
├── tests/                    # Testes unitários e de integração
├── static/                   # Arquivos estáticos (HTML, CSS)
├── main.py                   # Arquivo principal da aplicação
├── requirements.txt          # Dependências Python
└── docker-compose.yml        # Configuração Docker
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.9+
- Docker e Docker Compose (opcional)
- PostgreSQL 12+ (se não usar Docker)
- pip (gerenciador de pacotes Python)

### Opção 1: Com Docker (Em desenvolvimento)

A forma mais fácil e isolada de executar o projeto.

#### Passos:

1. **Clone o repositório**
   ```bash
   git clone https://github.com/a5ur4/Pocket_go.git
   cd Pocket_go
   ```

2. **Configure as variáveis de ambiente**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   DATABASE_USER=pocket_go_user
   DATABASE_PASSWORD=seu_senha_segura
   DATABASE_NAME=pocket_go_db
   DATABASE_HOST=db
   DATABASE_PORT=5432
   
   TELEGRAM_BOT_TOKEN=seu_token_do_telegram
   ```

3. **Inicie os containers**
   ```bash
   docker-compose up -d
   ```

4. **Aguarde a inicialização do banco de dados** (pode levar alguns segundos)

5. **Execute as migrações** (se necessário)
   ```bash
   docker-compose exec api python -c "from database.engine_db import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Acesse a aplicação**
   - API: http://localhost:8000
   - Documentação Swagger: http://localhost:8000/docs
   - Documentação ReDoc: http://localhost:8000/redoc

#### Parar os containers:
```bash
docker-compose down
```

#### Ver logs:
```bash
docker-compose logs -f api
docker-compose logs -f db
```

---

### Opção 2: Sem Docker (Instalação Local)

Execute diretamente em sua máquina.

#### Passos:

1. **Clone o repositório**
   ```bash
   git clone https://github.com/a5ur4/Pocket_go.git
   cd Pocket_go
   ```

2. **Crie um ambiente virtual** (recomendado)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**
   
   - **Instale PostgreSQL** (se ainda não tiver):
     - [Download PostgreSQL](https://www.postgresql.org/download/)
     - Instale também a extensão PostGIS
   
   - **Crie o banco de dados**:
     ```bash
     psql -U postgres
     CREATE USER pocket_go_user WITH PASSWORD 'sua_senha_segura';
     CREATE DATABASE pocket_go_db OWNER pocket_go_user;
     \c pocket_go_db
     CREATE EXTENSION postgis;
     ```

5. **Configure as variáveis de ambiente**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   DATABASE_USER=pocket_go_user
   DATABASE_PASSWORD=sua_senha_segura
   DATABASE_NAME=pocket_go_db
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   
   TELEGRAM_BOT_TOKEN=seu_token_do_telegram
   ```

6. **Crie as tabelas do banco**
   ```bash
   python -c "from database.engine_db import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

7. **Execute a aplicação**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Acesse a aplicação**
   - API: http://localhost:8000
   - Documentação Swagger: http://localhost:8000/docs
   - Documentação ReDoc: http://localhost:8000/redoc

---

## 🧪 Testes

Execute os testes para validar a implementação:

```bash
# Com Docker
docker-compose exec api pytest

# Sem Docker (ambiente local)
pytest
```

Para testes com saída mais bonita:
```bash
pytest -v
```

---

## 📡 Endpoints Principais da API

### Usuários
- `GET /users` - Listar usuários
- `POST /users` - Criar usuário
- `GET /users/{id}` - Obter detalhes do usuário
- `PUT /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário

### Hotéis
- `GET /hotels` - Listar hotéis
- `POST /hotels` - Criar hotel
- `GET /hotels/{id}` - Detalhes do hotel
- `GET /hotels/search` - Buscar hotéis por localização

### Cidades
- `GET /cities` - Listar cidades
- `POST /cities` - Criar cidade

### Avaliações
- `GET /evaluations` - Listar avaliações
- `POST /evaluations` - Criar avaliação
- `GET /evaluations/{id}` - Detalhes da avaliação

### Logs
- `GET /logs` - Visualizar logs do sistema

### Health Check
- `GET /health` - Verificar status da aplicação

Para documentação interativa, visite `/docs` após iniciar a aplicação.

---

## 🤖 Bot do Telegram

O bot oferece funcionalidades interativas:

- Buscar hotéis por localização
- Ver detalhes e avaliações de hotéis
- Deixar avaliações
- Visualizar histórico de buscas

Para usar o bot:

1. Configure `TELEGRAM_BOT_TOKEN` no `.env`
2. Inicie o bot com Docker ou localmente
3. Procure pelo bot no Telegram e comece a usar

---

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```env
# Database
DATABASE_USER=pocket_go_user
DATABASE_PASSWORD=sua_senha_segura
DATABASE_NAME=pocket_go_db
DATABASE_HOST=localhost (ou 'db' com Docker)
DATABASE_PORT=5432

# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=seu_token_aqui

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Desenvolvimento

Para contribuir com o projeto:

1. Crie uma branch para sua feature: `git checkout -b feature/sua-feature`
2. Commit suas mudanças: `git commit -m 'Add some feature'`
3. Push para a branch: `git push origin feature/sua-feature`
4. Abra um Pull Request