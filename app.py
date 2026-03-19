import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import graphics
from login import login, inscription
# AJOUT : On importe la connexion BDD pour récupérer soldes et transactions
from config import get_connection

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# App
class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Buddy")
        self.geometry("1000x700")

        self.current_user = None
        
        # SUPPRESSION des fausses données (transactions_cc et transactions_annexe retirées)
        self.current_cc_id = None
        self.current_annexe_id = None

        # Création des pages
        self.page_menu = PageMenu(self)
        self.page_login = PageLogin(self)
        self.page_register = PageRegister(self)
        self.page_home = PageHome(self)
        self.page_history = PageHistory(self)

        # affichage
        self.show_page(self.page_menu)

    def show_page(self, page):
        for p in (self.page_menu, self.page_login, self.page_register,
                  self.page_home, self.page_history):
            p.pack_forget()
        page.pack(fill="both", expand=True)

    def register_user(self, nom, prenom, email, mdp, code=""):
        return inscription(nom, prenom, email, "", mdp, code)

    def login_user(self, email, mdp):
        user_data = login(email, mdp)
        if user_data:
            self.current_user = user_data
            return True
        return False

    # AJOUT : Fonction pour récupérer les vrais comptes de l'utilisateur
    def get_user_comptes(self):
        if not self.current_user: return []
        cnx = get_connection()
        res = []
        if cnx:
            cur = cnx.cursor()
            cur.execute("SELECT ID, Type, Solde FROM Compte WHERE ID_User = %s", (self.current_user['id'],))
            res = cur.fetchall()
            cur.close()
            cnx.close()
        return res

    # AJOUT : Fonction pour récupérer le vrai historique d'un compte
    def get_compte_transactions(self, compte_id):
        if not compte_id: return []
        cnx = get_connection()
        res = []
        if cnx:
            cur = cnx.cursor()
            query = """
                SELECT T.ID, T.Date, T.Description, C.Nom, T.Type, T.Montant, T.ID_Emetteur, T.ID_Beneficiaire
                FROM Transaction T
                LEFT JOIN Categorie C ON T.ID_Categorie = C.ID
                WHERE T.ID_Emetteur = %s OR T.ID_Beneficiaire = %s
                ORDER BY T.Date DESC
            """
            cur.execute(query, (compte_id, compte_id))
            res = cur.fetchall()
            cur.close()
            cnx.close()
        return res


# Menu
class PageMenu(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 32))
        title.pack(pady=40)
        btn_login = ctk.CTkButton(self, text="Connexion", height=45, width=220, command=lambda: master.show_page(master.page_login))
        btn_login.pack(pady=10)
        btn_register = ctk.CTkButton(self, text="Inscription", height=45, width=220, command=lambda: master.show_page(master.page_register))
        btn_register.pack(pady=10)


# Connexion
class PageLogin(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Connexion", font=("Arial", 28)).pack(pady=20)
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=320, height=35)
        self.entry_email.pack(pady=10)
        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*", width=320, height=35)
        self.entry_mdp.pack(pady=10)
        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)
        btn_login = ctk.CTkButton(self, text="Se connecter", width=200, height=40, command=self.valider_connexion)
        btn_login.pack(pady=20)
        btn_back = ctk.CTkButton(self, text="← Retour", width=150, command=lambda: master.show_page(master.page_menu))
        btn_back.pack(pady=10)

    def valider_connexion(self):
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()
        if self.master.login_user(email, mdp):
            self.master.page_home.update_header()
            self.master.show_page(self.master.page_home)
        else:
            self.label_info.configure(text="Email ou mot de passe incorrect")


