import customtkinter as ctk
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import graphics as gp

# On importe les styles depuis setting.py
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


# --- FENÊTRE DIALOGUE : DEPOT / RETRAIT / VIR INTERNE ---
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
        mt, desc, cat_nom = (
            self.entry_montant.get().strip(),
            self.entry_desc.get().strip(),
            self.combo_cat.get(),
        )
        try:
            id_cat = next(c["ID"] for c in self.categories_data if c["Nom"] == cat_nom)
            if mt and desc:
                self.callback(mt, desc, id_cat)
                self.destroy()
        except StopIteration:
            print("DEBUG: Erreur catégorie")


# --- FENÊTRE DIALOGUE : VIREMENT EXTERNE ---
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
        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Nom", width=220)
        self.entry_nom.pack(pady=10)
        self.entry_prenom = ctk.CTkEntry(self, placeholder_text="Prénom", width=220)
        self.entry_prenom.pack(pady=10)
        self.entry_mt = ctk.CTkEntry(self, placeholder_text="Montant (€)", width=220)
        self.entry_mt.pack(pady=10)

        ctk.CTkButton(
            self,
            text="Envoyer",
            fg_color=ACCENT_BLUE,
            height=40,
            command=self.clic_envoyer,
        ).pack(pady=25)

    def clic_envoyer(self):
        self.callback(
            self.entry_nom.get(), self.entry_prenom.get(), self.entry_mt.get()
        )
        self.destroy()


