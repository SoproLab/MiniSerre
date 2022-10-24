import sys
from os import chdir
from micropython import const
from machine import Pin, I2C, PWM, ADC, time_pulse_us
from bme280 import BME280
from time import ticks_ms, sleep_ms, sleep

pin_ledBlanche = const(13) # Commande d'éclairage
pin_anemometre = const(27) # Broche de connexion avec l'anemometre
pin_inter = const(15) # Broche de connexion vers l'interrupteur
pin_bp = const(2) # Broche de connexion vers le bouton poussoir
pin_LDR = const(33) # Broche de connexion vers la LDR
    
anemometre = Pin( pin_anemometre, Pin.IN )
interrupteur = Pin( pin_inter, Pin.IN )
bp = Pin( pin_bp, Pin.IN )
ldr = ADC( Pin(pin_LDR) ) # Capteur de lumière
ldr.atten(ADC.ATTN_11DB) # Conversion AD sur la plage de 0 à 3,3V
led = Pin( pin_ledBlanche, Pin.OUT )

# Utilisation du BME280 en mode i2C
bus_i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
capteurBME = BME280 ( i2c = bus_i2c )

class Console ( ):
    def __init__ ( self ):
        pass
    def afficher ( self, x, y, texte ):
        print(texte)
    def effacer ( self ):
        pass
    def backlight_off ( self ):
        pass    
    def backlight_on ( self ):
        pass    
    def off ( self ):
        pass
try :
    lcd = Lcd( i2c = bus_i2c )      # Utilisation de l'écran LCD 1602
    lcd.backlight_off()
except :
    lcd = Console ( )      # Redirection vers la console de Thonny
    
# ============================================================================ lire_html (...)
def lire_fichier ( fichier_source:str ) -> str :
    """
    Permet de lire des fichiers du dossier www pour les charger dans une variable texte
    Entrée : fichier_source -> nom du fichier à ouvrir
    Sortie : chaîne de caractères contenant le fichier html / CSS / JavaScipt
    """
    chdir("www")
    with open(fichier_source,"r") as fichier : # Ouvrir le fichier html
        code = fichier.readlines()
    instructions = "".join(code) # assembler toutes les lignes
    if fichier_source=="indexihm.html" :
        instructions = instructions.replace("\n","") # supprimer les fins de lignes
        instructions = instructions.replace("\r","") # supprimer les retours à la ligne
    # print("/n============== ",fichier_source, "====================")
    # print(instructions)
    # print("/n======================================================")
    chdir("..")
    return instructions
    
        
        
    
    