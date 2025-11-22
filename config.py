import os

class Config:
    BOT_TOKEN = "8579547514:AAFJQR6CL_Ui2Q8-Ac0g_y4vBtwrR4tXraU"
    WEBAPP_URL = "https://your-app.herokuapp.com"  # Замените на ваш URL
    SECRET_KEY = "crypto_bot_secret_key_2024"
    
    # Настройки базы данных
    DATABASE_URL = "sqlite:///crypto_bot.db"
    
    # Криптовалюты для торговли
    CRYPTO_CURRENCIES = {
        'BTC': {'name': 'Bitcoin', 'price': 45000.0},
        'ETH': {'name': 'Ethereum', 'price': 2500.0},
        'SOL': {'name': 'Solana', 'price': 120.0},
        'ADA': {'name': 'Cardano', 'price': 0.48},
        'DOT': {'name': 'Polkadot', 'price': 7.2},
        'USDT': {'name': 'Tether', 'price': 1.0}
    }
    
    # Начальный баланс для новых пользователей
    STARTING_BALANCE = {
        'USD': 10000.0,
        'BTC': 0.0,
        'ETH': 0.0,
        'SOL': 0.0,
        'ADA': 0.0,
        'DOT': 0.0,
        'USDT': 0.0
    }
