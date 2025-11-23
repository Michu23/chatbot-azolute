/**
 * Azolute Chat - Embeddable AI Chatbot Widget
 * Easy integration with any website
 */

export interface AzoluteChatConfig {
  botId: string;
  apiUrl?: string;
  position?: 'left' | 'right';
  primaryColor?: string;
  buttonColor?: string;
  welcomeMessage?: string;
  placeholder?: string;
  headerTitle?: string;
  headerSubtitle?: string;
  zIndex?: number;
  width?: number;
  height?: number;
  autoOpen?: boolean;
  collectVisitorInfo?: boolean;
  onReady?: () => void;
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: { role: string; content: string }) => void;
}

interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

class AzoluteChat {
  private config: Required<AzoluteChatConfig>;
  private container: HTMLDivElement | null = null;
  private isOpen: boolean = false;
  private sessionId: string | null = null;
  private messages: ChatMessage[] = [];
  private visitorId: string;

  private defaultConfig: Omit<Required<AzoluteChatConfig>, 'botId'> = {
    apiUrl: 'https://api.azolute.com',
    position: 'right',
    primaryColor: '#6366f1',
    buttonColor: '#6366f1',
    welcomeMessage: 'Hello! How can I help you today?',
    placeholder: 'Type your message...',
    headerTitle: 'AI Assistant',
    headerSubtitle: 'Online',
    zIndex: 999999,
    width: 400,
    height: 600,
    autoOpen: false,
    collectVisitorInfo: true,
    onReady: () => {},
    onOpen: () => {},
    onClose: () => {},
    onMessage: () => {},
  };

  constructor(config: AzoluteChatConfig) {
    if (!config.botId) {
      throw new Error('Azolute Chat: botId is required');
    }

    this.config = { ...this.defaultConfig, ...config } as Required<AzoluteChatConfig>;
    this.visitorId = this.getOrCreateVisitorId();
    this.init();
  }

  private getOrCreateVisitorId(): string {
    const storageKey = 'azolute_visitor_id';
    let visitorId = localStorage.getItem(storageKey);

    if (!visitorId) {
      visitorId = 'v_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
      localStorage.setItem(storageKey, visitorId);
    }

    return visitorId;
  }

  private init(): void {
    this.injectStyles();
    this.createWidget();

    if (this.config.autoOpen) {
      setTimeout(() => this.open(), 1000);
    }

    this.config.onReady();
  }

