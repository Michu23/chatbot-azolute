/**
 * Azolute Chat - Embeddable AI Chatbot Widget
 */

export interface AzoluteChatConfig {
  /** Your unique bot ID from the dashboard (required) */
  botId: string;
  /** Your API server URL */
  apiUrl?: string;
  /** Chat button position */
  position?: 'left' | 'right';
  /** Primary theme color */
  primaryColor?: string;
  /** Chat button color */
  buttonColor?: string;
  /** Initial bot message */
  welcomeMessage?: string;
  /** Input placeholder text */
  placeholder?: string;
  /** Chat window header title */
  headerTitle?: string;
  /** Chat window subtitle */
  headerSubtitle?: string;
  /** CSS z-index */
  zIndex?: number;
  /** Chat window width (px) */
  width?: number;
  /** Chat window height (px) */
  height?: number;
  /** Auto-open chat on load */
  autoOpen?: boolean;
  /** Collect visitor info automatically */
  collectVisitorInfo?: boolean;
  /** Called when widget is ready */
  onReady?: () => void;
  /** Called when chat opens */
  onOpen?: () => void;
  /** Called when chat closes */
  onClose?: () => void;
  /** Called on new message */
  onMessage?: (message: { role: string; content: string }) => void;
}

export declare class AzoluteChat {
  constructor(config: AzoluteChatConfig);

  /** Open the chat window */
  open(): void;

  /** Close the chat window */
  close(): void;

  /** Toggle chat window open/close */
  toggle(): void;

  /** Remove the widget from DOM */
  destroy(): void;

  /** Set visitor information */
  setVisitorInfo(info: { name?: string; email?: string; phone?: string }): void;
}

export default AzoluteChat;
