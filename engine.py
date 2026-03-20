from config import *
import datetime

# Imports déplacés dans les méthodes pour éviter l'ImportError
# from datamanagement import (
#     historique,
#     virement,
#     retrait,
#     depot,
#     trier_par,
#     recuperer_client_par_banquier,
# )


class CompteBancaires:
    def __init__(self, id, user_id, solde, typecompte):
        self.id = id
        self.user_id = user_id
        self.solde = solde
        self.typecompte = typecompte
        self.transactions = []

    def calculer_solde(self):
        # On part du solde enregistré en BDD (ou 0 si tu préfères tout recalculer)
        solde_temporaire = self.solde

        for t in self.transactions:
            if t.type == "Depot":
                solde_temporaire += t.montant
            elif t.type == "Retrait":
                solde_temporaire -= t.montant
            elif t.type == "Transfert":
                if t.emetteur == self.id:
                    solde_temporaire -= t.montant
                elif t.beneficiaire == self.id:
                    solde_temporaire += t.montant

        return solde_temporaire

    def peut_faire_transfert(self, destination_type):

        match self.typecompte:
            case "Courant":
                return True
            case "Annexe":
                if destination_type == "Courant":  # uniquement vers compte courant
                    return True
                else:
                    print(
                        "Erreur: Un compte annexe transfère uniquement vers le compte courant"
                    )
                    return False
            case _:
                return False

    # .        [ OPERATION DE DEBIT ET CREDIT SUR SOLDE DES COMPTES ]
    def effectuer_transfert(self, montant, compte_destination, description="Transfert"):

        if self.peut_faire_transfert(compte_destination.typecompte):

            if self.calculer_solde() >= montant:
                from datamanagement import virement

                succes = virement(
                    montant=montant,
                    description=description,
                    id_cat=3,
                    date_op=datetime.date.today(),
                    id_emetteur=self.id,
                    id_beneficiaire=compte_destination.id,
                )
                if succes:
                    print("Transfert autorisé et effectué.")
                    self.solde -= montant
                    compte_destination.solde += montant
                return True
            else:
                print("Solde insuffisant.")

    def effectuer_depot(self, montant, description="Depot"):
        if montant > 0:
            from datamanagement import depot

            succes = depot(
                id_compte=self.id,
                montant=montant,
                date_op=datetime.date.today(),
                description=description,
                id_cat=1,
            )

            if succes:
                print(f"Votre depot {montant} a été pris en compte")
                self.solde += montant
                from datamanagement import historique

                historique(self.id_compte, "Dépôt", montant)
                return True
            else:
                print("Erreur, veuillez aller au guichet")

    def effectuer_retrait(self, montant, description="Retrait"):
        if montant > 0 and montant <= self.solde:
            from datamanagement import retrait

            succes = retrait(
                id_compte=self.id,
                montant=montant,
                description=description,
                id_cat=2,
                date_op=datetime.date.today(),
            )
            if succes:
                print(f"Votre retrait d'un montant de {montant} € a été pris en compte")
                self.solde -= montant
                return True
            else:
                print("Erreur technique lors du retrait.")
                return False
        else:
            if montant > self.solde:
                print("Solde Insuffisant pour ce retrait.")
            else:
                print("Le montant doit être supérieur à 0.")
            return False


class Users:
    def __init__(self, id, id_banquier, nom, prenom, email, adresse, mdp, role):
        self.id = id
        self.id_banquier = id_banquier
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.adresse = adresse
        self.mdp = mdp
        self.role = role


