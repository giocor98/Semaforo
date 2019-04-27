from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout

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

Nome_Macchina_1 = "Macchina_1"
Nome_Macchina_2 = "Macchina_2"
Nome_Macchina_3 = "Macchina_3"
Nome_Corsa = "Corsa"

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
        return Nome_Macchina_1

    def F_Nome_2(self, *args):
        global Nome_Macchina_2
        return Nome_Macchina_2

    def F_Nome_3(self, *args):
        global Nome_Macchina_3
        return Nome_Macchina_3

    def Counter(self, *args):
        global T
        global ErrorDesc
        global ser
        global STo
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

    def Start(self, *args):
        global ser
        global T
        global ErrorDesc
        global STo
        if CheckSer() == 0:
            print("Errore nell'apertura della seriale con lo start")
            ErrorDesc = "Non riesco ad aprire la seriale con lo start"
            self.parent.new_Error_screen()
            return
        while (ser.in_waiting >0):
            ser.read()
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



    def Stop(self, *args):
        Clock.unschedule(self.Counter)
        self.ids.stop_button.color = (1, 0, 0, 1)
        self.ids.settings_button.color= (0, 1, 0, 1)
        self.ids.start_button.color = (0, 1, 0, 1)

    pass

class Impostazioni(Screen):

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

class WIP(Screen):
    pass

class root_widget(Widget):
    pass

class SemaphApp(App):
    pass

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

SemaphApp().run()
