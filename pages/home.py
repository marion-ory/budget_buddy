import customtkinter as ctk
from tkinter import messagebox
import setting as st
import datetime


class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        # On applique le fond noir profond du thème Revolut
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
        # 2. CARTE DE SOLDE (Compte Courant)
        # =========================================================
        self.card_main = ctk.CTkFrame(
            self, fg_color=th.CARD_BG, corner_radius=th.RADIUS
        )
        self.card_main.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            self.card_main,
            text="Compte Courant",
            font=th.FONT_SUB,
            text_color=th.TEXT_GRAY,
        ).pack(pady=(15, 0))

        # Ce label sera mis à jour par refresh_data()
        self.label_solde_cc = ctk.CTkLabel(
            self.card_main, text="0.00 €", font=th.FONT_MONEY, text_color=th.TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(0, 20))

        # =========================================================
        # 3. COMPTE ANNEXE (Affichage Épargne)
        # =========================================================
        self.card_annexe = ctk.CTkFrame(
            self, fg_color=th.CARD_BG, corner_radius=th.RADIUS
        )
        self.card_annexe.pack(pady=5, padx=20, fill="x")

        self.label_annexe_titre = ctk.CTkLabel(
            self.card_annexe,
            text="Épargne Annexe",
            font=th.FONT_SUB,
            text_color=th.TEXT_GRAY,
        )
        self.label_annexe_titre.pack(side="left", padx=20, pady=15)

        self.label_solde_annexe = ctk.CTkLabel(
            self.card_annexe, text="0.00 €", font=th.FONT_SUB, text_color=th.TEXT_WHITE
        )
        self.label_solde_annexe.pack(side="right", padx=20, pady=15)

        # =========================================================
        # 4. ZONE D'OPÉRATIONS (Input utilisateurs)
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

        # --- Bouton DEPOT & RETRAIT ---
        btn_grid = ctk.CTkFrame(self, fg_color="transparent")
        btn_grid.pack(pady=5, padx=20, fill="x")

        self.btn_depot = ctk.CTkButton(
            btn_grid,
            text="Déposer",
            fg_color=th.SUCCESS_GREEN,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_depot,
        )
        self.btn_depot.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_retrait = ctk.CTkButton(
            btn_grid,
            text="Retirer",
            fg_color=th.ERROR_RED,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_retrait,
        )
        self.btn_retrait.grid(row=0, column=1, padx=5, sticky="ew")
        btn_grid.columnconfigure((0, 1), weight=1)

        # --- Bouton VIREMENT ---
        self.btn_virement = ctk.CTkButton(
            self,
            text="Virement vers l'Épargne",
            fg_color=th.ACCENT_BLUE,
            height=50,
            corner_radius=th.RADIUS,
            font=th.FONT_SUB,
            command=self.action_virement,
        )
        self.btn_virement.pack(pady=10, padx=25, fill="x")

        # =========================================================
        # 5. NAVIGATION & HISTORIQUE
        # =========================================================
        self.btn_history = ctk.CTkButton(
            self,
            text="📊 Voir l'historique des comptes",
            fg_color="transparent",
            text_color=th.TEXT_WHITE,
            hover_color=th.CARD_BG,
            command=lambda: master.show_page(master.page_history),
        )
        self.btn_history.pack(pady=(20, 0))

        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=th.ERROR_RED,
            hover_color=th.CARD_BG,
            command=lambda: master.show_page(master.page_menu),
        )
        self.btn_logout.pack(pady=10)

    # =========================================================
    # MÉTHODES DE LIAISON (Lien avec engine.py)
    # =========================================================

    def action_depot(self):
        try:
            montant = float(self.entry_montant.get())
            if self.master.user_obj.comptes[0].effectuer_depot(montant):
                self.refresh_data()
                self.entry_montant.delete(0, "end")
                messagebox.showinfo("Succès", f"Dépôt de {montant}€ effectué.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")

    def action_retrait(self):
        try:
            montant = float(self.entry_montant.get())
            if self.master.user_obj.comptes[0].effectuer_retrait(montant):
                self.refresh_data()
                self.entry_montant.delete(0, "end")
                messagebox.showinfo("Succès", f"Retrait de {montant}€ effectué.")
            else:
                messagebox.showwarning("Refusé", "Solde insuffisant.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")

    def action_virement(self):
        try:
            montant = float(self.entry_montant.get())
            user = self.master.user_obj
            if len(user.comptes) > 1:
                # Appel du RAPPEL ENGINE.PY pour le transfert
                if user.comptes[0].effectuer_transfert(montant, user.comptes[1]):
                    self.refresh_data()
                    self.entry_montant.delete(0, "end")
                    messagebox.showinfo(
                        "Virement", "L'argent a été transféré vers l'épargne."
                    )
            else:
                messagebox.showerror("Erreur", "Aucun compte épargne trouvé.")
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide")

    def refresh_data(self):
        """Met à jour l'affichage avec les données réelles de la BDD"""
        user = self.master.user_obj
        if user:
            self.label_bienvenue.configure(text=f"Bonjour {user.prenom},")

            # Mise à jour Compte Courant
            if len(user.comptes) > 0:
                self.label_solde_cc.configure(text=f"{user.comptes[0].solde:.2f} €")

            # Mise à jour Annexe
            if len(user.comptes) > 1:
                self.label_solde_annexe.configure(text=f"{user.comptes[1].solde:.2f} €")

        print("DEBUG: Dashboard rafraîchi avec les données réelles")
