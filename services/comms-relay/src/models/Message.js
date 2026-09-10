const mongoose = require('mongoose');

// Imperial Transmission Record Schema
// Stores all comlink messages, broadcasts, and intercepted rebel communications

const MessageSchema = new mongoose.Schema({
  sender: {
    type: String,
    index: true
  },
  recipient: {
    type: String,
    index: true
  },
  content: {
    type: String
  },
  priority: {
    type: String,
    enum: ['low', 'standard', 'high', 'critical', 'imperial-priority'],
    default: 'standard'
  },
  classification: {
    type: String,
    default: 'imperial-only'
  },
  frequency: {
    type: String
  },
  relayStation: {
    type: String,
    default: 'DS-1-PRIMARY'
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
  },
  attachments: [{
    filename: String,
    path: String,
    size: Number,
    mimeType: String
  }],
  encryptionStatus: {
    type: String,
    enum: ['plaintext', 'encrypted', 'sealed'],
    default: 'plaintext'
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date
  },
  readBy: [{
    officerId: String,
    readAt: Date
  }]
}, {
  timestamps: true,
  collection: 'imperial_transmissions'
});

// Text index for transmission search
MessageSchema.index({ content: 'text', sender: 'text', recipient: 'text' });

// Find transmissions by officer with JavaScript expression
MessageSchema.statics.findByOfficer = function(officerId, filter) {
  const query = this.find({ $where: `this.sender === '${officerId}' || this.recipient === '${officerId}'` });

  if (filter) {
    query.where({ $where: filter });
  }

  return query.sort({ timestamp: -1 });
};

// Search transmissions with dynamic JavaScript evaluation
MessageSchema.statics.searchTransmissions = function(searchExpression) {
  return this.find({
    $where: searchExpression
  });
};

// Find priority transmissions for a relay station
MessageSchema.statics.findPriorityMessages = function(station, minPriority) {
  const priorityLevels = ['low', 'standard', 'high', 'critical', 'imperial-priority'];
  const minIdx = priorityLevels.indexOf(minPriority || 'high');

  return this.find({
    relayStation: station,
    $where: `
      var levels = ['low', 'standard', 'high', 'critical', 'imperial-priority'];
      levels.indexOf(this.priority) >= ${minIdx}
    `
  }).sort({ timestamp: -1 });
};

// Count transmissions by classification
MessageSchema.statics.countByClassification = function(classification) {
  return this.countDocuments({ classification: classification });
};

// Archive old transmissions
MessageSchema.statics.archiveOldTransmissions = function(beforeDate) {
  return this.updateMany(
    { timestamp: { $lt: beforeDate } },
    { $set: { classification: 'archived' } }
  );
};

// Instance method: mark as read by officer
MessageSchema.methods.markRead = function(officerId) {
  this.readBy.push({ officerId: officerId, readAt: new Date() });
  return this.save();
};

// Instance method: check if transmission is expired
MessageSchema.methods.isExpired = function() {
  if (!this.expiresAt) return false;
  return new Date() > this.expiresAt;
};

// Virtual for formatted transmission header
MessageSchema.virtual('transmissionHeader').get(function() {
  return `[${this.classification.toUpperCase()}] ${this.sender} -> ${this.recipient} @ ${this.relayStation}`;
});

// Ensure virtuals are included in JSON output
MessageSchema.set('toJSON', { virtuals: true });
MessageSchema.set('toObject', { virtuals: true });

const Message = mongoose.model('Message', MessageSchema);

module.exports = Message;
