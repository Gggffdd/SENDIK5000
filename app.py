from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlalchemy
from database import SessionLocal, User, Transaction, Order
import config
import json
from datetime import datetime
import os

app = Flask(__name__, 
            static_folder='public/static',
            template_folder='public')
app.secret_key = config.Config.SECRET_KEY
cfg = config.Config()

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('public/static', path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

@app.route('/trading')
def trading():
    pair = request.args.get('pair', 'BTC')
    return render_template('trading.html', pair=pair)

@app.route('/exchange')
def exchange():
    return render_template('exchange.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

# API endpoints
@app.route('/api/user/<int:telegram_id>')
def get_user(telegram_id):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'balances': {
                'USD': user.balance_usd,
                'BTC': user.balance_btc,
                'ETH': user.balance_eth,
                'SOL': user.balance_sol,
                'ADA': user.balance_ada,
                'DOT': user.balance_dot,
                'USDT': user.balance_usdt
            },
            'total_value': calculate_total_value(user)
        }
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/prices')
def get_prices():
    return jsonify(cfg.CRYPTO_CURRENCIES)

@app.route('/api/buy', methods=['POST'])
def buy_crypto():
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        crypto = data.get('crypto')
        amount = float(data.get('amount'))
        price = float(data.get('price'))
        
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        total_cost = amount * price
        
        if user.balance_usd < total_cost:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Обновляем балансы
        user.balance_usd -= total_cost
        crypto_balance_attr = f'balance_{crypto.lower()}'
        current_balance = getattr(user, crypto_balance_attr)
        setattr(user, crypto_balance_attr, current_balance + amount)
        
        # Создаем транзакцию
        transaction = Transaction(
            user_id=user.id,
            type='buy',
            crypto_symbol=crypto,
            amount=amount,
            price=price,
            total=total_cost
        )
        db.add(transaction)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully bought {amount} {crypto}',
            'new_balances': {
                'USD': user.balance_usd,
                crypto: getattr(user, crypto_balance_attr)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/sell', methods=['POST'])
def sell_crypto():
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        crypto = data.get('crypto')
        amount = float(data.get('amount'))
        price = float(data.get('price'))
        
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        crypto_balance_attr = f'balance_{crypto.lower()}'
        current_balance = getattr(user, crypto_balance_attr)
        
        if current_balance < amount:
            return jsonify({'error': 'Insufficient crypto balance'}), 400
        
        total_value = amount * price
        
        # Обновляем балансы
        user.balance_usd += total_value
        setattr(user, crypto_balance_attr, current_balance - amount)
        
        # Создаем транзакцию
        transaction = Transaction(
            user_id=user.id,
            type='sell',
            crypto_symbol=crypto,
            amount=amount,
            price=price,
            total=total_value
        )
        db.add(transaction)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully sold {amount} {crypto}',
            'new_balances': {
                'USD': user.balance_usd,
                crypto: getattr(user, crypto_balance_attr)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/transactions/<int:telegram_id>')
def get_transactions(telegram_id):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        transactions = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.timestamp.desc()).limit(50).all()
        
        transactions_data = []
        for tx in transactions:
            transactions_data.append({
                'id': tx.id,
                'type': tx.type,
                'crypto': tx.crypto_symbol,
                'amount': tx.amount,
                'price': tx.price,
                'total': tx.total,
                'timestamp': tx.timestamp.isoformat()
            })
        
        return jsonify(transactions_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def calculate_total_value(user):
    total = user.balance_usd
    for crypto, data in cfg.CRYPTO_CURRENCIES.items():
        balance = getattr(user, f'balance_{crypto.lower()}')
        total += balance * data['price']
    return total

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'CryptoPro API is running'})

# Для Vercel
if __name__ == '__main__':
    from database import init_db
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
