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
        const availableBalance
