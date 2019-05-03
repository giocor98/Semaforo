from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import BooleanProperty, StringProperty, NumericProperty

from kivy.clock import Clock

from kivy.uix.widget import Widget

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from time import sleep
import time
import serial

ser = 0
ErrorDesc = "GenericError"
T = 0

STo = 0

To = 30

Nome_Macchina_1 = "Macchina_1"
Nome_Macchina_2 = "Macchina_2"
Nome_Macchina_3 = "Macchina_3"

Corre_Macchina_1 = True
Corre_Macchina_2 = True
Corre_Macchina_3 = True

nGiri = 0

Nome_Corsa = "Corsa"

tipoPista = 1
LastGiro = 3

#funzioni per l'Arduino

SerOccupata = False         #Variabile che indica se la Seriale è o meno occupata

Tipo_Sensore = 0            #Indice del tipo di sensore in utilizzo sull arduino

Ser_To = 0                  #Variabile con il timeout della lettura dei sensori

Ser_Tc = 1000               #Variabile con il tempo del check

Sensori_Accesi = False      #Indica se i sensori sono o meno accesi

#funzione che apre öa seriale
def OpenSer():
    global ErrorDesc
    global ser
    print("Apro la Seriale")
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout= 0.1)
        print("Seriale aperta correttamente")
        sleep(.2)
        ser.write("P\n".encode())
        sleep(.8)
        while ser.in_waiting:
            ser.read()
        ser.write("P\n".encode())
        sleep(.1)
        if ser.read() == b'A' :
            print("Seriale aperta correttamente")
        else:
            print("Probabile errore durante l'apertura della seriale...")
            ##Faccio qualcosa di stupido per far salire un'eccezione
            ser.close()
            ser = 0
            ser.write("ciao") #cosa stupida
        while ser.in_waiting:
            ser.read()
    except:
        print("Non riesco ad aprire la seriale")
        ErrorDesc="Non riesco a aprire la seriale"
        ser = 0

#funzione che controlla se ser è la seriale e se è aperta
def CheckSer():
    global ser
    if ser == 0:
        OpenSer()
    else:
        try:
            while ser.in_waiting:
                ser.read()
            ser.write("P\n".encode())
            sleep (.5)
            if ser.in_waiting:
                if not  ser.read() == b'A':
                    print("Errore sulla Seriale")
            while ser.in_waiting:
                ser.read()
        except:
            ser = 0
    return ser

#Funzione che scrive sulla Seriale
#In: Messaggio da scrivere sulla Seriale
#out: True if Ack recived, False else
def SerScrivi(PS):
    global SerOccupata
    global ser
    if SerOccupata:
        if not(PS[-1] == '\n'):
            PS = PS + "\n"
        try:
            CheckSer()
            ser.write(PS.encode())
            return SerSimpleCheck(10)
        except:
            return False
    else:
        return False

#Funzione che svuota la seriale
def SerFlush():
    global ser
    try:
        while ser.in_waiting:
            ser.read()
        return True
    except:
        return False

#Funzione che esegue un check rapido per controllare se Arduino ha scritto A oppure E
def SerSimpleCheck(l):
    global ser

    for t in range (l):
        if ser.in_waiting:
            sleep(.05)
            while ser.in_waiting:
                c = ser.read()
                c = c.decode()
                if(c == 'A'):
                    SerFlush()
                    return True
                elif (c == 'E'):
                    SerFlush()
                    return False
        sleep(.05)
    return False

#Funzione per prenotare la Seriale
#ritorna true se la seriale era libera e ora è stata occupata dal richiedente, falso altrimenti
def GetSer():
    global SerOccupata
    if SerOccupata:
        return False
    else:
        SerOccupata = True
        return True

#funzione che rilascia la Seriale
def LeaveSer():
    global SerOccupata
    SerOccupata = False

#funzione per gestire i messaggi piu semplici della seriale.
#Prende in ingresso il messaggio da mandare
#restituisce 1 se manda il messaggio con successo, 0 se la Seriale è occupata, -1 se avviene un errore
def EasySerMsg(msg):
    if GetSer():
        if SerScrivi(msg):
            r = 1
        else:
            r = -1
        LeaveSer()
        return r
    else:
        return 0

#funzione che implementa la funnzione di Ping
def SerPing():
    return EasySerMsg("P\n")

#funzione che implementa la funnzione di Preparare i sensori
def SerPreparaSensori():
    global Sensori_Accesi
    r =  EasySerMsg("R\n")
    if(r == 1):
        Sensori_Accesi = True
    return r

