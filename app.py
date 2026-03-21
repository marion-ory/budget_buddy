import customtkinter as ctk
from databank import setup_database
from config import get_connection

# 1. IMPORT DES PAGES
from pages.auth import PageMenu, PageLogin, PageRegister
from pages.home import PageHome
from pages.history import PageHistory
from pages.banker import PageBanquier

# 2. IMPORT DES LOGIQUES (Manu & Toi)
from login import login, inscription
from datamanagement import recuperer_client_complet, recuperer_banquier_complet
from engine import Banquier

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Buddy")
        self.geometry("1200x700")

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
        self.page_banquier = PageBanquier(self)
        self.show_page(self.page_menu)
        self.protocol("WM_DELETE_WINDOW", self.quitter)

    def quitter(self):
        self.destroy()
        import sys
        sys.exit(0)

    def show_page(self, page):
        # 1. On cache TOUTES les pages d'un coup
        for p in [
            self.page_menu,
            self.page_login,
            self.page_register,
            self.page_home,
            self.page_history,
            self.page_banquier,
        ]:
            if p:
                p.pack_forget()

        # 2. On affiche UNIQUEMENT la page demandée
        # expand=True et fill="both" permettent à la page de prendre TOUTE la place
        page.pack(expand=True, fill="both")

        # 3. On rafraîchit les données si besoin
        if hasattr(page, "refresh_data"):
            page.refresh_data()

    # --- CONNEXION À LA VRAIE BDD (Vérifie bien l'alignement ici !) ---
    def login_user(self, email, mdp):
        user_info = login(email, mdp)

        if user_info:
            user_id = user_info.get("id") or user_info.get("ID")
            role = user_info.get("role")

            if role == "Client":
                self.user_obj = recuperer_client_complet(user_id)
            elif role == "Banquier":
                from datamanagement import recuperer_banquier_complet
                self.user_obj = recuperer_banquier_complet(user_id)

            if self.user_obj:
                print(f"DEBUG APP: {self.user_obj.prenom} chargé, rôle={role}")
                return True

        return False

if __name__ == "__main__":
    print("Vérification de la base de données...")
    setup_database()

    print("Création de l'app...")
    app = BudgetBuddyApp()
    print("Lancement mainloop...")
    app.mainloop()
