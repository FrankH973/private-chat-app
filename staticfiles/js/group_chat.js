// Group Chat Management
class GroupChatManager {
    constructor(groupId) {
        this.groupId = groupId;
        this.socket = null;
        this.onlineUsers = new Set();
        this.initWebSocket();
        this.setupEventListeners();
    }

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/group/${this.groupId}/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Group chat connected');
            this.updateConnectionStatus(true);
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.socket.onclose = () => {
            console.log('Group chat disconnected');
            this.updateConnectionStatus(false);
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.initWebSocket(), 3000);
        };
    }

    handleMessage(data) {
        if (data.type === 'user_status') {
            this.updateUserStatus(data.user, data.status);
        } else {
            this.displayMessage(data);
        }
    }

    sendMessage(message, messageType = 'text', replyTo = null, fileData = null) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                message: message,
                type: messageType,
                reply_to: replyTo,
                file_data: fileData
            }));
        }
    }

    displayMessage(data) {
        const messagesContainer = document.getElementById('group-messages');
        const messageElement = this.createMessageElement(data);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    createMessageElement(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.sender_id === currentUserId ? 'sent' : 'received'}`;
        messageDiv.setAttribute('data-message-id', data.message_id);

        let replyHtml = '';
        if (data.reply_to) {
            const originalMessage = document.querySelector(`[data-message-id="${data.reply_to}"]`);
            if (originalMessage) {
                replyHtml = `<div class="reply-reference">Replying to: ${originalMessage.textContent.substring(0, 50)}...</div>`;
            }
        }

        messageDiv.innerHTML = `
            ${replyHtml}
            <div class="message-header">
                <span class="sender">${data.sender}</span>
                <span class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${data.message}</div>
            <div class="message-actions">
                <button onclick="groupChat.replyToMessage('${data.message_id}', '${data.sender}')">Reply</button>
                ${data.sender_id === currentUserId ? '<button onclick="groupChat.editMessage(\'' + data.message_id + '\')">Edit</button>' : ''}
            </div>
        `;

        return messageDiv;
    }

    updateUserStatus(username, status) {
        if (status === 'online') {
            this.onlineUsers.add(username);
        } else {
            this.onlineUsers.delete(username);
        }
        this.updateOnlineUsersList();
    }

    updateOnlineUsersList() {
        const onlineList = document.getElementById('online-users');
        if (onlineList) {
            onlineList.innerHTML = Array.from(this.onlineUsers)
                .map(user => `<div class="online-user">${user}</div>`)
                .join('');
        }
    }

    replyToMessage(messageId, senderName) {
        const replyContainer = document.getElementById('reply-container');
        const messageInput = document.getElementById('message-input');
        
        replyContainer.innerHTML = `
            <div class="replying-to">
                Replying to ${senderName}
                <button onclick="groupChat.cancelReply()">Cancel</button>
            </div>
        `;
        replyContainer.style.display = 'block';
        replyContainer.setAttribute('data-reply-to', messageId);
        messageInput.focus();
    }

    cancelReply() {
        const replyContainer = document.getElementById('reply-container');
        replyContainer.style.display = 'none';
        replyContainer.removeAttribute('data-reply-to');
    }

    setupEventListeners() {
        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
        const fileInput = document.getElementById('file-input');

        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const message = messageInput.value.trim();
                if (message) {
                    const replyContainer = document.getElementById('reply-container');
                    const replyTo = replyContainer.getAttribute('data-reply-to');
                    
                    this.sendMessage(message, 'text', replyTo);
                    messageInput.value = '';
                    this.cancelReply();
                }
            });
        }

        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileUpload(file);
                }
            });
        }
    }

    handleFileUpload(file) {
        const reader = new FileReader();
        reader.onload = () => {
            const fileData = {
                name: file.name,
                size: file.size,
                type: file.type,
                content: reader.result.split(',')[1] // Remove data:type;base64, prefix
            };
            
            this.sendMessage(file.name, 'file', null, fileData);
        };
        reader.readAsDataURL(file);
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.className = connected ? 'connected' : 'disconnected';
            statusIndicator.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    // Group management functions
    inviteUser(email) {
        fetch(`/groups/${this.groupId}/invite/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({email: email})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Invitation sent successfully!');
            } else {
                alert('Error sending invitation: ' + data.error);
            }
        });
    }

    leaveGroup() {
        if (confirm('Are you sure you want to leave this group?')) {
            fetch(`/groups/${this.groupId}/leave/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/groups/';
                }
            });
        }
    }
}

// Initialize group chat when page loads
let groupChat;
document.addEventListener('DOMContentLoaded', function() {
    const groupId = document.body.getAttribute('data-group-id');
    const currentUserId = document.body.getAttribute('data-user-id');
    
    if (groupId) {
        groupChat = new GroupChatManager(groupId);
    }
});