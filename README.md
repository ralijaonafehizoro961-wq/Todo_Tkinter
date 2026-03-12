# 📝 Todo List — Tkinter + MySQL

Application de gestion de tâches en Python avec interface graphique.

## Technologies
- Python 3 + Tkinter (GUI)
- MySQL (base de données)
- mysql-connector-python

## Installation
```bash
git clone https://github.com/ralijaonafehizoro961-wq/Todo_Tkinter
cd Todo-Tkinter
pip3 install mysql-connector-python
```

Crée la base de données :
```sql
CREATE DATABASE Todo_app;
USE Todo_app;
CREATE TABLE taches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    description TEXT,
    statut ENUM('en_cours','termine') DEFAULT 'en_cours',
    date_creation DATETIME DEFAULT NOW()
);
```

Lance l'application :
```bash
python3 main.py
```

## Auteur
Fehizoro RALIJAONA 🇲🇬