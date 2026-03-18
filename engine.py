from config import *
from datamanagement import historique, virement, retrait, depot, trier_par


class CompteBancaires:
    def __init__(self, id, user_id, typecompte, solde_initial):
        self.id = id
        self.user_id = user_id
        self.typecompte = typecompte
        self.solde_initial = solde_initial
        self.transactions = []

    def calculer_solde(self):
        solde = self.solde_initial
        for t in self.transactions:
            match t.type:
                case "depot":
                    solde += t.montant
                case "retrait":
                    solde -= t.montant
                case "transfert":
                    # Si je(emetteur) passe le virement on soustrait le montant à mon compte (emetteur)
                    if t.emetteur == self.user_id:
                        solde -= t.montant
                    # Si je (beneficiaire )== à mon user id alors on ajoute la somme
                    elif t.beneficiaire == self.user_id:
                        solde += t.montant
                case _:
                    print(f"Type de transaction inconnu : {t.type}")
        return solde

    def peut_faire_transfert(self, destination_type):

        match self.typecompte:
            case "courant":
                return True
            case "annexe":
                if destination_type == "courant":  # uniquement vers compte courant
                    return True
                else:
                    print(
                        "Erreur: Un compte annexe transfère uniquement vers le compte courant"
                    )
                    return False
            case _:
                return False

    def effectuer_transfert(self, montant, compte_destination):
        if self.peut_faire_transfert(montant, compte_destination.typecompte):
            if self.calculer_solde() >= montant:
                print("Transfert autorisé et effectué.")
                # Ici, tu ajouteras la création de l'objet Transaction
            else:
                print("Solde insuffisant.")


class Users:
    def __init__(self, id, nom, prenom, mail, mdp, adresse, role):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.mdp = mdp
        self.adresse = adresse
        self.role = role


class Client(Users):
    def __init__(self, id, nom, prenom, email, mdp, id_banquier):
        super().__init__(id, nom, prenom, email, mdp, role="client")
        self.id_banquier = id_banquier

    def faire_virement(self, montant, description, id_cat, date_op, id_beneficiaire):
        print(f"Demande de virement {montant} par {self.nom}")
        virement(montant, description, id_cat, date_op, self.id, id_beneficiaire)

    def faire_depot(self, montant, description, id_cat, date_op):
        print(f"Votre depot de {montant} € a été pris en compte")
        depot(self.id, montant, date_op, description, id_cat)

    def faire_retrait(self, montant, description, id_cat, date_op):
        print(f"Vous avez effectué un retrait de  {montant} €")
        retrait(self.id, montant, description, id_cat, date_op)

    def charger_transactions_client(self):
        donnees_BDD = historique(self.id)
        self.transaction = []

        for ligne in donnees_BDD:
            nouvelles_transactions = Transaction(
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

            self.transaction.append(nouvelles_transactions)

        print(f"HISTORIQUE TRANSACTION :  {len(nouvelles_transactions)}")
        mon_client = Client(
            1, "Dupont", "Jean", "jean@mail.com", "mdp123", id_banquier=2
        )
        mon_client.charger_transactions_client()
        solde_actuel = mon_client.calculer_solde()
        print(f"Votre solde actuel est de {solde_actuel} €")


class Banquier(Users):
    def __init__(self, id, nom, prenom, email, mdp, titre):
        super().__init__(id, nom, prenom, email, mdp, role="banquier")
        self.titre = titre

    def faire_virement(
        self, id_emetteur, id_beneficaire, montant, id_cat, date_op, description
    ):
        # Le banquier a le privilège de choisir le compte émetteur (celui de ses clients)
        print(
            f"Le banquier {self.nom} effectue un virement de {montant} depuis le compte {compte_emetteur} vers le beneficiaire {compte_dest}"
        )
        virement(montant, description, id_cat, date_op, id_emetteur, id_beneficaire)

    def modifier_user(self, user_id, nouvelles_infos):
        print(f"Modification de l'utilisateur {user_id} par le banquier.")


class Transaction:
    def __init__(
        self,
        id,
        description,
        montant,
        date,
        emetteur,
        beneficiaire,
        type,
        user_id,
        categories,
    ):
        self.id = id
        self.description = description
        self.montant = montant
        self.date = date
        self.emetteur = emetteur
        self.beneficiaire = beneficiaire
        self.type = type
        self.user_id = user_id
        self.categories = categories

    def __str__(self):
        return f"Le {self.type} d'un {self.montant} en date du {self.date} depuis le compte {self.emetteur} vers {self.beneficiaire}, dépense de {self.categories}"

    def traiter_operations(type, montant_actuel, montant_operation):
        if type == "retrait":
            return montant_actuel - montant_operation
        elif type == "depot":
            return montant_actuel + montant_operation
        elif type == "transfert":
            pass
            return montant_actuel
