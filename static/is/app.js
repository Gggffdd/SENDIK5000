class CryptoApp {
    constructor() {
        this.user = null;
        this.prices = {};
        this.init();
    }

    async init() {
        await this.initTelegramWebApp();
        await this.loadUserData();
        await this.loadMarketData();
        this.setupEventListeners();
    }

    async initTelegramWebApp() {
        if (window.Telegram && Telegram.WebApp) {
            Telegram.WebApp.ready();
            Telegram.WebApp.expand();
            Telegram.WebApp.enableClosingConfirmation();
            
            const tg = Telegram.WebApp;
            this.telegramUserId = tg.initDataUnsafe.user?.id;
            
            if (this.telegramUserId) {
                console.log('Telegram User ID:', this.telegramUserId);
            }
        } else {
            console.log('Running outside Telegram');
            // Для тестирования
            this.telegramUserId = 123456789;
        }
    }

    async loadUserData() {
        try {
            if (!this.telegramUserId) {
                throw new Error('No Telegram user ID');
            }

            const response = await fetch(`/api/user/${this.telegramUserId}`);
            if (!response.ok) {
                throw new Error('Failed to load user data');
            }

            this.user = await response.json();
            this.updateUI();
        } catch (error) {
            console.error('Error loading user data:', error);
            this.showError('Failed to load user data');
        }
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/prices');
            this.prices = await response.json();
            this.updateMarketOverview();
        } catch (error) {
            console.error('Error loading market data:', error);
        }
    }

    updateUI() {
        if (!this.user) return;

        // Обновляем общий баланс
        const totalBalance = document.getElementById('totalBalance');
        const availableBalance = document.getElementById('availableBalance');
        const assetsValue = document.getElementById('assetsValue');
        const userInfo = document.getElementById('userInfo');

        if (totalBalance) {
            totalBalance.textContent = `$${this.user.total_value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        if (availableBalance) {
            availableBalance.textContent = `$${this.user.balances.USD.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        if (assetsValue) {
            const assetsTotal = this.user.total_value - this.user.balances.USD;
            assetsValue.textContent = `$${assetsTotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        if (userInfo) {
            userInfo.innerHTML = `👤 ${this.user.first_name || 'User'}`;
        }

        // Обновляем список активов на странице кошелька
        this.updateWalletAssets();
    }

    updateMarketOverview() {
        const marketList = document.getElementById('marketList');
        if (!marketList) return;

        marketList.innerHTML = '';

        Object.entries(this.prices).forEach(([symbol, data]) => {
            const change = (Math.random() - 0.5) * 10; // Имитация изменения цены
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeIcon = change >= 0 ? '↗' : '↘';

            const marketItem = document.createElement('div');
            marketItem.className = 'market-item';
            marketItem.innerHTML = `
                <div class="crypto-info">
                    <div class="crypto-icon">${symbol.substring(0, 3)}</div>
                    <div class="crypto-details">
                        <h4>${symbol}</h4>
                        <span>${data.name}</span>
                    </div>
                </div>
                <div class="crypto-price">
                    <div class="price">$${data.price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    <div class="change-badge ${changeClass}">
                        ${changeIcon} ${Math.abs(change).toFixed(2)}%
                    </div>
                </div>
            `;

            marketItem.addEventListener('click', () => {
                navigateTo(`/trading?pair=${symbol}`);
            });

            marketList.appendChild(marketItem);
        });
    }

    updateWalletAssets() {
        const assetsList = document.querySelector('.assets-list');
        if (!assetsList || !this.user) return;

        assetsList.innerHTML = '';

        Object.entries(this.user.balances).forEach(([symbol, balance]) => {
            if (symbol === 'USD' || balance === 0) return;

            const price = this.prices[symbol]?.price || 0;
            const value = balance * price;

            const assetItem = document.createElement('div');
            assetItem.className = 'asset-item';
            assetItem.innerHTML = `
                <div class="asset-left">
                    <div class="asset-icon">${symbol.substring(0, 3)}</div>
                    <div class="asset-details">
                        <h4>${symbol}</h4>
                        <span>${this.prices[symbol]?.name || symbol}</span>
                    </div>
                </div>
                <div class="asset-value">
                    <div class="asset-amount">${balance.toFixed(6)}</div>
                    <div class="asset-usd">$${value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                </div>
            `;

            assetsList.appendChild(assetItem);
        });
    }

    setupEventListeners() {
        // Обработчики для торговли
        this.setupTradingHandlers();
    }

    setupTradingHandlers() {
        const buyBtn = document.getElementById('buyBtn');
        const sellBtn = document.getElementById('sellBtn');

        if (buyBtn) {
            buyBtn.addEventListener('click', () => this.executeTrade('buy'));
        }

        if (sellBtn) {
            sellBtn.addEventListener('click', () => this.executeTrade('sell'));
        }
    }

    async executeTrade(type) {
        const amountInput = document.getElementById('amount');
        const priceInput = document.getElementById('price');
        const cryptoSelect = document.getElementById('crypto');

        if (!amountInput || !priceInput || !cryptoSelect) return;

        const crypto = cryptoSelect.value || 'BTC';
        const amount = parseFloat(amountInput.value);
        const price = parseFloat(priceInput.value);

        if (!amount || amount <= 0) {
            this.showError('Please enter a valid amount');
            return;
        }

        try {
            const response = await fetch(`/api/${type}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    telegram_id: this.telegramUserId,
                    crypto: crypto,
                    amount: amount,
                    price: price
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess(result.message);
                await this.loadUserData();
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            console.error('Trade error:', error);
            this.showError('Trade failed');
        }
    }

    showError(message) {
        alert(`Error: ${message}`);
    }

    showSuccess(message) {
        alert(`Success: ${message}`);
    }
}

// Глобальные функции навигации
function navigateTo(path) {
    window.location.href = path;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Инициализация приложения
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new CryptoApp();
});
