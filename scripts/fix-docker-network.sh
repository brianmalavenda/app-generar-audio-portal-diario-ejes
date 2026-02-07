#!/bin/bash
echo "Restaurando reglas iptables para Docker..."
sudo iptables -P FORWARD ACCEPT
sudo iptables -I DOCKER-USER -i br-+ -o br-+ -j ACCEPT  # Aceptar tráfico entre bridges Docker
echo "Listo"

# EJECUTAR DESPUES DE UNA DESCONEXION DE VPN

# MAS RAPIDO
alias fix-docker="sudo iptables -P FORWARD ACCEPT && echo 'Docker network restaurado'"
# Te desconectaste de la VPN y Docker no funciona?
fix-docker


# REGLAS PERMANENTES
# Permitir todo tráfico entre redes Docker (seguro porque son locales)
sudo iptables -I DOCKER-USER -s 172.16.0.0/12 -d 172.16.0.0/12 -j ACCEPT
sudo iptables -I DOCKER-USER -i docker+ -o docker+ -j ACCEPT
sudo iptables -I DOCKER-USER -i br-+ -o br-+ -j ACCEPT

# PARA WIREGUARD
# En tu cliente WireGuard, comenta o ajusta:
# PostUp = iptables -P FORWARD DROP  # <-- Eliminar o comentar
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT

# SPLIT TUNELING
# Ejemplo: WireGuard con AllowedIPs específicas
[Peer]
AllowedIPs = 10.0.0.0/8, 192.168.0.0/16  # Solo redes corporativas, NO 0.0.0.0/0