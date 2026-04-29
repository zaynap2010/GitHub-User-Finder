import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime
import threading
import webbrowser

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        self.current_results = []
        
        self.setup_ui()
        self.load_favorites_display()
        
    def setup_ui(self):
        # Панель поиска
        search_frame = ttk.LabelFrame(self.root, text="Поиск пользователя", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Логин GitHub:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40, font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())
        
        self.search_btn = ttk.Button(search_frame, text="🔍 Найти", command=self.search_user)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.search_tab = ttk.Frame(self.notebook)
        self.favorites_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="📋 Результаты поиска")
        self.notebook.add(self.favorites_tab, text="⭐ Избранное")
        
        self.setup_search_tab()
        self.setup_favorites_tab()
        
        # Статусная строка
        self.status_var = tk.StringVar(value="✅ Готов к работе. Введите логин пользователя GitHub.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_search_tab(self):
        columns = ("username", "name", "repos", "followers", "following")
        self.search_tree = ttk.Treeview(self.search_tab, columns=columns, show="headings", height=18)
        
        self.search_tree.heading("username", text="Логин")
        self.search_tree.heading("name", text="Имя")
        self.search_tree.heading("repos", text="Репозитории")
        self.search_tree.heading("followers", text="Подписчики")
        self.search_tree.heading("following", text="Подписки")
        
        self.search_tree.column("username", width=150)
        self.search_tree.column("name", width=200)
        self.search_tree.column("repos", width=100)
        self.search_tree.column("followers", width=100)
        self.search_tree.column("following", width=100)
        
        scrollbar = ttk.Scrollbar(self.search_tab, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = ttk.Frame(self.search_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="⭐ Добавить в избранное", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🌐 Открыть профиль", command=self.open_profile).pack(side=tk.LEFT, padx=5)
        
    def setup_favorites_tab(self):
        columns = ("username", "name", "repos", "followers", "added_date")
        self.favorites_tree = ttk.Treeview(self.favorites_tab, columns=columns, show="headings", height=18)
        
        self.favorites_tree.heading("username", text="Логин")
        self.favorites_tree.heading("name", text="Имя")
        self.favorites_tree.heading("repos", text="Репозитории")
        self.favorites_tree.heading("followers", text="Подписчики")
        self.favorites_tree.heading("added_date", text="Дата добавления")
        
        self.favorites_tree.column("username", width=150)
        self.favorites_tree.column("name", width=200)
        self.favorites_tree.column("repos", width=100)
        self.favorites_tree.column("followers", width=100)
        self.favorites_tree.column("added_date", width=150)
        
        scrollbar = ttk.Scrollbar(self.favorites_tab, orient=tk.VERTICAL, command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=scrollbar.set)
        
        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = ttk.Frame(self.favorites_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="❌ Удалить из избранного", command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)
        
    def search_user(self):
        username = self.search_entry.get().strip()
        
        # Проверка на пустое поле
        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return
            
        self.search_btn.config(state=tk.DISABLED)
        self.status_var.set(f"⏳ Поиск пользователя: {username}...")
        
        thread = threading.Thread(target=self.fetch_user_data, args=(username,))
        thread.daemon = True
        thread.start()
        
    def fetch_user_data(self, username):
        try:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.root.after(0, self.display_user_result, user_data)
                self.root.after(0, lambda: self.status_var.set(f"✅ Найден пользователь: {user_data.get('name', username)}"))
            elif response.status_code == 404:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден на GitHub!"))
                self.root.after(0, lambda: self.status_var.set("❌ Пользователь не найден"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}"))
                self.root.after(0, lambda: self.status_var.set("❌ Ошибка при поиске"))
                
        except requests.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка сети: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("❌ Ошибка соединения"))
        finally:
            self.root.after(0, lambda: self.search_btn.config(state=tk.NORMAL))
            
    def display_user_result(self, user):
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
            
        self.current_results = [user]
        
        values = (
            user.get("login", "N/A"),
            user.get("name", "Не указано"),
            user.get("public_repos", 0),
            user.get("followers", 0),
            user.get("following", 0)
        )
        
        self.search_tree.insert("", tk.END, values=values, iid=user.get("login"))
        
    def add_to_favorites(self):
        selected = self.search_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Сначала найдите пользователя!")
            return
            
        username = selected[0]
        
        for user in self.current_results:
            if user.get("login") == username:
                if username not in self.favorites:
                    self.favorites[username] = {
                        "login": user.get("login"),
                        "name": user.get("name", "Не указано"),
                        "public_repos": user.get("public_repos", 0),
                        "followers": user.get("followers", 0),
                        "following": user.get("following", 0),
                        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "html_url": user.get("html_url", "")
                    }
                    self.save_favorites()
                    self.load_favorites_display()
                    self.status_var.set(f"⭐ {username} добавлен в избранное")
                else:
                    messagebox.showinfo("Информация", f"{username} уже в избранном!")
                break
                
    def remove_from_favorites(self):
        selected = self.favorites_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить выбранного пользователя из избранного?"):
            username = selected[0]
            del self.favorites[username]
            self.save_favorites()
            self.load_favorites_display()
            self.status_var.set(f"❌ {username} удален из избранного")
            
    def open_profile(self):
        selected = self.search_tree.selection()
        if selected:
            username = selected[0]
            webbrowser.open(f"https://github.com/{username}")
            
    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
            
    def load_favorites_display(self):
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
            
        for username, data in self.favorites.items():
            values = (
                data.get("login"),
                data.get("name"),
                data.get("public_repos"),
                data.get("followers"),
                data.get("added_date")
            )
            self.favorites_tree.insert("", tk.END, values=values, iid=username)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
