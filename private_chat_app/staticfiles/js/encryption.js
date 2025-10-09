// Simple client-side encryption utilities
class ChatEncryption {
    constructor() {
        this.keyPair = null;
    }

    async generateKeyPair() {
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

    async encryptMessage(message, publicKey) {
        const encoded = new TextEncoder().encode(message);
        const encrypted = await window.crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            publicKey,
            encoded
        );
        return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
    }

    async decryptMessage(encryptedMessage, privateKey) {
        const encrypted = Uint8Array.from(atob(encryptedMessage), c => c.charCodeAt(0));
        const decrypted = await window.crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            encrypted
        );
        return new TextDecoder().decode(decrypted);
    }
}