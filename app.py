import customtkinter as ctk
from databank import setup_database
from config import get_connection
from pages.home import PageHome

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
    recuperer_client_complet,
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
        self.transactions_cc = []  # Liste vide par défaut pour éviter le crash
        self.transactions_annexe = []
        self.page_history = PageHistory(self)

        self.show_page(self.page_menu)

    def show_page(self, page):
        # ... (ton code actuel qui cache les pages)
        page.pack(fill="both", expand=True)
        if hasattr(page, "refresh_data"):
            page.refresh_data()

    # --- CONNEXION À LA VRAIE BDD (Vérifie bien l'alignement ici !) ---
    def login_user(self, email, mdp):
        # 1. On vérifie les identifiants via Manu
        user_info = login(email, mdp)

        if user_info:
            # On récupère l'ID
            user_id = user_info.get("id") or user_info.get("ID")

            # 2. On transforme le dict en OBJET Client (via datamanagement)
            self.user_obj = recuperer_client_complet(user_id)

            if self.user_obj:
                # IMPORTANT : On lie l'objet à l'application
                # La page home pourra alors lire self.master.user_obj
                print(
                    f"DEBUG APP: {self.user_obj.prenom} chargé avec {len(self.user_obj.comptes)} comptes."
                )
                return True

        return False


# if __name__ == "__main__":
#     print("Vérification de la base de données...")
#     setup_database()

#     app = BudgetBuddyApp()
#     app.mainloop()
if __name__ == "__main__":
    print("Vérification de la base de données...")
    # setup_database()  <-- METS UN # DEVANT POUR TESTER

    print("Création de l'app...")
    app = BudgetBuddyApp()
    print("Lancement mainloop...")
    app.mainloop()