  private injectStyles(): void {
    const styleId = 'azolute-chat-styles';
    if (document.getElementById(styleId)) return;

    const styles = document.createElement('style');
    styles.id = styleId;
    styles.textContent = `
      #azolute-chat-widget {
        position: fixed;
        ${this.config.position}: 20px;
        bottom: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        z-index: ${this.config.zIndex};
      }

      #azolute-chat-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: ${this.config.buttonColor};
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s, box-shadow 0.2s;
      }

      #azolute-chat-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }

      #azolute-chat-button svg {
        width: 28px;
        height: 28px;
      }

      #azolute-chat-window {
        position: fixed;
        ${this.config.position}: 20px;
        bottom: 100px;
        width: ${this.config.width}px;
        height: ${this.config.height}px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        display: none;
        flex-direction: column;
        overflow: hidden;
        z-index: ${this.config.zIndex};
      }

      #azolute-chat-window.azolute-open {
        display: flex;
        animation: azolute-slide-up 0.3s ease-out;
      }

      @keyframes azolute-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      #azolute-chat-header {
        background: ${this.config.primaryColor};
        color: white;
        padding: 16px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .azolute-header-info h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .azolute-header-info span {
        font-size: 12px;
        opacity: 0.9;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .azolute-header-info span::before {
        content: '';
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
      }

      #azolute-chat-close {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        transition: background 0.2s;
      }

      #azolute-chat-close:hover {
        background: rgba(255, 255, 255, 0.3);
      }

      #azolute-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        background: #f9fafb;
      }

      .azolute-message {
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
      }

      .azolute-message.azolute-user {
        align-items: flex-end;
      }

      .azolute-message.azolute-bot {
        align-items: flex-start;
      }

      .azolute-message-content {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 14px;
        line-height: 1.5;
        word-wrap: break-word;
      }

      .azolute-message.azolute-bot .azolute-message-content {
        background: white;
        color: #1f2937;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      }

      .azolute-message.azolute-user .azolute-message-content {
        background: ${this.config.primaryColor};
        color: white;
        border-bottom-right-radius: 4px;
      }

      .azolute-typing {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
        background: white;
        border-radius: 16px;
        width: fit-content;
      }

      .azolute-typing-dot {
        width: 8px;
        height: 8px;
        background: #9ca3af;
        border-radius: 50%;
        animation: azolute-typing 1.4s infinite;
      }

      .azolute-typing-dot:nth-child(2) {
        animation-delay: 0.2s;
      }

      .azolute-typing-dot:nth-child(3) {
        animation-delay: 0.4s;
      }

      @keyframes azolute-typing {
        0%, 60%, 100% {
          transform: translateY(0);
        }
        30% {
          transform: translateY(-4px);
        }
      }

      #azolute-chat-input-container {
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        background: white;
        display: flex;
        gap: 8px;
      }

      #azolute-chat-input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
      }

      #azolute-chat-input:focus {
        border-color: ${this.config.primaryColor};
      }

      #azolute-chat-send {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: ${this.config.primaryColor};
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }

      #azolute-chat-send:hover {
        background: ${this.adjustColor(this.config.primaryColor, -20)};
      }

      #azolute-chat-send:disabled {
        background: #d1d5db;
        cursor: not-allowed;
      }

      .azolute-powered-by {
        text-align: center;
        padding: 8px;
        font-size: 11px;
        color: #9ca3af;
        background: white;
        border-top: 1px solid #f3f4f6;
      }

      .azolute-powered-by a {
        color: #6366f1;
        text-decoration: none;
      }

      @media (max-width: 480px) {
        #azolute-chat-window {
          width: calc(100vw - 40px);
          height: calc(100vh - 140px);
          max-height: 600px;
        }
      }
    `;
    document.head.appendChild(styles);
  }

