import customtkinter as ctk
import setting as st
import graphics as gp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datamanagement import charger_comptes_utilisateurs
from engine import CompteBancaires

class PageBanquier(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=st.BG_COLOR)
        self.master = master
        self.client_selectionne = None

        # --- TITRE ---
        ctk.CTkLabel(
            self,
            text="Espace Banquier",
            font=st.FONT_TITLE,
            text_color=st.TEXT_WHITE,
        ).pack(pady=(20, 10))

        # --- BOUTON DÉCONNEXION ---
        ctk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="transparent",
            text_color=st.TEXT_GRAY,
            command=lambda: self.master.show_page(self.master.page_menu),
        ).pack(side="bottom", pady=20)


        # --- CONTENEUR PRINCIPAL (2 colonnes) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20)

    # --- COLONNE GAUCHE : 2 sous-colonnes ---
        self.frame_gauche = ctk.CTkFrame(
            self.main_container, fg_color="transparent"
        )
        self.frame_gauche.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # --- SOUS-COLONNE 1 : LISTE DES CLIENTS (1/4) ---
        self.frame_clients = ctk.CTkFrame(
            self.frame_gauche, fg_color=st.CARD_BG, corner_radius=st.RADIUS, width=200
        )
        self.frame_clients.pack(side="left", fill="both", padx=(0, 10), pady=0)
        self.frame_clients.pack_propagate(False)  # force la largeur fixe

        ctk.CTkLabel(
            self.frame_clients,
            text="Mes clients",
            font=st.FONT_BODY,
            text_color=st.ACCENT_BLUE,
        ).pack(pady=10)

        self.scroll_clients = ctk.CTkScrollableFrame(
            self.frame_clients, fg_color="transparent"
        )
        self.scroll_clients.pack(fill="both", expand=True, padx=10, pady=10)

        # --- SOUS-COLONNE 2 : GRAPHIQUE + HISTORIQUE (3/4) ---
        self.frame_contenu = ctk.CTkFrame(
            self.frame_gauche, fg_color=st.CARD_BG, corner_radius=st.RADIUS
        )
        self.frame_contenu.pack(side="left", fill="both", expand=True)

        # Graphique
        self.frame_graph = ctk.CTkFrame(self.frame_contenu, fg_color="transparent", height=400)
        self.frame_graph.pack(fill="both", expand=True, padx=10, pady=10)

        # Historique
        ctk.CTkLabel(
            self.frame_contenu,
            text="Historique",
            font=st.FONT_BODY,
            text_color=st.ACCENT_BLUE,
        ).pack(pady=(10, 0))

        self.scroll_historique = ctk.CTkScrollableFrame(
            self.frame_contenu, fg_color="transparent", height=200
        )
        self.scroll_historique.pack(fill="both", expand=True, padx=10, pady=10)


        # --- COLONNE DROITE : INFOS CLIENT + BOUTON ---
        self.frame_detail = ctk.CTkFrame(
            self.main_container, fg_color=st.CARD_BG, corner_radius=st.RADIUS, width=400
        )
        self.frame_detail.pack_propagate(False)
        self.frame_detail.pack(side="right", fill="y", padx=(10, 0), pady=10)

        self.label_client_nom = ctk.CTkLabel(
            self.frame_detail,
            text="Sélectionnez\nun client",
            font=st.FONT_TITLE,
            text_color=st.TEXT_WHITE,
        )
        self.label_client_nom.pack(pady=20, padx=10)

        self.label_solde_cc = ctk.CTkLabel(
            self.frame_detail, text="", font=st.FONT_BODY, text_color=st.TEXT_GRAY, wraplength=320
        )
        self.label_solde_cc.pack(pady=5, padx=10)

        self.label_solde_annexe = ctk.CTkLabel(
            self.frame_detail, text="", font=st.FONT_BODY, text_color=st.TEXT_GRAY, wraplength=320
        )
        self.label_solde_annexe.pack(pady=5, padx=10)

        self.btn_virement = ctk.CTkButton(
            self.frame_detail,
            text="💸 Virement",
            fg_color=st.ACCENT_BLUE,
            height=st.BTN_HEIGHT,
            corner_radius=st.RADIUS,
            command=self.ouvrir_virement,
            state="disabled",
        )
        self.btn_virement.pack(pady=20, padx=20, fill="x")


    def refresh_data(self):
        """Recharge la liste des clients du banquier."""
        # Vider la liste
        for widget in self.scroll_clients.winfo_children():
            widget.destroy()

        banquier = self.master.user_obj
        if not banquier:
            return

        self.label_client_nom.configure(text=f"Bonjour {banquier.prenom},")

        # Afficher chaque client comme un bouton cliquable
        for client in banquier.client:
            ctk.CTkButton(
                self.scroll_clients,
                text=f"{client.prenom} {client.nom}",
                fg_color="transparent",
                text_color=st.TEXT_WHITE,
                hover_color=st.ACCENT_BLUE,
                anchor="w",
                command=lambda c=client: self.selectionner_client(c),
            ).pack(fill="x", pady=3)

    def selectionner_client(self, client):
            """Affiche les infos du client sélectionné."""
            self.client_selectionne = client

            # Charger les comptes du client
            comptes_sql = charger_comptes_utilisateurs(client.id)
            client.comptes = []
            for c in comptes_sql:
                client.comptes.append(CompteBancaires(
                    id=c["ID"],
                    user_id=c["ID_User"],
                    solde=float(c["Solde"]),
                    typecompte=c["Type"],
                ))

            # Afficher les soldes
            self.label_client_nom.configure(text=f"{client.prenom} {client.nom}")
            solde_cc = next((c.solde for c in client.comptes if c.typecompte == "Courant"), None)
            solde_annexe = next((c.solde for c in client.comptes if c.typecompte == "Annexe"), None)
            self.label_solde_cc.configure(
                text=f"Compte Courant : {solde_cc:,.2f} €".replace(",", " ") if solde_cc is not None else "Pas de compte courant"
            )
            self.label_solde_annexe.configure(
                text=f"Compte Annexe : {solde_annexe:,.2f} €".replace(",", " ") if solde_annexe is not None else "Pas de compte annexe"
            )
            self.btn_virement.configure(state="normal")

            # --- GRAPHIQUE ---
            for widget in self.frame_graph.winfo_children():
                widget.destroy()

            fig = gp.creer_camembert_depenses(client.id)
            if fig:
                canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
                canvas.get_tk_widget().pack(fill="both", expand=True)
                canvas.draw()
            else:
                ctk.CTkLabel(
                    self.frame_graph,
                    text="Aucune dépense enregistrée",
                    text_color=st.TEXT_GRAY,
                ).pack(pady=20)

            # --- HISTORIQUE ---
            for widget in self.scroll_historique.winfo_children():
                widget.destroy()

            from datamanagement import historique
            transactions = historique(client.id)

            if not transactions:
                ctk.CTkLabel(
                    self.scroll_historique,
                    text="Aucune transaction",
                    text_color=st.TEXT_GRAY,
                ).pack(pady=10)
            else:
                for t in transactions:
                    row = ctk.CTkFrame(self.scroll_historique, fg_color="transparent")
                    row.pack(fill="x", pady=4, padx=5)

                    date_str = str(t.get("Date", ""))[:10]
                    ctk.CTkLabel(row, text=date_str, width=80,
                                text_color=st.TEXT_GRAY, font=("Arial", 11)).pack(side="left")

                    desc = t.get("Description") or "Opération"
                    ctk.CTkLabel(row, text=desc, anchor="w",
                                font=st.FONT_BODY).pack(side="left", padx=10, expand=True, fill="x")

                    montant = float(t.get("Montant", 0))
                    t_type = t.get("Type", "")
                    color = st.SUCCESS_GREEN if t_type == "Depot" else st.ERROR_RED
                    ctk.CTkLabel(row, text=f"{montant:,.2f} €".replace(",", " "),
                                text_color=color, font=("Arial", 13, "bold"),
                                width=100, anchor="e").pack(side="right", padx=5)

                    ctk.CTkFrame(self.scroll_historique, height=1,
                                fg_color="#333333").pack(fill="x", padx=5)

    def ouvrir_virement(self):
        if self.client_selectionne:
            VirementBanquierDialog(self, self.master.user_obj, self.client_selectionne)

