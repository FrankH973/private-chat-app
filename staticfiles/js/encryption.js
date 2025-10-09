// static/js/encryption.js
// Client-side encryption utilities with fallback for non-secure contexts

class ChatEncryption {
    constructor() {
        this.keyPair = null;
        this.symmetricKey = null;
        this.encryptionAvailable = this.checkCryptoAvailability();
    }

    // Check if Web Crypto API is available
    checkCryptoAvailability() {
        const available = window.crypto && window.crypto.subtle;
        if (!available) {
            console.warn('Web Crypto API not available - encryption disabled (HTTP context)');
        }
        return available;
    }

    // Generate encryption key pair for user
    async generateKeyPair() {
        if (!this.encryptionAvailable) return null;
        
        this.keyPair = await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256",
            },
            true,
            ["encrypt", "decrypt"]
        );
        return this.keyPair;
    }

    // Generate symmetric key for room
    async generateSymmetricKey() {
        if (!this.encryptionAvailable) return null;
        
        this.symmetricKey = await window.crypto.subtle.generateKey(
            {
                name: "AES-GCM",
                length: 256
            },
            true,
            ["encrypt", "decrypt"]
        );
        return this.symmetricKey;
    }

    // Encrypt message with symmetric key
    async encryptMessage(message) {
        // If encryption not available, return plain text
        if (!this.encryptionAvailable) {
            return message;
        }

        if (!this.symmetricKey) {
            await this.generateSymmetricKey();
        }

        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(message);
            const iv = window.crypto.getRandomValues(new Uint8Array(12));

            const encrypted = await window.crypto.subtle.encrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                this.symmetricKey,
                data
            );

            // Combine IV and encrypted data
            const combined = new Uint8Array(iv.length + encrypted.byteLength);
            combined.set(iv, 0);
            combined.set(new Uint8Array(encrypted), iv.length);

            return btoa(String.fromCharCode(...combined));
        } catch (e) {
            console.error('Encryption failed:', e);
            return message; // Return plain text if encryption fails
        }
    }

    // Decrypt message
    async decryptMessage(encryptedMessage) {
        // If encryption not available, return message as-is
        if (!this.encryptionAvailable || !this.symmetricKey) {
            return encryptedMessage;
        }

        try {
            const combined = Uint8Array.from(atob(encryptedMessage), c => c.charCodeAt(0));
            const iv = combined.slice(0, 12);
            const data = combined.slice(12);

            const decrypted = await window.crypto.subtle.decrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                this.symmetricKey,
                data
            );

            const decoder = new TextDecoder();
            return decoder.decode(decrypted);
        } catch (e) {
            console.error('Decryption failed:', e);
            return encryptedMessage; // Return original if decryption fails
        }
    }

    // Export key for storage
    async exportKey(key) {
        if (!this.encryptionAvailable) return null;
        
        const exported = await window.crypto.subtle.exportKey("jwk", key);
        return JSON.stringify(exported);
    }

    // Import key from storage
    async importKey(keyData, type = 'symmetric') {
        if (!this.encryptionAvailable) return null;
        
        const keyJson = JSON.parse(keyData);
        
        if (type === 'symmetric') {
            return await window.crypto.subtle.importKey(
                "jwk",
                keyJson,
                { name: "AES-GCM" },
                true,
                ["encrypt", "decrypt"]
            );
        }
    }

    // Save key to sessionStorage
    async saveKey(roomId) {
        if (!this.encryptionAvailable || !this.symmetricKey) return;
        
        const exported = await this.exportKey(this.symmetricKey);
        sessionStorage.setItem(`chat_key_${roomId}`, exported);
    }

    // Load key from sessionStorage
    async loadKey(roomId) {
        if (!this.encryptionAvailable) return false;
        
        const keyData = sessionStorage.getItem(`chat_key_${roomId}`);
        if (keyData) {
            this.symmetricKey = await this.importKey(keyData, 'symmetric');
            return true;
        }
        return false;
    }
}