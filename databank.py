import mysql.connector
from config import get_connection
import hashlib
from security import securite_mdp


def setup_database():
    """Initialise et synchronise la structure et les données de la base."""
    try:
        # 1. Connexion initiale pour créer la base si besoin
        temp_cnx = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=8889,
        )
        curseur = temp_cnx.cursor()
        curseur.execute("CREATE DATABASE IF NOT EXISTS databank")
        temp_cnx.close()

        # 2. Connexion officielle
        cnx = get_connection()
        if not cnx:
            return

        curseur = cnx.cursor(dictionary=True)
        curseur.execute("USE databank")

        # --- CRÉATION DES TABLES ---
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
            CREATE TABLE IF NOT EXISTS Compte (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_User INT,
                Solde DECIMAL(15,2),
                Type ENUM('Courant', 'Annexe'),
                FOREIGN KEY (ID_User) REFERENCES User(ID)
            )
        """
        )

        curseur.execute(
            "CREATE TABLE IF NOT EXISTS Categorie (ID INT AUTO_INCREMENT PRIMARY KEY, Nom VARCHAR(255) UNIQUE)"
        )

        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS `Transaction` (
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

        for b in banquiers_data:
            curseur.execute(
                "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role) VALUES (%s, %s, %s, %s, %s, %s)",
                b,
            )

        cnx.commit()

        # Récupération des IDs Banquiers pour les lier aux clients
        curseur.execute("SELECT ID FROM User WHERE Role = 'Banquier' ORDER BY ID ASC")
        banquiers = curseur.fetchall()
        id_b1 = banquiers[0]["ID"]
        id_b2 = banquiers[1]["ID"] if len(banquiers) > 1 else id_b1

        # --- LISTE DES CLIENTS (RAW DATA) ---
        clients_raw = [
            (
                "Rostain",
                "Michel",
                "michel.rostain@laplateforme.io",
                "43 rue Neuve Sainte Catherine",
                "azerty",
                id_b1,
            ),
            (
                "Durand",
                "Marie",
                "durand.marie@mail.com",
                "5, rue Verte, Nantes",
                "pass1",
                id_b1,
            ),
            (
                "Mercier",
                "Lucas",
                "l.mercier@mail.com",
                "34 Bd Gambetta, Grenoble",
                "pass10",
                id_b2,
            ),
            (
                "Moreau",
                "Camille",
                "c.moreau@mail.com",
                "88 Av de la Liberté, Lille",
                "pass3",
                id_b1,
            ),
            (
                "Petit",
                "Nicolas",
                "n.petit@mail.com",
                "3 Square du Bois, Nice",
                "pass4",
                id_b1,
            ),
            (
                "Rousseau",
                "Julie",
                "j.rousseau@mail.com",
                "101 Route de Brest, Rennes",
                "pass5",
                id_b1,
            ),
            (
                "Blanc",
                "Kevin",
                "k.blanc@mail.com",
                "14 Rue du Lac, Annecy",
                "pass6",
                id_b2,
            ),
            (
                "Garnier",
                "Sophie",
                "s.garnier@mail.com",
                "22 Rue des Fleurs, Toulouse",
                "pass7",
                id_b2,
            ),
            (
                "Faure",
                "Julien",
                "j.faure@mail.com",
                "9 Rue de l'Eglise, Marseille",
                "pass8",
                id_b2,
            ),
            (
                "Andre",
                "Lea",
                "l.andre@mail.com",
                "67 Rue de la Paix, Strasbourg",
                "pass9",
                id_b2,
            ),
        ]

        # Insertion/Vérification des Clients
        for c in clients_raw:
            curseur.execute("SELECT ID FROM User WHERE Email = %s", (c[2],))
            if not curseur.fetchone():
                mdp_h = securite_mdp(c[4], c[2])
                curseur.execute(
                    """
                    INSERT INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier)
                    VALUES (%s, %s, %s, %s, %s, 'Client', %s)
                """,
                    (c[0], c[1], c[2], c[3], mdp_h, c[5]),
                )
                print(f"-> Nouveau client créé : {c[1]} {c[0]}")

        cnx.commit()

        # --- SOLDES PERSONNALISÉS ---
        soldes_personnalises = {
            "michel.rostain@laplateforme.io": {"Courant": 1250.50, "Annexe": 5000.00},
            "durand.marie@mail.com": {"Courant": 2100.00, "Annexe": 150.00},
            "l.mercier@mail.com": {"Courant": 1143.30, "Annexe": 20.00},
            "c.moreau@mail.com": {"Courant": 877.30, "Annexe": 120000.00},
            "n.petit@mail.com": {"Courant": 3247.30, "Annexe": 120.00},
            "j.rousseau@mail.com": {"Courant": 247.30, "Annexe": 12.00},
            "k.blanc@mail.com": {"Courant": 1233.30, "Annexe": 5236.00},
            "s.garnier@mail.com": {"Courant": 3243.30, "Annexe": 36.00},
            "j.faure@mail.com": {"Courant": 43.30, "Annexe": 0.00},
            "l.andre@mail.com": {"Courant": 143.30, "Annexe": 20.00},
        }

        # --- SYNCHRONISATION DES COMPTES ---
        curseur.execute("SELECT ID, Email FROM User WHERE Role = 'Client'")
        clients_bdd = curseur.fetchall()

        for client in clients_bdd:
            c_id = client["ID"]
            email = client["Email"]
            montants = soldes_personnalises.get(email, {"Courant": 0.0, "Annexe": 0.0})

            for type_c in ["Courant", "Annexe"]:
                curseur.execute(
                    "SELECT ID FROM Compte WHERE ID_User = %s AND Type = %s",
                    (c_id, type_c),
                )
                compte_existant = curseur.fetchone()

                if not compte_existant:
                    curseur.execute(
                        "INSERT INTO Compte (ID_User, Solde, Type) VALUES (%s, %s, %s)",
                        (c_id, montants[type_c], type_c),
                    )
                    print(f"   [OK] Compte {type_c} créé pour {email}")
                else:
                    # On met à jour le solde pour être sûr qu'il correspond au dictionnaire
                    curseur.execute(
                        "UPDATE Compte SET Solde = %s WHERE ID_User = %s AND Type = %s",
                        (montants[type_c], c_id, type_c),
                    )

        cnx.commit()
        print("\nStructure et données synchronisées avec succès.")

        curseur.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Erreur MySQL : {err}")


if __name__ == "__main__":
    setup_database()
