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
        self.users = {}          # {email: {"nom": ..., "prenom": ..., "mdp": ...}}
        self.current_user = None

        # fausses données de transactions pour l'affichage
        self.transactions_cc = [
            {"id": 1, "date": "2026-03-10", "desc": "Courses Carrefour", "cat": "Loisir", "type": "Retrait", "montant": -45.80, "dest": "Carrefour"},
            {"id": 2, "date": "2026-03-11", "desc": "Salaire", "cat": "Revenu", "type": "Dépôt", "montant": 2500.00, "dest": "Entreprise"},
            {"id": 3, "date": "2026-03-12", "desc": "Restaurant", "cat": "Repas", "type": "Retrait", "montant": -30.00, "dest": "McDo"},
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
        for p in (self.page_menu, self.page_login, self.page_register,
                  self.page_home, self.page_history):
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


# Menu
class PageMenu(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 32))
        title.pack(pady=40)

        btn_login = ctk.CTkButton(
            self,
            text="Connexion",
            height=45,
            width=220,
            command=lambda: master.show_page(master.page_login)
        )
        btn_login.pack(pady=10)

        btn_register = ctk.CTkButton(
            self,
            text="Inscription",
            height=45,
            width=220,
            command=lambda: master.show_page(master.page_register)
        )
        btn_register.pack(pady=10)


