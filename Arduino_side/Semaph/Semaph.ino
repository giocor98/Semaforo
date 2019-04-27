#define GREEN 2
#define YELLOW 3
#define RED 4
#define MAX_MSGLEN 25

#define LED_P_0 8
#define LED_P_1 9
#define LED_P_2 10

#define SENS_P_0 A1
#define SENS_P_1 A2
#define SENS_P_2 A3

//Funzine che legge la seriale per i comandi e li esegue.
void HandleMessage();

//Funzione che regola il funzionamento del Semaforo.
void Semaforo();

//Variabili per la gestione dei sensori
int PinLedPista[3];
int PinSensPista[3];
bool PistaSel[3];

void setup() {

  //Inizializzazione delle variabili dei pin
  PinLedPista[0] = LED_P_0;
  PinSensPista[0] = SENS_P_0;
  PinLedPista[1] = LED_P_1;
  PinSensPista[1] = SENS_P_1;
  PinLedPista[2] = LED_P_2;
  PinSensPista[2] = SENS_P_2;
  PistaSel[0] = false;
  PistaSel[1] = false;
  PistaSel[2] = false;
  
  //Inizializzo i pin del semaforo
  pinMode(GREEN, OUTPUT);
  pinMode(YELLOW, OUTPUT);
  pinMode(RED, OUTPUT);
  pinMode(LED_P_0, OUTPUT);
  pinMode(LED_P_1, OUTPUT);
  pinMode(LED_P_2, OUTPUT);

  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, LOW);
  digitalWrite(LED_P_0, LOW);
  digitalWrite(LED_P_1, LOW);
  digitalWrite(LED_P_2, LOW);
  //Inizializzo la seriale a 115200
  Serial.begin(115200);

}

void loop() {
  //Se c'è qualcosa da leggere sulla seriale allora la leggo
  if (Serial.available()){
    delay(5);
    HandleMessage();
  }
  delay(5);
}

//Funnzione che legge la seriale, interpreta il comando e lo esegue
//In : null
//Out: null
void HandleMessage(){
  int n = MAX_MSGLEN-1;
  char msg[MAX_MSGLEN];
  if(Serial.available()){
    digitalWrite(13, HIGH);
  }else{
    digitalWrite(13, LOW);
  }
  //Leggo i messaggi sulla seriale fino a una lunghezza massima di MAX_MSGLEN caratteri
  while((Serial.available()>0) && (n>0)){
    msg[n] = Serial.read();
    if(msg[n] == '\n'){      
      break;
    }
    n--;
  }
  //Metto il terminatore alla fine del messaggio ricevuto
  msg[n] = 0;

  //Se il messaggio è lungo 1 carattere:
  if (MAX_MSGLEN-n ==2){
    n = MAX_MSGLEN-1;
    //Se è P il messaggio rispondo con A (Ping -> Ack)
    if (msg[n] == 'P'){
      Serial.println("A");
      return;
    }
    //Se è S il messaggio, allora avvio la sequenza del semaforo
    if(msg[n] == 'S'){
      Semaforo();
    }
  }else{
    //Se il Messaggio è di lunghezza maggiore di 1
    n = MAX_MSGLEN-1;
    if(msg[n] == 's'){
      //Se il messaggio ha il primo carattere 's'

      //Imposto tutte le PistaSel a false 
      for (int i=0; i<3; i++){
        PistaSel[i] = false;
      }
      while(msg[n] != 0){
        //Setto a true i soli PistaSel impostati
        if (msg[n] == '0'){
          PistaSel[0] = true;
        }else if (msg[n] == '1'){
          PistaSel[1] = true;
        }else if (msg[n] == '2'){
          PistaSel[2] = true;
        }
        n--;
      }
    }
  }
}

//Funzione che regola il funzionamento del Semaforo.
//In: null
//out: null
void Semaforo(){
  // Setta tutte le luci spente
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, LOW);
  //Invia il messaggio di "Black"
  Serial.println("B");

  //Aspetta 1 secondo
  //TODO: Effettuare i controlli inquesto secondo sui sensori
  delay(1000);

  // Accende il Rosso
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Red"
  Serial.println("R");

  //Aspetta 1 secondo
  //TODO: Effettuare i controlli inquesto secondo sui sensori
  delay(1000);

  // Accende il giallo
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Yellow"
  Serial.println("Y");

  //Aspetta 1 secondo
  //TODO: Effettuare i controlli inquesto secondo sui sensori
  delay(1000);

  // Accende il Verde
  digitalWrite(GREEN, HIGH);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Green"
  Serial.println("G");

  // Inizia la rilevazione dei sensori per detectare il passaggio delle macchinine.
  
}
