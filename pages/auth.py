import hashlib
import customtkinter as ctk

# Importation des fonctions logiques
from login import login, inscription, verifier_banquier


# Connexion
class PageLogin(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Connexion", font=("Arial", 28)).pack(pady=20)

        self.entry_email = ctk.CTkEntry(
            self, placeholder_text="Adresse email", width=320, height=35
        )
        self.entry_email.pack(pady=10)

        self.entry_mdp = ctk.CTkEntry(
            self, placeholder_text="Mot de passe", show="*", width=320, height=35
        )
        self.entry_mdp.pack(pady=10)

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        btn_login = ctk.CTkButton(
            self,
            text="Se connecter",
            width=200,
            height=40,
            command=self.valider_connexion,
        )
        btn_login.pack(pady=20)

        btn_back = ctk.CTkButton(
            self,
            text="← Retour",
            width=150,
            command=lambda: master.show_page(master.page_menu),
        )
        btn_back.pack(pady=10)

    def valider_connexion(self):
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()

        # 1. On utilise la fonction de app.py qui fait TOUT le travail
        # (Vérification MDP + Chargement de l'OBJET avec ses comptes)
        if self.master.login_user(email, mdp):

            # 2. Une fois que l'objet est chargé dans self.master.user_obj,
            # on demande à la page home de se mettre à jour
            self.master.page_home.refresh_data()

            # 3. On affiche la page
            self.master.show_page(self.master.page_home)
        else:
            # Petit message d'erreur si ça rate
            if hasattr(self, "label_info"):
                self.label_info.configure(text="Email ou mot de passe incorrect")
            else:
                print("Erreur : Email ou mot de passe incorrect")


class PageRegister(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Inscription", font=("Arial", 28)).pack(pady=20)

        self.entry_nom = ctk.CTkEntry(
            self, placeholder_text="Nom", width=320, height=35
        )
        self.entry_nom.pack(pady=8)

        self.entry_prenom = ctk.CTkEntry(
            self, placeholder_text="Prénom", width=320, height=35
        )
        self.entry_prenom.pack(pady=8)

        self.entry_email = ctk.CTkEntry(
            self, placeholder_text="Adresse email", width=320, height=35
        )
        self.entry_email.pack(pady=8)

        self.entry_mdp = ctk.CTkEntry(
            self,
            placeholder_text="Mot de passe (10+ caractères)",
            show="*",
            width=320,
            height=35,
        )
        self.entry_mdp.pack(pady=8)

        self.entry_code = ctk.CTkEntry(
            self, placeholder_text="Code (optionnel)", width=320, height=35
        )
        self.entry_code.pack(pady=5)

        ctk.CTkLabel(
            self,
            text="À ne remplir que si vous avez reçu un code de la banque",
            font=("Arial", 12),
            text_color="gray",
        ).pack(pady=(0, 15))

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        btn_register = ctk.CTkButton(
            self,
            text="Créer mon compte",
            width=220,
            height=40,
            command=self.valider_inscription,
        )
        btn_register.pack(pady=10)

        btn_back = ctk.CTkButton(
            self,
            text="← Retour",
            width=150,
            command=lambda: master.show_page(master.page_menu),
        )
        btn_back.pack(pady=10)

    def valider_inscription(self):
        # 1. Récupération des données saisies
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()
        code = self.entry_code.get().strip()

        # 2. Vérifications de base (Champs vides)
        if not (nom and prenom and email and mdp):
            self.label_info.configure(
                text="Tous les champs sauf le code sont obligatoires", text_color="red"
            )
            return

        # 3. Vérification de la sécurité (Longueur du MDP)
        if len(mdp) < 10:
            self.label_info.configure(
                text="Mot de passe trop court (10 caractères minimum)", text_color="red"
            )
            return

        # 4. Tentative d'inscription dans la BDD
        # Note : On envoie une adresse vide "" par défaut
        if inscription(nom, prenom, email, "", mdp, code):

            # 5. AUTO-LOGIN : Si l'inscription réussit, on connecte l'utilisateur direct
            user_info = login(email, mdp)

            if user_info:
                # On stocke les infos dans l'objet global de l'app
                self.master.user_obj = user_info

                # On déclenche la mise à jour des labels (Bonjour + Soldes)
                self.master.page_home.refresh_data()

                # On bascule enfin sur l'écran d'accueil
                self.master.show_page(self.master.page_home)
        else:
            # Si l'email existe déjà ou erreur SQL
            self.label_info.configure(
                text="Erreur : Cet email est déjà utilisé.", text_color="orange"
            )

        # Appel SQL avec hachage
        if inscription(nom, prenom, email, "", mdp, code):
            role = verifier_banquier(code)
            self.master.current_user = {"nom": nom, "prenom": prenom, "role": role}
            self.master.page_home.update_header()
            self.master.show_page(self.master.page_home)
        else:
            self.label_info.configure(
                text="Erreur lors de l'inscription (Email déjà pris ?)"
            )


# Menu
class PageMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 32))
        title.pack(pady=40)

        btn_login = ctk.CTkButton(
            self,
            text="Connexion",
            height=45,
            width=220,
            command=lambda: master.show_page(master.page_login),
        )
        btn_login.pack(pady=10)

        btn_register = ctk.CTkButton(
            self,
            text="Inscription",
            height=45,
            width=220,
            command=lambda: master.show_page(master.page_register),
        )
        btn_register.pack(pady=10)
