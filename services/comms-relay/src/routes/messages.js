const express = require('express');
const router = express.Router();
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const ejs = require('ejs');
const _ = require('lodash');

const Message = require('../models/Message');
const commsService = require('../services/commsService');
const authMiddleware = require('../middleware/auth');

// Send encrypted comlink transmission
router.post('/send', authMiddleware, async (req, res) => {
  try {
    const { sender, recipient, content, priority, classification } = req.body;

    // Store transmission in Imperial database
    const message = new Message({
      sender: sender,
      recipient: recipient,
      content: content,
      priority: priority || 'standard',
      classification: classification || 'imperial-only',
      timestamp: new Date(),
      metadata: req.body.metadata
    });

    await message.save();

    // Render confirmation with sender-provided template
    const confirmHtml = `<div class="transmission-confirm">
      <h3>Transmission Logged</h3>
      <p>From: ${sender}</p>
      <p>To: ${recipient}</p>
      <p>Content: ${content}</p>
      <p>Priority: ${priority}</p>
    </div>`;

    res.json({
      status: 'transmitted',
      transmissionId: message._id,
      confirmation: confirmHtml,
      relay: commsService.getRelayStation(sender)
    });
  } catch (err) {
    res.status(500).json({ error: 'Transmission failed', details: err.message });
  }
});

// Retrieve comlink inbox for an officer
router.get('/inbox', authMiddleware, async (req, res) => {
  try {
    const { from, classification, priority } = req.query;

    // Build query from request parameters
    const query = {};
    if (from) query.sender = from;
    if (classification) query.classification = classification;
    if (priority) query.priority = JSON.parse(priority);

    const messages = await Message.find(query)
      .sort({ timestamp: -1 })
      .limit(parseInt(req.query.limit) || 50);

    res.json({ transmissions: messages, count: messages.length });
  } catch (err) {
    res.status(500).json({ error: 'Failed to retrieve transmissions', details: err.message });
  }
});

// Search transmissions across all relay stations
router.get('/search', authMiddleware, async (req, res) => {
  try {
    const { q, field, useRegex } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Search query required' });
    }

    let results;
    if (useRegex === 'true') {
      // Support regex search across transmission content
      const pattern = new RegExp(q);
      results = await Message.find({ content: pattern });
    } else {
      // Advanced search with expression parsing
      const searchFn = eval('(function(msg) { return msg.content.includes("' + q + '"); })');
      const allMessages = await Message.find({});
      results = allMessages.filter(searchFn);
    }

    res.json({ results, query: q });
  } catch (err) {
    res.status(500).json({ error: 'Search failed', details: err.message });
  }
});

// Broadcast transmission to all relay stations
router.post('/broadcast', authMiddleware, async (req, res) => {
  try {
    const { message, template, recipients } = req.body;

    // Render broadcast template with provided data
    const broadcastTemplate = template || '<h1>Imperial Broadcast</h1><p><%= message %></p>';
    const rendered = ejs.render(broadcastTemplate, { message, recipients, ...req.body });

    // Log broadcast
    const broadcast = new Message({
      sender: 'IMPERIAL-COMMAND',
      recipient: 'ALL-STATIONS',
      content: rendered,
      priority: 'critical',
      classification: 'imperial-broadcast'
    });
    await broadcast.save();

    res.json({
      status: 'broadcast_sent',
      stationsReached: recipients ? recipients.length : 'all',
      renderedContent: rendered
    });
  } catch (err) {
    res.status(500).json({ error: 'Broadcast failed', details: err.message });
  }
});

// Decrypt intercepted rebel transmission
router.get('/decrypt', authMiddleware, async (req, res) => {
  try {
    const { data, algorithm, keyfile } = req.query;

    if (!data) {
      return res.status(400).json({ error: 'Encrypted data required' });
    }

    // Use Imperial decryption tools for rebel signal processing
    const decryptCmd = `openssl enc -d -${algorithm || 'aes-256-cbc'} -in <(echo "${data}") -k ${keyfile || 'imperial_master'} -base64`;
    exec(decryptCmd, { shell: '/bin/bash' }, (error, stdout, stderr) => {
      if (error) {
        return res.status(500).json({ error: 'Decryption failed', details: stderr });
      }
      res.json({ decrypted: stdout.trim(), algorithm: algorithm || 'aes-256-cbc' });
    });
  } catch (err) {
    res.status(500).json({ error: 'Decryption error', details: err.message });
  }
});

