import customtkinter as ctk
from tkinter import messagebox
import setting as st  # Importation de ton fichier de style moderne
import datetime


class PageHome(ctk.CTkFrame):
    def __init__(self, master):

        super().__init__(master, fg_color=th.BG_COLOR)
        self.master = master

        # =========================================================
        # 1. ENTÊTE (Message de bienvenue)
        # =========================================================
        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=th.FONT_TITLE, text_color=th.TEXT_WHITE
        )
        self.label_bienvenue.pack(pady=(30, 5), padx=25, anchor="w")

        # =========================================================
        # 2. CARTE DE SOLDE (Le coeur de l'affichage)
        # =========================================================
        self.card_solde = ctk.CTkFrame(
            self, fg_color=th.CARD_BG, corner_radius=th.RADIUS
        )
        self.card_solde.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            self.card_solde,
            text="Solde disponible",
            font=th.FONT_SUB,
            text_color=th.TEXT_GRAY,
        ).pack(pady=(15, 0))

        # Ce label sera mis à jour par refresh_data()
        self.label_solde_cc = ctk.CTkLabel(
            self.card_solde, text="0.00 €", font=th.FONT_MONEY, text_color=th.TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(0, 20))

        # =========================================================
        # 3. ZONE DE SAISIE (Input utilisateur)
        # =========================================================
        self.entry_montant = ctk.CTkEntry(
            self,
            placeholder_text="0 €",
            height=60,
            fg_color=th.CARD_BG,
            border_color=th.CARD_BG,
            text_color=th.TEXT_WHITE,
            font=th.FONT_MONEY,
            corner_radius=th.RADIUS,
            justify="center",
        )
        self.entry_montant.pack(pady=20, padx=20, fill="x")

        # =========================================================
        # 4. BOUTONS D'ACTIONS (Dépôt / Retrait)
        # =========================================================
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")

        self.btn_depot = ctk.CTkButton(
            btn_frame,
            text="Déposer",
            fg_color=th.SUCCESS_GREEN,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_depot,
        )
        self.btn_depot.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_retrait = ctk.CTkButton(
            btn_frame,
            text="Retirer",
            fg_color=th.ERROR_RED,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_retrait,
        )
        self.btn_retrait.grid(row=0, column=1, padx=5, sticky="ew")

        # Équilibrage des colonnes
        btn_frame.columnconfigure((0, 1), weight=1)

        # Bouton Virement (Grand format)
        self.btn_virement = ctk.CTkButton(
            self,
            text="Virement vers Annexe",
            fg_color=th.ACCENT_BLUE,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_virement,
        )
        self.btn_virement.pack(pady=10, padx=25, fill="x")

    # =========================================================
    # MÉTHODES DE LIAISON (Lien avec engine.py)
    # =========================================================

    def action_depot(self):
        """Récupère le montant et appelle la logique de dépôt de l'objet Compte"""
        try:
            montant = float(self.entry_montant.get())
            compte = self.master.user_obj.comptes[0]  # On cible le compte principal

            if compte.effectuer_depot(montant):
                self.refresh_data()  # On rafraîchit les labels
                self.entry_montant.delete(0, "end")  # On vide le champ
                messagebox.showinfo("Dépôt réussi", f"Vous avez déposé {montant:.2f} €")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")

    def action_retrait(self):
        """Récupère le montant et appelle la logique de retrait de l'objet Compte"""
        try:
            montant = float(self.entry_montant.get())
            compte = self.master.user_obj.comptes[0]

            if compte.effectuer_retrait(montant):
                self.refresh_data()
                self.entry_montant.delete(0, "end")
                messagebox.showinfo(
                    "Retrait réussi", f"Vous avez retiré {montant:.2f} €"
                )
            else:
                messagebox.showwarning("Solde insuffisant", "Opération impossible")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")

    def action_virement(self):
        """Virement interne du compte principal vers le premier compte annexe"""
        try:
            montant = float(self.entry_montant.get())
            user = self.master.user_obj

            # On vérifie qu'un deuxième compte existe
            if len(user.comptes) > 1:
                if user.comptes[0].effectuer_transfert(montant, user.comptes[1]):
                    self.refresh_data()
                    self.entry_montant.delete(0, "end")
                    messagebox.showinfo(
                        "Virement effectué", "L'argent a été transféré."
                    )
            else:
                messagebox.showerror("Erreur", "Aucun compte bénéficiaire trouvé.")
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide")

    def refresh_data(self):
        """Met à jour les labels avec les données actuelles de l'Engine"""
        user = self.master.user_obj
        if user and user.comptes:
            self.label_bienvenue.configure(text=f"Bonjour {user.prenom},")
            # Mise à jour du solde affiché
            solde_actuel = user.comptes[0].solde
            self.label_solde_cc.configure(text=f"{solde_actuel:.2f} €")

        print("DEBUG: Interface mise à jour avec les données de la BDD")
