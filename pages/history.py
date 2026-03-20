import customtkinter as ctk
import setting as st


class PageHistory(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=st.BG_COLOR)
        self.master = master

        # --- TITRE ---
        ctk.CTkLabel(
            self,
            text="Historique des opérations",
            font=st.FONT_TITLE,
            text_color=st.TEXT_WHITE,
        ).pack(pady=20)

        # --- NAVIGATION COMPTES ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_cc = ctk.CTkButton(
            btn_frame,
            text="Compte Courant",
            fg_color=st.ACCENT_BLUE,
            corner_radius=st.RADIUS,
            command=self.show_compte_courant,
        )
        self.btn_cc.grid(row=0, column=0, padx=10)

        self.btn_annexe = ctk.CTkButton(
            btn_frame,
            text="Compte Épargne",
            fg_color=st.CARD_BG,
            corner_radius=st.RADIUS,
            command=self.show_compte_annexe,
        )
        self.btn_annexe.grid(row=0, column=1, padx=10)

        # --- ZONE D'AFFICHAGE (Scroll) ---
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=st.CARD_BG, corner_radius=st.RADIUS, height=400
        )
        self.scroll.pack(pady=20, padx=20, fill="both", expand=True)

        # --- BOUTON RETOUR ---
        self.btn_back = ctk.CTkButton(
            self,
            text="← Retour à l'accueil",
            fg_color="transparent",
            text_color=st.TEXT_WHITE,
            hover_color=st.CARD_BG,
            command=lambda: master.show_page(master.page_home),
        )
        self.btn_back.pack(pady=10)

    def clear_scroll(self):
        for child in self.scroll.winfo_children():
            child.destroy()

    def refresh_data(self):
        user = self.master.user_obj
        if user:
            # On force le rechargement depuis la BDD
            self.show_compte_courant()

    def show_compte_courant(self):
        user = self.master.user_obj
        if not user or not user.comptes:
            return
        self.btn_cc.configure(fg_color=st.ACCENT_BLUE)
        self.btn_annexe.configure(fg_color=st.CARD_BG)
        self._afficher_liste(user.comptes[0].id)

    def show_compte_annexe(self):
        user = self.master.user_obj
        if not user or len(user.comptes) < 2:
            self.clear_scroll()
            ctk.CTkLabel(
                self.scroll, text="Aucun compte épargne.", text_color=st.TEXT_GRAY
            ).pack(pady=20)
            return
        self.btn_cc.configure(fg_color=st.CARD_BG)
        self.btn_annexe.configure(fg_color=st.ACCENT_BLUE)
        self._afficher_liste(user.comptes[1].id)

    def _afficher_liste(self, id_compte_actif):
        self.clear_scroll()

        # 1. Récupération via ta fonction datamanagement
        from datamanagement import historique

        # On passe l'ID du compte pour avoir ses transactions
        transactions = historique(id_compte_actif)

        if not transactions:
            ctk.CTkLabel(
                self.scroll,
                text="Aucune opération sur ce compte.",
                text_color=st.TEXT_GRAY,
            ).pack(pady=40)
            return

        # 2. Construction de la liste
        for t in transactions:
            # VÉRIFICATION DE LA CASSE SQL :
            # On utilise les noms exacts de ton CREATE TABLE
            id_dest = t.get("ID_Beneficiaire")
            is_credit = id_dest == id_compte_actif

            prefix = "+" if is_credit else "-"
            color = st.SUCCESS_GREEN if is_credit else "#FF5555"

            # Création de la ligne (Frame)
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=8, padx=15)

            # Date (Formatée proprement)
            date_val = t.get("Date", "00-00-0000")
            ctk.CTkLabel(
                row, text=str(date_val), width=100, text_color=st.TEXT_GRAY
            ).pack(side="left")

            # Description (ou Type si vide)
            desc_text = t.get("Description") or t.get("Type", "Transaction")
            ctk.CTkLabel(row, text=desc_text, width=200, anchor="w").pack(
                side="left", padx=15
            )

            # Montant
            mt_val = float(t.get("Montant", 0))
            ctk.CTkLabel(
                row,
                text=f"{prefix} {mt_val:,.2f} €".replace(",", " "),
                text_color=color,
                font=st.FONT_MAIN_BOLD,
            ).pack(side="right", padx=10)

            # Petite ligne de séparation subtile
            ctk.CTkFrame(self.scroll, height=1, fg_color="#333333").pack(
                fill="x", padx=20
            )
