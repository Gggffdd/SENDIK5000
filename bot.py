from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlalchemy
from database import SessionLocal, User, Transaction, Order
import config

class CryptoBot:
    def __init__(self):
        self.config = config.Config()
        self.application = Application.builder().token(self.config.BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("wallet", self.wallet))
        self.application.add_handler(CommandHandler("trade", self.trade))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db = SessionLocal()
        
        # Создаем или получаем пользователя
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.add(db_user)
            db.commit()
        
        keyboard = [
            [InlineKeyboardButton("💰 Кошелек", callback_data="wallet")],
            [InlineKeyboardButton("📊 Торговать", callback_data="trade")],
            [InlineKeyboardButton("📈 Портфель", callback_data="portfolio")],
            [InlineKeyboardButton("🔄 Обмен", callback_data="exchange")],
            [InlineKeyboardButton("🌐 Открыть Web App", web_app=WebAppInfo(url=f"{self.config.WEBAPP_URL}/"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🚀 **Добро пожаловать в CryptoPro!**\n\n"
            f"Привет, {user.first_name}! Это профессиональная платформа для торговли криптовалютами.\n\n"
            f"📊 **Доступные функции:**\n"
            f"• Торговля криптовалютами\n"
            f"• Управление портфелем\n"
            f"• Реальный-time графики\n"
            f"• Безопасный кошелек\n\n"
            f"Нажмите кнопку ниже чтобы начать:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db = SessionLocal()
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text("Пользователь не найден. Используйте /start")
            return
        
        balance_text = f"💼 **Ваш кошелек**\n\n"
        balance_text += f"💵 USD: ${db_user.balance_usd:,.2f}\n"
        balance_text += f"₿ BTC: {db_user.balance_btc:.6f}\n"
        balance_text += f"🔷 ETH: {db_user.balance_eth:.4f}\n"
        balance_text += f"🔶 SOL: {db_user.balance_sol:.4f}\n"
        balance_text += f"🟣 ADA: {db_user.balance_ada:.2f}\n"
        balance_text += f"🔴 DOT: {db_user.balance_dot:.4f}\n"
        balance_text += f"💲 USDT: {db_user.balance_usdt:.2f}\n\n"
        balance_text += f"💎 **Общая стоимость:** ${self.calculate_total_value(db_user):,.2f}"
        
        keyboard = [
            [InlineKeyboardButton("📥 Депозит", callback_data="deposit"),
             InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
            [InlineKeyboardButton("🔄 История", callback_data="transaction_history"),
             InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=f"{self.config.WEBAPP_URL}/wallet"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(balance_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("BTC/USD", callback_data="trade_BTC"),
             InlineKeyboardButton("ETH/USD", callback_data="trade_ETH")],
            [InlineKeyboardButton("SOL/USD", callback_data="trade_SOL"),
             InlineKeyboardButton("ADA/USD", callback_data="trade_ADA")],
            [InlineKeyboardButton("DOT/USD", callback_data="trade_DOT"),
             InlineKeyboardButton("USDT/USD", callback_data="trade_USDT")],
            [InlineKeyboardButton("🌐 Расширенная торговля", web_app=WebAppInfo(url=f"{self.config.WEBAPP_URL}/trading"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📊 **Выберите торговую пару:**\n\n"
            "Доступные пары для торговли:",
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "wallet":
            await self.show_wallet(query)
        elif data == "trade":
            await self.show_trading_pairs(query)
        elif data == "portfolio":
            await self.show_portfolio(query)
        elif data == "exchange":
            await self.show_exchange(query)
        elif data.startswith("trade_"):
            crypto = data.split("_")[1]
            await self.show_trading_interface(query, crypto)
    
    async def show_wallet(self, query):
        user = query.from_user
        db = SessionLocal()
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        balance_text = f"💼 **Ваш кошелек**\n\n"
        balance_text += f"💵 USD: ${db_user.balance_usd:,.2f}\n"
        balance_text += f"₿ BTC: {db_user.balance_btc:.6f}\n"
        balance_text += f"🔷 ETH: {db_user.balance_eth:.4f}\n"
        balance_text += f"🔶 SOL: {db_user.balance_sol:.4f}\n"
        balance_text += f"🟣 ADA: {db_user.balance_ada:.2f}\n"
        balance_text += f"🔴 DOT: {db_user.balance_dot:.4f}\n"
        balance_text += f"💲 USDT: {db_user.balance_usdt:.2f}\n\n"
        balance_text += f"💎 **Общая стоимость:** ${self.calculate_total_value(db_user):,.2f}"
        
        keyboard = [
            [InlineKeyboardButton("📥 Депозит", callback_data="deposit"),
             InlineKeyboardButton("📤 Вывод", callback_data="withdraw")],
            [InlineKeyboardButton("🔄 История", callback_data="transaction_history"),
             InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=f"{self.config.WEBAPP_URL}/wallet"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(balance_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_trading_interface(self, query, crypto):
        price = self.config.CRYPTO_CURRENCIES[crypto]['price']
        
        text = f"📊 **Торговля {crypto}/USD**\n\n"
        text += f"💰 Текущая цена: ${price:,.2f}\n"
        text += f"📈 Изменение за 24ч: +2.4%\n"
        text += f"💎 Объем: ${self.format_volume(crypto)}\n\n"
        text += "Выберите действие:"
        
        keyboard = [
            [InlineKeyboardButton("🟢 Купить", callback_data=f"buy_{crypto}"),
             InlineKeyboardButton("🔴 Продать", callback_data=f"sell_{crypto}")],
            [InlineKeyboardButton("📊 График", callback_data=f"chart_{crypto}"),
             InlineKeyboardButton("ℹ️ Инфо", callback_data=f"info_{crypto}")],
            [InlineKeyboardButton("🌐 Расширенная торговля", web_app=WebAppInfo(url=f"{self.config.WEBAPP_URL}/trading?pair={crypto}"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def calculate_total_value(self, user):
        total = user.balance_usd
        for crypto, data in self.config.CRYPTO_CURRENCIES.items():
            balance = getattr(user, f'balance_{crypto.lower()}')
            total += balance * data['price']
        return total
    
    def format_volume(self, crypto):
        volumes = {
            'BTC': '25.4B',
            'ETH': '14.2B',
            'SOL': '3.8B',
            'ADA': '1.2B',
            'DOT': '850M',
            'USDT': '45.6B'
        }
        return volumes.get(crypto, 'N/A')
    
    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    from database import init_db
    init_db()
    bot = CryptoBot()
    bot.run()