# Connexion
class PageLogin(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Connexion", font=("Arial", 28)).pack(pady=20)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=320, height=35)
        self.entry_email.pack(pady=10)

        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*", width=320, height=35)
        self.entry_mdp.pack(pady=10)

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        btn_login = ctk.CTkButton(self, text="Se connecter", width=200, height=40,
                                  command=self.valider_connexion)
        btn_login.pack(pady=20)

        btn_back = ctk.CTkButton(self, text="← Retour", width=150,
                                 command=lambda: master.show_page(master.page_menu))
        btn_back.pack(pady=10)

    def valider_connexion(self):
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()

        if self.master.login_user(email, mdp):
            # Maj aaccueil
            self.master.page_home.update_header()
            self.master.show_page(self.master.page_home)
        else:
            self.label_info.configure(text="Email ou mot de passe incorrect")


# Inscription
class PageRegister(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Inscription", font=("Arial", 28)).pack(pady=20)

        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Nom", width=320, height=35)
        self.entry_nom.pack(pady=8)

        self.entry_prenom = ctk.CTkEntry(self, placeholder_text="Prénom", width=320, height=35)
        self.entry_prenom.pack(pady=8)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=320, height=35)
        self.entry_email.pack(pady=8)

        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe (10+ caractères)", show="*",
                                      width=320, height=35)
        self.entry_mdp.pack(pady=8)

        self.entry_code = ctk.CTkEntry(self, placeholder_text="Code (optionnel)", width=320, height=35)
        self.entry_code.pack(pady=5)

        ctk.CTkLabel(
            self,
            text="À ne remplir que si vous avez reçu un code de la banque",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(0, 15))

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        btn_register = ctk.CTkButton(self, text="Créer mon compte", width=220, height=40,
                                     command=self.valider_inscription)
        btn_register.pack(pady=10)

        btn_back = ctk.CTkButton(self, text="← Retour", width=150,
                                 command=lambda: master.show_page(master.page_menu))
        btn_back.pack(pady=10)

    def valider_inscription(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()
        code = self.entry_code.get().strip()

        if not (nom and prenom and email and mdp):
            self.label_info.configure(text="Tous les champs sauf le code sont obligatoires")
            return

        if len(mdp) < 10:
            self.label_info.configure(text="Mot de passe trop court (10 caractères minimum)")
            return

        # SQL
        self.master.register_user(nom, prenom, email, mdp, code)

        # Connexion auto après inscription
        self.master.current_user = {"nom": nom, "prenom": prenom, "mdp": mdp}
        self.master.page_home.update_header()
        self.master.show_page(self.master.page_home)


#  Page 2
class PageHome(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        self.label_bienvenue = ctk.CTkLabel(self, text="Bienvenue", font=("Arial", 30))
        self.label_bienvenue.pack(pady=20)

        frame_soldes = ctk.CTkFrame(self)
        frame_soldes.pack(pady=10, padx=40, fill="x")

        # Compte courant
        ctk.CTkLabel(frame_soldes, text="Solde compte courant :", font=("Arial", 18)).grid(
            row=0, column=0, sticky="w", padx=20, pady=10
        )
        self.label_solde_cc = ctk.CTkLabel(frame_soldes, text="1 234,56 €", font=("Arial", 18))
        self.label_solde_cc.grid(row=0, column=1, sticky="w", padx=20, pady=10)

        # Annexes
        ctk.CTkLabel(frame_soldes, text="Annexe 1 :", font=("Arial", 16)).grid(
            row=1, column=0, sticky="w", padx=20, pady=5
        )
        self.label_annexe1 = ctk.CTkLabel(frame_soldes, text="2 500,00 €", font=("Arial", 16))
        self.label_annexe1.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        ctk.CTkLabel(frame_soldes, text="Annexe 2 :", font=("Arial", 16)).grid(
            row=2, column=0, sticky="w", padx=20, pady=5
        )
        self.label_annexe2 = ctk.CTkLabel(frame_soldes, text="800,00 €", font=("Arial", 16))
        self.label_annexe2.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        # Boutons bas
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=40)

        btn_history = ctk.CTkButton(
            btn_frame,
            text="Voir l'historique des comptes",
            width=240,
            height=40,
            command=lambda: master.show_page(master.page_history)
        )
        btn_history.grid(row=0, column=0, padx=10)

        btn_logout = ctk.CTkButton(
            btn_frame,
            text="Déconnexion",
            width=160,
            height=40,
            command=lambda: master.show_page(master.page_menu)
        )
        btn_logout.grid(row=0, column=1, padx=10)

    def update_header(self):
        user = self.master.current_user
        if user:
            self.label_bienvenue.configure(text=f"Bienvenue {user['prenom']} {user['nom']}")


#  Page 3
class PageHistory(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Historique des comptes", font=("Arial", 28)).pack(pady=20)

        #choisir le compte
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        self.btn_cc = ctk.CTkButton(btn_frame, text="Compte courant", width=160,
                                    command=self.show_compte_courant)
        self.btn_cc.grid(row=0, column=0, padx=10)

        self.btn_annexe = ctk.CTkButton(btn_frame, text="Compte annexe", width=160,
                                        command=self.show_compte_annexe)
        self.btn_annexe.grid(row=0, column=1, padx=10)

        # scroll
        self.scroll = ctk.CTkScrollableFrame(self, width=900, height=450)
        self.scroll.pack(pady=20, padx=40, fill="both", expand=True)

        #  retour
        btn_back = ctk.CTkButton(self, text="← Retour à l'accueil",
                                 command=lambda: master.show_page(master.page_home))
        btn_back.pack(pady=10)

        #  compte courant
        self.show_compte_courant()

    def clear_scroll(self):
        for child in self.scroll.winfo_children():
            child.destroy()

    def show_compte_courant(self):
        self.clear_scroll()

        # En-tête
        header = "ID | DATE       | DESCRIPTION        | CATEGORIE   | TYPE    | MONTANT   | DESTINATAIRE"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

    
        for t in self.master.transactions_cc:
            ligne = f"{t['id']:2} | {t['date']:10} | {t['desc'][:18]:18} | {t['cat'][:10]:10} | {t['type'][:7]:7} | {t['montant']:8.2f}€ | {t['dest']}"
            color = "green" if t["montant"] > 0 else "red"
            ctk.CTkLabel(self.scroll, text=ligne, font=("Consolas", 12), text_color=color).pack(
                anchor="w", padx=10, pady=2
            )

    def show_compte_annexe(self):
        self.clear_scroll()

        header = "ID | DATE       | DESCRIPTION"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        for t in self.master.transactions_annexe:
            ligne = f"{t['id']:2} | {t['date']:10} | {t['desc']}"
            ctk.CTkLabel(self.scroll, text=ligne, font=("Consolas", 12)).pack(
                anchor="w", padx=10, pady=2
            )


if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()
