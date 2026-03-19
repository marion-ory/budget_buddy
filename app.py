# connection
from config import get_connection

# securite & login
from login import login, inscription

# gestion de données
from datamanagement import (
    charger_comptes_utilisateurs,
    recuperer_portefeuille_banquier,
    virement,
    depot,
    retrait,
)

# SQL objet python
from engine import Client, Banquier, CompteBancaires
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# App
class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Buddy")
        self.geometry("1000x700")

        # BDD
        self.users = {}  # {email: {"nom": ..., "prenom": ..., "mdp": ...}}
        self.current_user = None

        # fausses données de transactions pour l'affichage
        self.transactions_cc = [
            {
                "id": 1,
                "date": "2026-03-10",
                "desc": "Courses Carrefour",
                "cat": "Loisir",
                "type": "Retrait",
                "montant": -45.80,
                "dest": "Carrefour",
            },
            {
                "id": 2,
                "date": "2026-03-11",
                "desc": "Salaire",
                "cat": "Revenu",
                "type": "Dépôt",
                "montant": 2500.00,
                "dest": "Entreprise",
            },
            {
                "id": 3,
                "date": "2026-03-12",
                "desc": "Restaurant",
                "cat": "Repas",
                "type": "Retrait",
                "montant": -30.00,
                "dest": "McDo",
            },
        ]
        self.transactions_annexe = [
            {"id": 1, "date": "2026-03-09", "desc": "Virement vers épargne"},
            {"id": 2, "date": "2026-03-13", "desc": "Intérêts épargne"},
        ]

        # Création des pages
        self.page_menu = PageMenu(self)
        self.page_login = PageLogin(self)
        self.page_register = PageRegister(self)
        self.page_home = PageHome(self)
        self.page_history = PageHistory(self)

        # affichage
        self.show_page(self.page_menu)

    def show_page(self, page):
        """Affiche une page et masque les autres."""
        for p in (
            self.page_menu,
            self.page_login,
            self.page_register,
            self.page_home,
            self.page_history,
        ):
            p.pack_forget()
        page.pack(fill="both", expand=True)

    #  BDD ICI
    def register_user(self, nom, prenom, email, mdp, code=""):
        self.users[email] = {"nom": nom, "prenom": prenom, "mdp": mdp}
        print(f"Compte créé pour {prenom} {nom} ({email})")

    def login_user(self, email, mdp):
        user = self.users.get(email)
        if user and user["mdp"] == mdp:
            self.current_user = user
            return True
        return False
