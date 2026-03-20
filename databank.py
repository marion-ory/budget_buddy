import mysql.connector
from config import get_connection
import hashlib
from security import securite_mdp  # On utilise cette fonction pour la cohérence !


def setup_database():
    """Fonction qui initialise toute la structure de la base de données"""
    try:
        # 1. Connexion initiale pour s'assurer que la base existe
        temp_cnx = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=8889,
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
            "CREATE TABLE IF NOT EXISTS Compte (ID INT AUTO_INCREMENT PRIMARY KEY, ID_User INT, Solde DECIMAL(15,2), Type ENUM('Courant', 'Annexe'), FOREIGN KEY (ID_User) REFERENCES User(ID))"
        )
        curseur.execute(
            "CREATE TABLE IF NOT EXISTS Categorie (ID INT AUTO_INCREMENT PRIMARY KEY, Nom VARCHAR(255) UNIQUE)"
        )
        curseur.execute(
            "CREATE TABLE IF NOT EXISTS `Transaction` (ID INT AUTO_INCREMENT PRIMARY KEY, ID_Categorie INT, Description VARCHAR(255), Montant DECIMAL(15,2), Date DATE, Type ENUM('Depot', 'Retrait', 'Transfert'), ID_Emetteur INT, ID_Beneficiaire INT, FOREIGN KEY (ID_Emetteur) REFERENCES Compte(ID), FOREIGN KEY (ID_Beneficiaire) REFERENCES Compte(ID), FOREIGN KEY (ID_Categorie) REFERENCES Categorie(ID))"
        )

        # --- INSERTION DES CATÉGORIES ---
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

        # --- INSERTION DES BANQUIERS ---
        banquiers_data = [
            (
                "Lupin",
                "Arsène",
                "a.lupin@databank.fr",
                "12 Rue de la Paix, Paris",
                securite_mdp("password123", "a.lupin@databank.fr"),
                "Banquier",
            ),
            (
                "Deschamps",
                "Didier",
                "d.deschamps@databank.fr",
                "45 Avenue des Bleus, Lyon",
                securite_mdp("worldcup2018", "d.deschamps@databank.fr"),
                "Banquier",
            ),
        ]

        query_user = "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for b in banquiers_data:
            curseur.execute(query_user, (b[0], b[1], b[2], b[3], b[4], b[5], None))

        cnx.commit()

        # Récupération des IDs Banquiers
        curseur.execute("SELECT ID FROM User WHERE Role = 'Banquier' LIMIT 2")
        banquiers = curseur.fetchall()

        if len(banquiers) >= 2:
            ID_Banquier1 = banquiers[0][0]
            ID_Banquier2 = banquiers[1][0]

            # --- INSERTION DES CLIENTS ---
            clients_raw = [
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
                    "Mercier",
                    "Lucas",
                    "l.mercier@mail.com",
                    "34 Bd Gambetta, Grenoble",
                    "pass10",
                    "Client",
                    ID_Banquier2,
                ),
            ]

            for c in clients_raw:
                mdp_hache = securite_mdp(c[4], c[2])
                donnees_finales = (c[0], c[1], c[2], c[3], mdp_hache, c[5], c[6])
                curseur.execute(query_user, donnees_finales)

            cnx.commit()

            # --- NOUVEAU : INSERTION DES COMPTES AVEC SOLDES DIFFÉRENTS ---

            # On définit les soldes par email pour la précision
            soldes_personnalises = {
                "michel.rostain@laplateforme.io": {
                    "Courant": 1250.50,
                    "Annexe": 5000.00,
                },
                "durand.marie@mail.com": {"Courant": 2100.00, "Annexe": 150.00},
                "l.mercier@mail.com": {"Courant": 45.30, "Annexe": 12000.00},
            }

            # On récupère tous les clients pour créer leurs comptes
            curseur.execute("SELECT ID, Email FROM User WHERE Role = 'Client'")
            clients = curseur.fetchall()

            for client_id, email in clients:
                # On récupère les montants prévus, sinon valeurs par défaut
                montants = soldes_personnalises.get(
                    email, {"Courant": 0.0, "Annexe": 0.0}
                )

                # Création Compte Courant
                curseur.execute(
                    "SELECT ID FROM Compte WHERE ID_User = %s AND Type = 'Courant'",
                    (client_id,),
                )
                if not curseur.fetchone():
                    curseur.execute(
                        "INSERT INTO Compte (ID_User, Solde, Type) VALUES (%s, %s, 'Courant')",
                        (client_id, montants["Courant"]),
                    )

                # Création Compte Annexe
                curseur.execute(
                    "SELECT ID FROM Compte WHERE ID_User = %s AND Type = 'Annexe'",
                    (client_id,),
                )
                if not curseur.fetchone():
                    curseur.execute(
                        "INSERT INTO Compte (ID_User, Solde, Type) VALUES (%s, %s, 'Annexe')",
                        (client_id, montants["Annexe"]),
                    )

            cnx.commit()
            print("Clients et comptes (soldes différenciés) initialisés.")

        print("Base de données initialisée avec succès avec hachage sécurisé.")
        curseur.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Erreur lors de l'initialisation : {err}")


if __name__ == "__main__":
    setup_database()
