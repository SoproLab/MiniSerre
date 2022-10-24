from serre_biblio import *
from toit import Toit
from uselect import poll, POLLIN
from machine import Pin, ADC
from time import sleep, ticks_ms

try:
  import usocket as socket
except:
  import socket

toit = Toit( )

# ============================================================================= b_poussoir (...)
bp_flag = 0 # Attention : Variable globale

def Set_BP_flag ( Pin ):
    global bp_flag
    bp_flag +=1

def b_poussoir():
    """ Si appui sur le BP -> interruption -> ouverture ou fermeture du toit """
    global bp_flag
    if bp_flag > 0:
        if not toit.OPEN :
            toit.ouvrir()
        elif not toit.CLOSE :
            toit.fermer()
        else :
            toit.fermer()
        bp_flag = 0
            
bp.irq ( trigger=Pin.IRQ_RISING, handler=Set_BP_flag )

# ============================================================================= web_page (...)
def web_page( )->str:
    # ----------------------------------------- État du toit
    if toit.CLOSE : 
        toit_html="FERMÉ"
    elif toit.OPEN :
        toit_html="OUVERT"
    else :
        toit_html="## INCONNU ##"
        
    # ----------------------------------------- Température
    temperature_html = str(capteurBME.temperature)
        
    # ----------------------------------------- Lecture code HTML / CSS / et JS
    page_html = lire_fichier ( "index.html" )
    fichier_css = lire_fichier ( "style.css" )
    fichier_js = lire_fichier ( "script.js" )
    
    # ----------------------------------------- Incorporer JS et CSS dans HTML
    page_html = page_html.replace("<fichier_css>",fichier_css)
    page_html = page_html.replace("<fichier_js>",fichier_js)

    page_html = page_html.replace("<variable_temperature>", temperature_html)
    page_html = page_html.replace("<variable_toit>", toit_html)

    return page_html #Affiche la page HTML



# ==================================================================================== main
if not toit.CLOSE :
    toit.fermer ( )
    
if toit.CLOSE and Wifi_Connected : # Tout est OK => Attendre une requête
        
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.bind(('', 80))
    my_socket.listen(3)
    print("En attente de connexion ...")
    repondre = False

    while True : # En mode AP_IF
        connexion = []
        poller = poll()
        poller.register(my_socket, POLLIN)
        i = 0
        while connexion==[] : 
            connexion = poller.poll(1000)
            b_poussoir() # Vérifier si appui sur le BP toutes les secondes
                
        conn, addr = my_socket.accept()
        print("\nRéception d'une requête depuis : "+ str(addr))
        request = conn.recv(1024)
        request = str(request)
        ouverture = request.find('/?open_toit=1') # Récupérer les arguments dans l'URL
        fermeture = request.find('/?close_toit=1')
        requete = request.find('GET / HTTP')

        if requete == 2 : # Eviter de gérer des connexions parasites
            repondre = True
            
        if ouverture == 6:
            if not toit.OPEN :
                toit.ouvrir ( )
            repondre = True
            
        if fermeture == 6:
            if not toit.CLOSE :
                toit.fermer ( )
            repondre = True
            
        if repondre :

            reponse_html = web_page( ) # Construction de la page Web

            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(reponse_html)
            conn.close()
            repondre = False