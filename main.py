from src.ui.app import OllamaApp
from src.core.ollama import ensure_admin

def main():
    # Mantendo a regra original de rodar como admin/root
    ensure_admin()
    
    app = OllamaApp()
    app.mainloop()

if __name__ == "__main__":
    main()
