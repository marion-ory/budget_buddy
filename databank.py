import mysql.connector
from config import get_connection


def setup_database():
    """Fonction qui initialise toute la structure de la base de données"""
    try:
        # 1. Connexion initiale pour s'assurer que la base existe
        temp_cnx = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=3306,  # Si tu es sur MAMP, vérifie s'il faut mettre 8889
        )
        curseur = temp_cnx.cursor()
        curseur.execute("CREATE DATABASE IF NOT EXISTS databank")
        temp_cnx.close()

        # 2. Connexion officielle via ta config
        cnx = get_connection()
        if not cnx:
            return

        curseur = cnx.cursor()
        curseur.execute("USE databank")

        # --- CREATION DES TABLES ---
        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS User(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_banquier INT NULL,
                Nom VARCHAR(255),
                Prenom VARCHAR(255),
                Email VARCHAR(255) UNIQUE,
                Adresse VARCHAR(255),
                MDP VARCHAR(255),
                Role ENUM('Client', 'Banquier'),
                FOREIGN KEY (ID_banquier) REFERENCES User(ID)
            )
        """
        )

        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS Compte(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_User INT,
                Solde DECIMAL(15,2),
                Type ENUM('Courant', 'Annexe'),
                FOREIGN KEY (ID_User) REFERENCES User(ID)
            )
        """
        )

        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS Categorie(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Nom VARCHAR(255) UNIQUE
            )
        """
        )

        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS `Transaction`(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_Categorie INT,
                Description VARCHAR(255),
                Montant DECIMAL(15,2),
                Date DATE,
                Type ENUM('Depot', 'Retrait', 'Transfert'),
                ID_Emetteur INT,
                ID_Beneficiaire INT,
                FOREIGN KEY (ID_Emetteur) REFERENCES Compte(ID),
                FOREIGN KEY (ID_Beneficiaire) REFERENCES Compte(ID),
                FOREIGN KEY (ID_Categorie) REFERENCES Categorie(ID)
            )
        """
        )

        # --- INSERTION DES DONNÉES PAR DÉFAUT ---
        categories = [
            "Alimentaire",
            "Vie quotidienne",
            "loisirs",
            "Véhicule",
            "Energie",
            "Logement",
            "Epargne",
        ]
        for cat in categories:
            curseur.execute("INSERT IGNORE INTO Categorie(Nom) VALUES(%s)", (cat,))

        banquiers_data = [
            (
                "Lupin",
                "Arsène",
                "a.lupin@databank.fr",
                "12 Rue de la Paix, Paris",
                "password123",
                "Banquier",
            ),
            (
                "Deschamps",
                "Didier",
                "d.deschamps@databank.fr",
                "45 Avenue des Bleus, Lyon",
                "worldcup2018",
                "Banquier",
            ),
        ]

        query_user = "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for b in banquiers_data:
            curseur.execute(query_user, (b[0], b[1], b[2], b[3], b[4], b[5], None))

        cnx.commit()

        # Récupération des IDs Banquiers pour les clients
        curseur.execute("SELECT ID FROM User WHERE Role = 'Banquier' LIMIT 2")
        banquiers = curseur.fetchall()

        if len(banquiers) >= 2:
            ID_Banquier1 = banquiers[0][0]
            ID_Banquier2 = banquiers[1][0]

            clients_data = [
                (
                    "Michel",
                    "Rostain",
                    "michel.rostain@laplateforme.io",
                    "43 rue Neuve Sainte Catherine, 13007 Marseille",
                    "azerty",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Durand",
                    "Marie",
                    "durand.marie@mail.com",
                    "5, rue Verte, Nantes",
                    "pass1",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Lefebvre",
                    "Thomas",
                    "t.lefe@mail.com",
                    "12 Bis Rue du Port, Bordeaux",
                    "pass2",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Moreau",
                    "Camille",
                    "c.moreau@mail.com",
                    "88 Av de la Liberté, Lille",
                    "pass3",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Petit",
                    "Nicolas",
                    "n.petit@mail.com",
                    "3 Square du Bois, Nice",
                    "pass4",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Rousseau",
                    "Julie",
                    "j.rousseau@mail.com",
                    "101 Route de Brest, Rennes",
                    "pass5",
                    "Client",
                    ID_Banquier1,
                ),
                (
                    "Blanc",
                    "Kevin",
                    "k.blanc@mail.com",
                    "14 Rue du Lac, Annecy",
                    "pass6",
                    "Client",
                    ID_Banquier2,
                ),
                (
                    "Garnier",
                    "Sophie",
                    "s.garnier@mail.com",
                    "22 Rue des Fleurs, Toulouse",
                    "pass7",
                    "Client",
                    ID_Banquier2,
                ),
                (
                    "Faure",
                    "Julien",
                    "j.faure@mail.com",
                    "9 Rue de l'Eglise, Marseille",
                    "pass8",
                    "Client",
                    ID_Banquier2,
                ),
                (
                    "Andre",
                    "Lea",
                    "l.andre@mail.com",
                    "67 Rue de la Paix, Strasbourg",
                    "pass9",
                    "Client",
                    ID_Banquier2,
                ),
                (
                    "Mercier",
                    "Lucas",
                    "l.mercier@mail.com",
                    "34 Bd Gambetta, Grenoble",
                    "pass10",
                    "Client",
                    ID_Banquier2,
                ),
            ]

            for c in clients_data:
                curseur.execute(query_user, c)

            cnx.commit()

        print("Base de données initialisée avec succès.")
        curseur.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Erreur lors de l'initialisation : {err}")
