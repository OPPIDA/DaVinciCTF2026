# Backdoor

## Pièces jointes
- [`system-images.txz`](./files/system-images.txz) (avec `git lfs pull` ou via [release](https://github.com/OPPIDA/DaVinciCTF2026/releases/download/files/system-images.txz))

## Installation
 
1. Télécharger et installer Android Studio (pensez à bien installer les outils d’émulation et les SDK Android).
2. Dans le dossier d’installation des SDK Android, décompresser le fichier ZIP fourni à cet emplacement.
3. Retourner sur Android Studio et créer un nouvel émulateur via le Device Manager (Tools → Device Manager).
4. Cliquer sur Create Virtual Device.
5. Sélectionner New Device.
6. Sélectionner l’onglet x86 Images, puis cliquer sur Next.
7. Sélectionner la seule image non grisée, puis cliquer sur Next.
8. Nommer l’émulateur comme vous le souhaitez, puis cliquer sur Finish.
9. Démarrer le téléphone depuis le Device Manager : l’installation est terminée.

## Description

### Partie 1: Une application pas comme les autres 
 
> Un ami a des soupçons sur la fiabilité de son téléphone : plusieurs choses étranges s’y sont passées.  
> Malgré l’utilisation d’un code OTP sur tous ses comptes, un hacker a réussi à s’y connecter.  
> Pourriez-vous retrouver de quelle manière ses OTP ont pu être dérobés ?
 
### Partie 2: Mais ou sont passé mes cryptos ?!
 
> Votre ami s’est fait vider son wallet Bitcoin. Il ne comprend pas : il a vérifié toutes les applications installées sur son téléphone, aucune ne semble être à l’origine de cette fraude.  
> Pourriez-vous retrouver la manière dont les hackers se sont connectés à son wallet ?
 
### Partie 3: Tous les chemins mènent à la ROM
 
> Bien que son téléphone ne soit pas rooté, l’application vérolée précédemment analysée a été installée en tant qu’application système.  
> Votre ami craint que la sécurité de son système entier soit compromise.  
> Trouvez la manière dont les attaquants ont pu obtenir des droits privilégiés.