from config import *
from engine import Client, CompteBancaires
from security import *
from login import inscription, login

#                      [    IDENTIFICATION      ]

# ---------> Recuperation client complet :


def recuperer_client_complet(id_user):
    conn = get_connection()
    if not conn:
        return None

    try:
        curseur = conn.cursor(dictionary=True)
        # On récupère les infos de l'utilisateur
        curseur.execute("SELECT * FROM User WHERE ID = %s", (id_user,))
        n = curseur.fetchone()

        if n:
            # On crée le VÉRITABLE OBJET Client
            nouveau_client = Client(
                n["ID"],
                n["ID_banquier"],
                n["Nom"],
                n["Prenom"],
                n["Email"],
                n["Adresse"],
                n["MDP"],
            )

            # On récupère ses comptes
            curseur.execute("SELECT * FROM Compte WHERE ID_User = %s", (id_user,))
            comptes_sql = curseur.fetchall()

            for c in comptes_sql:
                # 1. On convertit d'abord
                solde_propre = float(c["Solde"])

                print(
                    f"DEBUG SQL: Lecture du compte {c['Type']} | Solde: {solde_propre}€"
                )

                # 2. On passe 'solde_propre' à l'objet !
                compte_obj = CompteBancaires(
                    id=c["ID"],
                    user_id=c["ID_User"],
                    solde=solde_propre,
                    typecompte=c["Type"],
                )
                nouveau_client.ajouter_compte(compte_obj)

            print(f"DEBUG: Objet créé avec succès pour {nouveau_client.prenom}")
            return nouveau_client

    except Exception as e:
        print(f"ERREUR dans recuperer_client_complet : {e}")
        return None
    finally:
        curseur.close()
        conn.close()


# --------> Recuperation des comptes  Client et Banquier :


def charger_comptes_utilisateurs(id_user):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            requete = "SELECT * FROM Compte WHERE ID_User= %s"
            curseur.execute(requete, (id_user,))
            listes_comptes = curseur.fetchall()  # recupere la liste de compte
            return listes_comptes
        except Exception as e:
            print("Erreur de chargement des comptes")
            conn.rollback()
            return []  # liste vide si le chargement ne se fait pas
        finally:
            curseur.close()
            conn.close()


# ----------> Recuperation portefeuille Banquier :


def recuperer_portefeuille_banquier(id_banquier):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            requete = "SELECT * FROM User WHERE ID_banquier = %s"
            curseur.execute(requete, (id_banquier,))
            return curseur.fetchall()
        except Exception as e:
            print(f"Erreur chargement du Portefeuille Client : {e}")
            conn.rollback()
            return []
        finally:
            curseur.close()
            conn.close()
    return []

# .                      [     OPERATIONS       ]


def historique(id_utilisateur):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)  # pour Tkinter colonnes affichage

            requete = "SELECT * FROM Transaction WHERE ID_Emetteur= %s OR  ID_Beneficiaire = %s ORDER BY Date DESC"

            curseur.execute(requete, (id_utilisateur, id_utilisateur))
            resultats = curseur.fetchall()
            return resultats
        except Exception as e:
            print("Une erreur est suvenue")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def retrait(id_compte, montant, description, id_cat, date_op):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)

            # DEBIT
            requete_debit = "UPDATE Compte SET Solde = Solde - %s WHERE ID =%s"
            curseur.execute(requete_debit, (montant, id_compte))

            # On définit la requête (6 colonnes au total)
            requete = "INSERT INTO Transaction (ID_Emetteur, Date, Montant, Description, Type, ID_Categorie) VALUES (%s, %s, %s, %s, 'Retrait', %s)"

            valeurs = (id_compte, date_op, montant, description, id_cat)

            curseur.execute(requete, valeurs)
            conn.commit()
            print(f"Retrait de {montant}€ effectué sur le compte {id_compte}")
            return True

        except Exception as e:
            print(f"Oups, une erreur : {e}")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def virement(montant, description, id_cat, date_op, id_emetteur, id_beneficiaire):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)

            # on retire l argent DEBIT

            requete_debit = "UPDATE Compte SET Solde = Solde - %s WHERE ID =%s"
            curseur.execute(requete_debit, (montant, id_emetteur))

            # on donne l argent CREDIT

            requete_credit = " UPDATE Compte SET Solde = Solde + %s WHERE ID= %s"
            curseur.execute(requete_credit, (montant, id_beneficiaire))

            # on le note

            requete = "INSERT INTO Transaction (ID_Emetteur,Date, Montant, Description, Type, ID_Categorie, ID_beneficiaire) VALUES (%s,%s, %s, %s, 'Transfert', %s,%s)"
            valeurs = (
                id_emetteur,
                date_op,
                montant,
                description,
                id_cat,
                id_beneficiaire,
            )

            curseur.execute(requete, valeurs)
            conn.commit()
            print("Virement pris en compte")
            return True
        except Exception as e:
            print("Une erreur est survenue, veuillez réessayer plus tard")
            conn.rollback()
            return False

        finally:
            curseur.close()
            conn.close()


