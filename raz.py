import mysql.connector

# On teste les deux clés possibles pour ton port 3306
options = [
    {"user": "root", "password": "root", "port": 8889},
    {"user": "root", "password": "", "port": 8889},
]

found = False
for config in options:
    try:
        print(f"Tentative de connexion avec mdp='{config['password']}'...")
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user=config["user"],
            password=config["password"],
            port=config["port"],
        )
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS databank")
        print(f"✅ SUCCÈS : Base supprimée avec le mdp '{config['password']}' !")
        conn.close()
        found = True
        break
    except Exception as e:
        print(f"❌ Échec avec '{config['password']}' : {e}")

if not found:
    print(
        "\n🚨 Aucune connexion n'a fonctionné. Vérifie que MAMP est bien lancé et que MySQL est sur le port 3306."
    )