class VirementBanquierDialog(ctk.CTkToplevel):
    def __init__(self, master, banquier, client):
        super().__init__(master)
        self.title("Virement Banquier")
        self.geometry("400x500")
        self.configure(fg_color=st.BG_COLOR)
        self.attributes("-topmost", True)
        self.after(100, self.grab_set)
        self.banquier = banquier
        self.client = client

        ctk.CTkLabel(self, text=f"Virement pour {client.prenom} {client.nom}",
                     font=st.FONT_TITLE, text_color=st.TEXT_WHITE).pack(pady=20)

        # Compte émetteur
        comptes_noms = [f"Compte {c.typecompte}" for c in client.comptes]
        ctk.CTkLabel(self, text="Émetteur :", font=st.FONT_BODY, text_color=st.TEXT_GRAY).pack(pady=(10, 0))
        self.combo_emetteur = ctk.CTkOptionMenu(self, values=comptes_noms, width=280, fg_color=st.ACCENT_BLUE)
        self.combo_emetteur.pack(pady=5)

        # Compte destinataire — tous les clients du banquier
        from datamanagement import recuperer_client_par_banquier, charger_comptes_utilisateurs
        tous_clients = recuperer_client_par_banquier(banquier.id)
        self.comptes_dest = []
        for c in tous_clients:
            comptes = charger_comptes_utilisateurs(c["ID"])
            for compte in comptes:
                label = f"{c['Prenom']} {c['Nom']} — {compte['Type']}"
                self.comptes_dest.append({"label": label, "id": compte["ID"]})

        noms_dest = [c["label"] for c in self.comptes_dest]
        ctk.CTkLabel(self, text="Destinataire :", font=st.FONT_BODY, text_color=st.TEXT_GRAY).pack(pady=(10, 0))
        self.combo_dest = ctk.CTkOptionMenu(self, values=noms_dest, width=280, fg_color=st.ACCENT_BLUE)
        self.combo_dest.pack(pady=5)

        # Montant
        self.entry_montant = ctk.CTkEntry(self, placeholder_text="Montant (€)", width=280)
        self.entry_montant.pack(pady=10)

        # Description
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Description", width=280)
        self.entry_desc.pack(pady=10)

        ctk.CTkButton(
            self,
            text="Confirmer",
            fg_color=st.ACCENT_BLUE,
            height=40,
            command=self.valider,
        ).pack(pady=20)

    def valider(self):
        mt = self.entry_montant.get().strip()
        desc = self.entry_desc.get().strip() or "Virement banquier"

        if not mt:
            ctk.CTkLabel(self, text="Le montant est obligatoire", text_color="red").pack()
            return

        # Compte émetteur
        nom_src = self.combo_emetteur.get()
        src = next(c for c in self.client.comptes if f"Compte {c.typecompte}" == nom_src)

        # Compte destinataire
        nom_dest = self.combo_dest.get()
        id_dest = next(c["id"] for c in self.comptes_dest if c["label"] == nom_dest)

        self.banquier.faire_virement(
            id_emetteur=src.id,
            id_beneficaire=id_dest,
            montant=float(mt),
            id_cat=None,
            date_op=__import__("datetime").date.today(),
            description=desc,
        )
        self.destroy()