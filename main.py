import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем API‑ключ из .env файла
API_KEY = os.getenv('API_KEY')
API_URL = "https://v6.exchangerate-api.com/v6/{key}/latest/{base}"

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("800x500")

        # Загрузка списка валют
        self.currencies = self.load_currencies()
        self.history = self.load_history()

        self.setup_ui()
        self.update_currency_lists()

    def load_currencies(self):
        """Загружает список поддерживаемых валют (можно расширить из API)"""
        return ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'RUB', 'CAD', 'AUD', 'CHF', 'SEK']

    def load_history(self):
        """Загружает историю из JSON‑файла, если он существует"""
        if os.path.exists('history.json'):
            with open('history.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_history(self):
        """Сохраняет историю в JSON‑файл"""
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        # Выбор валюты «из»
        tk.Label(self.root, text="Из валюты:").grid(row=0, column=0, padx=10, pady=10)
        self.from_currency = ttk.Combobox(self.root, values=self.currencies)
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)

        # Выбор валюты «в»
        tk.Label(self.root, text="В валюту:").grid(row=1, column=0, padx=10, pady=10)
        self.to_currency = ttk.Combobox(self.root, values=self.currencies)
        self.to_currency.grid(row=1, column=1, padx=10, pady=10)

        # Поле ввода суммы
        tk.Label(self.root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)

        # Кнопка конвертации
        self.convert_button = tk.Button(self.root, text="Конвертировать", command=self.convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Поле вывода результата
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Таблица истории
        self.history_tree = ttk.Treeview(self.root, columns=('From', 'To', 'Amount', 'Result'), show='headings')
        self.history_tree.heading('From', text='Из валюты')
        self.history_tree.heading('To', text='В валюту')
        self.history_tree.heading('Amount', text='Сумма')
        self.history_tree.heading('Result', text='Результат')
        self.history_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        # Обновляем таблицу истории
        self.update_history_table()

    def update_currency_lists(self):
        """Обновляет списки валют в выпадающих меню"""
        self.from_currency['values'] = self.currencies
        self.to_currency['values'] = self.currencies

    def convert(self):
        """Выполняет конвертацию валюты"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        amount_str = self.amount_entry.get()

        # Валидация ввода
        if not from_curr or not to_curr:
            messagebox.showerror("Ошибка", "Выберите обе валюты!")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
            return

        # Получение курса через API
        try:
            response = requests.get(API_URL.format(key=API_KEY, base=from_curr))
            response.raise_for_status()
            data = response.json()

            if to_curr not in data['conversion_rates']:
                messagebox.showerror("Ошибка", f"Валюта {to_curr} не поддерживается!")
                return

            rate = data['conversion_rates'][to_curr]
            result = amount * rate

            # Отображение результата
            self.result_label.config(text=f"{amount} {from_curr} = {result:.2f} {to_curr}")

            # Добавление в историю
            entry = {
                'from': from_curr,
                'to': to_curr,
                'amount': amount,
                'result': round(result, 2)
            }
            self.history.append(entry)
            self.save_history()
            self.update_history_table()

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось получить данные: {e}")

    def update_history_table(self):
        """Обновляет таблицу истории"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for entry in self.history:
            self.history_tree.insert('', 'end', values=(
                entry['from'],
                entry['to'],
                entry['amount'],
                entry['result']
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