# --- PAGE ACCUEIL PRINCIPALE ---
class PageHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master

        # 1. Header (Bonjour...)
        self.label_bienvenue = ctk.CTkLabel(
            self, text="Bonjour,", font=FONT_TITLE, text_color=TEXT_WHITE
        )
        self.label_bienvenue.pack(pady=(20, 10), padx=30, anchor="w")

        # 2. Conteneur Principal (Structure en 2 colonnes)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20)

        # --- COLONNE GAUCHE (GRAPHIQUE) ---
        self.frame_stats = ctk.CTkFrame(
            self.main_container, fg_color=CARD_BG, corner_radius=RADIUS
        )
        self.frame_stats.pack(
            side="left", fill="both", expand=True, padx=(0, 10), pady=10
        )

        # --- COLONNE DROITE (CARTES & ACTIONS) ---
        self.right_col = ctk.CTkFrame(
            self.main_container, fg_color="transparent", width=400
        )
        self.right_col.pack(side="right", fill="both", padx=(10, 0))

        self._creer_cartes_soldes()
        self._creer_boutons_actions()
        self._creer_section_filtres()

        # Bouton Déconnexion
        self.btn_logout = ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=TEXT_GRAY,
            command=lambda: self.master.show_page(self.master.page_menu),
        )
        self.btn_logout.pack(side="bottom", pady=20)

    def _creer_cartes_soldes(self):
        # Carte Compte Courant
        self.card_cc = ctk.CTkFrame(
            self.right_col, fg_color=CARD_BG, corner_radius=RADIUS
        )
        self.card_cc.pack(pady=5, fill="x")
        ctk.CTkLabel(
            self.card_cc, text="Compte Courant", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(10, 0), padx=20, anchor="w")
        self.label_solde_cc = ctk.CTkLabel(
            self.card_cc, text="0.00 €", font=FONT_MONEY, text_color=TEXT_WHITE
        )
        self.label_solde_cc.pack(pady=(5, 10), padx=20, anchor="w")

        # Carte Compte Annexe
        self.card_annexe = ctk.CTkFrame(
            self.right_col, fg_color=CARD_BG, corner_radius=RADIUS
        )
        self.card_annexe.pack(pady=5, fill="x")
        ctk.CTkLabel(
            self.card_annexe, text="Compte Annexe", font=FONT_BODY, text_color=TEXT_GRAY
        ).pack(pady=(10, 0), padx=20, anchor="w")
        self.label_solde_annexe = ctk.CTkLabel(
            self.card_annexe, text="0.00 €", font=FONT_TITLE, text_color=ACCENT_BLUE
        )
        self.label_solde_annexe.pack(pady=(5, 10), padx=20, anchor="w")

    def _creer_boutons_actions(self):
        self.frame_actions = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.frame_actions.pack(pady=10)
        btn_style = {
            "fg_color": ACCENT_BLUE,
            "hover_color": "#0056b3",
            "height": BTN_HEIGHT,
            "corner_radius": RADIUS,
            "width": 185,
        }

        ctk.CTkButton(
            self.frame_actions, text="➕ Dépôt", command=self.ouvrir_depot, **btn_style
        ).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(
            self.frame_actions,
            text="➖ Retrait",
            command=self.ouvrir_retrait,
            **btn_style,
        ).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(
            self.frame_actions,
            text="🔄 Vir. Interne",
            command=self.ouvrir_virement,
            **btn_style,
        ).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(
            self.frame_actions,
            text="💸 Vir. Externe",
            command=self.ouvrir_virement_externe,
            **btn_style,
        ).grid(row=1, column=1, padx=5, pady=5)

    def _creer_section_filtres(self):
        self.frame_filtres = ctk.CTkFrame(
            self.right_col, fg_color=CARD_BG, corner_radius=RADIUS
        )
        self.frame_filtres.pack(pady=10, fill="x")

        ctk.CTkLabel(
            self.frame_filtres,
            text="Tri & Historique",
            font=FONT_BODY,
            text_color=ACCENT_BLUE,
        ).pack(pady=5)

        # Filtre Catégorie
        from datamanagement import recuperer_categories

        cats = [c["Nom"] for c in recuperer_categories()]
        self.combo_filter_cat = ctk.CTkOptionMenu(
            self.frame_filtres,
            values=["Toutes Catégories"] + cats,
            fg_color=BG_COLOR,
            width=350,
        )
        self.combo_filter_cat.pack(pady=5, padx=10)

        # Filtre Période
        self.combo_filter_date = ctk.CTkOptionMenu(
            self.frame_filtres,
            values=["Tout l'historique", "7 derniers jours", "30 derniers jours"],
            fg_color=BG_COLOR,
            width=350,
        )
        self.combo_filter_date.pack(pady=5, padx=10)

        # Bouton Historique
        self.btn_history = ctk.CTkButton(
            self.frame_filtres,
            text="📜 Appliquer & Voir l'Historique",
            fg_color=ACCENT_BLUE,
            height=40,
            width=350,
            command=self.aller_a_historique_filtre,
        )
        self.btn_history.pack(pady=15, padx=10)

    def aller_a_historique_filtre(self):
        """Passe les filtres à la page historique et change de page."""
        categorie = self.combo_filter_cat.get()
        periode = self.combo_filter_date.get()

        # On suppose que master (app.py) possède une instance de page_history
        if hasattr(self.master, "page_history"):
            # Si tu as créé cette méthode dans page_history.py
            if hasattr(self.master.page_history, "appliquer_filtres_depuis_accueil"):
                self.master.page_history.appliquer_filtres_depuis_accueil(
                    categorie, periode
                )

            self.master.show_page(self.master.page_history)

    def refresh_data(self):
        user = self.master.user_obj
        if user and user.comptes:
            # --- TRI AUTOMATIQUE PAR DATE DÉCROISSANTE ---
            for compte in user.comptes:
                compte.transactions.sort(key=lambda x: x.date, reverse=True)

            self.label_bienvenue.configure(text=f"Bonjour {user.prenom},")
            self.label_solde_cc.configure(
                text=f"{user.comptes[0].solde:,.2f} €".replace(",", " ")
            )
            if len(user.comptes) > 1:
                self.label_solde_annexe.configure(
                    text=f"{user.comptes[1].solde:,.2f} €".replace(",", " ")
                )

            self.update_graph(user.id)

    def update_graph(self, user_id):
        for widget in self.frame_stats.winfo_children():
            widget.destroy()

        fig = gp.creer_camembert_depenses(user_id)
        if fig:
            fig.patch.set_facecolor(CARD_BG)
            self.afficher_graphique(self.frame_stats, fig)
        else:
            ctk.CTkLabel(
                self.frame_stats,
                text="Aucune donnée de dépense",
                font=FONT_BODY,
                text_color=TEXT_GRAY,
            ).pack(expand=True)

    def afficher_graphique(self, parent_frame, figure):
        canvas = FigureCanvasTkAgg(figure, master=parent_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg=CARD_BG, highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.draw()

    # --- ACTIONS ---
    def ouvrir_depot(self):
        OperationDialog(self, "Effectuer un Dépôt", self.traiter_depot)

    def traiter_depot(self, mt, desc, id_cat):
        if self.master.user_obj.comptes[0].effectuer_depot(float(mt), desc, id_cat):
            self.refresh_data()

    def ouvrir_retrait(self):
        OperationDialog(self, "Effectuer un Retrait", self.traiter_retrait)

    def traiter_retrait(self, mt, desc, id_cat):
        if self.master.user_obj.comptes[0].effectuer_retrait(float(mt), desc, id_cat):
            self.refresh_data()

    def ouvrir_virement(self):
        if len(self.master.user_obj.comptes) >= 2:
            OperationDialog(self, "Virement Interne", self.traiter_virement_interne)

    def traiter_virement_interne(self, mt, desc, id_cat):
        src, dest = self.master.user_obj.comptes[0], self.master.user_obj.comptes[1]
        if src.effectuer_transfert(float(mt), dest, desc, id_cat):
            self.refresh_data()

    def ouvrir_virement_externe(self):
        VirementExterneDialog(self, self.traiter_virement_externe)

    def traiter_virement_externe(self, nom, prenom, montant):
        from datamanagement import trouver_id_compte_par_nom

        id_dest = trouver_id_compte_par_nom(nom, prenom)
        if id_dest and self.master.user_obj.comptes[0].effectuer_transfert(
            float(montant), id_dest, f"Virement à {prenom} {nom}", 3
        ):
            self.refresh_data()
