import customtkinter as ctk


#  Page 2
class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.label_bienvenue = ctk.CTkLabel(self, text="Bienvenue", font=("Arial", 30))
        self.label_bienvenue.pack(pady=20)

        frame_soldes = ctk.CTkFrame(self)
        frame_soldes.pack(pady=10, padx=40, fill="x")

        # Compte courant
        ctk.CTkLabel(
            frame_soldes, text="Solde compte courant :", font=("Arial", 18)
        ).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.label_solde_cc = ctk.CTkLabel(
            frame_soldes, text="1 234,56 €", font=("Arial", 18)
        )
        self.label_solde_cc.grid(row=0, column=1, sticky="w", padx=20, pady=10)

        # Annexes
        ctk.CTkLabel(frame_soldes, text="Annexe 1 :", font=("Arial", 16)).grid(
            row=1, column=0, sticky="w", padx=20, pady=5
        )
        self.label_annexe1 = ctk.CTkLabel(
            frame_soldes, text="2 500,00 €", font=("Arial", 16)
        )
        self.label_annexe1.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        ctk.CTkLabel(frame_soldes, text="Annexe 2 :", font=("Arial", 16)).grid(
            row=2, column=0, sticky="w", padx=20, pady=5
        )
        self.label_annexe2 = ctk.CTkLabel(
            frame_soldes, text="800,00 €", font=("Arial", 16)
        )
        self.label_annexe2.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        # Boutons bas
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=40)

        btn_history = ctk.CTkButton(
            btn_frame,
            text="Voir l'historique des comptes",
            width=240,
            height=40,
            command=lambda: master.show_page(master.page_history),
        )
        btn_history.grid(row=0, column=0, padx=10)

        btn_logout = ctk.CTkButton(
            btn_frame,
            text="Déconnexion",
            width=160,
            height=40,
            command=lambda: master.show_page(master.page_menu),
        )
        btn_logout.grid(row=0, column=1, padx=10)

    def update_header(self):
        user = self.master.current_user
        if user:
            self.label_bienvenue.configure(
                text=f"Bienvenue {user['prenom']} {user['nom']}"
            )


def refresh_data(self):
    """
    C'est ici que la magie opère.
    Cette fonction 'nettoie' et 'remplit' la page avec les vraies infos.
    """
    user = self.master.user_obj  # On récupère le client créé au login

    if user:
        # On met à jour le texte des labels existants
        self.label_bienvenue.configure(text=f"Ravi de vous revoir, {user.prenom} !")

        if user.comptes:
            # On prend le premier compte (Courant)
            solde_actuel = user.comptes[0].solde
            self.label_solde.configure(text=f"{solde_actuel} €")
        else:
            self.label_solde.configure(text="Aucun compte")

    print("DEBUG: Page Home rafraîchie avec les données BDD")
