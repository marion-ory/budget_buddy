import customtkinter as ctk

# On importe tes styles depuis setting.py
from setting import (
    BG_COLOR,
    CARD_BG,
    ACCENT_BLUE,
    TEXT_WHITE,
    TEXT_GRAY,
    SUCCESS_GREEN,
    FONT_MAIN_BOLD,
    FONT_TITLE,
    FONT_BODY,
    FONT_MONEY,
    RADIUS,
    BTN_HEIGHT,
)


# RETOUR À LA CLASSE CLASSIQUE (Plus d'erreur de Canvas)
class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)

        # --- EN-TÊTE / BIENVENUE ---
        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=FONT_TITLE, text_color=TEXT_GRAY
        )
        self.label_bienvenue.pack(pady=(30, 5), padx=30, anchor="w")

        # --- CARTE DU COMPTE COURANT ---
        self.card_cc = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        self.card_cc.pack(pady=10, padx=20, fill="x")

        self.label_titre_cc = ctk.CTkLabel(
            self.card_cc, text="Compte Courant", font=FONT_BODY, text_color=TEXT_GRAY
        )
        self.label_titre_cc.pack(pady=(15, 0), padx=20, anchor="w")

        self.label_solde_cc = ctk.CTkLabel(
            self.card_cc, text="0.00 €", font=FONT_MONEY, text_color=TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(5, 20), padx=20, anchor="w")

        # --- CARTE DU COMPTE ANNEXE ---
        self.card_annexe = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        self.card_annexe.pack(pady=10, padx=20, fill="x")

        self.label_titre_annexe = ctk.CTkLabel(
            self.card_annexe, text="Compte Annexe", font=FONT_BODY, text_color=TEXT_GRAY
        )
        self.label_titre_annexe.pack(pady=(15, 0), padx=20, anchor="w")

        self.label_solde_annexe = ctk.CTkLabel(
            self.card_annexe, text="0.00 €", font=FONT_TITLE, text_color=ACCENT_BLUE
        )
        self.label_solde_annexe.pack(pady=(5, 15), padx=20, anchor="w")

        # --- GRILLE DE BOUTONS D'ACTION ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(pady=25)

        btn_style = {
            "fg_color": ACCENT_BLUE,
            "hover_color": "#0056b3",
            "height": BTN_HEIGHT,
            "corner_radius": RADIUS,
        }

        self.btn_depot = ctk.CTkButton(
            self.frame_actions,
            text="➕ Dépôt",
            width=150,
            **btn_style,
            command=self.ouvrir_depot,
        )
        self.btn_depot.grid(row=0, column=0, padx=10, pady=10)

        self.btn_retrait = ctk.CTkButton(
            self.frame_actions,
            text="➖ Retrait",
            width=150,
            **btn_style,
            command=self.ouvrir_retrait,
        )
        self.btn_retrait.grid(row=0, column=1, padx=10, pady=10)

        self.btn_virement = ctk.CTkButton(
            self.frame_actions,
            text="💸 Virement",
            width=150,
            **btn_style,
            command=self.ouvrir_virement,
        )
        self.btn_virement.grid(row=1, column=0, padx=10, pady=10)

        self.btn_history = ctk.CTkButton(
            self.frame_actions,
            text="📜 Historique",
            width=150,
            **btn_style,
            command=lambda: self.master.show_page(self.master.page_history),
        )
        self.btn_history.grid(row=1, column=1, padx=10, pady=10)

        # Bouton Déconnexion
        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=TEXT_GRAY,
            hover_color="#333333",
            height=30,
            command=lambda: self.master.show_page(self.master.page_menu),
        )
        self.btn_logout.pack(side="bottom", pady=20)

    def refresh_data(self):
        user = self.master.user_obj
        if user and hasattr(user, "comptes") and len(user.comptes) > 0:
            self.label_bienvenue.configure(text=f"Bonjour {user.prenom},")

            solde_cc = user.comptes[0].solde
            self.label_solde_cc.configure(text=f"{solde_cc:,.2f} €".replace(",", " "))

            if len(user.comptes) > 1:
                solde_annexe = user.comptes[1].solde
                self.label_solde_annexe.configure(
                    text=f"{solde_annexe:,.2f} €".replace(",", " ")
                )

            print(f"DEBUG HOME: Dashboard mis à jour pour {user.prenom}")
        else:
            print("DEBUG HOME: Données utilisateur manquantes")

    def ouvrir_depot(self):
        dialog = ctk.CTkInputDialog(text="Montant à déposer :", title="Dépôt")
        montant_saisi = dialog.get_input()
        if montant_saisi:
            try:
                valeur = float(montant_saisi)
                # On récupère l'objet compte (qui est une instance de CompteBancaires)
                compte = self.master.user_obj.comptes[0]

                # On utilise la méthode de ta classe Engine !
                if compte.effectuer_depot(valeur):
                    # Pas besoin de faire += valeur ici, ta classe le fait déjà !
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

    def ouvrir_retrait(self):
        dialog = ctk.CTkInputDialog(text="Montant à retirer :", title="Retrait")
        montant_saisi = dialog.get_input()
        if montant_saisi:
            try:
                valeur = float(montant_saisi)
                compte = self.master.user_obj.comptes[0]

                # On utilise la méthode de ta classe Engine !
                if compte.effectuer_retrait(valeur):
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

    def ouvrir_virement(self):
        # Pour un virement interne simple (Courant -> Annexe)
        if len(self.master.user_obj.comptes) < 2:
            print("Action impossible : un seul compte trouvé.")
            return

        dialog = ctk.CTkInputDialog(
            text="Montant (Courant -> Annexe) :", title="Virement"
        )
        montant_saisi = dialog.get_input()
        if montant_saisi:
            try:
                valeur = float(montant_saisi)
                compte_src = self.master.user_obj.comptes[0]
                compte_dest = self.master.user_obj.comptes[1]

                # On utilise la méthode de ta classe Engine !
                if compte_src.effectuer_transfert(valeur, compte_dest):
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

                # --- PRÉPARATION DES DONNÉES PAR DÉFAUT ---
                date_op = datetime.now().strftime("%Y-%m-%d")
                id_cat = 1  # ID de catégorie par défaut (ex: 'Transfert')
                desc = "Virement depuis l'application"

                # --- CAS INTERNE ---
                if destinataire.upper() == "ANNEXE":
                    if len(user.comptes) < 2:
                        print("Erreur : Aucun compte annexe.")
                        return
                    id_beneficiaire = user.comptes[1].id_compte

                    # APPEL À TA FONCTION (Attention à l'ordre des arguments !)
                    virement(
                        montant, desc, id_cat, date_op, id_emetteur, id_beneficiaire
                    )

                    # Mise à jour visuelle locale
                    user.comptes[0].solde -= montant
                    user.comptes[1].solde += montant
                    self.refresh_data()

                # --- CAS EXTERNE ---
                else:
                    id_beneficiaire = int(
                        destinataire
                    )  # On suppose que c'est un ID (ex: 14)

                    virement(
                        montant, desc, id_cat, date_op, id_emetteur, id_beneficiaire
                    )

                    # Mise à jour visuelle locale
                    user.comptes[0].solde -= montant
                    self.refresh_data()

            except ValueError:
                print("Erreur : Entrez des nombres valides (ID et Montant)")
            except Exception as e:
                print(f"Erreur lors du virement : {e}")
