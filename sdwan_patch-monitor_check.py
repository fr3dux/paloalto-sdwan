# ===============================================================
# Script em Python para consulta de métricas SD-WAN em firewalls Palo Alto
# Coleta dados diretamente dos dispositivos via API
# Autor: Frederico Pereira (fredux / fr3d00x)
# ===============================================================

import requests
import xml.etree.ElementTree as ET
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dados de acesso ao Firewall para gerar a chave API
FIREWALL_IP = "192.168.1.1"
USERNAME = "admin"
PASSWORD = "sua_senha"

# Gerando a chave API
def generate_api_key(firewall_ip, username, password):
    url = f"https://{firewall_ip}/api/"
    params = {
        "type": "keygen",
        "user": username,
        "password": password
    }

    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        return root.find(".//key").text
    except Exception as e:
        print(f"[ERRO] Falha ao gerar API Key: {e}")
        return None

# Pegando as informações de métricas sdwan (similar ao comando show sdwan path-monitor stats all-dp yes via CLI)
def get_sdwan_metrics(firewall_ip, api_key):
    url = f"https://{firewall_ip}/api/"
    cmd = """
    <show>
      <sdwan>
        <path-monitor>
          <stats>
            <all-dp>yes</all-dp>
          </stats>
        </path-monitor>
      </sdwan>
    </show>
    """

    params = {
        "type": "op",
        "cmd": cmd,
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERRO] Falha na requisição: {e}")
        return None

# Fazendo o parse das informações extraídas
def parse_metrics(xml_data):
    root = ET.fromstring(xml_data)
    entries = root.findall(".//entry")

    if not entries:
        print("Nenhuma métrica encontrada.")
        return

    print("\n=== Métricas SD-WAN Path Monitor ===")
    for entry in entries:
        # Coleta os dados corretamente
        link = entry.findtext("if_name") or entry.findtext("vif_name") or "-"
        latency = entry.findtext("latency") or "-"
        jitter = entry.findtext("jitter") or "-"
        packet_loss = entry.findtext("loss") or "-"

        print(f"Link: {link} | Latência: {latency}ms | Jitter: {jitter}ms | Perda: {packet_loss}%")

# Printa na tela o processo do script 
if __name__ == "__main__":
    print("Gerando API Key...")
    api_key = generate_api_key(FIREWALL_IP, USERNAME, PASSWORD)

    if api_key:
        print("API Key obtida com sucesso!\n")
        xml_response = get_sdwan_metrics(FIREWALL_IP, api_key)
        if xml_response:
            print("Resposta recebida. Interpretando dados...\n")
            parse_metrics(xml_response)
        else:
            print("Nenhuma resposta recebida.")
    else:
        print("Não foi possível obter a API Key.")
