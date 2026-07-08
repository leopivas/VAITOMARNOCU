# 🎬 Creatools — Guia Completo de Instalação

> **Dashboard em tempo real para monitorar TikTok LIVE** — visualize os principais canais ao vivo, monitore streams via WebSocket, verifique status em massa e utilize recursos de IA (Claude + Sora) via Emergent Integrations.

---

## 📑 Sumário

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Estrutura de Diretórios](#2-estrutura-de-diretórios)
3. [Requisitos de Sistema](#3-requisitos-de-sistema)
4. [Variáveis de Ambiente](#4-variáveis-de-ambiente)
5. [Instalação Passo a Passo (Local)](#5-instalação-passo-a-passo-local)
6. [Rodando o App](#6-rodando-o-app)
7. [Comandos Úteis](#7-comandos-úteis)
8. [Deploy em Produção](#8-deploy-em-produção)
9. [Testes](#9-testes)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Visão Geral da Arquitetura

O Creatools é composto por **3 camadas** que rodam em conjunto:

```
┌──────────────────────────────────────────────────────────────────┐
│  BROWSER (usuário)                                               │
└───────────────────────────┬──────────────────────────────────────┘
                            │  HTTPS
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Frontend React + Vite  (porta 3000)                             │
│  Diretório: /app/tiks/artifacts/creatools/                       │
│  Launcher:  /app/frontend/  (roda o Vite do creatools)           │
└───────────────────────────┬──────────────────────────────────────┘
                            │  chamadas /api/*
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  FastAPI Proxy  (porta 8001)                                     │
│  Diretório: /app/backend/                                        │
│  - server.py    → sobe subprocess Node e proxya /api/*           │
│  - ai_router.py → rotas /api/ai/* (Claude + Sora + Storage)      │
└───────────────────────────┬──────────────────────────────────────┘
                            │  proxy interno (loopback)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Node Express 5 API Server  (porta 8081)                         │
│  Diretório: /app/tiks/artifacts/api-server/                      │
│  - rotas: tiktok, auth, config, system, stripe, admin, setup     │
│  - proxya chamadas para tik.tools (WebSocket + REST)             │
└───────────────────────────┬──────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      ┌──────────────┐            ┌───────────────┐
      │ PostgreSQL   │            │  tik.tools    │
      │ (drizzle-orm)│            │  (API externa)│
      └──────────────┘            └───────────────┘
```

### 🧩 Stack Técnica

| Camada | Tecnologia | Versão |
|---|---|---|
| **Proxy/AI Backend** | Python + FastAPI + Uvicorn | Python 3.11+, FastAPI 0.110.1 |
| **Core API** | Node.js + Express 5 + TypeScript | Node 24, TS 5.9 |
| **Frontend** | React 19 + Vite 7 + Tailwind v4 + shadcn/ui + wouter | React 19.1.0 |
| **Banco de Dados** | PostgreSQL (via drizzle-orm) | PG 14+ |
| **Package Manager** | pnpm (workspaces) + yarn (launcher) | pnpm 9+, yarn 1.22+ |
| **API Codegen** | Orval (a partir de `openapi.yaml`) | — |
| **Validação** | Zod v3/v4 + drizzle-zod | — |
| **IA** | Claude Sonnet 4.5 + Sora 2 (via Emergent LLM Key) | — |

---

## 2. Estrutura de Diretórios

### 📂 Diretório raiz `/app/`

```
/app/
├── README.md                        ← Este arquivo
├── test_result.md                   ← Log de testes
├── memory/                          ← Notas de sessão do agent
├── tests/                           ← Testes globais
├── test_reports/                    ← Relatórios de teste
│
├── backend/                         ← 🐍 FastAPI Proxy + AI Router
│   ├── server.py                    ← Ponto de entrada FastAPI (porta 8001)
│   ├── ai_router.py                 ← Rotas /api/ai/* (Claude + Sora + Storage)
│   ├── requirements.txt             ← Dependências Python
│   ├── pytest.ini                   ← Configuração de testes Python
│   └── tests/                       ← Testes do backend Python
│       ├── test_tiktok_and_plans.py
│       ├── test_iter5_regression.py
│       ├── test_iter5_bugfixes.py
│       ├── test_overlays_phase1.py
│       └── test_ai_and_regression.py
│
├── frontend/                        ← ⚛️ Launcher do Frontend (thin wrapper)
│   ├── package.json                 ← Script "start" que chama Vite do creatools
│   └── yarn.lock
│
└── tiks/                            ← 📦 Workspace pnpm (monorepo real do app)
    ├── package.json                 ← Workspace root
    ├── pnpm-workspace.yaml          ← Configuração de packages + catálogo
    ├── pnpm-lock.yaml               ← Lockfile pnpm
    ├── tsconfig.base.json           ← Config TypeScript raiz
    ├── tsconfig.json                ← Config TypeScript do workspace
    ├── replit.md                    ← Notas do projeto (arquitetura original)
    │
    ├── artifacts/                   ← Aplicações executáveis
    │   ├── api-server/              ← 🟢 Node Express 5 (porta 8081)
    │   │   ├── package.json
    │   │   ├── build.mjs            ← Bundler esbuild
    │   │   ├── tsconfig.json
    │   │   ├── data/
    │   │   │   ├── config.json      ← Fallback do TIKTOOLS_API_KEY
    │   │   │   └── media/           ← Arquivos de mídia
    │   │   └── src/
    │   │       ├── index.ts         ← Entry point Express
    │   │       ├── startup.ts       ← Bootstrap (DB, migrations)
    │   │       ├── lib/             ← Helpers (logger, objectStorage, etc.)
    │   │       ├── middlewares/     ← Auth, error handling, etc.
    │   │       └── routes/          ← Handlers HTTP
    │   │           ├── tiktok.ts    ← Proxy tik.tools + JWT WebSocket
    │   │           ├── auth.ts      ← Login, TikTok OAuth
    │   │           ├── config.ts    ← Gestão de API key
    │   │           ├── system.ts    ← Health, status
    │   │           ├── admin-tools.ts   ← Stripe, config admin
    │   │           └── setup.ts     ← Setup inicial
    │   │
    │   ├── creatools/               ← 🎨 Frontend React (porta 3000)
    │   │   ├── package.json
    │   │   ├── vite.config.ts       ← Config Vite
    │   │   ├── tsconfig.json
    │   │   ├── components.json      ← Config shadcn/ui
    │   │   ├── index.html           ← HTML entry (define html.dark)
    │   │   ├── public/              ← Assets estáticos
    │   │   └── src/
    │   │       ├── main.tsx         ← Entry point React
    │   │       ├── App.tsx
    │   │       ├── pages/           ← Rotas (dashboard, monitor, bulk-check, settings)
    │   │       ├── components/      ← Componentes UI
    │   │       │   └── layout/app-layout.tsx  ← Sidebar
    │   │       ├── context/         ← React Context (Auth, etc.)
    │   │       ├── hooks/           ← Custom hooks
    │   │       ├── lib/             ← Utilities
    │   │       └── .generated/      ← Código gerado pelo Orval
    │   │
    │   └── mockup-sandbox/          ← 🧪 App auxiliar para mockups
    │       ├── package.json
    │       └── src/
    │
    ├── lib/                         ← Bibliotecas compartilhadas do workspace
    │   ├── api-spec/                ← Contrato OpenAPI (fonte da verdade)
    │   │   └── openapi.yaml         ← ⭐ Especificação da API
    │   ├── api-client-react/        ← Cliente React Query gerado
    │   │   └── src/generated/api.ts
    │   ├── api-zod/                 ← Schemas Zod gerados
    │   │   └── src/generated/api.ts
    │   └── db/                      ← Schemas do banco (drizzle-orm)
    │       └── src/schema/          ← Definições de tabelas
    │
    ├── scripts/                     ← Scripts utilitários TypeScript
    │   ├── package.json
    │   ├── src/
    │   ├── post-merge.sh            ← Hook Git
    │   └── tsconfig.json
    │
    ├── attached_assets/             ← Imagens, screenshots
    ├── skills-lock.json
    └── .agents/                     ← Memória/skills do agente
```

### 🔑 Arquivos mais importantes para conhecer

| Arquivo | Propósito |
|---|---|
| `/app/backend/server.py` | FastAPI. Sobe Node como subprocess e proxya `/api/*` |
| `/app/backend/ai_router.py` | Rotas `/api/ai/*` (Claude, Sora, Object Storage) |
| `/app/backend/requirements.txt` | Dependências Python |
| `/app/backend/.env` | Variáveis de ambiente Python (criar você) |
| `/app/frontend/package.json` | Launcher: `yarn start` chama o Vite do creatools |
| `/app/frontend/.env` | `REACT_APP_BACKEND_URL` para o frontend |
| `/app/tiks/artifacts/api-server/src/index.ts` | Entry point Express |
| `/app/tiks/artifacts/api-server/data/config.json` | Fallback do TIKTOOLS_API_KEY |
| `/app/tiks/artifacts/creatools/vite.config.ts` | Configuração Vite |
| `/app/tiks/lib/api-spec/openapi.yaml` | Contrato OpenAPI (fonte da verdade) |
| `/etc/supervisor/conf.d/supervisord.conf` | Configuração do supervisor (readonly no Emergent) |

---

## 3. Requisitos de Sistema

### 💻 Sistema Operacional

- Linux (Ubuntu 20.04+ recomendado) — testado
- macOS 12+
- Windows (via WSL2)

### 📦 Softwares necessários

| Software | Versão mínima | Comando de instalação (Linux) |
|---|---|---|
| **Python** | 3.11+ | `sudo apt install python3.11 python3.11-venv` |
| **Node.js** | 20+ (24 recomendado) | Ver [nodejs.org](https://nodejs.org) ou usar `nvm` |
| **pnpm** | 9+ | `npm install -g pnpm` |
| **yarn** | 1.22+ | `npm install -g yarn` |
| **PostgreSQL** | 14+ | `sudo apt install postgresql` |
| **Git** | Qualquer | `sudo apt install git` |
| **Supervisor** (produção) | 4+ | `sudo apt install supervisor` |

### 🔑 Chaves/API externas necessárias

| Serviço | Onde obter | Obrigatório? |
|---|---|---|
| **tik.tools API Key** | [tik.tools](https://tik.tools) → Dashboard → API Keys | ✅ Sim |
| **Emergent LLM Key** | Plataforma Emergent → Perfil → Universal Key | ⚠️ Só para IA |
| **Stripe** (secret + publishable + webhook + price IDs) | [stripe.com/dashboard](https://dashboard.stripe.com) | ⚠️ Só para billing |
| **TikTok OAuth** (client key + secret) | [developers.tiktok.com](https://developers.tiktok.com) | ⚠️ Só para OAuth |

---

## 4. Variáveis de Ambiente

### 📄 `/app/backend/.env` — Backend Python

Crie este arquivo com o conteúdo abaixo. **Substitua os valores** pelos seus:

```bash
# ─── IA (Emergent LLM Key) ──────────────────────────────────────
EMERGENT_LLM_KEY=sk-emergent-XXXXXXXXXXXXXXXX

# ─── JWT (deve bater com o do Node) ─────────────────────────────
JWT_SECRET=troque-por-uma-string-aleatoria-muito-longa

# ─── URLs (Emergent gerencia; em local, use localhost) ──────────
APP_URL=http://localhost:3000
INTEGRATION_PROXY_URL=https://integrations.emergentagent.com

# ─── PostgreSQL (usado pelo Node subprocess) ────────────────────
DATABASE_URL=postgres://usuario:senha@localhost:5432/creatools

# ─── tik.tools API ──────────────────────────────────────────────
TIKTOOLS_API_KEY=sua-chave-tiktools-aqui

# ─── Object Storage (Emergent) ──────────────────────────────────
PUBLIC_OBJECT_SEARCH_PATHS=/public
PRIVATE_OBJECT_DIR=/private

# ─── Stripe (opcional) ──────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_XXXXXXXX
STRIPE_PUBLISHABLE_KEY=pk_test_XXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXX
STRIPE_PRICE_ID_BASIC=price_XXXXXXXX
STRIPE_PRICE_ID_PRO=price_XXXXXXXX

# ─── TikTok OAuth (opcional) ────────────────────────────────────
TIKTOK_CLIENT_KEY=seu-client-key
TIKTOK_CLIENT_SECRET=seu-client-secret
TIKTOK_REDIRECT_URI=http://localhost:8001/api/auth/tiktok/callback
FRONTEND_URL=http://localhost:3000

# ─── Node ambiente ──────────────────────────────────────────────
NODE_ENV=development
LOG_LEVEL=info
```

### 📄 `/app/frontend/.env` — Frontend React

```bash
# URL do backend (FastAPI proxy). Em local:
REACT_APP_BACKEND_URL=http://localhost:8001

# Em produção (Emergent), essa URL é fornecida automaticamente
# e NÃO deve ser modificada.
```

> ⚠️ **NUNCA** modifique `MONGO_URL` (se existir) ou `REACT_APP_BACKEND_URL` no ambiente Emergent — essas variáveis são gerenciadas pela plataforma.

---

## 5. Instalação Passo a Passo (Local)

Siga na ordem exata:

### 🪜 Passo 1 — Clonar o repositório

```bash
git clone https://github.com/leopivas/APPFINALV3.git /app
cd /app
```

### 🪜 Passo 2 — Instalar Python + dependências do backend

```bash
# Verificar Python
python3 --version   # deve ser 3.11+

# Criar virtualenv
python3 -m venv /root/.venv
source /root/.venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r /app/backend/requirements.txt

# Instalar Emergent Integrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### 🪜 Passo 3 — Instalar Node.js 24 + pnpm

```bash
# Instalar nvm (opcional, recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Instalar Node 24
nvm install 24
nvm use 24

# Instalar pnpm e yarn globalmente
npm install -g pnpm@latest yarn
```

### 🪜 Passo 4 — Instalar dependências do workspace pnpm

```bash
cd /app/tiks
pnpm install
```

> ⚠️ Este passo instala **todas** as dependências do monorepo (api-server, creatools, libs). Pode demorar 5-10 minutos na primeira vez.

### 🪜 Passo 5 — Instalar dependências do launcher frontend

```bash
cd /app/frontend
yarn install
```

### 🪜 Passo 6 — Configurar PostgreSQL

```bash
# Instalar PostgreSQL (se ainda não tiver)
sudo apt install postgresql postgresql-contrib

# Iniciar serviço
sudo service postgresql start

# Criar usuário e banco
sudo -u postgres psql <<EOF
CREATE USER creatools WITH PASSWORD 'sua-senha-forte';
CREATE DATABASE creatools OWNER creatools;
GRANT ALL PRIVILEGES ON DATABASE creatools TO creatools;
EOF
```

Coloque a string de conexão em `/app/backend/.env`:

```bash
DATABASE_URL=postgres://creatools:sua-senha-forte@localhost:5432/creatools
```

### 🪜 Passo 7 — Criar arquivos `.env`

Crie os dois arquivos:

- `/app/backend/.env` (conteúdo do item [4](#4-variáveis-de-ambiente))
- `/app/frontend/.env` (conteúdo do item [4](#4-variáveis-de-ambiente))

### 🪜 Passo 8 — Fazer o build do API server (Node)

```bash
cd /app/tiks/artifacts/api-server
pnpm run build
```

Isso gera `/app/tiks/artifacts/api-server/dist/index.mjs` que o FastAPI usa como subprocess.

### 🪜 Passo 9 — Regenerar o código a partir do OpenAPI (opcional)

Se você alterou `/app/tiks/lib/api-spec/openapi.yaml`:

```bash
cd /app/tiks
pnpm --filter @workspace/api-spec run codegen
```

### 🪜 Passo 10 — Verificar tipos (opcional)

```bash
cd /app/tiks
pnpm run typecheck
```

---

## 6. Rodando o App

### 🚀 Modo Local (desenvolvimento)

Você precisa de **2 terminais** rodando ao mesmo tempo:

#### Terminal 1 — Backend (FastAPI + Node subprocess)

```bash
cd /app/backend
source /root/.venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

✅ FastAPI sobe na porta **8001** e automaticamente sobe o Node na porta **8081** como subprocess.

#### Terminal 2 — Frontend (Vite via launcher)

```bash
cd /app/frontend
yarn start
```

✅ Frontend sobe na porta **3000**.

### 🌐 Acesso

- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8001/api/**
- Health check: **http://localhost:8001/api/_proxy/health**

### 🎛️ Modo Produção (com supervisor)

O ambiente Emergent já vem com supervisor configurado. Localmente, você pode replicar:

```bash
sudo apt install supervisor
# Criar /etc/supervisor/conf.d/creatools.conf conforme modelo abaixo
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl start all
```

Configuração de referência (`/etc/supervisor/conf.d/creatools.conf`):

```ini
[program:backend]
command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log

[program:frontend]
command=yarn start
directory=/app/frontend
environment=HOST="0.0.0.0",PORT="3000"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
```

Controle:

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
sudo supervisorctl status
```

---

## 7. Comandos Úteis

### 📜 pnpm (workspace)

```bash
# Rodar api-server em modo dev (com hot-reload próprio)
pnpm --filter @workspace/api-server run dev

# Rodar creatools em modo dev
pnpm --filter @workspace/creatools run dev

# Build de todos os pacotes
cd /app/tiks && pnpm run build

# Typecheck em todos os pacotes
cd /app/tiks && pnpm run typecheck

# Regenerar hooks + Zod a partir do OpenAPI
pnpm --filter @workspace/api-spec run codegen
```

### 🐍 Python

```bash
# Ativar venv
source /root/.venv/bin/activate

# Rodar backend
cd /app/backend && uvicorn server:app --reload --port 8001

# Rodar testes
cd /app/backend && pytest

# Formatar código
cd /app/backend && black . && isort .
```

### 📝 Logs

```bash
# Backend
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

---

## 8. Deploy em Produção

### 🥇 Opção 1: Deploy no Emergent (recomendado)

1. No topo do chat, clique em **"Deploy"**
2. Clique em **"Deploy Now"**
3. Aguarde ~10 minutos
4. Copie a URL pública gerada
5. (Opcional) Configure domínio via **"Link domain"**

Custo: 50 créditos/mês por app. SSL/HTTPS automático.

### 🥈 Opção 2: VPS / Cloud próprio

Suba um servidor Ubuntu 22.04 (mínimo 2 vCPU / 4 GB RAM):

```bash
# 1. Clonar repo
git clone https://github.com/leopivas/APPFINALV3.git /app

# 2. Seguir passos 2-9 da seção "Instalação Passo a Passo"

# 3. Configurar Nginx como reverse proxy
sudo apt install nginx certbot python3-certbot-nginx
# Config em /etc/nginx/sites-available/creatools

# 4. Configurar supervisor
# (ver seção "Modo Produção" acima)

# 5. SSL grátis com Certbot
sudo certbot --nginx -d seu-dominio.com
```

### 🥉 Opção 3: AWS

- **Frontend**: AWS Amplify (conectar ao GitHub)
- **Backend**: AWS App Runner (Docker) ou ECS Fargate
- **DB**: RDS PostgreSQL
- **Storage**: S3 + CloudFront

Passos gerais:
1. Criar Dockerfile no backend
2. Criar `amplify.yml` no frontend
3. Push do código para GitHub
4. Amplify + App Runner conectam ao repositório
5. Configurar variáveis de ambiente em cada serviço

---

## 9. Testes

### 🧪 Testes Python (backend)

```bash
cd /app/backend
source /root/.venv/bin/activate
pytest -v
```

Testes disponíveis em `/app/backend/tests/`:
- `test_tiktok_and_plans.py`
- `test_iter5_regression.py`
- `test_iter5_bugfixes.py`
- `test_overlays_phase1.py`
- `test_ai_and_regression.py`

### 🧪 Typecheck (frontend + libs)

```bash
cd /app/tiks
pnpm run typecheck
```

---

## 10. Troubleshooting

### ❌ `Node health check timed out` no log do backend

O FastAPI não conseguiu subir o Node subprocess. Verifique:

```bash
# 1. Confirme que o build do api-server foi feito
ls /app/tiks/artifacts/api-server/dist/index.mjs

# 2. Se não existir, faça o build
cd /app/tiks/artifacts/api-server && pnpm run build

# 3. Reinicie o backend
sudo supervisorctl restart backend
```

### ❌ Frontend mostra "Cannot connect to backend"

Verifique se `REACT_APP_BACKEND_URL` em `/app/frontend/.env` está correto e se o backend está rodando na porta 8001.

### ❌ Erro de conexão com PostgreSQL

```bash
# Verifique se o serviço está rodando
sudo service postgresql status

# Teste conexão manualmente
psql -U creatools -d creatools -h localhost
```

### ❌ Erro "EMERGENT_LLM_KEY not configured" nas rotas de IA

- Verifique se a variável está em `/app/backend/.env`
- Reinicie o backend após alterar o `.env`: `sudo supervisorctl restart backend`
- Obtenha uma nova chave em: Plataforma Emergent → Perfil → Universal Key

### ❌ Erro "Use pnpm instead" ao rodar `npm install`

Esse repositório **exige pnpm** no workspace `/app/tiks`. Instale com:

```bash
npm install -g pnpm
cd /app/tiks && pnpm install
```

### ❌ Vite dev server não abre (porta 3000 ocupada)

```bash
# Descobrir o que está usando a porta
sudo lsof -i :3000

# Matar processo
sudo kill -9 <PID>
```

### ❌ Após alterar `openapi.yaml`, typecheck falha

Rode o codegen antes:

```bash
cd /app/tiks
pnpm --filter @workspace/api-spec run codegen
pnpm run typecheck
```

### ❌ Erros de WebSocket no monitor de streams

- tik.tools Sandbox tier permite apenas **3 WebSockets concorrentes** e sessões de **10 min**
- Verifique sua tier em: [tik.tools](https://tik.tools) → Dashboard → Plans

---

## 📞 Suporte

- **Dúvidas técnicas do app**: abra uma issue no repositório GitHub
- **Dúvidas sobre Emergent (deploy, faturamento)**: support@emergent.sh
- **Documentação tik.tools**: https://tik.tools/docs
- **Documentação Emergent Integrations**: contate o suporte Emergent

---

## 📝 Notas Finais

- **Fonte da verdade da API**: `/app/tiks/lib/api-spec/openapi.yaml` — qualquer mudança de contrato começa aqui
- **Sem banco de dados para dados de TikTok**: tudo é proxy em tempo real do tik.tools
- **API key nunca no frontend**: o backend gera JWTs de curta duração para WebSockets
- **Dark mode fixo**: `html.dark` no `index.html` + custom-variant Tailwind v4
- **MongoDB no supervisor**: o `mongod` está listado em `supervisord.conf` mas **este app não usa MongoDB** (apenas PostgreSQL via Node subprocess). Pode ser desabilitado se não usar outros apps.

---

**Última atualização**: Julho 2025
**Versão do documento**: 1.0.0
**Repositório**: https://github.com/leopivas/APPFINALV3
