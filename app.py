import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy")
        self.geometry("500x500")
        
        # Simulation base de données (ton équipe mettra SQL ici)
        self.users = {}  # {"email": {"nom": "", "prenom": "", "mdp": ""}}
        self.current_user = None
        
        # Toutes les pages
        self.page_menu = PageMenu(self)
        self.page_connexion = PageConnexion(self)
        self.page_inscription = PageInscription(self)
        self.page_accueil = PageAccueil(self)
        
        self.show_page(self.page_menu)

    def show_page(self, page):
        # Cache toutes les pages
        for p in [self.page_menu, self.page_connexion, self.page_inscription, self.page_accueil]:
            p.pack_forget()
        page.pack(fill="both", expand=True)

    def register_user(self, nom, prenom, email, mdp, code=""):
        """Crée un utilisateur (simulation BDD)"""
        self.users[email] = {
            "nom": nom,
            "prenom": prenom, 
            "mdp": mdp  # en vrai : hash du mdp !
        }
        print(f" Compte créé : {prenom} {nom} ({email})")

    def login_user(self, email, mdp):
        """Vérifie connexion (simulation BDD)"""
        if email in self.users and self.users[email]["mdp"] == mdp:
            self.current_user = self.users[email]
            return True
        return False

# Page 1 : Menu principal
class PageMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 28)).pack(pady=40)
        ctk.CTkButton(self, text=" Connexion", 
                     command=lambda: master.show_page(master.page_connexion),
                     height=40, font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(self, text=" Inscription", 
                     command=lambda: master.show_page(master.page_inscription),
                     height=40, font=("Arial", 16)).pack(pady=10)

# Page 1.1 : Connexion  
class PageConnexion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        ctk.CTkLabel(self, text="Connexion", font=("Arial", 24)).pack(pady=30)
        
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=300, height=35)
        self.entry_email.pack(pady=10)
        
        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*", width=300, height=35)
        self.entry_mdp.pack(pady=10)
        
        btn_ok = ctk.CTkButton(self, text="Se connecter", 
                              command=self.valider_connexion, width=200, height=35)
        btn_ok.pack(pady=20)
        
        ctk.CTkButton(self, text="← Retour", 
                     command=lambda: master.show_page(master.page_menu)).pack()

    def valider_connexion(self):
        email = self.entry_email.get()
        mdp = self.entry_mdp.get()
        
        if self.master.login_user(email, mdp):
            print(f" Connexion réussie : {email}")
            self.master.page_accueil.update()
            self.master.show_page(self.master.page_accueil)
        else:
            ctk.CTkLabel(self, text=" Email ou mot de passe incorrect", 
                        text_color="red", font=("Arial", 16)).pack(pady=10)

# Page 1.2 : INSCRIPTION COMPLÈTE (NOUVEAU !)
class PageInscription(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        ctk.CTkLabel(self, text="Inscription", font=("Arial", 24)).pack(pady=20)
        
        # Champs obligatoires
        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Nom", width=300, height=35)
        self.entry_nom.pack(pady=8)
        self.entry_prenom = ctk.CTkEntry(self, placeholder_text="Prénom", width=300, height=35)
        self.entry_prenom.pack(pady=8)
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=300, height=35)
        self.entry_email.pack(pady=8)
        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe (10+ caractères)", show="*", width=300, height=35)
        self.entry_mdp.pack(pady=8)
        
        # Champ optionnel CODE
        self.entry_code = ctk.CTkEntry(self, placeholder_text="Code banque (optionnel)", width=300, height=35)
        self.entry_code.pack(pady=5)
        ctk.CTkLabel(self, text="À remplir seulement si vous avez reçu un code de la banque",
                    font=("Arial", 12), text_color="gray").pack(pady=(0,15))
        
        btn_ok = ctk.CTkButton(self, text="Créer mon compte", 
                              command=self.valider_inscription, width=200, height=35)
        btn_ok.pack(pady=10)
        
        ctk.CTkButton(self, text="← Retour", 
                     command=lambda: master.show_page(master.page_menu)).pack()

    def valider_inscription(self):
        nom = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        email = self.entry_email.get()
        mdp = self.entry_mdp.get()
        code = self.entry_code.get()
        
        # Vérifications simples
        if not all([nom, prenom, email, mdp]):
            ctk.CTkLabel(self, text=" Remplissez tous les champs obligatoires", 
                        text_color="red", font=("Arial", 16)).pack(pady=10)
            return
        
        if len(mdp) < 10:
            ctk.CTkLabel(self, text=" Mot de passe trop court (10+ caractères)", 
                        text_color="red", font=("Arial", 16)).pack(pady=10)
            return
        
        # Crée l'utilisateur
        self.master.register_user(nom, prenom, email, mdp, code)
        
        # Simulation : se connecte automatiquement après inscription
        self.master.current_user = {"nom": nom, "prenom": prenom}
        self.master.page_accueil.update()
        self.master.show_page(self.master.page_accueil)

# Page 2 : Accueil
class PageAccueil(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        self.label_bienvenue = ctk.CTkLabel(self, text="Bienvenue !", font=("Arial", 24))
        self.label_bienvenue.pack(pady=30)
        
        # Soldes
        frame_soldes = ctk.CTkFrame(self)
        frame_soldes.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(frame_soldes, text=" Compte courant :", font=("Arial", 16)).pack(anchor="w", padx=20, pady=10)
        self.label_solde_cc = ctk.CTkLabel(frame_soldes, text="1 234,56 €", font=("Arial", 20))
        self.label_solde_cc.pack(anchor="w", padx=20)
        
        ctk.CTkLabel(frame_soldes, text=" Annexe 1 :", font=("Arial", 16)).pack(anchor="w", padx=20, pady=(20,5))
        self.label_annexe1 = ctk.CTkLabel(frame_soldes, text="2 500,00 €", font=("Arial", 16))
        self.label_annexe1.pack(anchor="w", padx=20)
        
        ctk.CTkLabel(frame_soldes, text=" Annexe 2 :", font=("Arial", 16)).pack(anchor="w", padx=20, pady=(10,5))
        self.label_annexe2 = ctk.CTkLabel(frame_soldes, text="800,00 €", font=("Arial", 16))
        self.label_annexe2.pack(anchor="w", padx=20)
        
        # Boutons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=30)
        ctk.CTkButton(btn_frame, text=" Historique", width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=" Déconnexion", 
                     command=lambda: master.show_page(master.page_menu),
                     width=120).pack(side="left", padx=10)

    def update(self):
        if self.master.current_user:
            nom = self.master.current_user.get("nom", "")
            prenom = self.master.current_user.get("prenom", "")
            self.label_bienvenue.configure(text=f"Bienvenue {prenom} {nom} !")

if __name__ == "__main__":
    app = App()
    app.mainloop()