class Client(Users):
    def __init__(self, id, id_banquier, nom, prenom, email, adresse, mdp):

        super().__init__(
            id, id_banquier, nom, prenom, email, adresse, mdp, role="Client"
        )

        self.comptes = []
        self.transactions = []

    def ajouter_compte(self, compte_obj):
        self.comptes.append(compte_obj)

    def faire_virement(self, montant, description, id_cat, date_op, id_beneficiaire):
        print(f"Demande de virement {montant} par {self.nom}")
        from datamanagement import virement

        virement(montant, description, id_cat, date_op, self.id, id_beneficiaire)

    def faire_depot(self, montant, description, id_cat, date_op):
        print(f"Votre depot de {montant} € a été pris en compte")
        from datamanagement import depot

        depot(self.id, montant, date_op, description, id_cat)

    def faire_retrait(self, montant, description, id_cat, date_op):
        print(f"Vous avez effectué un retrait de  {montant} €")
        from datamanagement import retrait

        retrait(self.id, montant, description, id_cat, date_op)

    def charger_comptes(self):
        """Récupère les comptes en BDD et les transforme en objets CompteBancaires"""
        from datamanagement import charger_comptes_utilisateurs

        # On récupère les dictionnaires SQL (ceux avec ID_User)
        donnees_sql = charger_comptes_utilisateurs(self.id)
        self.comptes = []

        for c in donnees_sql:

            nouveau_compte = CompteBancaires(
                id=c["ID"],
                user_id=c["ID_User"],
                solde=float(c["Solde"]),
                type_compte=c["Type"],
            )
            self.comptes.append(nouveau_compte)

        print(f" {len(self.comptes)} comptes chargés pour {self.prenom}")

    def initialiser_donnees(self):
        """Charge TOUT : comptes et transactions d'un coup"""
        self.charger_comptes()
        self.charger_transactions_client()

    def afficher_historique_tri(self, critere, dates=None):
        from datamanagement import trier_par

        donnees_triees = trier_par(self.id, critere, dates)
        self.transaction = []

        for ligne in donnees_triees:
            trie = Transaction(
                id=ligne["ID"],
                categorie=ligne["ID_Categorie"],
                description=ligne["Description"],
                montant=ligne["Montant"],
                date=ligne["Date"],
                type=ligne["Type"],
                emetteur=ligne["ID_Emetteur"],
                beneficiaire=ligne["ID_Beneficiaire"],
                user_id=self.id,
            )
            self.transaction.append(trie)

        print(f"Historique rechargé et trié par : {critere}")


class Banquier(Users):
    def __init__(self, id, nom, prenom, email, adresse, mdp, titre):

        super().__init__(id, None, nom, prenom, email, adresse, mdp, role="Banquier")
        self.titre = titre
        self.clients_geres = []

    def faire_virement(
        self, id_emetteur, id_beneficaire, montant, id_cat, date_op, description
    ):
        from datamanagement import virement

        # Le banquier a le privilège de choisir le compte émetteur (celui de ses clients)
        print(
            f"Le banquier {self.nom} effectue un virement de {montant} depuis le compte {id_emetteur} vers le beneficiaire {id_beneficaire}"
        )
        virement(montant, description, id_cat, date_op, id_emetteur, id_beneficaire)

    def modifier_user(self, user_id, nouvelles_infos):
        print(f"Modification de l'utilisateur {user_id} par le banquier.")

    def charger_portefeuille(self):
        from datamanagement import recuperer_client_par_banquier

        clients_BDD = recuperer_client_par_banquier(self.id)
        self.client = []

        for ligne in clients_BDD:
            nouveaux_clients = Client(
                id=ligne["ID"],
                nom=ligne["Nom"],
                prenom=ligne["Prenom"],
                mail=ligne["Email"],
                adresse=ligne["Adresse"],
                mdp="*****",  # securite
                id_banquier=self.id,
            )

            self.client.append(nouveaux_clients)
        print(f"GESTION PORTEFEUILLE {len(self.client)} ")

    def faire_depot_client(self, id_compte, description, montant, date_op, id_cat):
        from datamanagement import depot

        description_complete = f"{description} (Par Banquier {self.nom})"
        print(
            f"le Banquier {self.nom} a effectué un depot de {montant} € sur le compte {id_compte}"
        )
        depot(id_compte, montant, date_op, description_complete, id_cat)

    def faire_retrait_client(self, id_compte, montant, description, id_cat, date_op):
        from datamanagement import retrait

        description_complete = f"{description} (Par Banquier {self.nom})"
        retrait(id_compte, montant, description_complete, id_cat, date_op)


class Transaction:
    def __init__(
        self,
        id,
        categories,
        description,
        montant,
        date,
        type,
        emetteur,
        beneficiaire,
        user_id=None,
    ):
        self.id = id
        self.categories = categories
        self.description = description
        self.montant = montant
        self.date = date
        self.type = type
        self.emetteur = emetteur
        self.beneficiaire = beneficiaire
        self.user_id = user_id

    def __str__(self):
        return f"Le {self.type} d'un {self.montant} en date du {self.date} depuis le compte {self.emetteur} vers {self.beneficiaire}, dépense de {self.categories}"

    def traiter_operations(type, montant_actuel, montant_operation):
        if type == "Retrait":
            return montant_actuel - montant_operation
        elif type == "Depot":
            return montant_actuel + montant_operation
        elif type == "Transfert":
            pass
            return montant_actuel