def depot(id_compte, montant, date_op, description, id_cat):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)

            requete_credit = " UPDATE Compte SET Solde = Solde + %s WHERE ID= %s"
            curseur.execute(requete_credit, (montant, id_compte))

            requete = "INSERT INTO Transaction (ID_Beneficiaire, Montant, Date, Description, ID_Categorie, Type) VALUES (%s,%s,%s,%s,%s,'Depot')"
            valeurs = (id_compte, montant, date_op, description, id_cat)

            curseur.execute(requete, valeurs)
            conn.commit()
            print(f"Dépôt de {montant}€ effectué sur le compte {id_compte}")
            return True
        except Exception as e:
            print("Une erreur est survenue, Veuillez réessayer plus tard")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def trier_par(id_user, critere, date=None):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            requete = "SELECT * FROM Transaction WHERE (ID_Emetteur= %s OR ID_Beneficiaire = %s)"
            # puisque dans la classe User accès pour le client et le banquier je dois chercher id a deux endroits
            match critere:
                case "date_recent":
                    requete += " ORDER BY Date DESC"

                case "categorie":
                    requete += " ORDER BY ID_Categorie"

                case "type_operation":
                    requete += " ORDER BY Type"

                case "montant_op_croissant":
                    requete += " ORDER BY Montant ASC"

                case "montant_op_decroissant":
                    requete += " ORDER BY Montant DESC"

                case "fourchette_date":
                    requete += " AND Date BETWEEN %s AND %s "

                case _:
                    return []

            if critere == "fourchette_date" and date:
                curseur.execute(requete, (id_user, id_user, date[0], date[1]))
            else:

                curseur.execute(requete, (id_user, id_user))
            resultats = curseur.fetchall()
            return resultats

        except Exception as e:
            print("Une erreur est survenue ")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def recuperer_client_par_banquier(id_banquier):
    conn = get_connection()

    curseur = conn.cursor(dictionary=True)

    requete = "SELECT * FROM User WHERE ID_banquier = %s "
    curseur.execute(requete, (id_banquier,))
    clients = curseur.fetchall()

    curseur.close()
    conn.close()
    return clients


def trouver_id_compte_par_nom(nom, prenom):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            curseur.execute("SELECT Nom, Prenom FROM User")
            tous = curseur.fetchall()
            print(f"DEBUG SQL: Liste réelle en BDD : {tous}")
            # 1. Nettoyage : on enlève les espaces et on met en minuscule
            n = nom.strip().lower()
            p = prenom.strip().lower()

            # 2. La requête magique : (Nom=n ET Prenom=p) OU (Nom=p ET Prenom=n)
            # On cherche spécifiquement le compte 'Courant'
            requete = """
                SELECT Compte.ID
                FROM Compte
                JOIN User ON Compte.ID_User = User.ID
                WHERE (
                    (LOWER(User.Nom) = %s AND LOWER(User.Prenom) = %s)
                    OR
                    (LOWER(User.Nom) = %s AND LOWER(User.Prenom) = %s)
                )
                AND Compte.Type = 'Courant'
            """

            # On envoie les paramètres dans les deux sens
            curseur.execute(requete, (n, p, p, n))
            resultat = curseur.fetchone()

            if resultat:
                print(
                    f"DEBUG SQL: Compte trouvé pour {prenom} {nom} -> ID {resultat['ID']}"
                )
                return resultat["ID"]
            else:
                print(
                    f"DEBUG SQL: Aucun compte trouvé pour '{prenom}' '{nom}' (Vérifie l'orthographe)"
                )
                return None

        except Exception as e:
            print(f"DEBUG SQL: Erreur lors de la recherche : {e}")
            return None
        finally:
            curseur.close()
            conn.close()
    return None


def recuperer_categories():
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            curseur.execute("SELECT * FROM Categorie")
            return (
                curseur.fetchall()
            )  # Retourne une liste de dict [{'ID': 1, 'Nom': 'Alimentaire'}, ...]
        finally:
            curseur.close()
            conn.close()
    return []

def recuperer_banquier_complet(id_user):
    conn = get_connection()
    if not conn:
        return None

    try:
        curseur = conn.cursor(dictionary=True)
        curseur.execute("SELECT * FROM User WHERE ID = %s", (id_user,))
        n = curseur.fetchone()

        if n:
            from engine import Banquier
            nouveau_banquier = Banquier(
                id=n["ID"],
                nom=n["Nom"],
                prenom=n["Prenom"],
                email=n["Email"],
                adresse=n["Adresse"],
                mdp=n["MDP"],
                titre="Conseiller",
            )
            # On charge son portefeuille de clients
            nouveau_banquier.charger_portefeuille()
            print(f"DEBUG: Banquier {nouveau_banquier.prenom} chargé avec {len(nouveau_banquier.client)} clients")
            return nouveau_banquier

    except Exception as e:
        print(f"ERREUR dans recuperer_banquier_complet : {e}")
        return None
    finally:
        curseur.close()
        conn.close()

def creer_comptes_client(id_user):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor()
            for type_c in ["Courant", "Annexe"]:
                curseur.execute(
                    "INSERT INTO Compte (ID_User, Solde, Type) VALUES (%s, %s, %s)",
                    (id_user, 0.00, type_c)
                )
            conn.commit()
            print(f"Comptes créés pour l'utilisateur {id_user}")
            return True
        except Exception as e:
            print(f"Erreur création comptes : {e}")
            conn.rollback()
            return False
        finally:
            curseur.close()
            conn.close()
    return False

def trouver_banquier_disponible():
    """Retourne l'ID du banquier ayant le moins de clients."""
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionary=True)
            curseur.execute("""
                SELECT User.ID, COUNT(Client.ID) as nb_clients
                FROM User
                LEFT JOIN User AS Client ON Client.ID_banquier = User.ID
                WHERE User.Role = 'Banquier'
                GROUP BY User.ID
                ORDER BY nb_clients ASC
                LIMIT 1
            """)
            resultat = curseur.fetchone()
            if resultat:
                return resultat["ID"]
        except Exception as e:
            print(f"Erreur recherche banquier : {e}")
            return None
        finally:
            curseur.close()
            conn.close()
    return None