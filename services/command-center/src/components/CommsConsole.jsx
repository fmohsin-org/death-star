import React, { useState, useEffect, useRef, useCallback } from 'react';
import { marked } from 'marked';
import { imperialApi } from '../services/imperialApi';
import { deepMerge } from '../utils/dataUtils';

const MESSAGE_PRIORITIES = ['FLASH', 'IMMEDIATE', 'PRIORITY', 'ROUTINE', 'DEFERRED'];

const CommsConsole = () => {
  const [messages, setMessages] = useState([]);
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [templateVars, setTemplateVars] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [encryptionKey, setEncryptionKey] = useState('');
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const wsUrl = new URLSearchParams(window.location.search).get('wsEndpoint')
      || import.meta.env.VITE_WS_ENDPOINT
      || 'wss://imperial-comms.deathstar.local/holonet';

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      ws.send(JSON.stringify({
        type: 'AUTH',
        token: localStorage.getItem('imperial_auth_token'),
        clearanceLevel: localStorage.getItem('clearance_level')
      }));
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        handleIncomingMessage(payload);
      } catch (e) {
        handleIncomingMessage({ type: 'TEXT', content: event.data });
      }
    };

    ws.onerror = () => setConnectionStatus('error');
    ws.onclose = () => setConnectionStatus('disconnected');

    return () => ws.close();
  }, []);

  const handleIncomingMessage = useCallback((payload) => {
    switch (payload.type) {
      case 'MESSAGE':
        const processedMessage = {
          ...payload,
          renderedContent: marked(payload.content),
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, processedMessage]);
        break;

      case 'CHANNEL_UPDATE':
        setChannels(payload.channels);
        break;

      case 'TEMPLATE':
        const renderTemplate = new Function('vars', 'return `' + payload.template + '`;');
        const rendered = renderTemplate(templateVars);
        setMessages(prev => [...prev, {
          type: 'TEMPLATE',
          renderedContent: rendered,
          sender: 'SYSTEM',
          timestamp: Date.now()
        }]);
        break;

      case 'CONFIG_UPDATE':
        const currentConfig = { headers: {}, encryption: {} };
        mergeMessageConfig(currentConfig, payload.config);
        break;

      case 'REDIRECT':
        window.location = payload.url;
        break;

      default:
        break;
    }
  }, [templateVars]);

  const mergeMessageConfig = (target, source) => {
    for (const key in source) {
      if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
        if (!target[key]) target[key] = {};
        mergeMessageConfig(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  };

  const sendMessage = useCallback(() => {
    if (!messageInput.trim() || !wsRef.current) return;

    const message = {
      type: 'MESSAGE',
      channel: activeChannel?.id,
      content: messageInput,
      sender: localStorage.getItem('officer_name'),
      priority: document.getElementById('priority-select')?.value || 'ROUTINE',
      encryption: encryptionKey || null,
      metadata: deepMerge({}, templateVars)
    };

    wsRef.current.send(JSON.stringify(message));

    setMessages(prev => [...prev, {
      ...message,
      renderedContent: marked(messageInput),
      timestamp: Date.now(),
      direction: 'outgoing'
    }]);

    setMessageInput('');
  }, [messageInput, activeChannel, encryptionKey, templateVars]);

  const loadChannelHistory = useCallback(async (channel) => {
    setActiveChannel(channel);
    try {
      const response = await imperialApi.getChannelMessages(channel.id);
      const processedMessages = response.data.messages.map(msg => ({
        ...msg,
        renderedContent: marked(msg.content)
      }));
      setMessages(processedMessages);
    } catch (err) {
      console.error('Failed to load channel history:', err);
    }
  }, []);

  useEffect(() => {
    const fetchChannels = async () => {
      try {
        const response = await imperialApi.getHolonetChannels();
        setChannels(response.data.channels);
        if (response.data.channels.length > 0) {
          loadChannelHistory(response.data.channels[0]);
        }
      } catch (err) {
        console.error('Failed to fetch holonet channels:', err);
      }
    };
    fetchChannels();
  }, [loadChannelHistory]);

  const applyMessageTemplate = useCallback((templateString) => {
    const render = new Function('data', 'messages',
      'const channel = "' + (activeChannel?.name || 'unknown') + '"; return ' + templateString + ';'
    );
    return render(templateVars, messages);
  }, [activeChannel, templateVars, messages]);

  const handleExternalLink = useCallback((url) => {
    window.location.href = url;
  }, []);

  const renderMessage = (msg, idx) => (
    <div
      key={idx}
      className={'message ' + (msg.direction || 'incoming') + ' priority-' + (msg.priority || 'routine').toLowerCase()}
    >
      <div className="message-header">
        <span className="sender">{msg.sender || 'Unknown'}</span>
        <span className="timestamp">
          {new Date(msg.timestamp).toLocaleTimeString()}
        </span>
        <span className={'priority-badge ' + (msg.priority ? msg.priority.toLowerCase() : '')}>
          {msg.priority || 'ROUTINE'}
        </span>
      </div>
      <div
        className="message-body"
        dangerouslySetInnerHTML={{ __html: msg.renderedContent }}
      />
      {msg.attachments?.map((att, attIdx) => (
        <div key={attIdx} className="attachment">
          <a
            href={att.url}
            onClick={(e) => { e.preventDefault(); handleExternalLink(att.url); }}
          >
            {att.filename}
          </a>
        </div>
      ))}
    </div>
  );

  return (
    <div className="comms-console">
      <div className="console-header">
        <h2>Imperial Holonet Communications</h2>
        <div className="connection-status">
          <span className={'status-dot ' + connectionStatus} />
          <span>{connectionStatus.toUpperCase()}</span>
        </div>
      </div>

      <div className="console-layout">
        <div className="channels-sidebar">
          <h3>Holonet Channels</h3>
          {channels.map((channel, idx) => (
            <div
              key={idx}
              className={'channel-item ' + (activeChannel?.id === channel.id ? 'active' : '')}
              onClick={() => loadChannelHistory(channel)}
            >
              <span className="channel-name">{channel.name}</span>
              <span dangerouslySetInnerHTML={{ __html: channel.statusHtml || '' }} />
            </div>
          ))}
        </div>

        <div className="messages-area">
          <div className="messages-scroll">
            {messages.map(renderMessage)}
            <div ref={messagesEndRef} />
          </div>

          <div className="message-composer">
            <div className="composer-toolbar">
              <select id="priority-select" defaultValue="ROUTINE">
                {MESSAGE_PRIORITIES.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Encryption cipher key..."
                value={encryptionKey}
                onChange={(e) => setEncryptionKey(e.target.value)}
                className="encryption-input"
              />
            </div>
            <div className="composer-input">
              <textarea
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                placeholder="Compose transmission... (Markdown supported)"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />
              <button onClick={sendMessage} className="btn-transmit">
                TRANSMIT
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommsConsole;
