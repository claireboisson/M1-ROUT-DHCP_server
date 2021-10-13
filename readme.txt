### server_DHCP.py ###


Le but du projet est de créer un serveur DHCP capable de répondre aux requêtes DHCP en provenance de machines du même réseau local. 
Pour cela il doit être capable de recevoir les messages Discover et Request et d’y répondre à l’aide des messages Offer et Acknowledgment.

""" ----- SERVER SETTINGS ----- """
Dans cette partie du code, nous retrouvons l’initialisation de la socket UDP afin d’écouter sur le port 67 comme demandé dans le sujet. 
Nous avons aussi l’initialisation de la destination qui est le couple (broadcast, 68).
68 étant le port d’écoute des clients.

""" ----- TESTING ADDRESSES INPUTS ----- """
Dans cette partie du code, nous avons trois fonctions permettant la vérification du bon format des adresses, dont nous discuterons par la suite.
	* testing_network_format()
	* testing_add_format()
	* testing_errors()

""" ----- ADDRESSES INPUTS ----- """
Dans cette partie du serveur nous retrouvons les différents input permettant d’initialiser l’adresse réseau et son masque, ainsi que la gateway et les DNS primaire et secondaire.

	* Pour l’adresse réseau et le masque nous testons le format à l’aide de la fonction  
	testing_network_format(). 
	Dans celle-ci nous vérifions que le format correspond bien à X.X.X.X/X à l’aide des expressions régulières. 
	Si le format est incorrect, l’utilisateur peut retenter sa chance à l’aide d’un nouvel input.
	exemple : 192.168.0.0.0/24 ; 192.168.0.0 ; 192.168.0.0/24.0 sont fausses
	Ensuite, nous vérifions qu’il s’agit bien d’une adresse réseau et de la conformité du masque à l’aide de la fonction testing_errors(), 
	celle-ci lève une exception lors d’une mauvaise entrée et le serveur fait un exit(-1). 
	exemple : 192.168.0.0/34 ; 256.0.0.0/8 ; 192.168.0.1/24 sont fausses.

	* De la même manière, nous vérifions le format X.X.X.X pour la gateway et les DNS primaire et secondaire à l’aide de la fonction testing_add_format(). 
	Si le format est incorrect, l’utilisateur peut retenter sa chance à l’aide d’un nouvel input.
	Nous vérifions aussi la conformité des adresses avec testing_errors().
	exemple : 192.168.0.256 est fausse

	* De plus, pour la gateway, nous effectuons une vérification supplémentaire. 
	En effet, nous vérifions à l’aide de la fonction hosts() de la bibliothèque ipaddress, que la gateway se trouve bien dans la plage d’adresse du réseau.

Dans cette partie nous créons aussi un input pour initialiser le bail et nous vérifions que ce bail est bien un nombre entier.

De plus, nous créons une liste et deux dictionnaires : 

	* la liste available_add qui, à l’aide de la fonction hosts(), va contenir toutes les adresses IP du réseau sous format string, 
	mais en évitant d’y ajouter l’adresse de la gateway et des DNS.
	* Nous avons ensuite deux dictionnaires, add_currently_used qui aura pour clé l’adresse MAC et comme valeur une liste contenant l’adresse IP attribuée 
	et la date de fin du bail à l’aide de datetime. 
	Ce dictionnaire a pour but de garder en mémoire les adresses IP en cours d’utilisation.
	* Le deuxième dictionnaire est add_mac_mem qui aura pour clé l’adresse MAC et comme valeur l’adresse IP. 
	Il aura pour but de se souvenir des adresses IP offertes afin de les offrir de nouveau aux même clients, si celles-ci sont disponibles.


""" ----- ADDRESSES AND LEASE TIME MANAGEMENT FUNCTIONS ----- """
Dans cette partie du code nous avons trois fonctions qui gèrent le choix de l’adresse IP pour les clients et leurs bails.

	* lease_time() : cette fonction prend en argument le bail précédemment initialisé. A l’aide de la bibliothèque datetime, 
	elle retourne la date de fin du bail en faisant la somme de la date actuelle avec le bail.

	* update_time() : cette fonction prend en argument les dictionnaires add_currently_used, add_mac_mem et la liste available_add 
	et a pour but la mise-à-jour des adresses IP en fonction du bail.
	Ainsi, elle vérifie pour chaque clé de add_currently_used si la date du bail est inférieure à la date actuelle. 
	Si tel est le cas, alors la liste available_add ajoute l’adresse IP qui était utilisée et le dictionnaire add_currently_used supprime la clé.
	De plus, avant l’ajout dans available_add, la fonction vérifie si la clé de add_currently_used se trouve bien dans le dictionnaire mémoire, add_mac_mem. 
	Si ce n’est pas le cas, alors on l’ajoute avec en valeur son IP courante.

	* offer_ip_selection() : cette fonction prend en argument l’adresse MAC, le bail et les dictionnaires et la liste (add_currently_used, add_mac_mem, available_add). 
	Elle a pour but d’offrir et de renvoyer une adresse IP.
	Tout d’abord elle appelle update_time() et lease_time().
	Si l’adresse MAC n’est pas connue d’aucun des dictionnaires, alors on lui propose la première adresse IP libre de la liste. 
		Ainsi, on la supprime de available_add, et on ajoute la MAC et son IP dans add_mac_mem, et aussi son bail dans add_currently_used.
	Sinon, si l’adresse MAC se trouve dans add_currently_used alors on retourne l’IP qui lui avait été assignée et on renouvelle son bail. 
		On vérifie que l’adresse IP ne se trouve pas dans la liste des IP disponibles et que le couple MAC/IP se trouve bien dans la mémoire, add_mac_mem.
	Autre cas du sinon, si l’adresse MAC se trouve dans la mémoire mais pas dans add_currently_used. 
		Alors on vérifie tout d’abord que son ancienne IP est bien dans la liste des adresses IP libres puis on la lui offre. 
		Si son ancienne adresse IP est indisponible, on lui offre la première adresse disponible de la liste available_add.


