# Projet de programmation d'un serveur DHCP

## 1. Installer le serveur

Pour installer le serveur, il suffit de télécharger les deux fichiers python “ server_DHCP.py ” et “ client_info.py ”.

“ server_DHCP.py ” correspond au serveur

“ client_info.py ” correspond au client permettant d’obtenir et d'afficher des informations sur les adresses IP en cours d’utilisation.


## 2. Utiliser le serveur

Pour utiliser le serveur, il faut tout d’abord ouvrir un terminal, puis se déplacer dans le dossier contenant les fichiers python précédemment téléchargés.

Puis pour lancer le serveur il suffit d’utiliser la commande :

		sudo python3 server_DHCP.py
Ensuite le serveur vous demandera l’adresse réseau et son masque sous le format “ X.X.X.X/X ”.
Il vous demandera également la gateway qui doit être une adresse IP appartenant au réseau et dont le format est “ X.X.X.X ”.
Il vous demandera aussi l’adresse des DNS primaire et secondaire, respectant aussi ce format “ X.X.X.X ”.
Pour finir, il vous demandera également de fournir un bail en seconde.

Lorsque le message “ Server is ready ” s’affiche, le serveur est prêt et peut être utilisé.

Ensuite pour lancer l'affichage des informations, utiliser la commande suivant dans un autre terminal :

		sudo python3 client_info.py
	
Le client vous demandera ce que vous voulez afficher :

* “1” pour afficher les adresses IP libres,
			
* “2” pour afficher les adresses IP en cours d'utilisation,

* “3” pour afficher les couples MAC/IP en mémoire du serveur,

* “4” pour afficher les trois informations précédentes en même temps.
	
Ensuite soit vous cliquez sur “y”, pour poursuivre d'autres affichages

Soit vous cliquez sur “n” pour stopper les affichages et ainsi terminer le programme “client_info.py”.
