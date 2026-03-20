import hashlib

#           [     SECURITE GENERALE CONNEXION   ]

PEPPER = "MonPoivreSecret123!"


def verifications_connexion(mdp_saisi, hask_stocke_bdd, email_user):
    # on vérifie avec le sel (email) pour que ça corresponde
    hash_tentative = securite_mdp(mdp_saisi, email_user)
    return hash_tentative == hask_stocke_bdd


def securite_mdp(mdp_correct, sel=""):
    # on utilise la combinaison POIVRE + MDP + SEL
    combinaison = PEPPER + mdp_correct + sel
    mdp_bytes = combinaison.encode("utf-8")
    mdp_hash = hashlib.sha256(mdp_bytes)
    return mdp_hash.hexdigest()


def traitement_mdp(mdp_saisi, email_user):
    # on passe l'email comme sel
    if mdp_conform(mdp_saisi):
        return securite_mdp(mdp_saisi, email_user)
    else:
        return None


#             [    VERIFICATION   UTILISATEUR    ]


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
