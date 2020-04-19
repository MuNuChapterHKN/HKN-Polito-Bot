Struttura e funzionamento del bot 
=================================

All'avvio del bot, dopo un messaggio di benvenuto, compaiono due bottoni per la scelta della lingua, consentendo l'utente di scegliere se utilizzare il bot in italiano o in inglese. Dopodiché viene costruita la tastiera, tramite la quale l'utente interagisce. In particolare, essa è composta da 8 ReplyKeyboardMarkup (bottoni della custom keyboard):

-   Events (Eventi)

-   News (Notizie)

-   Study Groups (Gruppi di studio)

-   Ask us something (Facci una domanda)

-   About (Chi siamo)

-   Subscribe to our Newsletter (Iscriviti alla Newsletter)

-   Drive

-   Contacts

Ognuno di questi è collegato, tramite opportuni handler (CommandHandler, per dare comandi testuali che iniziano con '/', e MessageHandler, per impartire comandi tramite i bottoni), ad una funzione che permette di gestirne il funzionamento. Vediamoli nel dettaglio.

Events 
------

L'handler che gestisce gli Eventi è la funzione *displayEvents(bot, update)*. Essa utilizza la funzione *load\_events(update)* per caricare gli eventi dal relativo file `events.json`, dopodiché mostra a schermo solo gli eventi imminenti del chapter, non quelli passati.

News 
----

L'handler che gestisce le Notizie è la funzione *fetch\_news(bot,
update)*. Essa ottiene direttamente i dati dal sito
<https://hknpolito.org>, in particolare mostra a schermo le ultime 3 news ottenute dalla sezione "Latest News" del sito.

Study Groups 
------------

L'handler che gestisce la sezione 'Gruppi di studio' è la funzione *tutoring(bot, update)* che si trova nel file `tutor.py`. Essa ottiene le informazioni necessarie dal sito <https://hknpolito.org/tutoring>, mostrando a schermo gli eventuali gruppi di studio presenti.

Ask us something 
----------------

L'handler che gestisce la sezione 'Facci una domanda' è differente rispetto a tutti gli altri, il più complesso. Infatti, esso è un ConversationalHandler, il cui entry point è dato da due possibili handler: Message Handler, se clicchiamo sul bottone "Ask us something", o Command Handler, se scriviamo in maniera testuale */questions*. A questo punto è possibile scrivere la domanda e non appena premiamo il tasto invio, partirà l'handler atto a gestire la risposta. Quest'ultimo andrà a scrivere la domanda sul file `questions.txt` e la invierà **soltanto agli admin** (che si trovano su un file `admins.txt`),
cosicché essi la potranno leggere e iniziare a pensare ad una risposta. Gli admin possono ora effettuare diverse azioni, gestite da un ulteriore ConversationalHandler, il cui entry point è dato dal Command Handler */reply*:

-   Scrivere direttamente la risposta (Message Handler) e premere invio. In questo modo partirà la funzione *answer\_question(bot, update)*, la quale, dopo aver rimosso la domanda dal file `questions.txt` (tramite la funzione *pop\_question()*), invia la risposta **solo all'utente che ha fatto la domanda**.

-   Utilizzare la parola chiave */skip*, da cui partirà il Command Handler *skip(bot, update)*, che permetterà di saltare la domanda (di fatto sposterà la domanda alla fine del file `questions.txt`), in maniera tale da rispondere ad essa in un secondo momento.

-   Utilizzare la parola chiave */delete*, da cui scatterà il Command Handler *delete\_question(bot, update)*, il quale semplicemente rimuoverà la domanda dal file `questions.txt`.

-   Utilizzare la parola chiave */save*, da cui verrà lanciato il
    Command Handler *save\_question(bot, update)*, che consentirà di salvare la domanda in un file chiamato `savedquestions.txt`.

-   Utilizzare la parola chiave */cancel*, per stoppare il
    ConversationalHandler, e quindi abbandonare la conversazione.

Inoltre, in ogni momento, **gli admin** possono conoscere quali sono le domande salvate e quelle a cui si deve ancora rispondere, tramite due parole chiave che scateneranno i rispettivi Command Handler: */showsaved* e */showpending*, rispettivamente. Il primo mostrerà a schermo tutte le domande che sono state salvate in precedenza (leggendole dal file `savedquestions.txt`), mentre il secondo mostrerà tutte le domande a cui non si è ancora risposto (leggendole dal file `questions.txt`).

