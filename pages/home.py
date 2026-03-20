import customtkinter as ctk
from datetime import datetime

# On importe tes styles depuis setting.py
from setting import (
    BG_COLOR,
    CARD_BG,
    ACCENT_BLUE,
    TEXT_WHITE,
    TEXT_GRAY,
    FONT_TITLE,
    FONT_BODY,
    FONT_MONEY,
    RADIUS,
    BTN_HEIGHT,
)

# ------ DIALOGUE OPERATION (DEPOT / RETRAIT / VIR INTERNE) __________________


class OperationDialog(ctk.CTkToplevel):
    def __init__(self, master, titre, callback):
        super().__init__(master)
        self.title(titre)
        self.geometry("350x450")
        self.callback = callback
        self.configure(fg_color=BG_COLOR)
        self.attributes("-topmost", True)
        self.grab_set()

        from datamanagement import recuperer_categories

        self.categories_data = recuperer_categories()
        # Liste des noms pour le menu déroulant
        self.categories_noms = [cat["Nom"] for cat in self.categories_data]

        ctk.CTkLabel(self, text=titre, font=FONT_TITLE).pack(pady=20)

        self.entry_montant = ctk.CTkEntry(
            self, placeholder_text="Montant (€)", width=220
        )
        self.entry_montant.pack(pady=10)

        self.entry_desc = ctk.CTkEntry(
            self, placeholder_text="Description (ex: Courses)", width=220
        )
        self.entry_desc.pack(pady=10)

        ctk.CTkLabel(
            self, text="Catégorie :", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(10, 0))
        self.combo_cat = ctk.CTkOptionMenu(
            self, values=self.categories_noms, width=220, fg_color=ACCENT_BLUE
        )
        self.combo_cat.pack(pady=10)

        self.btn_valider = ctk.CTkButton(
            self,
            text="Confirmer",
            fg_color=ACCENT_BLUE,
            height=40,
            command=self.valider,
        )
        self.btn_valider.pack(pady=30)

    def valider(self):
        mt = self.entry_montant.get().strip()
        desc = self.entry_desc.get().strip()
        cat_nom = self.combo_cat.get()

        # Trouver l'ID correspondant au nom sélectionné
        try:
            id_cat = next(c["ID"] for c in self.categories_data if c["Nom"] == cat_nom)
            if mt and desc:
                self.callback(mt, desc, id_cat)
                self.destroy()
            else:
                print("DEBUG: Champs montant ou description vides")
        except StopIteration:
            print("DEBUG: Catégorie non trouvée")


