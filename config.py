import mysql.connector


def get_connection():
    """
    Centralise la connexion à la base de données.
    """
    try:
        return mysql.connector.connect(
            host="localhost",
            user="michel",
            password="",
            database="databank",
            port=3306,
        )
    except mysql.connector.Error as err:
        print(f"Erreur de connexion : {err}")
        return None