About
-----

L'handler che gestisce la sezione 'Chi siamo' è la funzione *about(bot, update)*. Essa banalmente mostra a schermo le informazioni relative al chapter HKN (leggendole in corrispondenza alla key 'abouttext' dal file `it.json` o `en.json`, a seconda della lingua scelta).

Subscribe to our newsletter
---------------------------

L'handler che gestisce l'iscrizione alla newsletter è la funzione
*display\_newsletterSubscription(bot, update)*. Essa mostra due
InlineKeyboardButton, uno per annullare l'operazione e un altro per confermare. Se viene premuto il tasto di conferma, allora viene inserito lo userID nel database, che tiene traccia di tutti gli utenti iscritti alla newsletter. Ovviamente verrà inviato un messaggio di errore se l'utente era già iscritto alla newsletter. A questo punto gli admin, quando lo desiderano, possono inviare la newsletter a tutti gli iscritti, tramite la funzione *sendNewsletter(bot, update)*, che verrà lanciata dopo aver inserito la parola chiave */sendnewsletter*. Questa funzione invierà, ad ogni utente iscritto alla newsletter, il messaggio corrispondente, leggendolo dal file `newsletter.json`.

Drive
---------------------------

L'handler che gestisce il drive hkn è la funzione
*display\_drive(bot, update)*. Essa stampa all'utente il link cliccabile del sito HKN nella sezione Drive (<https://hknpolito.org/drive/>), leggendolo dal file  `en.json` o  `it.json` in base alla lingua selezionata.

Contacts
---------------------------
L'handler che gestisce la sezione 'Contatti' è la funzione *contact(bot, update)*. Essa mostra all'utente le informazioni relative ai contatti email, facebook e in instagram di HKN, traendole direttamente dalla key 'contacttext' nei file `it.json` o `en.json` in relazione alla lingua selezionata.

#### 
&nbsp;
####

Infine, oltre alle ReplyKeyboardMarkup (bottoni della custom keyboard), sono presenti degli "Inline button", ovvero dei bottoni non fisicamente presenti sulla tastiera del bot, ma ridisegnati al momento, sotto un testo all'interno del corpo del messaggio. Essi sono i seguenti:

-   <ins>Back</ins>: per annullare l'ultima operazione

-   <ins>Confirm</ins>: per confermare l'iscrizione alla newsletter

-   <ins>Unsubscribe</ins>: per annullare l'iscrizione alla
    newsletter

-   <ins>Lang:it</ins> : per scegliere la lingua italiana, all'avvio
    del bot

-   <ins>Lang:en</ins> : per scegliere la lingua inglese, all'avvio
    del bot

Problemi attuali e possibili soluzioni 
======================================

Problemi generali (minimali)
----------------------------

-   Se premo sull'inline button 'Back' compare un orologio per qualche secondo sul tasto stesso, anche se il messaggio viene inviato subito. Dipenderà dal server? Questa cosa non succede solo con 'Back' ma con altri, forse tutti.\
   **Possibile soluzione** (bruta): non far comparire del tutto l'orologio (se possibile), tanto il messaggio viene mandato
    immediatamente.\
    **Tempo stimato**: *fattibile in 1/2 settimane, se si riesce a capire come far scomparire l'orologio*

Problemi riscontrati nella sezione 'Ask us something'
-----------------------------------------------------

Nessun problema riscontrato in questa sezione.

Problemi riscontrati nella newsletter
-------------------------------------

Nessun problema riscontrato in questa sezione. 

Possibili implementazioni future 
================================

-   Organizzazione in cartelle del bot: gestire il bot in più file, nello specifico dividere il file principale `hkn_bot.py` in 2 file, almeno per adesso: uno che gestisce i vari handler (per gli users) e uno che gestisce le varie funzioni che possono usare soltanto gli admin. Per adesso non è un grossissimo problema in quanto il file non è troppo grande (circa 500 righe di codice), ma potrebbe esserlo se si ha intenzione di inserire ulteriori funzionalità al bot. Si potrebbero inoltre creare due cartelle separate, una per i documenti *.txt* (utilities) e una per i documenti *.py* (source code).

-   Tastiera differente per gli admin (es. per risposta alle domande), al posto di usare i Command Handler.