#funzione che implementa la funnzione di Rilasciare i sensori
def SerRilasciaSensori():
    global Sensori_Accesi
    r = EasySerMsg("r\n")
    if(r == 1):
        Sensori_Accesi = False
    return r

#funzione che implementa la funnzione di Halt
def SerHalt():
    global Sensori_Accesi
    r = EasySerMsg("H\n")
    if(r == 1):
        Sensori_Accesi = False
    return r

#Funzione che implementa la funzione di Imposta Tipo di Sensoroi
#Controlla che il tipo passato sia valido
#Invia il tipo
#Se non ci sono errori aggiorna il tipo di sensore
def SerImpostaTipoSensori(tipo):
    try:
        tipo = int(tipo)
    except:
        #il tipo non è valido, quindi vai in Errore
        return -1
    if (tipo<0):
        #il tipo non è valido, quindi vai in Errore
        return -1
    return EasySerMsg("p" + str(tipo) + "\n")

#funzione che imposta le piste da controllare
#accetta in ingresso o una stringa con 0, 1, 2 o un array
def SerImpostaSensori(sensori):
    msg = "s"
    if ((type(sensori))==(type([])) and(len(sensori)>=3)):
        for i in range(3):
            if ((sensori[i] == True) or (sensori[i] == 1)):
                msg = msg + str(i)
    elif (type(sensori) == type("stringa")):
        for i in range(3):
            if str(i) in sensori:
                msg = msg + str(i)
    if msg == "s":
        #L'input era errato
        return -1
    else:
        msg = msg + "\n"
        return EasySerMsg(msg)

#Funzione che Imposta il timeout
def SerImpostaTimeOut(tempo):
    global Ser_To
    try:
        tempo = int(tempo)
    except:
        return -1
    if(tempo<=0):
        return -1
    r = EasySerMsg("T" + str(tempo) + "\n")
    if(r == 1):
        Ser_To = tempo
    return r

#Funzione che Imposta il timecheck
def SerImpostaTimeCheck(tempo):
    global Ser_Tc
    try:
        tempo = int(tempo)
    except:
        return -1
    if(tempo<=0):
        return -1
    r = EasySerMsg("t" + str(tempo) + "\n")
    if(r == 1):
        Ser_Tc = tempo
    return r

#Funzione per i comandi piu' lunghi
def LongSerMsg(msg):
    if GetSer():
        if SerScrivi(msg):
            return 1
        else:
            LeaveSer()
            return -1
    else:
        return 0

#Funzione per testare la calibrazione dei sensori
def TryCheck():
    global Ser_Tc
    global Sensori_Accesi
    prec = Sensori_Accesi
    r = SerImpostaSensori([1,1,1])
    if not (r == 1):
        if not(prec):
            SerRilasciaSensori()
        return r
    r = SerImpostaTimeCheck(Ser_Tc)
    if not (r == 1):
        if not(prec):
            SerRilasciaSensori()
        return r
    r = LongSerMsg("C\n")
    if r == 1:
        sleep(Ser_Tc/1000)
        if SerSimpleCheck(10):
            LeaveSer()
            if not(prec):
                SerRilasciaSensori()
            return 1
        else:
            LeaveSer()
            if not(prec):
                SerRilasciaSensori()
            return -1
    else:
        if not(prec):
            SerRilasciaSensori()
        return r

class Welcome(Screen):
    inFunz=0
    def PreRace(self, *args):
        if (self.inFunz==0):
            self.inFunz= self.inFunz +1
            if(self.inFunz == 1):
                self.race()
            else:
                print("Troppe chiamate...")

    def race(self, *args):
        if CheckSer() == 0:
            self.parent.new_Error_screen()
        else:
            self.parent.current = "Impostazioni"

class Error(Screen):
    def ErrCode(self, *args):
        return str(ErrorDesc)

    def EndProgram(self, *args):
        quit()

class SecondScreen(Screen):
    pass

