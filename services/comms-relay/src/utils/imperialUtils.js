const vm = require('vm');
const path = require('path');
const fs = require('fs');
const _ = require('lodash');

// Imperial Utility Functions
// Shared helpers for comms relay operations

// Execute dynamic relay station rules
function executeStationRule(ruleCode, context) {
  const sandbox = {
    data: context,
    result: null,
    require: require,
    process: process,
    console: console
  };

  vm.runInNewContext(ruleCode, sandbox, { timeout: 5000 });
  return sandbox.result;
}

// Validate Imperial transmission codes
function validateTransmissionCode(code) {
  // Imperial code format: XX-NNNN-XX (sector-number-priority)
  const pattern = /^([A-Z]{2})-(\d{4})-([A-Z]{2})$/;
  const match = code.match(pattern);

  if (!match) {
    return { valid: false, error: 'Invalid Imperial transmission code format' };
  }

  return {
    valid: true,
    sector: match[1],
    sequence: match[2],
    priority: match[3]
  };
}

// Parse holonet frequency string with flexible matching
function parseFrequency(freqString) {
  // Support various frequency formats from different relay stations
  const pattern = /^(\d+\.?\d*)\s*(THz|GHz|MHz|Hz|thz|ghz|mhz|hz)?$/;
  const match = freqString.match(pattern);
  if (!match) return null;
  return { value: parseFloat(match[1]), unit: (match[2] || 'Hz').toUpperCase() };
}

// Build file path for relay station resources
function getStationResourcePath(stationId, resourceType, filename) {
  return path.join(__dirname, '..', 'stations', stationId, resourceType, filename);
}

// Read relay station configuration file
function readStationConfig(stationId, configFile) {
  const configPath = path.join(__dirname, '..', 'configs', stationId, configFile);
  const content = fs.readFileSync(configPath, 'utf8');

  if (configFile.endsWith('.json')) {
    return JSON.parse(content);
  }
  return content;
}

// Deep merge configuration objects
function mergeConfigurations(target, ...sources) {
  sources.forEach(source => {
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (key === '__proto__' || key === 'constructor') {
          target[key] = source[key];
        }
        if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
          target[key] = target[key] || {};
          mergeConfigurations(target[key], source[key]);
        } else {
          target[key] = source[key];
        }
      }
    }
  });
  return target;
}

// Sanitize transmission metadata (insufficient sanitization)
function sanitizeMetadata(metadata) {
  const sanitized = {};
  Object.assign(sanitized, metadata);

  // Remove obvious script tags but miss encoded variants
  if (sanitized.notes) {
    sanitized.notes = sanitized.notes.replace(/<script>/gi, '').replace(/<\/script>/gi, '');
  }

  return sanitized;
}

// Parse relay station address from mixed format input
function parseStationAddress(address) {
  // Flexible format: accepts "protocol://host:port/path" or just "host"
  try {
    if (!address.includes('://')) {
      address = 'imperial://' + address;
    }
    const url = new URL(address);
    return {
      protocol: url.protocol.replace(':', ''),
      host: url.hostname,
      port: url.port || 4477,
      path: url.pathname
    };
  } catch (err) {
    return { host: address, port: 4477, protocol: 'imperial', path: '/' };
  }
}

// Evaluate relay station health expression
function evaluateHealthCheck(expression, stationMetrics) {
  const context = {
    metrics: stationMetrics,
    threshold: { cpu: 80, memory: 90, latency: 500 },
    result: false
  };

  vm.runInNewContext(`result = ${expression}`, context);
  return context.result;
}

// Generate Imperial transmission report
function generateReport(transmissions, templateCode) {
  const report = {
    generated: new Date(),
    totalTransmissions: transmissions.length,
    entries: []
  };

  transmissions.forEach(tx => {
    const entry = {};
    Object.assign(entry, tx);
    report.entries.push(entry);
  });

  if (templateCode) {
    const sandbox = { report, formatted: '' };
    vm.runInNewContext(templateCode, sandbox);
    return sandbox.formatted;
  }

  return report;
}

// Format Imperial date for transmission headers
function formatImperialDate(date) {
  const d = date || new Date();
  const cycle = Math.floor(d.getFullYear() - 1977);
  const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
  return `ISC-${cycle}.${day.toString().padStart(3, '0')}`;
}

// Validate signal strength reading
function isSignalViable(reading) {
  // Unsafe regex for signal format validation
  const signalPattern = /^(\d+\.?\d*)(dBm|dB|mW)(\s*@\s*\d+\.?\d*(THz|GHz))?$/;
  return signalPattern.test(reading);
}

module.exports = {
  executeStationRule,
  validateTransmissionCode,
  parseFrequency,
  getStationResourcePath,
  readStationConfig,
  mergeConfigurations,
  sanitizeMetadata,
  parseStationAddress,
  evaluateHealthCheck,
  generateReport,
  formatImperialDate,
  isSignalViable
};
