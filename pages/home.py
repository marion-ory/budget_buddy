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


# --- FENÊTRE PERSONNALISÉE : VIREMENT PAR NOM/PRÉNOM ---
class VirementExterneDialog(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Nouveau Virement")
        self.geometry("350x350")
        self.callback = callback
        self.configure(fg_color=BG_COLOR)

        # On force la fenêtre au premier plan et on bloque l'arrière
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
            print(f"DEBUG: Envoi des données {nom} {prenom} {montant}€")
            self.callback(nom, prenom, montant)
            self.destroy()
        else:
            print("DEBUG: Formulaire incomplet")


# --- PAGE ACCUEIL PRINCIPALE ---
class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master

        # --- EN-TÊTE ---
        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=FONT_TITLE, text_color=TEXT_GRAY
        )
        self.label_bienvenue.pack(pady=(30, 5), padx=30, anchor="w")

        # --- CARTES DE SOLDES ---
        self._creer_cartes_soldes()

        # --- GRILLE DE BOUTONS D'ACTION ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(pady=25)

        btn_style = {
            "fg_color": ACCENT_BLUE,
            "hover_color": "#0056b3",
            "height": BTN_HEIGHT,
            "corner_radius": RADIUS,
            "width": 160,
        }

        # Ligne 1 : Dépôt / Retrait
        ctk.CTkButton(
            self.frame_actions, text="➕ Dépôt", command=self.ouvrir_depot, **btn_style
        ).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(
            self.frame_actions,
            text="➖ Retrait",
            command=self.ouvrir_retrait,
            **btn_style,
        ).grid(row=0, column=1, padx=10, pady=10)

        # Ligne 2 : Virement Interne / Virement Externe
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

        # Ligne 3 : Historique
        self.btn_history = ctk.CTkButton(
            self.frame_actions,
            text="📜 Historique",
            **btn_style,
            command=lambda: self.master.show_page(self.master.page_history),
        )
        self.btn_history.grid(row=2, column=0, columnspan=2, pady=10)

        # Bouton Déconnexion
        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=TEXT_GRAY,
            hover_color="#333333",
            command=lambda: self.master.show_page(self.master.page_menu),
        )
        self.btn_logout.pack(side="bottom", pady=20)

    def _creer_cartes_soldes(self):
        # Compte Courant
        self.card_cc = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        self.card_cc.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(
            self.card_cc, text="Compte Courant", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(15, 0), padx=20, anchor="w")
        self.label_solde_cc = ctk.CTkLabel(
            self.card_cc, text="0.00 €", font=FONT_MONEY, text_color=TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(5, 20), padx=20, anchor="w")

        # Compte Annexe
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

    def ouvrir_depot(self):
        m = ctk.CTkInputDialog(text="Montant à déposer :", title="Dépôt").get_input()
        if m:
            try:
                if self.master.user_obj.comptes[0].effectuer_depot(float(m)):
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

    def ouvrir_retrait(self):
        m = ctk.CTkInputDialog(text="Montant à retirer :", title="Retrait").get_input()
        if m:
            try:
                if self.master.user_obj.comptes[0].effectuer_retrait(float(m)):
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

    def ouvrir_virement(self):
        """Virement interne Courant -> Annexe"""
        if len(self.master.user_obj.comptes) < 2:
            return
        m = ctk.CTkInputDialog(text="Montant (Interne) :", title="Virement").get_input()
        if m:
            try:
                src, dest = (
                    self.master.user_obj.comptes[0],
                    self.master.user_obj.comptes[1],
                )
                if src.effectuer_transfert(float(m), dest):
                    self.refresh_data()
            except ValueError:
                print("Montant invalide")

    def ouvrir_virement_externe(self):
        """Déclenche l'ouverture de la nouvelle fenêtre de dialogue"""
        VirementExterneDialog(self, self.traiter_virement_externe)

    def traiter_virement_externe(self, nom, prenom, montant):
        """Recherche l'ID par nom et effectue l'opération"""
        from datamanagement import trouver_id_compte_par_nom

        print(f"DEBUG: Recherche de {prenom} {nom}...")
        id_dest = trouver_id_compte_par_nom(nom, prenom)

        if id_dest is None:
            print("❌ Erreur: Utilisateur introuvable.")
            return

        try:
            mt = float(montant)
            compte_source = self.master.user_obj.comptes[0]

            # Transfert avec ID trouvé
            if compte_source.effectuer_transfert(
                mt, id_dest, description=f"Virement à {prenom} {nom}"
            ):
                self.refresh_data()
                print("✅ Virement externe réussi !")
        except ValueError:
            print("❌ Erreur: Montant invalide")
