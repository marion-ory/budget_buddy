import customtkinter as ctk


#  Page 3
class PageHistory(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="Historique des comptes", font=("Arial", 28)).pack(
            pady=20
        )

        # choisir le compte
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        self.btn_cc = ctk.CTkButton(
            btn_frame,
            text="Compte courant",
            width=160,
            command=self.show_compte_courant,
        )
        self.btn_cc.grid(row=0, column=0, padx=10)

        self.btn_annexe = ctk.CTkButton(
            btn_frame, text="Compte annexe", width=160, command=self.show_compte_annexe
        )
        self.btn_annexe.grid(row=0, column=1, padx=10)

        # scroll
        self.scroll = ctk.CTkScrollableFrame(self, width=900, height=450)
        self.scroll.pack(pady=20, padx=40, fill="both", expand=True)

        #  retour
        btn_back = ctk.CTkButton(
            self,
            text="← Retour à l'accueil",
            command=lambda: master.show_page(master.page_home),
        )
        btn_back.pack(pady=10)

        #  compte courant
        self.show_compte_courant()

    def clear_scroll(self):
        for child in self.scroll.winfo_children():
            child.destroy()

    def show_compte_courant(self):
        self.clear_scroll()

        # En-tête
        header = "ID | DATE       | DESCRIPTION        | CATEGORIE   | TYPE    | MONTANT   | DESTINATAIRE"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        for t in self.master.transactions_cc:
            ligne = f"{t['id']:2} | {t['date']:10} | {t['desc'][:18]:18} | {t['cat'][:10]:10} | {t['type'][:7]:7} | {t['montant']:8.2f}€ | {t['dest']}"
            color = "green" if t["montant"] > 0 else "red"
            ctk.CTkLabel(
                self.scroll, text=ligne, font=("Consolas", 12), text_color=color
            ).pack(anchor="w", padx=10, pady=2)

    def show_compte_annexe(self):
        self.clear_scroll()

        header = "ID | DATE       | DESCRIPTION"
        ctk.CTkLabel(self.scroll, text=header, font=("Consolas", 13, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        for t in self.master.transactions_annexe:
            ligne = f"{t['id']:2} | {t['date']:10} | {t['desc']}"
            ctk.CTkLabel(self.scroll, text=ligne, font=("Consolas", 12)).pack(
                anchor="w", padx=10, pady=2
            )


if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()