# --- FENÊTRE PERSONNALISÉE : VIREMENT PAR NOM/PRÉNOM ---
class VirementExterneDialog(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Nouveau Virement")
        self.geometry("350x380")
        self.callback = callback
        self.configure(fg_color=BG_COLOR)

        self.attributes("-topmost", True)
        self.grab_set()

        ctk.CTkLabel(self, text="Bénéficiaire Externe", font=FONT_TITLE).pack(pady=20)

        self.entry_nom = ctk.CTkEntry(
            self, placeholder_text="Nom du destinataire", width=220
        )
        self.entry_nom.pack(pady=10)

        self.entry_prenom = ctk.CTkEntry(
            self, placeholder_text="Prénom du destinataire", width=220
        )
        self.entry_prenom.pack(pady=10)

        self.entry_mt = ctk.CTkEntry(self, placeholder_text="Montant (€)", width=220)
        self.entry_mt.pack(pady=10)

        self.btn_valider = ctk.CTkButton(
            self,
            text="Envoyer l'argent",
            fg_color=ACCENT_BLUE,
            height=40,
            command=self.clic_envoyer,
        )
        self.btn_valider.pack(pady=25)

    def clic_envoyer(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        montant = self.entry_mt.get().strip()

        if nom and prenom and montant:
            self.callback(nom, prenom, montant)
            self.destroy()


# --- PAGE ACCUEIL PRINCIPALE ---
class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master

        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=FONT_TITLE, text_color=TEXT_GRAY
        )
        self.label_bienvenue.pack(pady=(30, 5), padx=30, anchor="w")

        self._creer_cartes_soldes()

        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(pady=25)

        btn_style = {
            "fg_color": ACCENT_BLUE,
            "hover_color": "#0056b3",
            "height": BTN_HEIGHT,
            "corner_radius": RADIUS,
            "width": 160,
        }

        ctk.CTkButton(
            self.frame_actions, text="➕ Dépôt", command=self.ouvrir_depot, **btn_style
        ).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(
            self.frame_actions,
            text="➖ Retrait",
            command=self.ouvrir_retrait,
            **btn_style,
        ).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(
            self.frame_actions,
            text="🔄 Vir. Interne",
            command=self.ouvrir_virement,
            **btn_style,
        ).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(
            self.frame_actions,
            text="💸 Vir. Externe",
            command=self.ouvrir_virement_externe,
            **btn_style,
        ).grid(row=1, column=1, padx=10, pady=10)

        self.btn_history = ctk.CTkButton(
            self.frame_actions,
            text="📜 Historique",
            **btn_style,
            command=lambda: self.master.show_page(self.master.page_history),
        )
        self.btn_history.grid(row=2, column=0, columnspan=2, pady=10)

        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=TEXT_GRAY,
            command=lambda: self.master.show_page(self.master.page_menu),
        )
        self.btn_logout.pack(side="bottom", pady=20)

    def _creer_cartes_soldes(self):
        self.card_cc = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        self.card_cc.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(
            self.card_cc, text="Compte Courant", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(15, 0), padx=20, anchor="w")
        self.label_solde_cc = ctk.CTkLabel(
            self.card_cc, text="0.00 €", font=FONT_MONEY, text_color=TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(5, 20), padx=20, anchor="w")

        self.card_annexe = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        self.card_annexe.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(
            self.card_annexe, text="Compte Annexe", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(15, 0), padx=20, anchor="w")
        self.label_solde_annexe = ctk.CTkLabel(
            self.card_annexe, text="0.00 €", font=FONT_TITLE, text_color=ACCENT_BLUE
        )
        self.label_solde_annexe.pack(pady=(5, 15), padx=20, anchor="w")

    def refresh_data(self):
        user = self.master.user_obj
        if user and user.comptes:
            self.label_bienvenue.configure(text=f"Bonjour {user.prenom},")
            self.label_solde_cc.configure(
                text=f"{user.comptes[0].solde:,.2f} €".replace(",", " ")
            )
            if len(user.comptes) > 1:
                self.label_solde_annexe.configure(
                    text=f"{user.comptes[1].solde:,.2f} €".replace(",", " ")
                )

    # --- ACTIONS ---

    def ouvrir_depot(self):
        OperationDialog(self, "Effectuer un Dépôt", self.traiter_depot)

    def traiter_depot(self, montant, description, id_cat):
        try:
            if self.master.user_obj.comptes[0].effectuer_depot(
                float(montant), description, id_cat
            ):
                self.refresh_data()
        except ValueError:
            print("Montant invalide")

    def ouvrir_retrait(self):
        OperationDialog(self, "Effectuer un Retrait", self.traiter_retrait)

    def traiter_retrait(self, montant, description, id_cat):
        try:
            if self.master.user_obj.comptes[0].effectuer_retrait(
                float(montant), description, id_cat
            ):
                self.refresh_data()
        except ValueError:
            print("Montant invalide")

    def ouvrir_virement(self):
        if len(self.master.user_obj.comptes) < 2:
            return
        OperationDialog(self, "Virement Interne", self.traiter_virement_interne)

    def traiter_virement_interne(self, montant, description, id_cat):
        try:
            src, dest = self.master.user_obj.comptes[0], self.master.user_obj.comptes[1]
            if src.effectuer_transfert(float(montant), dest, description, id_cat):
                self.refresh_data()
        except ValueError:
            print("Montant invalide")

    def ouvrir_virement_externe(self):
        VirementExterneDialog(self, self.traiter_virement_externe)

    def traiter_virement_externe(self, nom, prenom, montant):
        from datamanagement import trouver_id_compte_par_nom

        id_dest = trouver_id_compte_par_nom(nom, prenom)
        if id_dest is None:
            print("❌ Erreur: Utilisateur introuvable.")
            return
        try:
            if self.master.user_obj.comptes[0].effectuer_transfert(
                float(montant), id_dest, f"Virement à {prenom} {nom}", id_cat=3
            ):
                self.refresh_data()
        except ValueError:
            print("❌ Erreur: Montant invalide")
