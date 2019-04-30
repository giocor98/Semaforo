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

#define soglia 7

//Funzine che legge la seriale per i comandi e li esegue.
void HandleMessage();

//Funzione che regola il funzionamento del Semaforo.
void Semaforo();


//Variabili che contengono il momento di lettura del sensore
unsigned long int TF[3];

//Variabile che contiene l'istante dal quale parto a controllare
unsigned long int TI = 0;




int Detect(int To);

//Variabili per la gestione dei sensori
int PinLedPista[3];
int PinSensPista[3];
bool PistaSel[3];
int Av_Pista[3];
int Max_Pista[3];
int Min_Pista[3];

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
  PreparaSensori();
  delay(1000);

  // Accende il Rosso
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Red"
  Serial.println("R");

  //Aspetta 1 secondo
  //TODO: Effettuare i controlli inquesto secondo sui sensori
  PreCheck(1000, 0);

  // Accende il giallo
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Yellow"
  Serial.println("Y");

  //Aspetta 1 secondo
  //TODO: Effettuare i controlli inquesto secondo sui sensori
  PreCheck(1000, 1);

  // Accende il Verde
  digitalWrite(GREEN, HIGH);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Green"
  Serial.println("G");

  //Imposta il tempo di partenza
  TI = micros();

  // Inizia la rilevazione dei sensori per detectare il passaggio delle macchinine.
  for(int i=0; i<3; i++){
    //Controlla i sensori
    Fast_Detect(10000);

    //Printa il risultato dei sensori:
    if (PrintRes()==0){
      break;
    }
  }  

  //Rilascia i sensori
  RilasciaSensori();  
}

//Funzione che prepara i sensori (accende i led)
//In : null
//Out: null
void PreparaSensori(){
  for (int i=0; i<3; i++){
    if (PistaSel[i]){
      digitalWrite(PinLedPista[i], HIGH);
    }
  }
}

//Funzione che prepara i sensori per essere controllati
//In: t int numero di millisecondi che deve durare il controllo
//    mode 0 se deve aggiornare gli stati iniziali, 1 se deve controllare se i valori rimangono nei valori fissati precedentemente
//Out: 0 se tutto ok, altro altrimenti
char PreCheck(int t, int mode){
  int n_cicli;
  unsigned long int t_fin = millis() + t;
  int j, i, tmp;
  unsigned long int sum[3];

  sum[0] = 0;
  sum[1]= 0;
  sum[2] = 0;

  if (mode == 0){
    n_cicli = 0;
  }else{
    n_cicli = 1;
  }
  //Accende i led, se non sono ancora accesi
  PreparaSensori();
  //inizio il controllo
  while (millis() < t_fin){
    for (j = 0; j<4; j++){
      for (i=0; i<3; i++){
        if (PistaSel[i]){
          tmp = analogRead(PinSensPista[i]);
          if(n_cicli == 0){
            Av_Pista[i] = tmp;
            Max_Pista[i]=tmp;
            Min_Pista[i] = tmp;
          }else{
            if ((tmp > Av_Pista[i]+soglia)||(tmp<Av_Pista[i]-soglia)){
              Serial.println("Errore");
              Serial.println(n_cicli);
              Serial.print(Av_Pista[i]);
              Serial.print(" - ");
              Serial.println(tmp);
              return 1;
            }else{
              sum[i] += tmp;
              Av_Pista[i] = sum[i]/n_cicli;
              if(tmp>Max_Pista[i]){
                Max_Pista[i]= tmp;
              }else if(tmp<Min_Pista[i]){
                Min_Pista[i] = tmp;
              }
            }
          }
        }
      }
      n_cicli++;
    }
  }
  Serial.println("Fine_Check");
  for(i = 0; i<3; i++){
    Av_Pista[i] = sum[i]/n_cicli;
    Serial.print("m:");
    Serial.print(Min_Pista[i]);
    Serial.print("e:");
    Serial.print(Av_Pista[i]);
    Serial.print("M:");
    Serial.println(Max_Pista[i]);
  }
  Serial.println(n_cicli);
  return 0;
}

//Funzione che Resetta i Sensori
//In : null
//Out: null
void RilasciaSensori(){
  for (int i=0; i<3; i++){
    PistaSel[i] = false;
    digitalWrite(PinLedPista[i], LOW);
  }
}

//N_di cicli che esegue il codice
#define N_CICLI_INTERNI 512

//Funzione per un Detect piu' veloce (si spera)
// In: To int con numero di millisecondi di timeout
// Out: 
void Fast_Detect (int To){
  //Variabile con il tempo in cui la funzione è costretta a ritornare;
  unsigned long int t_fin = millis()+To;
  //Variabile temporanea per la lettura dei sensori
  int tmp;
  //Variabile che contiene il numero di piste da controllare
  int n_piste = 0;
  //Variabili per il tempo
  unsigned long int T1 [3], T2[3];
  //Booleano che indica il modo della pista: true se i parametri sono nella norma, false altrimenti
  bool mod[3];
  //Booleano che indica se i parametri attuali sono o meno nella norma
  bool iR, PistaToCheck[3];
  //Variabili di supporto
  int i, j;

  //Inizializzo il numero di piste e i paramtri delle piste
  for(i=0; i<3; i++){
    TF[i] = 0;
    PistaToCheck[i] = false;
    if (PistaSel[i]){
      n_piste ++;   //Aggiorna numero di piste da controllare

      //Aggiorna i parametri delle piste
      Max_Pista[i] = (Av_Pista[i] + soglia);
      Min_Pista[i] = (Av_Pista[i] - soglia);
      mod[i] = true;
      PistaToCheck[i] = true;
    }
  }
    
  //Finchè non va in timeout e ci sono piste da controllare  
  while (millis()<t_fin){
    for(j=0; j<N_CICLI_INTERNI; j++){
      //Ciclo su tutte le piste
      for(i=0;i<3;i++){
        //Se la pista non è selezionata ripeti il ciclo
        if (PistaToCheck[i] == true){
          //Leggo il sensore
          tmp = analogRead(PinSensPista[i]);
          //Calcolo se la lettura è nel range
          iR = ((tmp<Max_Pista[i])&&(tmp>Min_Pista[i]));
  
           //Se la iR e il mod della pistaa non sono concordi, allora è cambiata la situazione della pista
          if(mod[i] != iR){
            if(iR){
              PistaToCheck[i] = false;
              TF[i] = micros();
              n_piste --;
              if(n_piste == 0){
                return;
              }
            }
            mod[i] = iR;
          }
        }
      }
    }
  }
}

//Funzione che Printa i risultati dei sensori
//In : null
//Out : if 3*To then 0, else 1
int PrintRes(){
  int c = 0;
  Serial.println("D:");
  for(int i = 0; i<3; i++){
    Serial.print(i);
    Serial.print(" : ");
    if (TF[i] > 0){
      Serial.println(TF[i] - TI);
    }else{
      Serial.println("To");
      c++;
    }
  }
  if(c>=3){
    return 0;
  }
  return 1;
}
