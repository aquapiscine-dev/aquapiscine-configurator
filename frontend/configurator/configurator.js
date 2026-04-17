/**
 * Configurator Piscine - Frontend JavaScript
 * Interfață chat conversațională cu Groq AI
 */

const AquaPiscineConfigurator = {
    apiUrl: 'https://aquapiscine-api.vercel.app/api',
    conversationId: null,
    config: {},
    
    init() {
        this.conversationId = this.generateUUID();
        this.setupEventListeners();
        this.sendInitialMessage();
    },
    
    setupEventListeners() {
        const sendBtn = document.getElementById('ap-send-btn');
        const userInput = document.getElementById('ap-user-input');
        const uploadBtn = document.getElementById('ap-upload-btn');
        const imageInput = document.getElementById('ap-image-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (userInput) {
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        if (uploadBtn && imageInput) {
            uploadBtn.addEventListener('click', () => imageInput.click());
            imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        }
    },
    
    async sendInitialMessage() {
        this.addAIMessage('Bună! Sunt asistentul tău AI pentru configurarea piscine. 🏊\n\nSă creăm împreună piscina perfectă!\n\nAi o poză cu grădina/terenul?');
        
        this.addQuickReplies([
            { text: '📸 DA, am poză', action: 'upload' },
            { text: '❌ NU, nu am', action: 'no_image' }
        ]);
    },
    
    async sendMessage() {
        const userInput = document.getElementById('ap-user-input');
        const message = userInput.value.trim();
        
        if (!message) return;
        
        // Afișează mesaj user
        this.addUserMessage(message);
        userInput.value = '';
        
        // Typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiUrl}/configurator`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.conversationId,
                    context: this.config
                })
            });
            
            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.success) {
                this.addAIMessage(data.response);
                
                if (data.products && data.products.length > 0) {
                    this.displayProducts(data.products);
                }
                
                if (data.estimated_price > 0) {
                    this.updatePriceDisplay(data.estimated_price);
                }
                
                this.config = data.config;
            } else {
                this.addErrorMessage(data.error);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage('Eroare conexiune. Te rog încearcă din nou.');
            console.error('Error:', error);
        }
    },
    
    async handleImageUpload(event) {
        const file = event.target.files[0];
        
        if (!file) return;
        
        // Validare tip fișier
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            this.addErrorMessage('Tip fișier invalid. Folosește JPG, PNG sau WebP.');
            return;
        }
        
        // Validare dimensiune (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.addErrorMessage('Imagine prea mare. Maxim 10MB.');
            return;
        }
        
        // Afișează preview
        this.addImagePreview(file);
        
        // Upload
        this.showTypingIndicator('Analizez imaginea...');
        
        try {
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch(`${this.apiUrl}/analyze_image`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.success) {
                this.displayImageAnalysis(data.analysis);
                this.addAIMessage(data.raw_response);
            } else {
                this.addErrorMessage(data.error);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage('Eroare analiză imagine.');
            console.error('Error:', error);
        }
    },
    
    addUserMessage(message) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ap-message ap-user-message';
        messageDiv.innerHTML = `
            <div class="ap-message-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
            <div class="ap-message-time">${this.getCurrentTime()}</div>
        `;
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    addAIMessage(message) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ap-message ap-ai-message';
        messageDiv.innerHTML = `
            <div class="ap-message-avatar">🤖</div>
            <div class="ap-message-content">
                ${this.formatMessage(message)}
            </div>
            <div class="ap-message-time">${this.getCurrentTime()}</div>
        `;
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    addErrorMessage(message) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ap-message ap-error-message';
        messageDiv.innerHTML = `
            <div class="ap-message-content">
                <p>❌ ${this.escapeHtml(message)}</p>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    addImagePreview(file) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ap-message ap-user-message';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            messageDiv.innerHTML = `
                <div class="ap-message-content">
                    <img src="${e.target.result}" alt="Teren" class="ap-uploaded-image">
                    <p>📸 Imagine încărcată</p>
                </div>
                <div class="ap-message-time">${this.getCurrentTime()}</div>
            `;
        };
        reader.readAsDataURL(file);
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    displayImageAnalysis(analysis) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const analysisDiv = document.createElement('div');
        analysisDiv.className = 'ap-analysis-card';
        analysisDiv.innerHTML = `
            <h4>📊 Analiză Teren</h4>
            <div class="ap-analysis-grid">
                <div class="ap-analysis-item">
                    <strong>Suprafață:</strong> ${analysis.terrain.area}
                </div>
                <div class="ap-analysis-item">
                    <strong>Formă:</strong> ${analysis.terrain.shape}
                </div>
                <div class="ap-analysis-item">
                    <strong>Înclinare:</strong> ${analysis.terrain.slope}
                </div>
                <div class="ap-analysis-item">
                    <strong>Dimensiune recomandată:</strong> ${analysis.recommendations.pool_size}
                </div>
                <div class="ap-analysis-item">
                    <strong>Tip recomandat:</strong> ${analysis.recommendations.pool_type}
                </div>
                <div class="ap-analysis-item">
                    <strong>Cost excavare:</strong> ${analysis.estimated_costs.excavation}
                </div>
            </div>
        `;
        chatMessages.appendChild(analysisDiv);
        this.scrollToBottom();
    },
    
    displayProducts(products) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const productsDiv = document.createElement('div');
        productsDiv.className = 'ap-products-grid';
        
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'ap-product-card';
            productCard.innerHTML = `
                ${product.image ? `<img src="${product.image}" alt="${product.name}">` : ''}
                <h5>${product.name}</h5>
                <p class="ap-product-price">${this.formatPrice(product.price)} RON</p>
                ${product.stock_status === 'instock' ? '<span class="ap-stock-badge">✅ Stoc</span>' : ''}
                <a href="${product.permalink}" target="_blank" class="ap-product-link">Vezi Detalii →</a>
            `;
            productsDiv.appendChild(productCard);
        });
        
        chatMessages.appendChild(productsDiv);
        this.scrollToBottom();
    },
    
    addQuickReplies(replies) {
        const chatMessages = document.getElementById('ap-chat-messages');
        const repliesDiv = document.createElement('div');
        repliesDiv.className = 'ap-quick-replies';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'ap-quick-reply-btn';
            button.textContent = reply.text;
            button.onclick = () => this.handleQuickReply(reply);
            repliesDiv.appendChild(button);
        });
        
        chatMessages.appendChild(repliesDiv);
        this.scrollToBottom();
    },
    
    handleQuickReply(reply) {
        if (reply.action === 'upload') {
            document.getElementById('ap-image-input').click();
        } else if (reply.action === 'no_image') {
            this.sendMessage();
            document.getElementById('ap-user-input').value = 'Nu am poză, continuăm fără';
            this.sendMessage();
        }
    },
    
    updatePriceDisplay(price) {
        const priceDisplay = document.getElementById('ap-price-display');
        if (priceDisplay) {
            priceDisplay.innerHTML = `
                <div class="ap-price-box">
                    <span class="ap-price-label">Preț Estimat:</span>
                    <span class="ap-price-value">${this.formatPrice(price)} RON</span>
                </div>
            `;
        }
    },
    
    showTypingIndicator(text = 'AI scrie...') {
        const chatMessages = document.getElementById('ap-chat-messages');
        const indicator = document.createElement('div');
        indicator.id = 'ap-typing-indicator';
        indicator.className = 'ap-typing-indicator';
        indicator.innerHTML = `
            <div class="ap-typing-dots">
                <span></span><span></span><span></span>
            </div>
            <span>${text}</span>
        `;
        chatMessages.appendChild(indicator);
        this.scrollToBottom();
    },
    
    hideTypingIndicator() {
        const indicator = document.getElementById('ap-typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    },
    
    formatMessage(message) {
        // Convert markdown-like formatting
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        message = message.replace(/\n/g, '<br>');
        message = message.replace(/- (.*?)(<br>|$)/g, '<li>$1</li>');
        message = message.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        return `<p>${message}</p>`;
    },
    
    formatPrice(price) {
        return new Intl.NumberFormat('ro-RO').format(price);
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    getCurrentTime() {
        const now = new Date();
        return `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
    },
    
    scrollToBottom() {
        const chatMessages = document.getElementById('ap-chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ap-configurator')) {
        AquaPiscineConfigurator.init();
    }
});
