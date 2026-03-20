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
        """Nettoie la zone d'affichage"""
        for child in self.scroll.winfo_children():
            child.destroy()

    def refresh_data(self):
        """Appelée automatiquement lors de l'ouverture de la page"""
        user = self.master.user_obj
        if user:
            # On charge les données depuis la BDD (méthode de ta classe Client)
            user.charger_transactions_client()
            # On affiche le compte courant par défaut
            self.show_compte_courant()

    def show_compte_courant(self):
        """Affiche les transactions du compte courant"""
        user = self.master.user_obj
        if not user or not user.comptes:
            return

        # UI : On active le bouton Courant
        self.btn_cc.configure(fg_color=st.ACCENT_BLUE)
        self.btn_annexe.configure(fg_color=st.CARD_BG)

        id_cc = user.comptes[0].id
        self._afficher_liste(id_cc)

    def show_compte_annexe(self):
        """Affiche les transactions du compte épargne"""
        user = self.master.user_obj
        if not user or len(user.comptes) < 2:
            self.clear_scroll()
            ctk.CTkLabel(
                self.scroll,
                text="Aucun compte épargne disponible.",
                text_color=st.TEXT_GRAY,
            ).pack(pady=20)
            return

        # UI : On active le bouton Épargne
        self.btn_cc.configure(fg_color=st.CARD_BG)
        self.btn_annexe.configure(fg_color=st.ACCENT_BLUE)

        id_annexe = user.comptes[1].id
        self._afficher_liste(id_annexe)

    def _afficher_liste(self, id_compte_actif):
        """Logique de filtrage et d'affichage des transactions"""
        self.clear_scroll()
        user = self.master.user_obj

        # 1. En-tête du tableau (Consolas pour un alignement parfait)
        header = f"{'DATE':<12} | {'DESCRIPTION':<20} | {'TYPE':<12} | {'MONTANT':>10}"
        ctk.CTkLabel(
            self.scroll,
            text=header,
            font=("Consolas", 13, "bold"),
            text_color=st.TEXT_GRAY,
        ).pack(anchor="w", padx=10, pady=(5, 15))

        # 2. Filtrage des transactions du client pour CE compte
        transactions_du_compte = [
            t
            for t in user.transactions
            if t.emetteur == id_compte_actif or t.beneficiaire == id_compte_actif
        ]

        # 3. Message si vide
        if not transactions_du_compte:
            ctk.CTkLabel(
                self.scroll,
                text="Aucune opération sur ce compte.",
                text_color=st.TEXT_GRAY,
            ).pack(pady=40)
            return

        # 4. Affichage des lignes (Plus récent en haut)
        for t in reversed(transactions_du_compte):
            # L'argent entre si le compte actif est le bénéficiaire
            is_credit = t.beneficiaire == id_compte_actif

            color = st.SUCCESS_
