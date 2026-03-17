import hashlib
from Engine import get_connection

code_banquier_attendu = "1234"


def mdp_conform(mdp):
    if len(mdp) < 10:
        return False
       
    a_majuscule = False
    a_minuscule = False
    a_chiffre = False
    a_special = False 
   
    #on vérifie chaque caractère
    for caractere in mdp:
        if caractere.isupper():
            a_majuscule = True
        elif caractere.islower():
            a_minuscule = True
        elif caractere.isdigit():
            a_chiffre = True
        elif not caractere.isalnum():
            a_special = True
           
    #le mot de passe est valide seulement si TOUT est True
    return a_majuscule and a_minuscule and a_chiffre and a_special


def securite_mdp(mdp_correct) :
    mdp_bytes = mdp_correct.encode('utf-8') #conversion en bytes
    mdp_hash = hashlib.sha256(mdp_bytes) #application de l'algo SHA-256
    #recuperation version hexadecimale (ce qu'on va stocker dans notre BDD)
    return mdp_hash.hexdigest()

#retourne le hash seulement si le mdp correspond aux criteres
def traitement_mdp(mdp_saisi):
    if mdp_conform(mdp_saisi):
        return securite_mdp(mdp_saisi)
    else:
        return None
    

def verifications_connexion(mdp_saisi, hask_stocke_bdd):
    hash_tentative = securite_mdp(mdp_saisi)
    return hash_tentative == hask_stocke_bdd


def code_banquier_valide(code_secret):
    if not code_secret:
        return True
    return code_secret.isdigit() and len(code_secret) == 4

hash_banquier_cible = hashlib.sha256(code_banquier_attendu.encode('utf-8')).hexdigest()

def verifier_banquier(code_saisi):
    if not code_saisi:
        return "Client"
    
    if securite_mdp(code_saisi) == hash_banquier_cible:
        return "Banquier"
    else:
        return "erreur_code"
    
def inscription(nom ,prenom, email, adresse, mdp, code_b):
    h_mdp = traitement_mdp(mdp)
    role = verifier_banquier(code_b)

    if h_mdp and role != "erreur_code":
        cnx = get_connection()
        if cnx:
            cur = cnx.cursor()
            query = "INSERT INTO User (Nom, Prenom, Email, Adresse, MDP, Role) VALUES (%s,%s,%s,%s,%s,%s)"
            cur.execute(query, (nom, prenom, email, adresse, h_mdp, role))
            cnx.commit()
            cur.close()
            cnx.close()
            return True
        return False
    
def login(email, mdp):
    cnx = get_connection()
    if cnx:
        cur = cnx.cursor()
        cur.execute("SELECT MDP, Role FROM User WHERE Email = %s", (email,))
        res = cur.fetchone()
        cur.close()
        cnx.close()
        
        if res and verifications_connexion(mdp, res[0]):
            return res[1] # Retourne 'Client' ou 'Banquier'
    return None
