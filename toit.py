from micropython import const
from machine import Pin, PWM
from time import sleep_ms, ticks_ms

FDC_CLOSE = const(12)
FDC_OPEN = const(4)
SERVO_MOTEUR = const(5)
PWM_MAX = const(1023)

OPEN = const(1)  # état des capteurs de fin de course pour l'ouverture du toit
CLOSE = const(0)
UNKNOWN = const(-1)

class Toit ( ):
    """
    mon_toit = Toit ( Pin_servo, Pin_fdc_close, fdc_open )
    Pin_servo -> Broche de connexion du servo moteur
    Pin_fdc_close -> broche de connexion du fin de course en fermeture
    Pin_fdc_open -> broche de connexion du fnn de course en ouverture
    """
    OPEN_ANGLE = const(0) # angle position servo-moteur "toit OUVERT"
    CLOSE_ANGLE = const(65) # angle position servo-moteur "toit FERME"

    def __init__ ( self ):
        self.__broche = SERVO_MOTEUR
        self.__servo = PWM(Pin(self.__broche), freq=50)   # duty 180° -> cycle 30 < ... < 125
        self.__servo.deinit ( ) # relâcher le servo moteur
        self.__Fdc_c = Pin(FDC_CLOSE, Pin.IN)
        self.__Fdc_o = Pin(FDC_OPEN, Pin.IN)
        self.__position = Toit.CLOSE_ANGLE
        self.__etat = CLOSE
        self.__fermer ( ) # Forcer la fermeture pour l'initialisation
    # ============================================================================= __fermer ( )
    def __fermer( self ) :
        """ Forcer la fermeture pour l'initialisation du toit """
        t0 = ticks_ms()
        t1 = t0
        self.__servo.init()   
        self.__servo.duty(self.degre_to_pwm(Toit.CLOSE_ANGLE))
        while t1 < t0 + 1000 : # Attente maximum : 1s
            if self.__Fdc_c.value() : # Ok fin de course activé -> toit fermé
                break
            t1 = ticks_ms()
        self.__servo.deinit()

    # ============================================================================= servo_degre ( )
    def degre_to_pwm ( self, angle:int )->int:
        """
        Conversion angle du servo moteur -> rapport cyclique en mode PWM ( duty )
        Entrée :
            - l'angle souhaité pour le positionnement du servo-moteur
        """
        return int( ((angle * 95 ) // 180 ) + 30)

    @property
    def OPEN ( self ):
        return True if self.__etat==OPEN else False
            
    @property
    def CLOSE ( self ):
        return True if self.__etat==CLOSE else False

    @property
    def position ( self ):
        return self.__position
    
    @position.setter
    def position ( self, angle ):
        self.__servo.init()   # duty 180° -> cycle 30 < ... < 125
        if self.__position > angle :
            pos_finale = angle-1
            step = -1
        else :
            pos_finale = angle+1
            step = 1
        self.__etat = UNKNOWN
        for i in range ( self.__position, pos_finale ,step ):
            self.__servo.duty(self.degre_to_pwm(i)) # Modification progressive de l'ouverture
            sleep_ms(15)
            if self.__Fdc_c.value() and angle == Toit.CLOSE_ANGLE :
                self.__etat = CLOSE
                break;
            elif self.__Fdc_o.value() and angle == Toit.OPEN_ANGLE :
                self.__etat = OPEN
                break
        self.__position = i
        self.__servo.deinit()
        
    # =========================================================================== fermer_toit (...)
    def fermer ( self )->bool:
        """
        Contrôler le servo moteur pour fermer le toit
        Sortie : True/False selon l'état du capteur de fin de course
        """
        fermeture_ok = self.__Fdc_c.value() # tester la valeur du fin de course
        if not fermeture_ok : # Si le toit n'est pas fermé, activier le moteur pour le fermer
            self.position = Toit.CLOSE_ANGLE 
            sleep_ms(500)
            fermeture_ok = self.__Fdc_c.value()  # fdc = etat du toit avant de relâcher le servomoteur
        if fermeture_ok :
            print(" ---------- Fermeture du toit -> OK")
            self.__etat = CLOSE
        else :
            print(" ########## PROBLEME pour la FERMETURE du toit ")
        return fermeture_ok
    # =========================================================================== ouvrir_toit (...)
    def ouvrir ( self )->bool:
        """
        Contrôler le servo moteur pour ouvrir le toit
        Sortie : True/False selon l'état du capteur de fin de course
        """
        ouverture_ok = self.__Fdc_o.value() # tester la valeur du fin de course
        if not ouverture_ok : # Si le toit n'est pas ouvert, activer le moteur pour l'ouvrir
            self.position = Toit.OPEN_ANGLE
            sleep_ms(500)
            ouverture_ok = self.__Fdc_o.value() # fdc = etat toit avant de relâcher le servomoteur
        if ouverture_ok :
            print(" ---------- Ouverture du toit -> OK")
            self.__etat = OPEN
        else :
            print(" ########## PROBLEME pour l' OUVERTURE du toit ")
        return ouverture_ok
# ==============================================================================
if __name__ == "__main__":
    mon_toit = Toit ( )

    mon_toit.ouvrir ( )
    sleep_ms(1500)
    mon_toit.fermer ( )
    sleep_ms(1500)
    mon_toit.position = 30