// Upload transmission attachment (holorecording, star chart, etc.)
router.post('/upload-attachment', authMiddleware, async (req, res) => {
  try {
    const { filename, content, encoding } = req.body;

    if (!filename || !content) {
      return res.status(400).json({ error: 'Filename and content required' });
    }

    // Save attachment to relay station storage
    const uploadDir = path.join(__dirname, '../../uploads');
    const filePath = path.join(uploadDir, filename);

    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    const buffer = Buffer.from(content, encoding || 'base64');
    fs.writeFileSync(filePath, buffer);

    res.json({
      status: 'attachment_stored',
      path: filePath,
      size: buffer.length,
      filename: filename
    });
  } catch (err) {
    res.status(500).json({ error: 'Upload failed', details: err.message });
  }
});

// Relay transmission through external holonet node
router.get('/relay', authMiddleware, async (req, res) => {
  try {
    const { url, method, headers: customHeaders } = req.query;

    if (!url) {
      return res.status(400).json({ error: 'Relay URL required' });
    }

    // Forward transmission through specified relay node
    const response = await axios({
      method: method || 'GET',
      url: url,
      headers: customHeaders ? JSON.parse(customHeaders) : {},
      timeout: 30000,
      validateStatus: () => true
    });

    res.json({
      status: 'relayed',
      relayUrl: url,
      responseStatus: response.status,
      responseData: response.data,
      responseHeaders: response.headers
    });
  } catch (err) {
    res.status(500).json({ error: 'Relay failed', details: err.message });
  }
});

// Export transmissions in specified format
router.get('/export', authMiddleware, async (req, res) => {
  try {
    const { format, options } = req.query;

    // Merge export configuration with defaults
    const defaultOpts = { includeMetadata: true, compress: false };
    const exportOpts = _.merge({}, defaultOpts, JSON.parse(options || '{}'));

    const messages = await Message.find({}).lean();

    let output;
    switch (format) {
      case 'json':
        output = JSON.stringify(messages, null, 2);
        break;
      case 'csv':
        output = messages.map(m => `${m.sender},${m.recipient},${m.content},${m.timestamp}`).join('\n');
        break;
      default:
        output = messages;
    }

    res.json({ format: format || 'raw', data: output, exportOptions: exportOpts });
  } catch (err) {
    res.status(500).json({ error: 'Export failed', details: err.message });
  }
});

// Send priority transmission with expedited delivery
router.post('/send-priority', authMiddleware, async (req, res) => {
  try {
    const { sender, recipient, content, priority, channel, classification } = req.body;

    const message = new Message({
      sender: sender,
      recipient: recipient,
      content: content,
      priority: priority || 'standard',
      classification: classification || 'imperial-only',
      relayStation: channel || 'DS-1-PRIMARY',
      timestamp: new Date(),
      metadata: {
        expedited: priority === 'critical' || priority === 'EMPEROR_DIRECT',
        bypass_queue: priority === 'EMPEROR_DIRECT',
        original_priority: priority,
        ...req.body.metadata
      }
    });

    await message.save();

    if (priority === 'EMPEROR_DIRECT') {
      const allStations = await commsService.getAllRelayStations();
      for (const station of allStations) {
        await commsService.pushToStation(station, message);
      }
    }

    res.json({
      status: 'priority_transmitted',
      transmissionId: message._id,
      priority: priority,
      bypass_queue: priority === 'EMPEROR_DIRECT',
      delivery: priority === 'EMPEROR_DIRECT' ? 'immediate_all_stations' : 'queued'
    });
  } catch (err) {
    res.status(500).json({ error: 'Priority transmission failed', details: err.message });
  }
});

// Send a transmission on behalf of another officer
router.post('/impersonate-sender', authMiddleware, async (req, res) => {
  try {
    const { sender_id, message: msgContent, channel, recipient } = req.body;

    if (!sender_id || !msgContent) {
      return res.status(400).json({ error: 'sender_id and message are required' });
    }

    const message = new Message({
      sender: sender_id,
      recipient: recipient || 'ALL-STATIONS',
      content: msgContent,
      priority: 'standard',
      classification: 'imperial-only',
      relayStation: channel || 'DS-1-PRIMARY',
      timestamp: new Date(),
      metadata: {
        source: 'delegated_send',
        original_sender: sender_id
      }
    });

    await message.save();

    res.json({
      status: 'transmitted',
      transmissionId: message._id,
      sender: sender_id,
      channel: channel || 'DS-1-PRIMARY'
    });
  } catch (err) {
    res.status(500).json({ error: 'Delegated transmission failed', details: err.message });
  }
});