class Race(Screen):

    MacchinaInPista = [1, 2, 3]

    CM1 = BooleanProperty(Corre_Macchina_1)
    CM2 = BooleanProperty(Corre_Macchina_2)
    CM3 = BooleanProperty(Corre_Macchina_3)

    IP1 = BooleanProperty(True)
    IP2 = BooleanProperty(True)
    IP3 = BooleanProperty(True)

    TempoStart = [0, 0, 0]

    Last_Runners = ListProperty(['', '', ''])

    TempoPiste = ListProperty(["No Time","No Time", "No Time", "No Time", "No Time", "No Time","No Time", "No Time", "No Time"] )

    def Aggiorna(self, *args):
        global Nome_Macchina_1
        global Nome_Macchina_2
        global Nome_Macchina_3
        global Nome_Corsa

        if (CheckSer()==0):
            self.ids.start_button.color = (1, 0, .1, 1)
        self.ids.TitoloCorsa.text = Nome_Corsa
        self.ids.macchina_1.text= Nome_Macchina_1
        self.ids.macchina_2.text= Nome_Macchina_2
        self.ids.macchina_3.text= Nome_Macchina_3

    def SerAv(self, *args):
        global ser
        if ser == 0:
            return 0
        else:
            return 1

    def F_Nome_1(self, *args):
        global Nome_Macchina_1
        global Corre_Macchina_1
        if (Corre_Macchina_1):
            return Nome_Macchina_1
        else:
            return ""

    def F_Nome_2(self, *args):
        global Nome_Macchina_2
        if (Corre_Macchina_2):
            return Nome_Macchina_2
        else:
            return ""

    def F_Nome_3(self, *args):
        global Nome_Macchina_3
        global Corre_Macchina_3
        if (Corre_Macchina_3):
            return Nome_Macchina_3
        else:
            return ""

    def Counter(self, *args):
        global T
        global ErrorDesc
        global ser
        global STo
        global nGiri
        try:
            pippo = ser.in_waiting
        except:
            print("Errore nella comunicazione con la Seriale")
            ErrorDesc = "Non riesco a connettermi con Arduino"
            ser = 0
            Clock.unschedule(self.Counter)
            self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.stop_button.color = (1, 0, 0, 1)
            self.ids.settings_button.color= (0, 1, 0, 1)
            self.ids.start_button.color = (0, 1, 0, 1)
            self.parent.new_Error_screen()
            return
        if (pippo>0):
            c = ser.read()
            if(c==b'R'):
                T = -200
                self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
            elif(c == b'Y'):
                T = -100
                self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
                self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
            elif(c == b'G'):
                self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
                self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
                self.ids.Green_Light.bgcolor = (0, 1, 0, 1)
                self.ids.stop_button.color = (0, 1, 0, 1)
                T = 0
            elif(c == b'E'):
                self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
                self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
                self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)
                print("Errore da parte di Arduino")
                Clock.unschedule(self.Counter)
                self.ids.stop_button.color = (1, 0, 0, 1)
                self.ids.settings_button.color= (0, 1, 0, 1)
                self.ids.start_button.color = (0, 1, 0, 1)
                ErrorDesc = "Errore sui sensori"
                self.parent.new_Error_screen()
            elif (c == b'D'):
                print("Arrivati tempi")
                sleep(.02)
                str0 = ser.readline()
                str1 = ser.readline()
                str2 = ser.readline()
                if (ser.in_waiting):
                    if not (str0.decode()[0] == '0'):
                        str0 = str1
                        str1 = str2
                        str2 = ser.readline()

                str0 = str0.decode()
                str1 = str1.decode()
                str2 = str2.decode()

                val = []

                if (' : ' in str0):
                    val.append(str0[str0.index(' : ') + 3:])
                if (' : ' in str1):
                    val.append(str1[str1.index(' : ') + 3:])
                if (' : ' in str2):
                    val.append(str2[str2.index(' : ') + 3:])

                for i in range(3):
                    val[i] = val[i].replace('\n', '')
                    val[i] = val[i].replace('\r', '')
                    if ('To' in val[i]):
                        val[i] = 0
                    else:
                        try:
                            val[i] = int(val[i])
                        except:
                            val[i] = 0
                self.CalcolaTempi(val, nGiri)
                nGiri = nGiri +1

                print(val)

        T = T+5
        if (T>=0):
            t = str(T)
        else:
            t = str(-T)
        while len(t)<5:
            t='0'+t
        self.ids.timer.text= t[0:3]+':'+t[3:5]
        if(T<=0):
            if ((T==0)and(not(self.ids.Green_Light.bgcolor[1]==1 ))):
                T = -50
                STo = STo+1
                if (STo >= 20):
                    print("No answer during Semaph")
                    ErrorDesc = "Errore sulla seriale: non ricevo risposta sul semaforo"
                    self.ids.stop_button.color = (1, 0, 0, 1)
                    self.ids.settings_button.color= (0, 1, 0, 1)
                    self.ids.start_button.color = (1, 0, 0, 1)
                    self.parent.new_Error_screen()

            self.ids.timer.text = '-' + self.ids.timer.text

    def CalcolaTempi(self, val, giro):
        global tipoPista
        global LastGiro
        if giro == 0:
            self.MacchinaInPista = [1, 2, 3]
            for i in range(3):
                if not(val[i] ==0):
                    if i==0:
                        self.IP1 = True
                    elif i == 1:
                        self.IP2 = True
                    elif i == 2:
                        self.IP3 = True
                    self.TempoStart[i] = val[i]
        else:
            for i in range(3):
                print(self.MacchinaInPista)
                print(i)
                if val[self.MacchinaInPista[i]-1] == 0:
                    if i==0:
                        self.IP1 = False
                    elif i == 1:
                        self.IP2 = False
                    elif i == 2:
                        self.IP3 = False
                elif (not(((i==0)and(self.IP1 == False))or((i==1)and(self.IP2 == False)) or((i==2)and(self.IP3==False)))):
                    self.TempoPiste[i + 3*(giro-1)] = str(val[self.MacchinaInPista[i]-1]-self.TempoStart[i])
        for i in range(3):
            self.MacchinaInPista[i] = self.MacchinaInPista[i] + tipoPista
            if(self.MacchinaInPista[i] >3):
                self.MacchinaInPista[i] = 1
            elif (self.MacchinaInPista[i] <1):
                self.MacchinaInPista[i] = 3
        if giro == LastGiro:
            print("Fine Gara")
            self.Stop()




    def Start(self, *args):
        global ser
        global T
        global ErrorDesc
        global STo
        global nGiri

        global Nome_Macchina_1
        global Nome_Macchina_2
        global Nome_Macchina_3

        nGiri = 0
        if CheckSer() == 0:
            print("Errore nell'apertura della seriale con lo start")
            ErrorDesc = "Non riesco ad aprire la seriale con lo start"
            self.parent.new_Error_screen()
            return
        while (ser.in_waiting >0):
            ser.read()

        #comunuco quali sono le piste da controllare:
        cmd_to_send = "s"

        if (self.CM1):
            cmd_to_send = cmd_to_send + "0"
        if (self.CM2):
            cmd_to_send = cmd_to_send + "1"
        if (self.CM3):
            cmd_to_send = cmd_to_send + "2"

        #Controlla che sia selezionata almeno una pista
        if (cmd_to_send == "s"):
            ErrorDesc = "Non hai selezionato alcuna pista"
            self.parent.new_Error_screen()
            return
        cmd_to_send = cmd_to_send + "\n"
        ser.write(cmd_to_send.encode())

        ser.write("S\n".encode())
        T = -300
        self.ids.stop_button.color = (.5, .5, 0, 1)
        self.ids.settings_button.color= (1, 0, 0, 1)
        self.ids.start_button.color = (1, 0, 0, 1)
        self.ids.Red_Light.bgcolor = (0, 0, 0, .9)
        self.ids.Yellow_Light.bgcolor = (0, 0, 0, .9)
        self.ids.Green_Light.bgcolor = (0, 0, 0, .9)
        sleep(.2)
        if(not(ser.read()==b'B')):
            self.ids.stop_button.color = (1, 0, 0, 1)
            self.ids.settings_button.color= (.3, .7, 0, 1)
            self.ids.start_button.color = (0, 1, 0, 1)
        else:
            Clock.schedule_interval(self.Counter, 0.05)
            STo = 0
            if self.CM1:
                self.Last_Runners[0] = Nome_Macchina_1
                self.IP1 = False
            else:
                self.Last_Runners[0] = ""
            if self.CM2:
                self.Last_Runners[1] = Nome_Macchina_2
                self.IP2 = False
            else:
                self.Last_Runners[1] = ""
            if self.CM3:
                self.Last_Runners[2] = Nome_Macchina_3
                self.IP3 = False
            else:
                self.Last_Runners[2] = ""
            for i in range(9):
                self.TempoPiste[i] = ''
            self.MacchinaInPista = [1, 2, 3]



    def Stop(self, *args):
        global T
        Clock.unschedule(self.Counter)
        ser.write("H\n".encode())
        self.ids.stop_button.color = (1, 0, 0, 1)
        self.ids.settings_button.color= (0, 1, 0, 1)
        self.ids.start_button.color = (1, 0, 0, 1)
        Clock.schedule_interval(self.Check_halt, 0.1)
        T = 10


    def Check_halt(self, *args):
        global ser
        global T
        global To
        global ErrorDesc
        try:
            pippo = ser.in_waiting
        except:
            print("Errore nella comunicazione con la Seriale")
            ErrorDesc = "Non riesco a connettermi con Arduino per terminare il controllo"
            Clock.unschedule(self.Check_halt)
            self.parent.new_Error_screen()
            return
        if pippo>0:
            if ser.read() == 'A'.encode():
                print("Arduino has stopped")
                self.ids.start_button.color = (0, 1, 0, 1)
                Clock.unschedule(self.Check_halt)
                while ser.in_waiting:
                    ser.read()
                return
        T = T +1
        if( T >=To*15):
            print("Arduino ci impiega troppo a rispondere")
            ErrorDesc = "Errore: Arduino non si ferma seppur sia scattato il timeout"
            Clock.unschedule(self.Check_halt)
            self.parent.new_Error_screen()
            return
    pass

