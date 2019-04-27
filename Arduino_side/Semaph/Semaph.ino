#define GREEN 2
#define YELLOW 3
#define RED 4
#define MAX_MSGLEN 25

//Funzine che legge la seriale per i comandi e li esegue.
void HandleMessage();

//Funzione che regola il funzionamento del Semaforo.
void Semaforo();


void setup() {

  //Inizializzo i pin del semaforo
  pinMode(GREEN, OUTPUT);
  pinMode(YELLOW, OUTPUT);
  pinMode(RED, OUTPUT);

  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, LOW);
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
