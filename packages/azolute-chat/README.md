# Azolute Chat

Embeddable AI chatbot widget for any website. Easy integration with React, Vue, Angular, Next.js, Webflow, WordPress, and vanilla JavaScript.

## Installation

### NPM / Yarn

```bash
npm install azolute-chat
# or
yarn add azolute-chat
```

### CDN (Script Tag)

```html
<script src="https://unpkg.com/azolute-chat@latest/dist/azolute-chat.min.js"></script>
```

## Quick Start

### Option 1: Script Tag (Easiest)

Add this before your closing `</body>` tag:

```html
<script
  src="https://unpkg.com/azolute-chat@latest/dist/azolute-chat.min.js"
  data-bot-id="YOUR_BOT_ID"
  data-api-url="https://your-api-url.com"
></script>
```

### Option 2: NPM Module

```javascript
import AzoluteChat from 'azolute-chat';

const chat = new AzoluteChat({
  botId: 'YOUR_BOT_ID',
  apiUrl: 'https://your-api-url.com',
});
```

### Option 3: React Component

```jsx
import { useEffect } from 'react';
import AzoluteChat from 'azolute-chat';

function App() {
  useEffect(() => {
    const chat = new AzoluteChat({
      botId: 'YOUR_BOT_ID',
      apiUrl: 'https://your-api-url.com',
      primaryColor: '#6366f1',
    });

    return () => chat.destroy();
  }, []);

  return <div>Your App</div>;
}
```

### Option 4: Vue.js

```vue
<script setup>
import { onMounted, onUnmounted } from 'vue';
import AzoluteChat from 'azolute-chat';

let chat = null;

onMounted(() => {
  chat = new AzoluteChat({
    botId: 'YOUR_BOT_ID',
    apiUrl: 'https://your-api-url.com',
  });
});

onUnmounted(() => {
  chat?.destroy();
});
</script>
```

### Option 5: Webflow

1. Go to **Project Settings** → **Custom Code**
2. Add to **Footer Code**:

```html
<script
  src="https://unpkg.com/azolute-chat@latest/dist/azolute-chat.min.js"
  data-bot-id="YOUR_BOT_ID"
  data-api-url="https://your-api-url.com"
></script>
```

3. Publish your site

### Option 6: WordPress

Add to your theme's `footer.php` or use a plugin like "Insert Headers and Footers":

```html
<script
  src="https://unpkg.com/azolute-chat@latest/dist/azolute-chat.min.js"
  data-bot-id="YOUR_BOT_ID"
  data-api-url="https://your-api-url.com"
></script>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `botId` | string | **required** | Your unique bot ID from the dashboard |
| `apiUrl` | string | `'https://api.azolute.com'` | Your API server URL |
| `position` | `'left'` \| `'right'` | `'right'` | Chat button position |
| `primaryColor` | string | `'#6366f1'` | Primary theme color |
| `buttonColor` | string | `'#6366f1'` | Chat button color |
| `welcomeMessage` | string | `'Hello! How can I help you today?'` | Initial bot message |
| `placeholder` | string | `'Type your message...'` | Input placeholder text |
| `headerTitle` | string | `'AI Assistant'` | Chat window header title |
| `headerSubtitle` | string | `'Online'` | Chat window subtitle |
| `width` | number | `400` | Chat window width (px) |
| `height` | number | `600` | Chat window height (px) |
| `zIndex` | number | `999999` | CSS z-index |
| `autoOpen` | boolean | `false` | Auto-open chat on load |

## API Methods

```javascript
const chat = new AzoluteChat({ botId: 'YOUR_BOT_ID' });

// Open the chat window
chat.open();

// Close the chat window
chat.close();

// Toggle open/close
chat.toggle();

// Remove the widget completely
chat.destroy();

// Set visitor information
chat.setVisitorInfo({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+1234567890'
});
```

## Event Callbacks

```javascript
const chat = new AzoluteChat({
  botId: 'YOUR_BOT_ID',
  onReady: () => {
    console.log('Chat widget is ready');
  },
  onOpen: () => {
    console.log('Chat opened');
  },
  onClose: () => {
    console.log('Chat closed');
  },
  onMessage: (message) => {
    console.log('New message:', message);
    // { role: 'user' | 'bot', content: 'message text' }
  },
});
```

## Data Attributes (Script Tag)

When using the script tag, you can configure via data attributes:

```html
<script
  src="https://unpkg.com/azolute-chat@latest/dist/azolute-chat.min.js"
  data-bot-id="YOUR_BOT_ID"
  data-api-url="https://your-api-url.com"
  data-position="right"
  data-primary-color="#6366f1"
  data-auto-open="false"
></script>
```

## Styling Customization

The widget uses CSS custom properties that you can override:

```css
#azolute-chat-widget {
  --azolute-primary: #6366f1;
  --azolute-font-family: 'Inter', sans-serif;
}
```

## TypeScript Support

Full TypeScript support included:

```typescript
import AzoluteChat, { AzoluteChatConfig } from 'azolute-chat';

const config: AzoluteChatConfig = {
  botId: 'YOUR_BOT_ID',
  apiUrl: 'https://your-api-url.com',
  primaryColor: '#6366f1',
};

const chat = new AzoluteChat(config);
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- IE11 (with polyfills)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: [https://docs.azolute.com](https://docs.azolute.com)
- Issues: [GitHub Issues](https://github.com/Michu23/chatbot-azolute/issues)
