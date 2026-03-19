import customtkinter as ctk
from databank import setup_database
from config import get_connection

# 1. IMPORT DES PAGES
from pages.auth import PageMenu, PageLogin, PageRegister
from pages.home import PageHome
from pages.history import PageHistory

# 2. IMPORT DES LOGIQUES (Manu & Toi)
from login import login, inscription
from datamanagement import (
    charger_comptes_utilisateurs,
    recuperer_portefeuille_banquier,
    virement,
    depot,
    retrait,
)
from engine import Client, Banquier, CompteBancaires

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Buddy")
        self.geometry("1000x700")

        # Session utilisateur
        self.current_user = None  # Contiendra le dictionnaire user de la BDD
        self.user_obj = None  # Contiendra l'objet Client ou Banquier (engine.py)

        # Création des pages
        self.page_menu = PageMenu(self)
        self.page_login = PageLogin(self)
        self.page_register = PageRegister(self)
        self.page_home = PageHome(self)
        self.page_history = PageHistory(self)

        self.show_page(self.page_menu)

    def show_page(self, page):
        for p in (
            self.page_menu,
            self.page_login,
            self.page_register,
            self.page_home,
            self.page_history,
        ):
            p.pack_forget()
        page.pack(fill="both", expand=True)

    # --- CONNEXION À LA VRAIE BDD ---
    def login_user(self, email, mdp):
        # On utilise la fonction de Manu qui cherche en BDD
        user_info = login(email, mdp)

        if user_info:
            self.current_user = user_info
            # Ici, tu pourras appeler ta fonction pour charger les comptes
            # self.charger_donnees_utilisateur()
            return True
        return False

    def register_user(self, nom, prenom, email, mdp, code=""):
        # On utilise la fonction d'inscription SQL
        return inscription(nom, prenom, email, "Adresse par défaut", mdp, code)


if __name__ == "__main__":
    print("Vérification de la base de données...")
    setup_database()

    app = BudgetBuddyApp()
    app.mainloop()
