import mysql.connector

cnx = mysql.connector.connect(
    host = "localhost",
    user = "michel",
    password = ""
)

curseur = cnx.cursor()
# Création de la base de données
curseur.execute("CREATE DATABASE IF NOT EXISTS databank")
print("DataBank créée")

# Connexion à la base de données
curseur.execute("USE databank")
# Création des tables
curseur.execute("""
        CREATE TABLE IF NOT EXISTS User(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_banquier INT NULL,
                Nom VARCHAR(255),
                Prenom VARCHAR(255),
                Email VARCHAR(255),
                Adresse VARCHAR(255),
                MDP VARCHAR(255),
                Role ENUM('Client', 'Banquier'),
                FOREIGN KEY (ID_banquier) REFERENCES User(ID)
                )
                """)

curseur.execute("""
        CREATE TABLE IF NOT EXISTS Compte(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_User INT,
                Solde DECIMAL,
                Type ENUM('Courant', 'Annexe'), 
                FOREIGN KEY (ID_User) REFERENCES User(ID)
                )
                """)

curseur.execute("""
        CREATE TABLE IF NOT EXISTS Categorie(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Nom VARCHAR(255) UNIQUE
                )     
                """)

# Ajout des catégories automatiquement à la table Catégorie lors de création de la base de donnée
categories = ["Alimentaire", "Vie quotidienne", "loisirs", "Véhicule", "Energie", "Logement", "Epargne"]
for cat in categories:
    curseur.execute("INSERT IGNORE INTO Categorie(Nom) VALUES(%s)",(cat,))
cnx.commit()

curseur.execute("""
        CREATE TABLE IF NOT EXISTS Transaction(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ID_Categorie INT,
                Description VARCHAR(255),
                Montant DECIMAL,
                Date DATE,
                Type ENUM('Depot', 'Retrait', 'Transfert'),
                ID_Emetteur INT,
                ID_Beneficiaire INT,
                FOREIGN KEY (ID_Emetteur) REFERENCES Compte(ID),
                FOREIGN KEY (ID_Beneficiaire) REFERENCES Compte(ID),
                FOREIGN KEY (ID_Categorie) REFERENCES Categorie(ID)
                )
                """)

curseur.close()
cnx.close()