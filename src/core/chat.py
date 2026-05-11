from typing import Dict, List, Optional
from src.utils.helpers import write_log, get_current_time
from src.config.settings import MAX_HISTORY_CONTEXT

class ChatManager:
    def __init__(self):
        self.chat_data: Dict[str, List[str]] = {}
        self.current_chat: Optional[str] = None
        self.selected_model: Optional[str] = None

    def create_chat(self, chat_name: str):
        if chat_name not in self.chat_data:
            self.chat_data[chat_name] = []

    def set_current_chat(self, chat_name: str):
        self.current_chat = chat_name

    def add_message(self, chat_name: str, sender: str, message: str):
        timestamp = get_current_time()
        formatted_msg = f"{timestamp} {sender}: {message}"
        
        if chat_name not in self.chat_data:
            self.chat_data[chat_name] = []
            
        self.chat_data[chat_name].append(formatted_msg)
        write_log(chat_name, formatted_msg)

    def get_history(self, chat_name: str) -> List[str]:
        return self.chat_data.get(chat_name, [])

    def clear_chat(self, chat_name: str):
        if chat_name in self.chat_data:
            self.chat_data[chat_name] = []
            write_log(chat_name, f"{get_current_time()} {chat_name} foi limpo.")

    def get_compacted_history(self, chat_name: str) -> str:
        history = self.get_history(chat_name)
        compacted = ""
        for message in reversed(history):
            if len(compacted) + len(message) > MAX_HISTORY_CONTEXT:
                break
            compacted = message + "\n" + compacted
        return compacted
