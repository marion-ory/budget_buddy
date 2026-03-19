import mysql.connector
from config import get_connection


def setup_database():
    """Fonction qui initialise toute la structure de la base de données"""
    try:
        # 1. Première connexion sans base spécifique pour la créer si besoin
        # On récupère les params de config mais on n'utilise pas encore la database
        temp_cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Change par "" si besoin
            port=8889,  # Port MAMP par défaut
        )
        curseur = temp_cnx.cursor()
        curseur.execute("CREATE DATABASE IF NOT EXISTS databank")
        temp_cnx.close()

        # 2. Maintenant on se connecte normalement via ta config
        cnx = get_connection()
        curseur = cnx.cursor()
        curseur.execute("USE databank")

        # --- TABLES (Le code de Michel) ---
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
                Solde DECIMAL(15,2) DEFAULT 0.00,
                Type ENUM('Courant', 'Annexe'),
                FOREIGN KEY (ID_User) REFERENCES User(ID)
            )
        """
        )

        curseur.execute(
            "CREATE TABLE IF NOT EXISTS Categorie(ID INT AUTO_INCREMENT PRIMARY KEY, Nom VARCHAR(255) UNIQUE)"
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

        # --- INSERTIONS AUTOMATIQUES ---
        categories = [
            "Alimentaire",
            "Vie quotidienne",
            "Loisirs",
            "Véhicule",
            "Energie",
            "Logement",
            "Epargne",
        ]
        for cat in categories:
            curseur.execute("INSERT IGNORE INTO Categorie(Nom) VALUES(%s)", (cat,))

        # Création des banquiers (Version simplifiée)
        banquiers_data = [
            (
                "Lupin",
                "Arsène",
                "a.lupin@databank.fr",
                "Paris",
                "password123",
                "Banquier",
            ),
            (
                "Deschamps",
                "Didier",
                "d.deschamps@databank.fr",
                "Lyon",
                "worldcup2018",
                "Banquier",
            ),
        ]
        query_user = "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for b in banquiers_data:
            curseur.execute(query_user, (*b, None))

        cnx.commit()
        print(" Base de données initialisée avec succès.")

        curseur.close()
        cnx.close()

    except Exception as e:
        print(f" Erreur lors de l'initialisation : {e}")


# Permet de tester le fichier tout seul si on l'exécute
if __name__ == "__main__":
    setup_database()
