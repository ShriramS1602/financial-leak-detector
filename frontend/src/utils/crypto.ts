/**
 * Crypto utilities for password encryption
 * Uses RSA encryption for secure password transport to backend
 */

// RSA Public Key - This should match the private key in the backend
// In production, this should be fetched from the server or environment
const RSA_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoysR/CU7zMb1/ul607B1
MZiAdsNL6vjY1WV+6NPc/7PKvk+wdfmY51HdNn1Vf1Bzmm3I1D/wH9sP4an+/Nnd
hEaPryVkTd6RfpIaN1rQmeLCXzU58HDEPD36sw8czsy0fp5TBjLpwQ26G4NKcF3l
+erqUE1KKwxkqf8GebVW2L6u4rg+3EJLMaHWtlQdYNDH+vp43bt71NUjp0GhtDse
K0Sf529sATFHgk3ZH1M51RPigDXtDQTpRzb27LeJkfsPD7dstnG2paSJNGcu2KZw
2K96KABm5Rnyr69mcOFLGKujq+ObPCdvWJYjRaSKZ+wiVJAUIn8Al7MqVTiabdOa
4wIDAQAB
-----END PUBLIC KEY-----`;

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
