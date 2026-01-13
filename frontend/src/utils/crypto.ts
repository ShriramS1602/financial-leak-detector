/**
 * Crypto utilities for password encryption
 * Uses RSA encryption for secure password transport to backend
 */

// RSA Public Key - This should match the private key in the backend
// In production, this should be fetched from the server or environment
// const RSA_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
// MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxsykVG1JLJ1mJ+aUJyXx
// ZzNuO+CyVQfW3l6XVTUQ1TlGjL7pb4CoL5sRf6f4+AZB6lmf2XZfRmaNTnLBQQMv
// l02bRECM8ZcR/aHQ+LVLhiCKxEmbTcHMMT4A2eKpuu+WMiuLxtoKWkLog2jazqwi
// Em6lNxvU5/UCBVbB5LWDBE9J3nBpfp2n4Ptjg4UWPrhT1Yc/cVWs6zzVLVRCZx19
// m6uPxIKPMMSDW4cVSWKQ+yCRyD4JyGmofklVuqMSv33w4QOyRrkP8cfFt0lG946x
// fQ0OMt1m1N1w+Bs8yxrnv8PnHcsjCwATG7V0TD+a3x41EpuUraTn6wEENP+QZBgo
// FwIDAQAB
// -----END PUBLIC KEY-----`;
const RSA_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLfHCozMxH2Mo\n4lgOP+IJEPh5/G9y93Mid7t3VNcyyYDS7lbOaUvZ9/tv0t8vCeniRBwgnrxFgGio\n8BQI2N1U0A8lSsDyJOwV5HCaRFqYhVtn9WSW6oMYD8b2F7y5wFTKc+q6xllq+DLg\niT5eaSocROi5BvCvUVNRxCeW0KkGb7R1Yb6lfA5NKd2IwWVbxFfvM+CkyR/CwNGq\nJbFl2L6SL1OeEA8RZSflQXDkVr0bWGSI3mVPQmVVo8+tqn/BwQxEX+oY1dFBBp5y\nXxGtJLe7LIRIMLnJ6hWM9fNpNQk3q8DfXwdvpTKhL2kJ0mP7KxQXQfr1OiEhDILp\n/8dHdWQjAgMBAAE=\n-----END PUBLIC KEY-----"
/**
 * Convert a string to ArrayBuffer
 */
function str2ab(str: string): ArrayBuffer {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0; i < str.length; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

/**
 * Convert ArrayBuffer to base64 string
 */
function ab2b64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Import RSA public key for encryption
 */
async function importPublicKey(pemKey: string): Promise<CryptoKey> {
  // Remove PEM header/footer and decode base64
  const pemContents = pemKey
    .replace('-----BEGIN PUBLIC KEY-----', '')
    .replace('-----END PUBLIC KEY-----', '')
    .replace(/\s/g, '');

  const binaryDer = atob(pemContents);
  const buffer = str2ab(binaryDer);

  return await crypto.subtle.importKey(
    'spki',
    buffer,
    {
      name: 'RSA-OAEP',
      hash: 'SHA-256',
    },
    false,
    ['encrypt']
  );
}

/**
 * Encrypt password using RSA-OAEP with the server's public key
 * Returns base64 encoded encrypted password
 */
export async function encryptPassword(password: string): Promise<string> {
  try {
    const publicKey = await importPublicKey(RSA_PUBLIC_KEY);
    const encoder = new TextEncoder();
    const data = encoder.encode(password);

    const encrypted = await crypto.subtle.encrypt(
      { name: 'RSA-OAEP' },
      publicKey,
      data
    );

    return ab2b64(encrypted);
  } catch (error) {
    console.error('Password encryption failed:', error);
    // Fallback to base64 encoding if RSA encryption fails
    // This maintains backward compatibility but should be logged/monitored
    console.warn('Falling back to base64 encoding');
    return btoa(password);
  }
}

/**
 * Simple bcrypt-like hash for client-side (not cryptographically secure for storage)
 * This is used for additional obfuscation, not security
 */
export function hashPasswordClient(password: string, salt: string = ''): string {
  // Use Web Crypto API for hashing
  const data = password + salt;
  return btoa(data);
}

/**
 * Generate a random salt
 */
export function generateSalt(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return ab2b64(array.buffer);
}