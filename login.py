from config import get_connection
# AJOUT : Import des éléments de security.py
from security import verifications_connexion, traitement_mdp, verifier_banquier, PEPPER



def code_banquier_valide(code_secret):
    if not code_secret:
        return True
    return code_secret.isdigit() and len(code_secret) == 4


def inscription(nom, prenom, email, adresse, mdp, code_b, id_banquier=None):
    h_mdp = traitement_mdp(mdp, email)
    role = verifier_banquier(code_b)

    if h_mdp and role != "erreur_code":
        conn = get_connection()
        if conn:
            try:
                curseur = conn.cursor()

                # Assigner automatiquement un banquier si c'est un client
                if role == "Client" and id_banquier is None:
                    from datamanagement import trouver_banquier_disponible
                    id_banquier = trouver_banquier_disponible()

                requete = """
                    INSERT INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                role_sql = role.capitalize()
                valeurs = (nom, prenom, email, adresse, h_mdp, role_sql, id_banquier)

                curseur.execute(requete, valeurs)
                conn.commit()

                if role_sql == "Client":
                    new_id = curseur.lastrowid
                    from datamanagement import creer_comptes_client
                    creer_comptes_client(new_id)

                return True
            except Exception as e:
                print(f"Erreur lors de l'inscription : {e}")
                conn.rollback()
            finally:
                curseur.close()
                conn.close()
    return False

def login(email, mdp):
    cnx = get_connection()
    if cnx:
        cur = cnx.cursor()
        # MODIFICATION : On sélectionne ID, Nom, Prenom pour pouvoir les utiliser dans app.py
        cur.execute("SELECT ID, Nom, Prenom, MDP, Role FROM User WHERE Email = %s", (email,))
        res = cur.fetchone()
        cur.close()
        cnx.close()

        # res[3] correspond au MDP haché dans la BDD
        if res and verifications_connexion(mdp, res[3], email):
            # MODIFICATION : On retourne un dictionnaire complet pour la session de l'app
            return {"id": res[0], "nom": res[1], "prenom": res[2], "role": res[4], "email": email}
    return None