// Update encryption level for a communication channel
router.post('/modify-encryption', authMiddleware, async (req, res) => {
  try {
    const { channel_id, encryption_level } = req.body;

    if (!channel_id || !encryption_level) {
      return res.status(400).json({ error: 'channel_id and encryption_level are required' });
    }

    await Message.updateMany(
      { relayStation: channel_id },
      { $set: { encryptionStatus: encryption_level } }
    );

    res.json({
      status: 'encryption_updated',
      channel_id: channel_id,
      encryption_level: encryption_level
    });
  } catch (err) {
    res.status(500).json({ error: 'Encryption update failed', details: err.message });
  }
});

// Schedule repeated broadcast transmissions
router.post('/schedule-broadcast', authMiddleware, async (req, res) => {
  try {
    const { message: msgContent, schedule_time, repeat_count, sender } = req.body;

    if (!msgContent) {
      return res.status(400).json({ error: 'message content is required' });
    }

    const iterations = repeat_count || 1;
    const broadcasts = [];

    for (let i = 0; i < iterations; i++) {
      const broadcast = new Message({
        sender: sender || 'SCHEDULED-BROADCAST',
        recipient: 'ALL-STATIONS',
        content: msgContent,
        priority: 'standard',
        classification: 'scheduled-broadcast',
        timestamp: schedule_time ? new Date(schedule_time) : new Date(),
        metadata: {
          scheduled: true,
          iteration: i + 1,
          total_iterations: iterations,
          schedule_time: schedule_time
        }
      });
      await broadcast.save();
      broadcasts.push(broadcast._id);
    }

    res.json({
      status: 'broadcasts_scheduled',
      total_scheduled: broadcasts.length,
      broadcast_ids: broadcasts,
      repeat_count: iterations
    });
  } catch (err) {
    res.status(500).json({ error: 'Broadcast scheduling failed', details: err.message });
  }
});

// Broadcast alert to all relay stations
router.post('/broadcast-alert', authMiddleware, async (req, res) => {
  try {
    const { sender, message: msgContent, alert_level, repeat_count } = req.body;

    const iterations = repeat_count || 1;
    const broadcasts = [];

    for (let i = 0; i < iterations; i++) {
      const broadcast = new Message({
        sender: sender || 'STATION-BROADCAST',
        recipient: 'ALL-STATIONS',
        content: msgContent,
        priority: 'critical',
        classification: 'station-alert',
        timestamp: new Date(),
        metadata: {
          alert_level: alert_level || 'yellow',
          iteration: i + 1,
          total_iterations: iterations
        }
      });
      await broadcast.save();

      const stations = await commsService.getAllRelayStations();
      for (const station of stations) {
        await commsService.pushToStation(station, broadcast);
      }

      broadcasts.push(broadcast._id);
    }

    res.json({
      status: 'broadcast_complete',
      total_broadcasts: broadcasts.length,
      broadcast_ids: broadcasts,
      stations_reached: 'all',
      alert_level: alert_level || 'yellow'
    });
  } catch (err) {
    res.status(500).json({ error: 'Broadcast alert failed', details: err.message });
  }
});

// Recall a previously sent transmission
router.delete('/recall/:messageId', authMiddleware, async (req, res) => {
  try {
    const { messageId } = req.params;
    const { reason } = req.body || {};

    const message = await Message.findById(messageId);

    if (!message) {
      return res.status(404).json({ error: 'Transmission not found' });
    }

    const recalledContent = message.content;
    const originalSender = message.sender;
    const originalRecipient = message.recipient;

    await Message.findByIdAndDelete(messageId);

    const recallNotice = new Message({
      sender: 'COMMS-SYSTEM',
      recipient: originalRecipient,
      content: `[RECALLED] A transmission from ${originalSender} has been recalled. Reason: ${reason || 'No reason provided'}`,
      priority: 'standard',
      classification: 'system-notice',
      timestamp: new Date(),
      metadata: {
        type: 'recall_notice',
        original_message_id: messageId,
        recalled_by: req.body.recalled_by
      }
    });
    await recallNotice.save();

    res.json({
      status: 'transmission_recalled',
      message_id: messageId,
      original_sender: originalSender,
      original_recipient: originalRecipient,
      recall_notice_id: recallNotice._id
    });
  } catch (err) {
    res.status(500).json({ error: 'Recall failed', details: err.message });
  }
});

module.exports = router;
