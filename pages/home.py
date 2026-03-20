import customtkinter as ctk
from tkinter import messagebox
import setting as st
import datetime


class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        # On applique le fond noir profond du thème Revolut
        super().__init__(master, fg_color=st.BG_COLOR)
        self.master = master

        # =========================================================
        # 1. ENTÊTE (Message de bienvenue)
        # =========================================================
        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=st.FONT_TITLE, text_color=st.TEXT_WHITE
        )
        self.label_bienvenue.pack(pady=(30, 5), padx=25, anchor="w")

        # =========================================================
        # 2. CARTE DE SOLDE (Compte Courant)
        # =========================================================
        self.card_main = ctk.CTkFrame(
            self, fg_color=st.CARD_BG, corner_radius=st.RADIUS
        )
        self.card_main.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            self.card_main,
            text="Compte Courant",
            font=st.FONT_TITLE,
            text_color=st.TEXT_GRAY,
        ).pack(pady=(15, 0))

        # Ce label sera mis à jour par refresh_data()
        self.label_solde_cc = ctk.CTkLabel(
            self.card_main, text="0.00 €", font=st.FONT_MONEY, text_color=st.TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(0, 20))

        # =========================================================
        # 3. COMPTE ANNEXE (Affichage Épargne)
        # =========================================================
        self.card_annexe = ctk.CTkFrame(
            self, fg_color=st.CARD_BG, corner_radius=st.RADIUS
        )
        self.card_annexe.pack(pady=5, padx=20, fill="x")

        self.label_annexe_titre = ctk.CTkLabel(
            self.card_annexe,
            text="Épargne Annexe",
            font=st.FONT_TITLE,
            text_color=st.TEXT_GRAY,
        )
        self.label_annexe_titre.pack(side="left", padx=20, pady=15)

        self.label_solde_annexe = ctk.CTkLabel(
            self.card_annexe,
            text="0.00 €",
            font=st.FONT_TITLE,
            text_color=st.TEXT_WHITE,
        )
        self.label_solde_annexe.pack(side="right", padx=20, pady=15)

        # =========================================================
        # 4. ZONE D'OPÉRATIONS (Input utilisateurs)
        # =========================================================
        self.entry_montant = ctk.CTkEntry(
            self,
            placeholder_text="0 €",
            height=60,
            fg_color=st.CARD_BG,
            border_color=st.CARD_BG,
            text_color=st.TEXT_WHITE,
            font=st.FONT_MONEY,
            corner_radius=st.RADIUS,
            justify="center",
        )
        self.entry_montant.pack(pady=20, padx=20, fill="x")

        # --- Bouton DEPOT & RETRAIT ---
        btn_grid = ctk.CTkFrame(self, fg_color="transparent")
        btn_grid.pack(pady=5, padx=20, fill="x")

        self.btn_depot = ctk.CTkButton(
            btn_grid,
            text="Déposer",
            fg_color=st.SUCCESS_GREEN,
            height=50,
            corner_radius=st.RADIUS,
            font=st.FONT_TITLE,
            command=self.action_depot,
        )
        self.btn_depot.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_retrait = ctk.CTkButton(
            btn_grid,
            text="Retirer",
            fg_color=st.ERROR_RED,
            height=50,
            corner_radius=st.RADIUS,
            font=st.FONT_TITLE,
            command=self.action_retrait,
        )
        self.btn_retrait.grid(row=0, column=1, padx=5, sticky="ew")
        btn_grid.columnconfigure((0, 1), weight=1)

        # --- Bouton VIREMENT ---
        self.btn_virement = ctk.CTkButton(
            self,
            text="Virement vers l'Épargne",
            fg_color=st.ACCENT_BLUE,
            height=50,
            corner_radius=st.RADIUS,
            font=st.FONT_TITLE,
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
            text_color=st.TEXT_WHITE,
            hover_color=st.CARD_BG,
            command=lambda: master.show_page(master.page_history),
        )
        self.btn_history.pack(pady=(20, 0))

        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=st.ERROR_RED,
            hover_color=st.CARD_BG,
            command=lambda: master.show_page(master.page_menu),
        )
        self.btn_logout.pack(pady=10)

    # =========================================================
    # MÉTHODES DE LIAISON (Lien avec engine.py)
    # =========================================================

    def action_depot(self):
        try:
            montant_str = self.entry_montant.get()
            if not montant_str:
                return messagebox.showwarning(
                    "Attention", "Veuillez saisir un montant."
                )

            montant = float(montant_str)
            if montant <= 0:
                return messagebox.showerror(
                    "Erreur", "Le montant doit être supérieur à 0€"
                )

            # On récupère le compte courant de l'utilisateur
            user = self.master.user_obj
            compte_courant = user.comptes[0]

            # On lance l'opération (qui va elle-même appeler le SQL via engine.py)
            if compte_courant.effectuer_depot(montant):
                # Si ça a marché, on rafraîchit l'affichage
                self.refresh_data()
                self.entry_montant.delete(0, "end")
                messagebox.showinfo("Succès", f"Dépôt de {montant:.2f}€ effectué.")
            else:
                messagebox.showerror(
                    "Erreur", "L'opération a échoué en base de données."
                )

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")

    def action_virement(self):
        try:
            montant_str = self.entry_montant.get()
            if not montant_str:
                return messagebox.showwarning("Attention", "Saisissez un montant")

            montant = float(montant_str)
            user = self.master.user_obj

            # On vérifie qu'il y a bien deux comptes
            if len(user.comptes) > 1:
                # On transfère du Courant (0) vers l'Épargne (1)
                if user.comptes[0].effectuer_transfert(montant, user.comptes[1]):
                    self.refresh_data()  # TRÈS IMPORTANT : met à jour les DEUX labels
                    self.entry_montant.delete(0, "end")
                    messagebox.showinfo(
                        "Virement", f"Virement de {montant:.2f}€ réussi !"
                    )
                else:
                    messagebox.showwarning(
                        "Refusé", "Solde insuffisant pour ce virement."
                    )
            else:
                messagebox.showerror("Erreur", "Vous n'avez pas de compte épargne.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")

    def action_retrait(self):
        try:
            montant_str = self.entry_montant.get()
            if not montant_str:
                return messagebox.showwarning(
                    "Attention", "Veuillez saisir un montant."
                )

            montant = float(montant_str)
            user = self.master.user_obj
            compte_courant = user.comptes[0]

            # On appelle la méthode de engine.py
            if compte_courant.effectuer_retrait(montant):
                self.refresh_data()
                self.entry_montant.delete(0, "end")
                messagebox.showinfo("Succès", f"Retrait de {montant:.2f}€ effectué.")
            else:
                # Le message d'erreur spécifique (solde insuffisant) est déjà géré par les print
                # dans engine, mais on peut ajouter un message ici aussi.
                messagebox.showwarning(
                    "Refusé",
                    "Opération impossible (solde insuffisant ou montant invalide).",
                )

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")


def refresh_data(self):
    # C'est ICI que le lien se fait avec app.py
    user = self.master.user_obj

    if user and hasattr(user, "comptes") and len(user.comptes) > 0:
        # On prend le premier compte (souvent le Courant)
        solde_a_afficher = user.comptes[0].solde
        self.label_solde_cc.configure(text=f"{solde_a_afficher:.2f} €")
        print(f"DEBUG HOME: Affichage du solde -> {solde_a_afficher}")
    else:
        print("DEBUG HOME: Aucun compte trouvé pour l'affichage")