# Inscription
class PageRegister(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Inscription", font=("Arial", 28)).pack(pady=20)
        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Nom", width=320, height=35)
        self.entry_nom.pack(pady=8)
        self.entry_prenom = ctk.CTkEntry(self, placeholder_text="Prénom", width=320, height=35)
        self.entry_prenom.pack(pady=8)
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Adresse email", width=320, height=35)
        self.entry_email.pack(pady=8)
        self.entry_mdp = ctk.CTkEntry(self, placeholder_text="Mot de passe (10+ caractères)", show="*", width=320, height=35)
        self.entry_mdp.pack(pady=8)
        self.entry_code = ctk.CTkEntry(self, placeholder_text="Code (optionnel)", width=320, height=35)
        self.entry_code.pack(pady=5)
        ctk.CTkLabel(self, text="À ne remplir que si vous avez reçu un code de la banque", font=("Arial", 12), text_color="gray").pack(pady=(0, 15))
        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)
        btn_register = ctk.CTkButton(self, text="Créer mon compte", width=220, height=40, command=self.valider_inscription)
        btn_register.pack(pady=10)
        btn_back = ctk.CTkButton(self, text="← Retour", width=150, command=lambda: master.show_page(master.page_menu))
        btn_back.pack(pady=10)

    def valider_inscription(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get().strip()
        code = self.entry_code.get().strip()

        if not (nom and prenom and email and mdp):
            self.label_info.configure(text="Tous les champs sauf le code sont obligatoires")
            return
        if len(mdp) < 10:
            self.label_info.configure(text="Mot de passe trop court (10 caractères minimum)")
            return

        if self.master.register_user(nom, prenom, email, mdp, code):
            self.master.login_user(email, mdp)
            self.master.page_home.update_header()
            self.master.show_page(self.master.page_home)
        else:
            self.label_info.configure(text="Erreur lors de l'inscription (Email déjà pris ?)")


# Page 2
class PageHome(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        self.label_bienvenue = ctk.CTkLabel(self, text="Bienvenue", font=("Arial", 30))
        self.label_bienvenue.pack(pady=20)

        frame_soldes = ctk.CTkFrame(self)
        frame_soldes.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_soldes, text="Solde compte courant :", font=("Arial", 18)).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.label_solde_cc = ctk.CTkLabel(frame_soldes, text="0,00 €", font=("Arial", 18))
        self.label_solde_cc.grid(row=0, column=1, sticky="w", padx=20, pady=10)

        ctk.CTkLabel(frame_soldes, text="Annexe 1 :", font=("Arial", 16)).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.label_annexe1 = ctk.CTkLabel(frame_soldes, text="0,00 €", font=("Arial", 16))
        self.label_annexe1.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        ctk.CTkLabel(frame_soldes, text="Annexe 2 :", font=("Arial", 16)).grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.label_annexe2 = ctk.CTkLabel(frame_soldes, text="0,00 €", font=("Arial", 16))
        self.label_annexe2.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        self.frame_graphs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_graphs.pack(pady=10, fill="both", expand=True)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=40)

        btn_graphs = ctk.CTkButton(btn_frame, text="📊 Afficher les graphiques", width=200, height=40, command=self.afficher_les_graphiques)
        btn_graphs.grid(row=0, column=0, padx=10)

        # On met à jour l'historique avant de changer de page
        btn_history = ctk.CTkButton(btn_frame, text="Voir l'historique des comptes", width=240, height=40, command=self.aller_historique)
        btn_history.grid(row=0, column=1, padx=10)

        btn_logout = ctk.CTkButton(btn_frame, text="Déconnexion", width=160, height=40, command=lambda: master.show_page(master.page_menu))
        btn_logout.grid(row=0, column=2, padx=10)

    def update_header(self):
        user = self.master.current_user
        if user:
            self.label_bienvenue.configure(text=f"Bienvenue {user['prenom']} {user['nom']}")
            
            # MODIFICATION : Récupération dynamique des soldes depuis la BDD
            comptes = self.master.get_user_comptes()
            self.label_solde_cc.configure(text="0.00 €")
            self.label_annexe1.configure(text="-")
            self.label_annexe2.configure(text="-")
            
            annexe_count = 1
            for compte in comptes:
                c_id, c_type, c_solde = compte[0], compte[1], compte[2]
                solde_str = f"{float(c_solde):.2f} €" if c_solde is not None else "0.00 €"
                
                if c_type == 'Courant':
                    self.label_solde_cc.configure(text=solde_str)
                    self.master.current_cc_id = c_id
                elif c_type == 'Annexe':
                    if annexe_count == 1:
                        self.label_annexe1.configure(text=solde_str)
                        self.master.current_annexe_id = c_id
                        annexe_count += 1
                    elif annexe_count == 2:
                        self.label_annexe2.configure(text=solde_str)
                        annexe_count += 1

    def aller_historique(self):
        self.master.page_history.show_compte_courant()
        self.master.show_page(self.master.page_history)

    def afficher_les_graphiques(self):
        for widget in self.frame_graphs.winfo_children():
            widget.destroy()

        user_id = self.master.current_user.get('id')
        if not user_id:
            return

        fig1 = graphics.creer_camembert_depenses(user_id)
        fig2 = graphics.creer_histo_flux(user_id)

        if fig1:
            canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_graphs)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)

        if fig2:
            canvas2 = FigureCanvasTkAgg(fig2, master=self.frame_graphs)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="right", fill="both", expand=True, padx=5)