""" ----- FUNCTIONS FOR MANAGING THE DATA RECEIVED ----- """
Dans cette partie du code nous avons deux fonctions qui gèrent la découverte des informations importantes des messages reçus provenant des clients.

	* search_message_type() : Cette fonction prend les données reçues en argument et a pour but de trouver l’option numéro 53 de DHCP, 
	afin d’identifier le type de message (discover ou request) et de le retourner. 
	De plus elle retourne l’adresse MAC, le numéro de transaction, et l’adresse IP du client (en cas de renouvellement de bail, l’IP est différente de 0.0.0.0).

	* request_requested_ip() : Cette fonction prend les données reçues d’un message request en argument. 
	Elle permet de trouver l’option numéro 50, contenant l’adresse IP demandée par le client. Ainsi, elle retourne l’adresse IP demandée.


""" ----- FUNCTIONS THAT MANAGES THE DATA TO BE SENT ----- """
Dans cette partie du code, nous avons deux fonctions permettant de créer les messages à l’attention des clients.

	* add_ip_in_hexa() : Cette fonction prend en paramètre une adresse IP au format string et elle permet de la convertir en format bytes.

	* server_message() : Cette fonction prend en paramètre l’adresse IP offerte, l’adresse IP du client (trouvée à l’aide de search_message_type()), 
	la transaction, l’adresse MAC, l’adresse du réseau, de la gateway, du DNS primaire, du serveur DHCP, le bail ainsi que le type du message reçu.
	Cette fonction permet de construire le message à renvoyer au client, la seule différence entre le message offer et ack 
	est l’option numéro 53 qui est définie en fonction du type de message reçu de la part du client.
	Ensuite, nous convertissons toutes les adresses mises en paramètres en bytes et nous formons le message.


""" ----- FUNCTIONS FOR THE SERVER ----- """
Dans cette partie du code, nous avons deux fonctions permettant de gérer le serveur.

	* handle_client() : Cette fonction prend en paramètre les données reçues en provenance du client. 
	Tout d’abord elle appelle search_message_type() afin d’obtenir l’adresse MAC, la transaction, l’IP du client et le type du message.

	Si le message a pour type “1” :
		* On ouvre le fichier logging.txt pour garder une trace.
		On y écrit le type de message, la date, l’adresse MAC et la transaction.
		* Ensuite on appelle update_time(), pour être sûr de la mise à jour des adresses IP.
		* On appelle offer_ip_selection() afin de trouver une adresse IP à proposer. Et on forme le message "Offer" à l’aide de server_message() pour ensuite l'envoyer au client. 
		On inscrit cette étape dans le fichier logging.txt
 	Si le message a pour type “3” :
		* On appelle d’abord la fonction request_requested_ip(), afin d’obtenir l’adresse IP demandée.
		* Ensuite on appelle update_time(), pour être sûr de la mise à jour des adresses IP.
		* On appelle offer_ip_selection() afin de trouver une adresse IP à proposer.
		* Si l’adresse IP proposée est la même que celle demandée ou que l’adresse IP proposée est la même que l’adresse IP du client :
   			* On ouvre le fichier logging.txt pour garder une trace.
			On y écrit le type de message, la date, l’adresse MAC et la transaction.
			* Puis, on forme le message “Ack” à l’aide de server_message() pour ensuite l'envoyer au client. On inscrit cette étape dans le fichier logging.txt
		* Sinon : 
   			* On précise dans logging.txt le message Request reçu et on ajoute aussi le fait que le client n’a pas accepté notre offre.
   			* Ainsi, nous supprimons la clé correspondant à l’adresse MAC dans les dictionnaires add_currently_used et add_mac_mem 
			et on pense à remettre l’adresse IP qui a été proposée dans la liste des adresses libres, available_add.


	* handle_info() : Cette fonction prend en paramètre les données reçues ainsi que le couple (adresse, port) du client.
	Cette fonction a pour but de gérer les requêtes envoyées par le fichier “client_info.py”.
	Ainsi, en fonction du numéro envoyé (1,2,3) soit le serveur renvoie au client la liste des adresses IP libres (available_add), 
	soit les adresses IP en cours d’utilisation avec l’adresse MAC et le bail (add_currently_used), soit les couples MAC/IP en mémoire du serveur (add_mac_mem).

Pour finir le serveur tourne en continue avec un “while True”, et si la longueur des données reçues est supérieure à 50, alors on appelle la fonction handle_client(), 
car il s’agit d’un message d’un client. 
Sinon, cela correspond à notre faux client, client_info.py, permettant d’afficher les informations, dont l’écoute se fait sur le port “1234”. 
Ainsi, nous appelons la fonction handle_info().


### client_info.py ###
Dans ce code, nous trouvons un faux client écoutant sur le port “1234”. Il propose différents input en fonction des envies de l’utilisateur.
Il demande au “server_DHCP.py” les différentes informations demandées puis les affiches.
Il propose à l’utilisateur de soit poursuivre s’il veut voir autre chose soit de fermer le programme.