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
# Création des tables. Dans la table User "UNIQUE" pour email car c'est l'identifiant unique de l'utilisateur pour se connecter
curseur.execute("""
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

curseur.execute("""
        CREATE TABLE IF NOT EXISTS `Transaction`(
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


################################# CREATION CATEGORIES
# Ajout des catégories automatiquement à la table Catégorie lors de création de la base de donnée
categories = ["Alimentaire", "Vie quotidienne", "loisirs", "Véhicule", "Energie", "Logement", "Epargne"]
for cat in categories:
    curseur.execute("INSERT IGNORE INTO Categorie(Nom) VALUES(%s)",(cat,))
cnx.commit()


################################# CREATION BANQUIERS ET CLIENTS FICTIFS
# Création des banquiers :
banquiers_data = [
    ('Lupin', 'Arsène', 'a.lupin@databank.fr', '12 Rue de la Paix, Paris', 'dabef5941589a923a08a00eae2fd2c55a8eb160871074aa859742ab2808b0bfe', 'Banquier'),
    ('Deschamps', 'Didier', 'd.deschamps@databank.fr', '45 Avenue des Bleus, Lyon', '08f97d80835a3a20238e8e1b6074a4f95be118d7cf2cf186c4f277b1f0329570', 'Banquier')
]

query_user = "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier) VALUES (%s, %s, %s, %s, %s, %s, %s)"

for b in banquiers_data:
    curseur.execute(query_user, (b[0], b[1], b[2], b[3], b[4], b[5], None))

cnx.commit()
print("Banquiers créés.")

# Récupération de l'ID des User dont le role est 'Banquier', afin de l'associer à nos clients fictifs créés avec la base de données : 
curseur.execute("SELECT ID FROM User WHERE Role = 'Banquier'")
banquiers = curseur.fetchall()

# Extraction des ID. Le premier [0] sélectionne l'index du premier tuple renvoyé par fetchall(), le deuxième sélectionne l'index de la première info du tuple, ici la première colonne, soit l'ID :
ID_Banquier1=banquiers[0][0]
ID_Banquier2=banquiers[1][0]

clients_data = [
        ('Michel', 'Rostain', 'michel.rostain@laplateforme.io', '43 rue Neuve Sainte Catherine, 13007 Marseille', '115a1d094efeceac441ea5f126edac09cf78d8aa55f58b490197250242113527', 'Client', ID_Banquier1),
        ('Durand', 'Marie', 'durand.marie@mail.com', '5, rue Verte, Nantes', '982ed77b187e9e053cdc14f177e8cbb48bd09c25a001f1dbcc4d80be47ccbc30', 'Client', ID_Banquier1),
        ('Lefebvre', 'Thomas', 't.lefe@mail.com', '12 Bis Rue du Port, Bordeaux', '2611520a1549ca4e6c4f99cb3386420b9f6e88d76e70ed7d7f29962caf105ec0', 'Client', ID_Banquier1),
        ('Moreau', 'Camille', 'c.moreau@mail.com', '88 Av de la Liberté, Lille', '82bad5c251b9d2abd6c2e5fbcb4e1b1675c90cf9c129d502adfd6a6c37118079', 'Client', ID_Banquier1),
        ('Petit', 'Nicolas', 'n.petit@mail.com', '3 Square du Bois, Nice', '90db711794c7f8d5e769a4dd36e90739e2591950794a86a076d2627b783796eb', 'Client', ID_Banquier1),
        ('Rousseau', 'Julie', 'j.rousseau@mail.com', '101 Route de Brest, Rennes', 'b9486da8f38f1d54ec49b75e47724b11d1a24256bc193974689138be0bf9d69c', 'Client', ID_Banquier1),
        ('Blanc', 'Kevin', 'k.blanc@mail.com', '14 Rue du Lac, Annecy', 'c13155ca9441bfbe6c16555649c5446a4e5ce2bacf90313a1427a6a5a5984d13', 'Client', ID_Banquier2),
        ('Garnier', 'Sophie', 's.garnier@mail.com', '22 Rue des Fleurs, Toulouse', '7e4e87d2ca33f8196471aa501314d776bcecc3d8bf6fedefd61e86bd4fa5a7e3', 'Client', ID_Banquier2),
        ('Faure', 'Julien', 'j.faure@mail.com', '9 Rue de l\'Eglise, Marseille', '1474c54d158defa0b461593579d5ed017c02d6381dc180dbf5d45464ddc418fe', 'Client', ID_Banquier2),
        ('Andre', 'Lea', 'l.andre@mail.com', '67 Rue de la Paix, Strasbourg', '239d1e40f2b309e4f0c75457a36cefd6d35b4bf982f0c7e7eee6612224c7d0f9', 'Client', ID_Banquier2),
        ('Mercier', 'Lucas', 'l.mercier@mail.com', '34 Bd Gambetta, Grenoble', '4e5bf0b0c992a370f940b9519ac1e680ed134a9b2742ab3faad77cfad380e54b', 'Client', ID_Banquier2)
]
# INSERT IGNORE permet d'éviter de créer des doublons 
query_user = "INSERT IGNORE INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_Banquier) VALUES (%s, %s, %s, %s, %s, %s, %s)"

# Ici "c" fait référence aux tuples contenant les infos de "clients_data", donc curseur.execute a besoin pour fonctionner de : la requête SQL(query_user), et des tuples ("c") qui vont remplacer les "%s" de la query_user:
for c in clients_data : 
        curseur.execute(query_user,c)
cnx.commit()
print("Clients créés.")

curseur.execute("SHOW TABLES")
tables=curseur.fetchall()
print(f"Il y a {len(tables)} tables présentes.")

curseur.close()
cnx.close()
print("Base de données créée avec succès.")