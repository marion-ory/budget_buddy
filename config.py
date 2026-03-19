import mysql.connector


def get_connection():
    """
    Centralise la connexion à la base de données.
    """
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="root", database="databank"
        )
    except mysql.connector.Error as err:
        print(f"Erreur de connexion : {err}")
        return None
