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
    cursor.execute("SELECT id, titre, categorie, statut, date_creation FROM taches ORDER BY date_creation DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def search_tasks(keyword):
    """Recherche des tâches par titre."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titre, categorie, statut, date_creation FROM taches WHERE titre LIKE %s ORDER BY date_creation DESC",
        (f"%{keyword}%",)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(titre, description, categorie):
    """Ajoute une nouvelle tâche dans la base."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO taches (titre, description, categorie) VALUES (%s, %s, %s)",
        (titre, description, categorie)
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
        self.root.geometry("750x750")
        self.root.configure(bg="#07070f")
        self.root.resizable(True, True)

        self.build_ui()
        self.refresh_list()

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
            height=1, width=40
        )
        self.entry_desc.grid(row=1, column=1, padx=10, pady=3, sticky="ew")

        tk.Label(form_frame, text="Catégorie :", font=("Arial", 10, "bold"),
                 bg="#0f0f1a", fg="#e2e8f0").grid(row=2, column=0, sticky="w", pady=3)

        self.categorie_var = tk.StringVar(value="Personnel")
        self.combo_categorie = ttk.Combobox(
            form_frame,
            textvariable=self.categorie_var,
            values=["Cours", "INSI", "Personnel", "Projet", "Révision", "Autre"],
            state="readonly",
            font=("Arial", 10),
            width=20
        )
        self.combo_categorie.grid(row=2, column=1, padx=10, pady=3, sticky="w")

        btn_add = tk.Button(
            form_frame, text="➕ Ajouter la tâche",
            font=("Arial", 10, "bold"),
            bg="#7c3aed", fg="white",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.add_task
        )
        btn_add.grid(row=3, column=1, padx=10, pady=8, sticky="e")

        form_frame.columnconfigure(1, weight=1)

        # ── BARRE DE RECHERCHE ── (NOUVEAU)
        search_frame = tk.Frame(self.root, bg="#07070f")
        search_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(search_frame, text="🔍", font=("Arial", 12),
                 bg="#07070f", fg="#06b6d4").pack(side="left", padx=(0, 5))

        self.entry_search = tk.Entry(
            search_frame, font=("Arial", 11),
            bg="#1a1a2e", fg="#e2e8f0",
            insertbackground="white", relief="flat",
            width=30
        )
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        tk.Button(
            search_frame, text="✖ Effacer",
            font=("Arial", 9),
            bg="#475569", fg="white",
            relief="flat", cursor="hand2",
            padx=8, pady=3,
            command=self.clear_search
        ).pack(side="left", padx=5)

        # ── LISTE DES TÂCHES ──
        list_frame = tk.Frame(self.root, bg="#07070f")
        list_frame.pack(fill="both", expand=False, padx=20, pady=(0, 10))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

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
            columns=("id", "titre", "categorie", "statut", "date"),
            show="headings",
            height=8,
            yscrollcommand=scrollbar.set
        )

        self.tree.heading("id",        text="")
        self.tree.heading("titre",     text="Titre")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("statut",    text="Statut")
        self.tree.heading("date",      text="Date")

        self.tree.column("id",        width=0,  stretch=False)
        self.tree.column("titre",     width=150, anchor="center")
        self.tree.column("categorie", width=100, anchor="center")
        self.tree.column("statut",    width=100, anchor="center")
        self.tree.column("date",      width=140, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_description)
        # ── DESCRIPTION DE LA TÂCHE SÉLECTIONNÉE ──
        self.label_desc = tk.Label(
            self.root, text="📌 Clique sur une tâche pour voir sa description",
            font=("Arial", 9), bg="#0f0f1a",
            fg="#475569", anchor="w", padx=10,
            wraplength=700
        )
        self.label_desc.pack(fill="x", padx=20, pady=(0, 5))
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
    def on_search(self, event=None):
        """Filtre les tâches en temps réel selon le titre."""
        keyword = self.entry_search.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = search_tasks(keyword) if keyword else get_all_tasks()
        for task in tasks:
            task_id, titre, categorie, statut, date = task
            date_str = date.strftime("%d/%m/%Y %H:%M") if date else ""
            statut_str = "✅ Terminé" if statut == "termine" else "🔄 En cours"
            self.tree.insert("", "end", values=(task_id, titre, categorie or "—", statut_str, date_str))

        self.status_bar.config(text=f"  {len(tasks)} tâche(s) trouvée(s)")

    def clear_search(self):
        """Efface la recherche et recharge toutes les tâches."""
        self.entry_search.delete(0, "end")
        self.refresh_list()

    def refresh_list(self):
        """Recharge toutes les tâches depuis MySQL et les affiche."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = get_all_tasks()
        for task in tasks:
            task_id, titre, categorie, statut, date = task
            date_str = date.strftime("%d/%m/%Y %H:%M") if date else ""
            statut_str = "✅ Terminé" if statut == "termine" else "🔄 En cours"
            self.tree.insert("", "end", values=(task_id, titre, categorie or "—", statut_str, date_str))

        self.status_bar.config(text=f"  {len(tasks)} tâche(s) au total")

    def add_task(self):
        """Récupère les valeurs du formulaire et ajoute la tâche."""
        titre = self.entry_titre.get().strip()
        description = self.entry_desc.get("1.0", "end").strip()
        categorie = self.categorie_var.get()

        if not titre:
            messagebox.showwarning("Attention", "Le titre est obligatoire !")
            return

        add_task(titre, description, categorie)

        self.entry_titre.delete(0, "end")
        self.entry_desc.delete("1.0", "end")
        self.categorie_var.set("Personnel")

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
        statut_str = item["values"][3]

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

        confirm = messagebox.askyesno(
            "Confirmer",
            f"Supprimer la tâche :\n\"{titre}\" ?"
        )
        if confirm:
            delete_task(task_id)
            self.refresh_list()
            self.status_bar.config(text="  🗑 Tâche supprimée.")
    def show_description(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        task_id = item["values"][0]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM taches WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        conn.close()

        desc = result[0] if result and result[0] else "Aucune description."
        self.label_desc.config(text=f"📌 {desc}", fg="#06b6d4")


# ─────────────────────────────────────────────
# LANCEMENT DE L'APPLICATION
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()