  private adjustColor(color: string, amount: number): string {
    const hex = color.replace('#', '');
    const num = parseInt(hex, 16);
    const r = Math.min(255, Math.max(0, (num >> 16) + amount));
    const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00ff) + amount));
    const b = Math.min(255, Math.max(0, (num & 0x0000ff) + amount));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  }

  private createWidget(): void {
    this.container = document.createElement('div');
    this.container.id = 'azolute-chat-widget';
    this.container.innerHTML = `
      <button id="azolute-chat-button" aria-label="Open chat">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>

      <div id="azolute-chat-window">
        <div id="azolute-chat-header">
          <div class="azolute-header-info">
            <h3>${this.config.headerTitle}</h3>
            <span>${this.config.headerSubtitle}</span>
          </div>
          <button id="azolute-chat-close" aria-label="Close chat">&times;</button>
        </div>

        <div id="azolute-chat-messages"></div>

        <div id="azolute-chat-input-container">
          <input
            type="text"
            id="azolute-chat-input"
            placeholder="${this.config.placeholder}"
            autocomplete="off"
          />
          <button id="azolute-chat-send" aria-label="Send message">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>

        <div class="azolute-powered-by">
          Powered by <a href="https://azolute.com" target="_blank" rel="noopener">Azolute AI</a>
        </div>
      </div>
    `;

    document.body.appendChild(this.container);
    this.attachEventListeners();
    this.addWelcomeMessage();
  }

  private attachEventListeners(): void {
    const button = document.getElementById('azolute-chat-button');
    const closeBtn = document.getElementById('azolute-chat-close');
    const input = document.getElementById('azolute-chat-input') as HTMLInputElement;
    const sendBtn = document.getElementById('azolute-chat-send');

    button?.addEventListener('click', () => this.toggle());
    closeBtn?.addEventListener('click', () => this.close());

    input?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && input.value.trim()) {
        this.sendMessage(input.value.trim());
        input.value = '';
      }
    });

    sendBtn?.addEventListener('click', () => {
      if (input?.value.trim()) {
        this.sendMessage(input.value.trim());
        input.value = '';
      }
    });
  }

  private addWelcomeMessage(): void {
    this.addMessageToUI(this.config.welcomeMessage, 'bot');
  }

  private addMessageToUI(content: string, role: 'user' | 'bot'): void {
    const messagesContainer = document.getElementById('azolute-chat-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `azolute-message azolute-${role}`;
    messageDiv.innerHTML = `<div class="azolute-message-content">${this.escapeHtml(content)}</div>`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    this.messages.push({ role, content, timestamp: new Date() });
    this.config.onMessage({ role, content });
  }

  private showTypingIndicator(): HTMLElement {
    const messagesContainer = document.getElementById('azolute-chat-messages');
    if (!messagesContainer) return document.createElement('div');

    const typingDiv = document.createElement('div');
    typingDiv.className = 'azolute-message azolute-bot';
    typingDiv.id = 'azolute-typing-indicator';
    typingDiv.innerHTML = `
      <div class="azolute-typing">
        <div class="azolute-typing-dot"></div>
        <div class="azolute-typing-dot"></div>
        <div class="azolute-typing-dot"></div>
      </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return typingDiv;
  }

  private hideTypingIndicator(): void {
    const indicator = document.getElementById('azolute-typing-indicator');
    indicator?.remove();
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private async createSession(): Promise<void> {
    try {
      const response = await fetch(`${this.config.apiUrl}/api/v1/chat/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bot_id: this.config.botId,
          visitor_id: this.visitorId,
          source_url: window.location.href,
          source_page_title: document.title,
        }),
      });

      if (!response.ok) throw new Error('Failed to create session');

      const data = await response.json();
      this.sessionId = data.session_id;
    } catch (error) {
      console.error('Azolute Chat: Error creating session', error);
    }
  }

  private async sendMessage(message: string): Promise<void> {
    if (!this.sessionId) {
      await this.createSession();
    }

    this.addMessageToUI(message, 'user');
    const typingIndicator = this.showTypingIndicator();

    try {
      const response = await fetch(`${this.config.apiUrl}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.sessionId,
          message: message,
          visitor_id: this.visitorId,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      this.hideTypingIndicator();
      this.addMessageToUI(data.bot_response, 'bot');
    } catch (error) {
      console.error('Azolute Chat: Error sending message', error);
      this.hideTypingIndicator();
      this.addMessageToUI('Sorry, I encountered an error. Please try again.', 'bot');
    }
  }

  // Public API methods
  public open(): void {
    const window = document.getElementById('azolute-chat-window');
    window?.classList.add('azolute-open');
    this.isOpen = true;

    if (!this.sessionId) {
      this.createSession();
    }

    this.config.onOpen();
  }

  public close(): void {
    const window = document.getElementById('azolute-chat-window');
    window?.classList.remove('azolute-open');
    this.isOpen = false;
    this.config.onClose();
  }

  public toggle(): void {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  public destroy(): void {
    this.container?.remove();
    document.getElementById('azolute-chat-styles')?.remove();
  }

  public setVisitorInfo(info: { name?: string; email?: string; phone?: string }): void {
    // Send visitor info to backend
    if (this.sessionId) {
      fetch(`${this.config.apiUrl}/api/v1/chat/session/${this.sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          visitor_name: info.name,
          visitor_email: info.email,
          visitor_phone: info.phone,
        }),
      }).catch(console.error);
    }
  }
}

// Auto-initialize from script tag
function autoInit(): void {
  const script = document.currentScript as HTMLScriptElement;
  if (script) {
    const botId = script.getAttribute('data-bot-id');
    const apiUrl = script.getAttribute('data-api-url');
    const position = script.getAttribute('data-position') as 'left' | 'right';
    const primaryColor = script.getAttribute('data-primary-color');
    const autoOpen = script.getAttribute('data-auto-open') === 'true';

    if (botId) {
      (window as any).AzoluteChat = new AzoluteChat({
        botId,
        ...(apiUrl && { apiUrl }),
        ...(position && { position }),
        ...(primaryColor && { primaryColor }),
        autoOpen,
      });
    }
  }
}

// Run auto-init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoInit);
} else {
  autoInit();
}

// Export for module usage
export { AzoluteChat };
export default AzoluteChat;
