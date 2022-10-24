import sys
import network

"""
Initialisation de la connexion Wifi en mode Access Point
"STA" connexion à un réseau local  //  "AP" -> serveur DHCP en local
"""
access = "AP" 
if access == "STA" : # STA_IF station Interface 
    infos_access = ('192.168.1.210', '255.255.255.0', '192.168.1.1', '213.186.33.102')
    ssid = ''      # my network
    passwrd = ''
    station = network.WLAN(network.STA_IF)
    station.ifconfig( infos_access )
    station.active(True)
    station.connect(ssid, passwrd) # connexion à un réseau Wifi disponible
        # ===== Attendre 7s que la connexion soit établie
    t0 = ticks_ms()
    delta_t = 0
    while station.active() == False and delta_t<7000 :
      delta_t = ticks_ms() - t0
      sleep(0.5)

else : #  AP_IF : Access Point
    ssid = 'wifigrp13'
    passwrd = 'NsiGrp13'
    infos_access = ('192.168.13.1', '255.255.255.0', '192.168.13.1', '8.8.8.8')
    station = network.WLAN(network.AP_IF)
    station.ifconfig( infos_access )
    station.config(essid=ssid, password=passwrd) # création d'un point d'accès WiFi
    station.active(True)

# ===== Si la connexion est établie afficher l'adresse IP
if station.active() == True :
    print(" ---------- Connection Wifi -> OK")
    print(station.ifconfig())
    Wifi_Connected = True
else:
    print("########## ECHEC d'initialisation de la connexion wifi ")
    Wifi_Connected = False

    