# Page 3
class PageHistory(ctk.CTkFrame):
    def __init__(self, master: BudgetBuddyApp):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Historique des comptes", font=("Arial", 28)).pack(pady=20)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        self.btn_cc = ctk.CTkButton(btn_frame, text="Compte courant", width=160, command=self.show_compte_courant)
        self.btn_cc.grid(row=0, column=0, padx=10)

        self.btn_annexe = ctk.CTkButton(btn_frame, text="Compte annexe", width=160, command=self.show_compte_annexe)
        self.btn_annexe.grid(row=0, column=1, padx=10)

        self.scroll = ctk.CTkScrollableFrame(self, width=900, height=450)
        self.scroll.pack(pady=20, padx=40, fill="both", expand=True)

        btn_back = ctk.CTkButton(self, text="← Retour à l'accueil", command=lambda: master.show_page(master.page_home))
        btn_back.pack(pady=10)

    def clear_scroll(self):
        for child in self.scroll.winfo_children():
            child.destroy()

    # MODIFICATION : Affiche l'historique BDD du compte courant
    def show_compte_courant(self):
        self.clear_scroll()
        header = "ID | DATE       | DESCRIPTION        | CATEGORIE  | TYPE    | MONTANT"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        
        if self.master.current_cc_id:
            transactions = self.master.get_compte_transactions(self.master.current_cc_id)
            for t in transactions:
                t_id, t_date, t_desc, t_cat, t_type, t_montant, id_emet, id_ben = t
                t_cat = t_cat if t_cat else "N/A"
                
                # Logique pour savoir si l'argent rentre ou sort
                montant = float(t_montant)
                if t_type == 'Retrait' or (t_type == 'Transfert' and id_emet == self.master.current_cc_id):
                    montant = -montant
                    
                ligne = f"{t_id:2} | {str(t_date)[:10]:10} | {str(t_desc)[:18]:18} | {str(t_cat)[:10]:10} | {str(t_type)[:7]:7} | {montant:8.2f}€"
                color = "green" if montant > 0 else "red"
                ctk.CTkLabel(self.scroll, text=ligne, font=("Consolas", 12), text_color=color).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(self.scroll, text="Aucun compte courant trouvé.", font=("Consolas", 12)).pack(anchor="w", padx=10, pady=2)

    # MODIFICATION : Affiche l'historique BDD du compte annexe
    def show_compte_annexe(self):
        self.clear_scroll()
        header = "ID | DATE       | DESCRIPTION        | CATEGORIE  | TYPE    | MONTANT"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        
        if self.master.current_annexe_id:
            transactions = self.master.get_compte_transactions(self.master.current_annexe_id)
            for t in transactions:
                t_id, t_date, t_desc, t_cat, t_type, t_montant, id_emet, id_ben = t
                t_cat = t_cat if t_cat else "N/A"
                
                montant = float(t_montant)
                if t_type == 'Retrait' or (t_type == 'Transfert' and id_emet == self.master.current_annexe_id):
                    montant = -montant
                    
                ligne = f"{t_id:2} | {str(t_date)[:10]:10} | {str(t_desc)[:18]:18} | {str(t_cat)[:10]:10} | {str(t_type)[:7]:7} | {montant:8.2f}€"
                color = "green" if montant > 0 else "red"
                ctk.CTkLabel(self.scroll, text=ligne, font=("Consolas", 12), text_color=color).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(self.scroll, text="Aucun compte annexe trouvé.", font=("Consolas", 12)).pack(anchor="w", padx=10, pady=2)


if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()