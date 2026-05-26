# Claude Leak

## Pièces jointes
- [`memory.dmp.gz`](./files/memory.dmp.gz) (avec `git lfs pull` ou via [release](https://github.com/OPPIDA/DaVinciCTF2026/releases/download/files/memory.dmp.gz))
- [`sqlite-mcp-server.sqlite3`](./files/sqlite-mcp-server.sqlite3)

## Description

### Général
> Les utilisateurs du projet open source `sqlite-mcp-server` ont remarqué que leur fichier de base de données a été chiffré après une mise à jour.  
> Ils ont signalé le problème et, en effet, l’ordinateur du développeur a été compromis.  
> Heureusement, nous avons réussi à effectuer un dump mémoire de sa machine, puisqu’il gardait des outils d’agents LLM en cours d’exécution et ne l’éteignait jamais.

### Partie 1
> Nous soupçonnons qu’un des programmes d’agent LLM exécutés sur son ordinateur est malveillant.  
> Quel est le nom ainsi que le PID du programme malveillant ?

Format du flag : `DVCTF{nom_du_processus:pid}`  
Exemple : `DVCTF{opencode:22222}`

### Partie 2
> L’attaquant semble avoir poussé un script malveillant ayant chiffré des fichiers de base de données.  
> Récupérez la base de données chiffrée. Quelle est la clé de chiffrement utilisée ?

Format du flag : `DVCTF{clé_de_chiffrement_hex}`  
Exemple : `DVCTF{e21e2b95ec0b030eeb29376bfb25ff3f}`

### Partie 3
> L’attaquant semble avoir exécuté des commandes via le programme malveillant.  
> Quelle est l’adresse IP et le port du serveur C2 de l’attaquant ?

Format du flag : `DVCTF{ip:port}`  
Exemple : `DVCTF{192.168.0.1:55555}`