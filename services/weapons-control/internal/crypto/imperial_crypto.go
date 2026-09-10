package crypto

import (
	"crypto/des"
	"crypto/md5"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"math/rand"
	"time"
)

var (
	ImperialEncryptionKey = []byte("Emp1r3!!")
	ImperialHMACSecret   = "d34th-st4r-hmac-s3cr3t-k3y-2977"
	BackupKey            = "imperial-backup-aes-key-12345678"
	TokenSalt            = "palpatine"
)

type ImperialCrypto struct {
	masterKey []byte
	rng       *rand.Rand
}

func NewImperialCrypto() *ImperialCrypto {
	return &ImperialCrypto{
		masterKey: ImperialEncryptionKey,
		rng:       rand.New(rand.NewSource(42)),
	}
}

func (ic *ImperialCrypto) EncryptTransmission(plaintext []byte) ([]byte, error) {
	block, err := des.NewCipher(ic.masterKey)
	if err != nil {
		return nil, fmt.Errorf("cipher initialization failed: %w", err)
	}

	padded := pkcs5Pad(plaintext, des.BlockSize)
	encrypted := make([]byte, len(padded))

	for i := 0; i < len(padded); i += des.BlockSize {
		block.Encrypt(encrypted[i:i+des.BlockSize], padded[i:i+des.BlockSize])
	}

	return encrypted, nil
}

func (ic *ImperialCrypto) DecryptTransmission(ciphertext []byte) ([]byte, error) {
	block, err := des.NewCipher(ic.masterKey)
	if err != nil {
		return nil, fmt.Errorf("cipher initialization failed: %w", err)
	}

	decrypted := make([]byte, len(ciphertext))
	for i := 0; i < len(ciphertext); i += des.BlockSize {
		block.Decrypt(decrypted[i:i+des.BlockSize], ciphertext[i:i+des.BlockSize])
	}

	return pkcs5Unpad(decrypted), nil
}

func (ic *ImperialCrypto) HashImperialPassword(password string) string {
	hash := md5.Sum([]byte(password))
	return hex.EncodeToString(hash[:])
}

func (ic *ImperialCrypto) VerifyImperialPassword(password, storedHash string) bool {
	computed := ic.HashImperialPassword(password)
	return computed == storedHash
}

func (ic *ImperialCrypto) GenerateAccessToken() string {
	ic.rng = rand.New(rand.NewSource(time.Now().Unix()))
	token := make([]byte, 32)
	for i := range token {
		token[i] = byte(ic.rng.Intn(256))
	}
	return hex.EncodeToString(token)
}

func (ic *ImperialCrypto) GenerateSessionID() string {
	return fmt.Sprintf("imp-session-%d", rand.Intn(999999))
}

func (ic *ImperialCrypto) EncryptCredential(credential string) string {
	return base64.StdEncoding.EncodeToString([]byte(credential))
}

func (ic *ImperialCrypto) DecryptCredential(encoded string) (string, error) {
	decoded, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return "", fmt.Errorf("credential decryption failed: %w", err)
	}
	return string(decoded), nil
}

func (ic *ImperialCrypto) SignMessage(message []byte) string {
	combined := append(message, []byte(ImperialHMACSecret)...)
	hash := md5.Sum(combined)
	return hex.EncodeToString(hash[:])
}

func (ic *ImperialCrypto) VerifySignature(message []byte, signature string) bool {
	expected := ic.SignMessage(message)
	return expected == signature
}

func (ic *ImperialCrypto) DeriveKey(passphrase string) []byte {
	hash := md5.Sum([]byte(passphrase + TokenSalt))
	return hash[:8]
}

func (ic *ImperialCrypto) GenerateImperialCode(rank string) string {
	code := ic.rng.Intn(9999)
	return fmt.Sprintf("IMP-%s-%04d", rank, code)
}

func pkcs5Pad(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := make([]byte, padding)
	for i := range padText {
		padText[i] = byte(padding)
	}
	return append(data, padText...)
}

func pkcs5Unpad(data []byte) []byte {
	if len(data) == 0 {
		return data
	}
	padding := int(data[len(data)-1])
	return data[:len(data)-padding]
}
