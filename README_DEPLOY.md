# 🚀 Sistema Híbrido de Sinais - Deploy Railway

## 📋 Visão Geral

Sistema completo de análise e geração de sinais de criptomoedas que combina:
- ✅ **Análise Técnica Tradicional** (RSI, MACD, SMA, Volume)
- ✅ **Análise de Sentimento** (News API + TextBlob)
- ✅ **Modelo ML com 2 anos de dados** (Principal)
- ✅ **IA Adaptativa** (Aprendizado contínuo)
- ✅ **API REST** para monitoramento e controle
- ✅ **Deploy automático no Railway**

## 🚀 Deploy no Railway via GitHub

### Passo 1: Preparar Repositório GitHub
1. Crie um novo repositório no GitHub
2. Faça upload de todos os arquivos do projeto
3. Certifique-se de que os seguintes arquivos estão incluídos:
   - `main.py` (ponto de entrada)
   - `requirements.txt` (dependências)
   - `Procfile` (comando de execução)
   - `railway.json` (configurações do Railway)
   - Todos os módulos Python (.py)

### Passo 2: Configurar Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com sua conta GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha o repositório do projeto
6. O Railway detectará automaticamente que é um projeto Python

### Passo 3: Configurar Variáveis de Ambiente
No painel do Railway, vá em "Variables" e adicione:

```bash
# OBRIGATÓRIAS
NEWS_API_KEY=sua_chave_da_news_api
TELEGRAM_BOT_TOKEN=seu_token_do_bot_telegram
TELEGRAM_CHAT_ID=seu_chat_id_telegram

# OPCIONAIS
AUTO_START_SCANNER=true
PORT=5000
DEBUG=false
```

### Passo 4: Deploy Automático
- O Railway fará o deploy automaticamente
- O processo levará alguns minutos
- Você receberá uma URL pública para acessar a API

## 🌐 API Endpoints

Após o deploy, sua aplicação terá os seguintes endpoints:

### Status e Monitoramento
- `GET /` - Informações básicas do sistema
- `GET /status` - Status detalhado do sistema
- `GET /health` - Health check
- `GET /config` - Configuração atual

### Controle do Scanner
- `POST /start` - Iniciar scanner
- `POST /stop` - Parar scanner

### Dados
- `GET /trades` - Trades abertos
- `GET /logs` - Logs do sistema

### Exemplo de Uso
```bash
# Verificar status
curl https://sua-app.railway.app/status

# Iniciar scanner
curl -X POST https://sua-app.railway.app/start

# Ver trades abertos
curl https://sua-app.railway.app/trades
```

## 📊 Monitoramento

### Dashboard Web
Acesse `https://sua-app.railway.app` para ver:
- Status do sistema em tempo real
- Configurações ativas
- Estatísticas de funcionamento

### Logs do Railway
- Acesse o painel do Railway
- Vá na aba "Logs" para ver logs em tempo real
- Monitore erros e atividade do sistema

## 🔧 Configurações Importantes

### Auto-Start
O sistema inicia automaticamente o scanner quando deployado.
Para desabilitar, defina `AUTO_START_SCANNER=false`.

### Modelo ML
- Coloque o arquivo `crypto_ml_model.pkl` na raiz do projeto
- O sistema detectará automaticamente e ativará o ML
- Sem o arquivo, o sistema funcionará apenas com IA adaptativa

### Análise de Sentimento
- Obtenha uma chave gratuita em [newsapi.org](https://newsapi.org)
- Configure `NEWS_API_KEY` nas variáveis de ambiente
- Sem a chave, o sistema funcionará sem análise de sentimento

## 🚨 Solução de Problemas

### Deploy Falhou
1. Verifique se todos os arquivos estão no repositório
2. Confirme que `requirements.txt` está correto
3. Verifique logs do Railway para erros específicos

### Scanner Não Inicia
1. Verifique variáveis de ambiente
2. Confirme que `TELEGRAM_BOT_TOKEN` está correto
3. Use endpoint `/start` para iniciar manualmente

### Erro de Dependências
1. Verifique se `requirements.txt` está completo
2. O Railway instala automaticamente as dependências
3. Verifique logs para erros de instalação

## 📈 Próximos Passos

Após o deploy bem-sucedido:

1. **Teste a API** usando os endpoints
2. **Configure notificações** do Telegram
3. **Monitore logs** para verificar funcionamento
4. **Adicione modelo ML** se disponível
5. **Configure domínio customizado** (opcional)

## 🔄 Atualizações

Para atualizar o sistema:
1. Faça push das alterações para o GitHub
2. O Railway fará redeploy automaticamente
3. Monitore logs durante a atualização

## 📞 Suporte

O sistema foi projetado para ser completamente automático. Em caso de problemas:

1. Verifique logs no painel do Railway
2. Use endpoints da API para diagnóstico
3. Confirme variáveis de ambiente
4. Verifique status dos serviços externos (News API, Telegram)

## 🎉 Resultado Esperado

Com o sistema funcionando no Railway:
- ✅ **Disponibilidade 24/7** na nuvem
- ✅ **Escalabilidade automática**
- ✅ **Monitoramento via API**
- ✅ **Deploy automático** via GitHub
- ✅ **Logs centralizados**
- ✅ **URL pública** para acesso

O sistema estará completamente operacional na nuvem, gerando sinais automaticamente e enviando notificações via Telegram!

