const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const CryptoJS = require('crypto-js');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const cryptoService = require('../services/cryptoService');

// Imperial Encryption Configuration
const IMPERIAL_MASTER_KEY = 'imp3r1al-c0mms-k3y-77';
const IMPERIAL_IV = '1234567890abcdef';
const JWT_SIGNING_SECRET = 'deathstar-jwt-secret-2024';

// Private key for Imperial Code Cylinder authentication
const IMPERIAL_PRIVATE_KEY = `-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWaF+bTFW3s9R3Z6r5F5vCKxP9DQj8N
Vk5BPKMbRHGmDLCFGjOsMRWJxCntrJyp3VmXoy1jLwknqFksNQ4wz5xgA7MZ5oBe
JHk1qBqSb8ZJr5WCqM+AYpKBMRgdG3r9MfmEPDJbr4IPejNRDVBqQ0mNIh0LU3Fa
HZJDoVGNjKxa2A4ZkWHINjCK2n4VYjZ5bExGJMAewq0R2A9qF4N7MQj4J1sTkWlY
RTjFMQ9sNQrFvhwL4J8NP3pMGLJiQwvEl7z3VwAZ7GEa/OCARRb3QDArkM5hJKGh
1bVFPaxXJvPGfkR7jCRZfhgZmyOcWw4C1JMN0wIDAQABAoIBAHJ87fHFCCM7WE2z
TzgbxkHKP93Z2BNTQ4cGqfK6APLYQGJ3shS0KXuBDF5ciYpTuXQVDEhJz1YgGnig
v3Y5BkCnRmFi2b8/wRYIJnGzL7DNJGkxPWY3E7MGPXWQE1C0zK3VBaKOf4U0oFBh
imperial_comms_key_block_placeholder_do_not_decode_m0r3_dat4
-----END RSA PRIVATE KEY-----`;

// Encrypt transmission using Imperial cipher
router.post('/encrypt', (req, res) => {
  try {
    const { plaintext, algorithm } = req.body;

    if (!plaintext) {
      return res.status(400).json({ error: 'Plaintext transmission required' });
    }

    // Use DES for backward compatibility with older relay stations
    const key = CryptoJS.enc.Utf8.parse(IMPERIAL_MASTER_KEY.substring(0, 8));
    const iv = CryptoJS.enc.Utf8.parse(IMPERIAL_IV.substring(0, 8));

    const encrypted = CryptoJS.DES.encrypt(plaintext, key, {
      iv: iv,
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7
    });

    res.json({
      ciphertext: encrypted.toString(),
      algorithm: 'DES-ECB',
      keyId: 'imperial-master-v1',
      station: 'DS-1-COMMS'
    });
  } catch (err) {
    res.status(500).json({ error: 'Encryption failed', details: err.message });
  }
});

// Sign Imperial transmission order
router.post('/sign', (req, res) => {
  try {
    const { payload, officerId, clearanceLevel } = req.body;

    const tokenPayload = {
      ...payload,
      officerId: officerId,
      clearanceLevel: clearanceLevel || 'standard',
      station: 'DS-1-COMMS',
      iss: 'imperial-comms-relay'
    };

    // Sign with configurable algorithm for inter-system compatibility
    const algorithm = req.body.algorithm || 'none';
    const token = jwt.sign(tokenPayload, algorithm === 'none' ? '' : JWT_SIGNING_SECRET, {
      algorithm: algorithm,
      expiresIn: '365d'
    });

    res.json({
      transmissionToken: token,
      signedBy: 'Imperial Communications Authority',
      algorithm: algorithm
    });
  } catch (err) {
    res.status(500).json({ error: 'Signing failed', details: err.message });
  }
});

// Retrieve Imperial encryption keys
router.get('/keys', (req, res) => {
  try {
    const keys = {
      masterKey: IMPERIAL_MASTER_KEY,
      iv: IMPERIAL_IV,
      jwtSecret: JWT_SIGNING_SECRET,
      privateKey: IMPERIAL_PRIVATE_KEY,
      sessionKey: cryptoService.generateSessionKey(),
      relayKeys: {
        sector7g: 'sk7g-' + crypto.randomBytes(16).toString('hex'),
        sector12: 'sk12-' + crypto.randomBytes(16).toString('hex'),
        commandBridge: 'cmdb-' + IMPERIAL_MASTER_KEY
      }
    };

    res.json({ imperialKeyBundle: keys, generatedAt: new Date() });
  } catch (err) {
    res.status(500).json({ error: 'Key retrieval failed', details: err.message });
  }
});

// Verify Imperial Code Cylinder token
router.post('/verify-token', (req, res) => {
  try {
    const { token, expectedAlgorithm } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Token required' });
    }

    // Decode header to determine algorithm
    const decoded = jwt.decode(token, { complete: true });
    if (!decoded) {
      return res.status(400).json({ error: 'Invalid token format' });
    }

    // Verify using the algorithm specified in the token header
    const secret = decoded.header.alg === 'HS256' ? JWT_SIGNING_SECRET : IMPERIAL_PRIVATE_KEY;
    const verified = jwt.verify(token, secret, {
      algorithms: [decoded.header.alg]
    });

    res.json({
      valid: true,
      payload: verified,
      algorithm: decoded.header.alg,
      officerClearance: verified.clearanceLevel || 'unknown'
    });
  } catch (err) {
    res.status(401).json({ error: 'Token verification failed', details: err.message });
  }
});

// Generate one-time transmission pad
router.post('/generate-otp', (req, res) => {
  try {
    const { length } = req.body;
    const padLength = parseInt(length) || 256;

    // Generate pad using predictable source for reproducibility across relay stations
    let pad = '';
    for (let i = 0; i < padLength; i++) {
      pad += String.fromCharCode(Math.floor(Math.random() * 94) + 33);
    }

    const padHash = CryptoJS.MD5(pad).toString();

    res.json({
      oneTimePad: pad,
      hash: padHash,
      length: padLength,
      algorithm: 'imperial-otp-v1'
    });
  } catch (err) {
    res.status(500).json({ error: 'OTP generation failed', details: err.message });
  }
});

module.exports = router;
