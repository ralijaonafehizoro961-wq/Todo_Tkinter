import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG
from datetime import datetime

# ─────────────────────────────────────────────
# CONNEXION BASE DE DONNÉES
# ─────────────────────────────────────────────
def get_connection():
    """Crée et retourne une connexion MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


# ─────────────────────────────────────────────
# FONCTIONS CRUD (Create, Read, Update, Delete)
# ─────────────────────────────────────────────
def get_all_tasks():
    """Récupère toutes les tâches depuis MySQL."""
    conn = get_connection()
    cursor = conn.cursor()
    # On trie par date pour voir les plus récentes en premier
    cursor.execute("SELECT id, titre, statut, date_creation FROM taches ORDER BY date_creation DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(titre, description):
    """Ajoute une nouvelle tâche dans la base."""
    conn = get_connection()
    cursor = conn.cursor()
    # On utilise %s pour éviter les injections SQL — bonne pratique !
    cursor.execute(
        "INSERT INTO taches (titre, description) VALUES (%s, %s)",
        (titre, description)
    )
    conn.commit()
    conn.close()

def toggle_task(task_id, current_status):
    """Change le statut d'une tâche entre en_cours et termine."""
    new_status = "termine" if current_status == "en_cours" else "en_cours"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE taches SET statut = %s WHERE id = %s",
        (new_status, task_id)
    )
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Supprime une tâche par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM taches WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# INTERFACE GRAPHIQUE TKINTER
# ─────────────────────────────────────────────
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Todo List")
        self.root.geometry("700x700")
        self.root.configure(bg="#07070f")
        self.root.resizable(True, True)

        self.build_ui()
        self.refresh_list()  # Charge les tâches au démarrage

    def build_ui(self):
        """Construit toute l'interface graphique."""

        # ── TITRE ──
        title = tk.Label(
            self.root,
            text="📝 Todo List",
            font=("Arial", 18, "bold"),
            bg="#07070f", fg="#7c3aed"
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Fehizoro",
            font=("Arial", 10),
            bg="#07070f", fg="#475569"
        )
        subtitle.pack(pady=(0, 15))

        # ── FORMULAIRE D'AJOUT ──
        form_frame = tk.Frame(self.root, bg="#0f0f1a", padx=15, pady=15)
        form_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(form_frame, text="Titre :", font=("Arial", 10, "bold"),
                 bg="#0f0f1a", fg="#e2e8f0").grid(row=0, column=0, sticky="w", pady=3)

        self.entry_titre = tk.Entry(
            form_frame, font=("Arial", 11),
            bg="#1a1a2e", fg="#e2e8f0",
            insertbackground="white", relief="flat",
            width=40
        )
        self.entry_titre.grid(row=0, column=1, padx=10, pady=3, sticky="ew")

        tk.Label(form_frame, text="Description :", font=("Arial", 10, "bold"),
                 bg="#0f0f1a", fg="#e2e8f0").grid(row=1, column=0, sticky="nw", pady=3)

        self.entry_desc = tk.Text(
            form_frame, font=("Arial", 10),
            bg="#1a1a2e", fg="#e2e8f0",
            insertbackground="white", relief="flat",
            height=3, width=40
        )
        self.entry_desc.grid(row=1, column=1, padx=10, pady=3, sticky="ew")

        # Bouton Ajouter
        btn_add = tk.Button(
            form_frame, text="➕ Ajouter la tâche",
            font=("Arial", 10, "bold"),
            bg="#7c3aed", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.add_task
        )
        btn_add.grid(row=2, column=1, padx=10, pady=8, sticky="e")

        form_frame.columnconfigure(1, weight=1)

        # ── LISTE DES TÂCHES ──
        list_frame = tk.Frame(self.root, bg="#07070f")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # Tableau des tâches
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background="#0f0f1a",
            foreground="#e2e8f0",
            fieldbackground="#0f0f1a",
            rowheight=30,
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading",
            background="#1a1a2e",
            foreground="#06b6d4",
            font=("Arial", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#7c3aed")])

        self.tree = ttk.Treeview(
            list_frame,
            columns=("id", "titre", "statut", "date"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        # Colonnes
        self.tree.heading("id",     text="ID")
        self.tree.heading("titre",  text="Titre")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("date",   text="Date")

        self.tree.column("id",     width=40,  anchor="center")
        self.tree.column("titre",  width=280, anchor="w")
        self.tree.column("statut", width=100, anchor="center")
        self.tree.column("date",   width=150, anchor="center")

        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # ── BOUTONS D'ACTION ──
        btn_frame = tk.Frame(self.root, bg="#07070f")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="✅ Terminer / Rouvrir",
            font=("Arial", 10, "bold"),
            bg="#10b981", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.toggle_task
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🗑 Supprimer",
            font=("Arial", 10, "bold"),
            bg="#ef4444", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.delete_task
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🔄 Actualiser",
            font=("Arial", 10, "bold"),
            bg="#475569", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.refresh_list
        ).pack(side="left", padx=5)

        # ── BARRE DE STATUT ──
        self.status_bar = tk.Label(
            self.root, text="Prêt",
            font=("Arial", 9), bg="#0f0f1a",
            fg="#475569", anchor="w", padx=10
        )
        self.status_bar.pack(fill="x", side="bottom")

    # ─────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────
    def refresh_list(self):
        """Recharge toutes les tâches depuis MySQL et les affiche."""
        # On vide d'abord la liste
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = get_all_tasks()
        for task in tasks:
            task_id, titre, statut, date = task
            # Formatage de la date
            date_str = date.strftime("%d/%m/%Y %H:%M") if date else ""
            # Icône selon le statut
            statut_str = "✅ Terminé" if statut == "termine" else "🔄 En cours"
            self.tree.insert("", "end", values=(task_id, titre, statut_str, date_str))

        count = len(tasks)
        self.status_bar.config(text=f"  {count} tâche(s) au total")

    def add_task(self):
        """Récupère les valeurs du formulaire et ajoute la tâche."""
        titre = self.entry_titre.get().strip()
        description = self.entry_desc.get("1.0", "end").strip()

        if not titre:
            messagebox.showwarning("Attention", "Le titre est obligatoire !")
            return

        add_task(titre, description)

        # On vide le formulaire après l'ajout
        self.entry_titre.delete(0, "end")
        self.entry_desc.delete("1.0", "end")

        self.refresh_list()
        self.status_bar.config(text="  ✅ Tâche ajoutée avec succès !")

    def toggle_task(self):
        """Change le statut de la tâche sélectionnée."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionne une tâche d'abord !")
            return

        item = self.tree.item(selected[0])
        task_id = item["values"][0]
        statut_str = item["values"][2]

        # On détermine le statut actuel depuis l'icône affichée
        current = "termine" if "Terminé" in statut_str else "en_cours"
        toggle_task(task_id, current)
        self.refresh_list()

    def delete_task(self):
        """Supprime la tâche sélectionnée après confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionne une tâche d'abord !")
            return

        item = self.tree.item(selected[0])
        task_id = item["values"][0]
        titre = item["values"][1]

        # Demande confirmation avant de supprimer
        confirm = messagebox.askyesno(
            "Confirmer",
            f"Supprimer la tâche :\n\"{titre}\" ?"
        )
        if confirm:
            delete_task(task_id)
            self.refresh_list()
            self.status_bar.config(text="  🗑 Tâche supprimée.")


# ─────────────────────────────────────────────
# LANCEMENT DE L'APPLICATION
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
