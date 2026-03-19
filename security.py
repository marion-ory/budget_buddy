import hashlib

PEPPER = "skj§!bafyvdn@co06219!8420§3204§654650"

def securite_mdp(mdp_correct, sel=""):
    combinaison = PEPPER + mdp_correct + sel
    mdp_bytes = combinaison.encode("utf-8")
    mdp_hash = hashlib.sha256(mdp_bytes)
    return mdp_hash.hexdigest()

def traitement_mdp(mdp_saisi, email_user):
    from login import mdp_conform
    if mdp_conform(mdp_saisi):
        return securite_mdp(mdp_saisi, email_user)
    else:
        return None

def verifications_connexion(mdp_saisi, hask_stocke_bdd, email_user):
    hash_tentative = securite_mdp(mdp_saisi, email_user)
    return hash_tentative == hask_stocke_bdd