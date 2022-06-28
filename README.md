# Slotherizer

**Slotherizer** permette di non perdere alcuna novità nei canali testuali presenti nei server Discord dove si possono ritrovare un gran numero di utenti, grazie ai riassunti automatici generati con GPT-3.

## Come iniziare
1. Avrai bisogno di un bot Discord da collegare al sistema, creane uno nuovo seguendo questa [guida](https://www.ionos.it/digitalguide/server/know-how/creare-un-bot-su-discord/)
   
   Servirà il ***Token*** del bot da inserire nella configurazione del Sistema (Controlla questa [guida](https://www.writebots.com/discord-bot-token/))
2. Avrai bisogno anche di un account [OpenAI](https://openai.com/api/) per utilizzare le api basate su GPT-3
   
   Serviranno
   - l'***Organization ID*** (Che troverai in questa [pagina](https://beta.openai.com/account/org-settings))
   - l'***API Key*** (Che troverai in questa [pagina](https://beta.openai.com/account/api-keys))
3. Creare il file di configurazione delle variabili d'ambiente `.env` nella root del progetto
   ```
   DISCORD_TOKEN="<Token>"
   ORGANIZATION="<Organization ID>"
   OPENAI_API_KEY="<API Key>"
   ```
4. Esegui un `docker-compose up` per buildare ed avviare **Slotherizer**

## Come utilizzarlo
Per utilizzare il **bot Discord** dovrai prima *invitarlo* nel tuo **server Discord** (Segui questa [guida](https://www.writebots.com/discord-bot-token/#5_add_your_bot_to_a_discord_server)).

Quando il bot è in un server, nelle chat testuali si potrà invocare il bot tramite il comando `!slotherizer <n>` inserendo al posto di `<n>` il numero di messaggi che vuoi riassumere.

## Metriche
In questo progetto usiamo Kibana per visualizzare le metriche di utilizzo del sistema, è presente una versione di default che si può importare su kibana non'appena si avvia che fornisce una dashboard con alcune metriche utili: `kibana/monitoring.ndjson`
