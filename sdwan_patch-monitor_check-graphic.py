# Script Python que consulta métricas de sdwan nos firewalls Palo alto e gera arquivos de imagem PNG com gráfico dessas métricas
# O script gera um imagem/métricas para cada interface e as imagens são salvas em uma pasta com o hostname do firewall (ele gera a pasta onde o script for executado)
# by Frederico Pereira (fredux/fr3d00x) - 06/04/2024
#

import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import numpy as np
import os
import urllib3
import re  # Importado para limpar nomes inválidos

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dados de acesso ao firewall para gerar a chave API
FIREWALL_IP = "192.168.1.1"
USERNAME = "admin"
PASSWORD = "sua_senha"

def generate_api_key(firewall_ip, username, password):
    url = f"https://{firewall_ip}/api/"
    params = {
        "type": "keygen",
        "user": username,
        "password": password
    }
    response = requests.get(url, params=params, verify=False, timeout=10)
    root = ET.fromstring(response.text)
    return root.find(".//key").text

def get_firewall_hostname(firewall_ip, api_key):
    """Obtém o nome do firewall via API"""
    url = f"https://{firewall_ip}/api/"
    cmd = "<show><system><info></info></system></show>"

    params = {
        "type": "op",
        "cmd": cmd,
        "key": api_key
    }

    response = requests.get(url, params=params, verify=False, timeout=10)
    root = ET.fromstring(response.text)
    hostname = root.find(".//hostname")
    
    return hostname.text if hostname is not None else "firewall_desconhecido"

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
    response = requests.get(url, params=params, verify=False, timeout=10)
    return response.text

def parse_metrics(xml_data):
    root = ET.fromstring(xml_data)
    entries = root.findall(".//entry")
    metrics = []

    timestamp = datetime.now().strftime("%H:%M:%S")

    for entry in entries:
        link = entry.findtext("if_name") or entry.findtext("vif_name") or "Desconhecido"
        latency = int(entry.findtext("latency") or 0)
        jitter = int(entry.findtext("jitter") or 0)
        loss = int(entry.findtext("loss") or 0)

        print(f"[DEBUG] {timestamp} | Link: {link} | Latência: {latency}ms | Jitter: {jitter}ms | Perda: {loss}%")

        metrics.append({
            "timestamp": timestamp,
            "link": link,
            "latency": latency,
            "jitter": jitter,
            "loss": loss
        })

    return metrics

def sanitize_filename(filename):
    """Remove caracteres inválidos do nome do arquivo"""
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return filename[:50]  # Limita para evitar nomes muito longos

def plot_metrics(metrics, save_dir):
    data_by_link = defaultdict(lambda: {"timestamps": [], "latency": [], "jitter": [], "loss": []})

    for item in metrics:
        link = item["link"]
        data_by_link[link]["timestamps"].append(item["timestamp"])
        data_by_link[link]["latency"].append(item["latency"])
        data_by_link[link]["jitter"].append(item["jitter"])
        data_by_link[link]["loss"].append(item["loss"])

    for link, data in data_by_link.items():
        if not data["latency"]:
            print(f"Nenhum dado válido para {link}. Pulando gráfico.")
            continue

        x = np.arange(len(data["timestamps"]))  
        width = 0.3  

        plt.figure(figsize=(12, 6))
        plt.bar(x - width, data["latency"], width, label="Latência (ms)", color="blue")
        plt.bar(x, data["jitter"], width, label="Jitter (ms)", color="orange")
        plt.bar(x + width, data["loss"], width, label="Perda (%)", color="red")

        for i in range(len(data["timestamps"])):
            plt.text(x[i] - width, data["latency"][i] + 1, str(data["latency"][i]), ha='center', fontsize=10, color="blue")
            plt.text(x[i], data["jitter"][i] + 1, str(data["jitter"][i]), ha='center', fontsize=10, color="orange")
            plt.text(x[i] + width, data["loss"][i] + 1, str(data["loss"][i]), ha='center', fontsize=10, color="red")

        plt.xticks(x, data["timestamps"], rotation=45)
        plt.title(f"Métricas SD-WAN - {link}", fontsize=14)
        plt.xlabel("Horário", fontsize=12)
        plt.ylabel("Valor", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        
        # Ajuste para evitar sobreposição de rótulos no eixo X
        plt.subplots_adjust(bottom=0.2)  

        filename = sanitize_filename(link.replace("/", "_"))
        filepath = os.path.join(save_dir, f"grafico_{filename}.png")

        plt.savefig(filepath)
        plt.close()
        print(f"Gráfico salvo: {filepath}")

if __name__ == "__main__":
    print("Gerando API Key...")
    api_key = generate_api_key(FIREWALL_IP, USERNAME, PASSWORD)

    if api_key:
        print("Obtendo hostname do firewall...")
        firewall_hostname = get_firewall_hostname(FIREWALL_IP, api_key)
        print(f"Hostname do firewall: {firewall_hostname}")

        save_directory = f"./metricas_{firewall_hostname}"
        os.makedirs(save_directory, exist_ok=True)

        print("Coletando métricas SD-WAN...")
        xml_response = get_sdwan_metrics(FIREWALL_IP, api_key)
        if xml_response:
            metrics = parse_metrics(xml_response)
            plot_metrics(metrics, save_directory)
