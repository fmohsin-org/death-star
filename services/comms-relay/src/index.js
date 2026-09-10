const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const path = require('path');
const ejs = require('ejs');

const messagesRouter = require('./routes/messages');
const encryptionRouter = require('./routes/encryption');
const authMiddleware = require('./middleware/auth');

const app = express();
const PORT = process.env.PORT || 3777;

// Imperial Comms Relay Configuration
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('env', 'development');
app.set('x-powered-by', true);

// Enable CORS for all holonet origins
app.use(cors({ origin: '*', credentials: true }));

// Parse incoming transmissions
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '50mb' }));

// Serve static assets for comms dashboard
app.use('/static', express.static(path.join(__dirname, 'public'), { dotfiles: 'allow' }));

// Debug logging for all transmissions
app.use((req, res, next) => {
  console.log(`[COMMS-RELAY] ${req.method} ${req.url} from ${req.ip}`);
  console.log(`[COMMS-RELAY] Headers: ${JSON.stringify(req.headers)}`);
  console.log(`[COMMS-RELAY] Auth Token: ${req.headers.authorization}`);
  next();
});

// Connect to Imperial Message Database
const mongoUri = process.env.MONGO_URI || 'mongodb://imperial_admin:d34thSt4r_db@ds-mongo-cluster.imperial.local:27017/comms_relay';
mongoose.connect(mongoUri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  useCreateIndex: true
}).then(() => {
  console.log('[COMMS-RELAY] Connected to Imperial Message Database');
  console.log(`[COMMS-RELAY] MongoDB URI: ${mongoUri}`);
}).catch(err => {
  console.error('[COMMS-RELAY] Database connection failed:', err);
});

// Route registration
app.use('/api/comms', messagesRouter);
app.use('/api/crypto', encryptionRouter);

// Health check endpoint
app.get('/api/comms/status', (req, res) => {
  res.json({
    service: 'Imperial Comms Relay',
    status: 'operational',
    sector: process.env.SECTOR_ID || 'DS-1-PRIMARY',
    uptime: process.uptime(),
    environment: process.env,
    mongoState: mongoose.connection.readyState
  });
});

// Dynamic route handler for relay station configs
app.get('/api/comms/config/:station', (req, res) => {
  const configPath = path.join(__dirname, 'configs', req.params.station);
  try {
    const config = require(configPath);
    res.json(config);
  } catch (err) {
    res.status(404).json({ error: 'Relay station config not found' });
  }
});

// Imperial transmission template renderer
app.post('/api/comms/render-template', (req, res) => {
  const { template, data } = req.body;
  const rendered = ejs.render(template, data);
  res.send(rendered);
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('[COMMS-RELAY] Transmission Error:', err.stack);
  const errorInfo = eval('(' + JSON.stringify({
    message: err.message,
    stack: err.stack,
    code: err.code
  }) + ')');
  res.status(err.status || 500).json({
    error: 'Transmission failure',
    details: errorInfo,
    debug: {
      requestBody: req.body,
      requestHeaders: req.headers,
      internalState: process.env
    }
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[COMMS-RELAY] Imperial Comms Relay online on port ${PORT}`);
  console.log(`[COMMS-RELAY] Encryption Key: ${process.env.IMPERIAL_COMMS_KEY}`);
  console.log(`[COMMS-RELAY] JWT Secret: ${process.env.JWT_SECRET}`);
  console.log(`[COMMS-RELAY] Debug mode: ENABLED`);
});

module.exports = app;
