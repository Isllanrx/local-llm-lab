import customtkinter as ctk
import threading
import webbrowser
from tkinter import messagebox
from typing import Optional

from src.config.settings import APP_TITLE, APP_GEOMETRY, DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, MAX_MESSAGE_LENGTH, LINKEDIN_URL
from src.core.ollama import OllamaClient
from src.core.chat import ChatManager
from src.utils.helpers import get_current_time

class OllamaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.font = ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE)

        self.ollama = OllamaClient()
        self.chat_manager = ChatManager()
        self.is_processing = False
        self.chat_lock = threading.Lock()

        self._setup_grid()
        self._create_widgets()
        self._initialize_chats()

    def _setup_grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

    def _create_widgets(self):
        self.sidebar_frame = ctk.CTkFrame(self)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, padx=5, pady=10, sticky="ns")
        self.grid_columnconfigure(0, weight=0)

        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkTextbox(self.chat_frame, wrap=ctk.WORD, state=ctk.DISABLED, font=self.font)
        self.chat_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.entry = ctk.CTkTextbox(self, height=100, font=self.font, wrap=ctk.WORD)
        self.entry.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.entry.bind('<Return>', self.send_message)

        self.send_button = ctk.CTkButton(self, text="Enviar", command=self.send_message, font=self.font)
        self.send_button.grid(row=4, column=1, pady=(10, 20), sticky="n")

        self.clear_button = ctk.CTkButton(self.sidebar_frame, text="Limpar Chat", font=self.font, command=self.clear_chat)
        self.clear_button.grid(row=100, column=0, padx=10, pady=20, sticky="s")

        self.sobre_button = ctk.CTkButton(self, text="Desenvolvido por Isllan Toso", font=self.font, command=self._open_linkedin)
        self.sobre_button.grid(row=4, column=1, padx=10, pady=10, sticky="se")

        models = self.ollama.get_models()
        self.model_dropdown = ctk.CTkOptionMenu(self, values=models, command=self._update_model_selection, font=self.font)
        self.model_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="n")
        self.model_dropdown.set("Selecione um modelo")

        self.error_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="red")
        self.error_label.grid(row=1, column=1, padx=10, pady=5, sticky="s")

    def _initialize_chats(self):
        for i in range(1, 6):
            chat_name = f"Chat {i}"
            self.chat_manager.create_chat(chat_name)
            self._add_chat_button(chat_name)

    def _add_chat_button(self, chat_name: str):
        btn = ctk.CTkButton(self.sidebar_frame, text=chat_name, font=self.font, command=lambda: self.open_chat(chat_name))
        btn.grid(row=len(self.sidebar_frame.winfo_children()), pady=5, sticky="w")

    def _open_linkedin(self):
        webbrowser.open(LINKEDIN_URL)

    def _update_model_selection(self, model: str):
        self.chat_manager.selected_model = model
        self._update_chat_ui_message(f"Modelo selecionado: {model}")
        if not self.chat_manager.current_chat:
            self.open_chat("Chat 1")

    def open_chat(self, chat_name: str):
        if self.is_processing:
            messagebox.showerror("Erro", "A IA está processando, aguarde a resposta antes de trocar de chat.")
            return

        if self.chat_manager.current_chat == chat_name:
            return

        self.chat_manager.set_current_chat(chat_name)
        self.chat_box.configure(state=ctk.NORMAL)
        self.chat_box.delete("1.0", ctk.END)
        
        timestamp = get_current_time()
        self.chat_box.insert(ctk.END, f"{timestamp} {chat_name} aberto.\n\n")

        for msg in self.chat_manager.get_history(chat_name):
            self.chat_box.insert(ctk.END, msg + "\n\n")
        
        self.chat_box.configure(state=ctk.DISABLED)
        self.chat_box.yview(ctk.END)

    def send_message(self, event=None):
        if self.is_processing:
            messagebox.showerror("Erro", "A IA está processando, aguarde a resposta.")
            return

        user_message = self.entry.get("1.0", ctk.END).strip()
        
        if not user_message:
            messagebox.showerror("Erro", "Por favor, digite uma mensagem antes de enviar.")
            return
            
        if not self.chat_manager.selected_model:
            messagebox.showerror("Erro", "Por favor, selecione um modelo antes de enviar a mensagem.")
            return

        if len(user_message) > MAX_MESSAGE_LENGTH:
            user_message = user_message[:MAX_MESSAGE_LENGTH]
            messagebox.showwarning("Aviso", f"Mensagem muito longa! Foi limitada até {MAX_MESSAGE_LENGTH} caracteres.")

        timestamp = get_current_time()
        self.chat_box.configure(state=ctk.NORMAL)
        self.chat_box.insert(ctk.END, f"{timestamp} Você: {user_message}\n\n", 'user')
        self.entry.delete("1.0", ctk.END)
        self.chat_box.configure(state=ctk.DISABLED)
        self.chat_box.yview(ctk.END)

        self.chat_manager.add_message(self.chat_manager.current_chat, "Você", user_message)

        self.is_processing = True
        threading.Thread(target=self._interact, args=(user_message,), daemon=True).start()

    def _interact(self, user_input: str):
        try:
            history = self.chat_manager.get_compacted_history(self.chat_manager.current_chat)
            prompt = f"Contexto:\n{history}\n\nUsuário: {user_input}\n"
            response = self.ollama.chat(self.chat_manager.selected_model, prompt)
            self.after(0, self._update_response_ui, response.strip())
        except Exception as e:
            self.after(0, self._update_response_ui, f"Erro: {str(e)}")
        finally:
            self.is_processing = False

    def _update_response_ui(self, response: str):
        timestamp = get_current_time()
        model_name = self.chat_manager.selected_model
        
        with self.chat_lock:
            self.chat_manager.add_message(self.chat_manager.current_chat, f"Llama ({model_name})", response)
            self.chat_box.configure(state=ctk.NORMAL)
            self.chat_box.insert(ctk.END, f"{timestamp} Llama ({model_name}): {response}\n\n", 'bot')
            self.chat_box.yview(ctk.END)
            self.chat_box.configure(state=ctk.DISABLED)

    def _update_chat_ui_message(self, message: str):
        self.chat_box.configure(state=ctk.NORMAL)
        self.chat_box.insert(ctk.END, f"{message}\n\n")
        self.chat_box.configure(state=ctk.DISABLED)
        self.chat_box.yview(ctk.END)

    def clear_chat(self):
        if not self.chat_manager.current_chat:
            return
            
        if messagebox.askyesno("Confirmar", "Você tem certeza que deseja limpar o chat?"):
            self.chat_manager.clear_chat(self.chat_manager.current_chat)
            self.chat_box.configure(state=ctk.NORMAL)
            self.chat_box.delete("1.0", ctk.END)
            self.chat_box.configure(state=ctk.DISABLED)
