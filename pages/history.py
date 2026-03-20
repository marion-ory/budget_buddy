import customtkinter as ctk
import setting as st


class PageHistory(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=st.BG_COLOR)
        self.master = master
        self.current_account_id = None

        # --- TITRE ---
        ctk.CTkLabel(
            self,
            text="Historique des opérations",
            font=st.FONT_TITLE,
            text_color=st.TEXT_WHITE,
        ).pack(pady=(20, 10))

        # --- NAVIGATION COMPTES ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_cc = ctk.CTkButton(
            btn_frame,
            text="Compte Courant",
            width=160,
            fg_color=st.ACCENT_BLUE,
            corner_radius=st.RADIUS,
            command=self.show_compte_courant,
        )
        self.btn_cc.grid(row=0, column=0, padx=10)

        self.btn_annexe = ctk.CTkButton(
            btn_frame,
            text="Compte Épargne",
            width=160,
            fg_color=st.CARD_BG,
            corner_radius=st.RADIUS,
            command=self.show_compte_annexe,
        )
        self.btn_annexe.grid(row=0, column=1, padx=10)

        # --- BARRE D'OUTILS (TRI & DATES) ---
        self.tool_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tool_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.tool_frame, text="Trier :", text_color=st.TEXT_GRAY).pack(
            side="left", padx=5
        )

        self.sort_options = ctk.CTkComboBox(
            self.tool_frame,
            values=[
                "Plus récent",
                "Catégorie",
                "Type",
                "Montant (Croissant)",
                "Montant (Décroissant)",
                "Par date",
            ],
            command=self.changer_tri,
            width=160,
        )
        self.sort_options.pack(side="left", padx=5)
        self.sort_options.set("Plus récent")

        # Container pour les dates
        self.date_frame = ctk.CTkFrame(self.tool_frame, fg_color="transparent")
        self.entry_d1 = ctk.CTkEntry(
            self.date_frame, placeholder_text="AAAA-MM-JJ", width=100
        )
        self.entry_d1.pack(side="left", padx=2)
        ctk.CTkLabel(self.date_frame, text="au", text_color=st.TEXT_GRAY).pack(
            side="left", padx=2
        )
        self.entry_d2 = ctk.CTkEntry(
            self.date_frame, placeholder_text="AAAA-MM-JJ", width=100
        )
        self.entry_d2.pack(side="left", padx=2)
        self.btn_search = ctk.CTkButton(
            self.date_frame,
            text="🔍",
            width=40,
            fg_color=st.ACCENT_BLUE,
            command=lambda: self._afficher_liste(self.current_account_id),
        )
        self.btn_search.pack(side="left", padx=5)

        # --- ZONE D'AFFICHAGE ---
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=st.CARD_BG, corner_radius=st.RADIUS, height=400
        )
        self.scroll.pack(pady=10, padx=20, fill="both", expand=True)

        self.btn_back = ctk.CTkButton(
            self,
            text="← Retour à l'accueil",
            fg_color="transparent",
            text_color=st.TEXT_GRAY,
            command=lambda: master.show_page(master.page_home),
        )
        self.btn_back.pack(pady=15)

    def changer_tri(self, selection):
        if selection == "Par date":
            self.date_frame.pack(side="left", padx=10)
        else:
            self.date_frame.pack_forget()
            if self.current_account_id:
                self._afficher_liste(self.current_account_id)

    def refresh_data(self):
        self.sort_options.set("Plus récent")
        self.date_frame.pack_forget()
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
            ).pack(pady=40)
            return
        self.btn_cc.configure(fg_color=st.CARD_BG)
        self.btn_annexe.configure(fg_color=st.ACCENT_BLUE)
        self._afficher_liste(user.comptes[1].id)

    def clear_scroll(self):
        for child in self.scroll.winfo_children():
            child.destroy()

    def _afficher_liste(self, id_compte_actif):
        self.clear_scroll()
        self.current_account_id = id_compte_actif

        mapping = {
            "Plus récent": "date_recent",
            "Catégorie": "categorie",
            "Type": "type_operation",
            "Montant (Croissant)": "montant_op_croissant",
            "Montant (Décroissant)": "montant_op_decroissant",
            "Par date": "fourchette_date",
        }
        selection = self.sort_options.get()
        critere = mapping.get(selection, "date_recent")

        dates = (
            (self.entry_d1.get(), self.entry_d2.get())
            if critere == "fourchette_date"
            else None
        )

        from datamanagement import trier_par, recuperer_categories

        # On récupère les transactions ET les noms de catégories pour l'affichage
        transactions = trier_par(id_compte_actif, critere, date=dates)
        categories_dict = {cat["ID"]: cat["Nom"] for cat in recuperer_categories()}

        if not transactions:
            ctk.CTkLabel(
                self.scroll, text="Aucune opération trouvée.", text_color=st.TEXT_GRAY
            ).pack(pady=40)
            return

        for t in transactions:
            is_credit = t.get("ID_Beneficiaire") == id_compte_actif
            color = "#2ECC71" if is_credit else "#E74C3C"  # Vert vs Rouge
            prefix = "+" if is_credit else "-"

            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=8, padx=10)

            # 1. Date (Gris discret)
            date_str = str(t.get("Date", ""))[:10]
            ctk.CTkLabel(
                row,
                text=date_str,
                width=80,
                text_color=st.TEXT_GRAY,
                font=("Arial", 11),
            ).pack(side="left")

            # 2. Catégorie (Petit badge)
            id_cat = t.get("ID_Categorie")
            nom_cat = categories_dict.get(id_cat, "Inconnu")
            cat_label = ctk.CTkLabel(
                row,
                text=nom_cat,
                width=100,
                text_color=st.ACCENT_BLUE,
                font=("Arial", 10, "italic"),
            )
            cat_label.pack(side="left", padx=5)

            # 3. Description
            desc = t.get("Description") or "Opération"
            ctk.CTkLabel(row, text=desc, anchor="w", font=st.FONT_BODY).pack(
                side="left", padx=10, expand=True, fill="x"
            )

            # 4. Montant
            montant = float(t.get("Montant", 0))
            ctk.CTkLabel(
                row,
                text=f"{prefix} {montant:,.2f} €".replace(",", " "),
                text_color=color,
                font=("Arial", 14, "bold"),
                width=100,
                anchor="e",
            ).pack(side="right", padx=10)

            # Ligne de séparation
            ctk.CTkFrame(self.scroll, height=1, fg_color="#333333").pack(
                fill="x", padx=15
            )
