import hashlib
from config import get_connection

code_banquier_attendu = "1234"
PEPPER = "skj§!bafyvdn@co06219!8420§3204§654650"


def mdp_conform(mdp):
    if len(mdp) < 10:
        return False
    a_majuscule = a_minuscule = a_chiffre = a_special = False
    for caractere in mdp:
        if caractere.isupper():
            a_majuscule = True
        elif caractere.islower():
            a_minuscule = True
        elif caractere.isdigit():
            a_chiffre = True
        elif not caractere.isalnum():
            a_special = True
    return a_majuscule and a_minuscule and a_chiffre and a_special


def code_banquier_valide(code_secret):
    if not code_secret:
        return True
    return code_secret.isdigit() and len(code_secret) == 4


# hash du code banquier (on utilise le poivre pour être cohérent)
hash_banquier_cible = hashlib.sha256(
    (PEPPER + code_banquier_attendu).encode("utf-8")
).hexdigest()


def verifier_banquier(code_saisi):
    if not code_saisi:
        return "Client"
    # on compare avec le hash poivré
    if (
        hashlib.sha256((PEPPER + code_saisi).encode("utf-8")).hexdigest()
        == hash_banquier_cible
    ):
        return "Banquier"
    else:
        return "erreur_code"


def inscription(nom, prenom, email, adresse, mdp, code_b, id_banquier=None):

    h_mdp = traitement_mdp(mdp, email)

    # verifie code banquier
    role = verifier_banquier(code_b)

    if h_mdp and role != "erreur_code":
        conn = get_connection()
        if conn:
            try:
                curseur = conn.cursor()

                # IMPORTANT : On ajoute ID_banquier pour que ton système
                # de portefeuille banquier fonctionne !
                requete = """
                    INSERT INTO User (Nom, Prenom, Email, Adresse, MDP, Role, ID_banquier)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                # majuscule pour fitter avec la bdd
                role_sql = role.capitalize()

                valeurs = (nom, prenom, email, adresse, h_mdp, role_sql, id_banquier)

                curseur.execute(requete, valeurs)
                conn.commit()
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
        cur.execute("SELECT MDP, Role FROM User WHERE Email = %s", (email,))
        res = cur.fetchone()
        cur.close()
        cnx.close()

        # on ajoute l'email pour la vérification du hash salé
        if res and verifications_connexion(mdp, res[0], email):
            return res[1]
    return None
