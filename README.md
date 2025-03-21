# 🔍 Arquivo sdwan_patch-monitor_check.py

Script em Python que consulta métricas SD-WAN de firewalls Palo Alto via API. Ideal para monitoramento rápido e diagnóstico de interfaces SD-WAN diretamente do terminal.

## 📦 Funcionalidades

- Acessa a API do firewall Palo Alto
- Coleta métricas detalhadas de interfaces SD-WAN
- Exibe as informações formatadas no terminal

## 📌 Requisitos

- Python 3.7+
- Acesso à API do firewall (usuário com permissões adequadas)
- Bibliotecas necessárias:

# 📦 Instalando dependencias  
pip install requests

⚙️ Como usar:

# Edite no script o IP e as credenciais do seu firewall

FIREWALL_IP = "192.0.2.1"
USERNAME = "admin"
PASSWORD = "sua_senha"

# Em seguida execute o script

python sdwan_patch-monitor_check.py

# 🔍 Arquivo sdwan_patch-monitor_check-graphic.py

Script em Python que consulta métricas de SD-WAN via API dos firewalls Palo Alto, gera gráficos em PNG para cada interface monitorada e organiza os arquivos em uma pasta nomeada com o hostname do equipamento.

## 📦 Funcionalidades

- Conecta-se ao firewall via API
- Coleta métricas SD-WAN por interface
- Gera gráficos de desempenho (PNG)
- Cria automaticamente uma pasta com o nome do hostname
- Salva os gráficos organizados por interface

## 📌 Requisitos

- Python 3.7+
- Acesso à API do firewall
- Bibliotecas Python:

# 📦 Instalando dependencias 
pip install requests matplotlib

⚙️ Como usar:

# Edite no script o IP e as credenciais do seu firewall

FIREWALL_IP = "192.0.2.1"
USERNAME = "admin"
PASSWORD = "sua_senha"

# Em seguida execute o script

python sdwan_patch-monitor_check-graphic.py

📅 Versão 1.0 - 06/04/2024

👨‍💻 Autor
Frederico Pereira (fredux / fr3d00x)

