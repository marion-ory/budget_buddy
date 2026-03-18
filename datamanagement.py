from config import *
import engine


def historique(id_utilisateur):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionnary=True)  # pour Tkinter colonnes

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
            curseur = conn.cursor(dictionnary=True)

            # On définit la requête (6 colonnes au total)
            requete = "INSERT INTO Transaction (ID_Emetteur, Date, Montant, Description, Type, ID_Categorie) VALUES (%s, %s, %s, %s, 'Retrait', %s)"

            # On aligne les valeurs EXACTEMENT sur l'ordre des colonnes ci-dessus
            valeurs = (id_compte, date_op, montant, description, id_cat)

            curseur.execute(requete, valeurs)
            conn.commit()
            print("Retrait Effectué")

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
            curseur = conn.cursor(dictionnary=True)

            requete = "INSERT INTO Transaction (ID_Emetteur,Date, Montant, Description, Type, ID_Categorie, ID_beneficiaire) VALUES (%s,%s, %s, %s, 'Virement', %s,%s)"
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
        except Exception as e:
            print("Une erreur est survenue, veuillez réessayer plus tard")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def depot(id_compte, montant, date_op, description, id_cat):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionnary=True)

            requete = "INSERT INTO Transaction (ID_Beneficiaire, Montant, Date, Description, ID_categorie, Type) VALUES (%s,%s,%s,%s,%s,'Depot')"
            valeurs = (id_compte, montant, date_op, description, id_cat)

            curseur.execute(requete, valeurs)
            conn.commit()
            print("Votre Depot a été pris en compte")
        except Exception as e:
            print("Une erreur est survenue, Veuillez réessayer plus tard")
            conn.rollback()
        finally:
            curseur.close()
            conn.close()


def trier_par(critere, date=None):
    conn = get_connection()
    if conn:
        try:
            curseur = conn.cursor(dictionnary=True)
            requete = "SELECT * FROM Transaction"

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
                    requete += " WHERE Date BETWEEN %s AND %s "

                case _:
                    return []

            if critere == "fourchette_date" and date:
                curseur.execute(requete, date)
            else:

                curseur.execute(requete)
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
    curseur.execute(requete, (id_banquier))
    clients = curseur.fetchall()

    curseur.close()
    conn.close()
    return clients
