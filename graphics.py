import matplotlib.pyplot as plt

# MODIFICATION : Import de config au lieu de Engine pour correspondre au reste de ton projet
from config import get_connection


# 1. GRAPHIQUE : RÉPARTITION DES DÉPENSES (CAMEMBERT)
def creer_camembert_depenses(user_id):
    cnx = get_connection()
    if not cnx:
        return None

    cursor = cnx.cursor()
    query = """
        SELECT Categorie.Nom, SUM(Transaction.Montant)
        FROM Transaction
        JOIN Categorie ON Transaction.ID_Categorie = Categorie.ID
        JOIN Compte ON Transaction.ID_Emetteur = Compte.ID
        WHERE Compte.ID_User = %s AND Transaction.Type = 'Retrait'
        GROUP BY Categorie.Nom
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    cnx.close()

    # --- AMÉLIORATION DU STYLE ---
    # On définit une taille plus grande (6x5 au lieu de 5x4)
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#1a1a1a")  # Fond sombre

    if data:
        labels = [row[0] for row in data]
        values = [float(row[1]) for row in data]

        # Couleurs vives pour que ça ressorte sur le noir
        couleurs = ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#9b59b6", "#e67e22"]

        # On crée le camembert avec du texte BLANC et plus GROS
        patches, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=couleurs,
            textprops={"color": "w", "fontsize": 12},  # Texte des labels en blanc
        )

        # On met les pourcentages en gras et blanc aussi
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_weight("bold")
            autotext.set_fontsize(10)
    else:
        ax.text(0.5, 0.5, "Aucune donnée", color="white", ha="center")

    ax.set_title("Répartition des Dépenses", color="white", fontsize=14, pad=20)
    return fig


# 2. GRAPHIQUE : FLUX FINANCIER (HISTOGRAMME DÉPÔTS VS RETRAITS)
def creer_histo_flux(user_id):
    cnx = get_connection()
    if not cnx:
        return None

    cursor = cnx.cursor()
    query = """
        SELECT Type, SUM(Montant)
        FROM Transaction
        JOIN Compte ON (Transaction.ID_Emetteur = Compte.ID OR Transaction.ID_Beneficiaire = Compte.ID)
        WHERE Compte.ID_User = %s AND Type IN ('Depot', 'Retrait')
        GROUP BY Type
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    cnx.close()

    fig, ax = plt.subplots(figsize=(5, 4))
    if data:
        types = [row[0] for row in data]
        montants = [float(row[1]) for row in data]
        # Vert pour les dépôts, Rouge pour les retraits
        couleurs = ["#2ecc71" if t == "Depot" else "#e74c3c" for t in types]
        ax.bar(types, montants, color=couleurs)
    else:
        ax.text(0.5, 0.5, "Aucun flux enregistré", ha="center")

    ax.set_title("Dépôts vs Retraits")
    ax.set_ylabel("Montant (€)")
    return fig


# 3. GRAPHIQUE : ÉVOLUTION DU SOLDE (COURBE)
def creer_courbe_solde(user_id):
    cnx = get_connection()
    if not cnx:
        return None

    cursor = cnx.cursor()
    query = """
        SELECT Date, Montant, Type, ID_Beneficiaire
        FROM Transaction
        JOIN Compte ON (Transaction.ID_Emetteur = Compte.ID OR Transaction.ID_Beneficiaire = Compte.ID)
        WHERE Compte.ID_User = %s
        ORDER BY Date ASC
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    cnx.close()

    fig, ax = plt.subplots(figsize=(5, 4))
    if data:
        dates = []
        soldes = []
        solde_cumule = 0

        for date, montant, t_type, id_ben in data:
            # On calcule le solde au fur et à mesure
            if t_type == "Depot" or (t_type == "Transfert" and id_ben is not None):
                solde_cumule += float(montant)
            else:
                solde_cumule -= float(montant)

            dates.append(date)
            soldes.append(solde_cumule)

        ax.plot(dates, soldes, marker="o", linestyle="-", color="#3498db", linewidth=2)
        plt.xticks(rotation=45)
    else:
        ax.text(0.5, 0.5, "Historique vide", ha="center")

    ax.set_title("Évolution du Solde Global")
    ax.set_grid(True, linestyle="--", alpha=0.6)
    return fig