class Impostazioni(Screen):

    SensoriAccesi = BooleanProperty(False)
    ValCheckSensori = NumericProperty(0)

    def on_pre_enter(self, *args):
        global Sensori_Accesi
        self.SensoriAccesi = Sensori_Accesi
        self.ValCheckSensori = 0

    def Accendi_Spegni_Sensori(self, *args):
        global Sensori_Accesi
        if self.SensoriAccesi :
            if (SerRilasciaSensori()==1):
                self.SensoriAccesi = False
        else:
            if(SerPreparaSensori()==1):
                self.SensoriAccesi = True

    def ControllaSensori(self, *args):
        self.ValCheckSensori = TryCheck()

    def F_Nome_C(self, *args):
        global Nome_Corsa
        return Nome_Corsa

    def Check_Nome_C(self, *args):
        global Nome_Corsa
        if (self.ids.Input_C.text == Nome_Corsa):
            self.ids.Button_Save_C.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_C.background_color=(1, 0, 0, .75)

    def Save_C(self, *args):
        global Nome_Corsa
        Nome_Corsa = self.ids.Input_C.text
        self.ids.Button_Save_C.background_color=(0, 1, 0, .75)

    def F_Nome_1(self, *args):
        global Nome_Macchina_1
        return Nome_Macchina_1

    def F_Nome_2(self, *args):
        global Nome_Macchina_2
        return Nome_Macchina_2

    def F_Nome_3(self, *args):
        global Nome_Macchina_3
        return Nome_Macchina_3

    def Check_Nome_1(self, *args):
        global Nome_Macchina_1
        if (self.ids.Input_N1.text == Nome_Macchina_1):
            self.ids.Button_Save_N1.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N1.background_color=(1, 0, 0, .75)

    def Check_Nome_2(self, *args):
        global Nome_Macchina_2
        if (self.ids.Input_N2.text == Nome_Macchina_2):
            self.ids.Button_Save_N2.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N2.background_color=(1, 0, 0, .75)

    def Check_Nome_3(self, *args):
        global Nome_Macchina_3
        if (self.ids.Input_N3.text == Nome_Macchina_3):
            self.ids.Button_Save_N3.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N3.background_color=(1, 0, 0, .75)

    def Save_N1(self, *args):
        global Nome_Macchina_1
        Nome_Macchina_1 = self.ids.Input_N1.text
        self.ids.Button_Save_N1.background_color=(0, 1, 0, .75)

    def Save_N2(self, *args):
        global Nome_Macchina_2
        self.ids.Button_Save_N2.background_color=(0, 1, 0, .75)
        Nome_Macchina_2 = self.ids.Input_N2.text

    def Save_N3(self, *args):
        global Nome_Macchina_3
        self.ids.Button_Save_N3.background_color=(0, 1, 0, .75)
        Nome_Macchina_3 = self.ids.Input_N3.text
    pass

class ColourScreen(Screen):
    colour = ListProperty([1., 0., 0., 1.])

class MyScreenManager(ScreenManager):
    def new_Error_screen(self):
        name = str(time.time())
        s = Error(name=name)
        self.add_widget(s)
        self.current = name
    pass

class MoreOptions(Screen):

    def GetTc(self, *args):
        global Ser_Tc
        return str(Ser_Tc)

    def SaveTc(self, *args):
        global Ser_Tc
        try:
            Ser_Tc = int(self.ids.Tc_In.text)
        except:
            Ser_Tc = Ser_Tc
            self.ids.Tc_In.txt = str(Ser_Tc)
    pass

class WIP(Screen):
    pass

class root_widget(Widget):
    pass

class SemaphApp(App):
    pass



SemaphApp().run()
