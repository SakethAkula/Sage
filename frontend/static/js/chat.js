// ===== SAGE CHAT FUNCTIONALITY =====

let selectedFile = null;
let currentSessionId = null;

// ===== THEME TOGGLE =====
function toggleTheme() {
    const body = document.body;
    if (body.classList.contains('light-mode')) {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        localStorage.setItem('sage-theme', 'dark');
    } else {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        localStorage.setItem('sage-theme', 'light');
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('sage-theme');
    if (savedTheme === 'dark') {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
    }
}

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('active');
}

// ===== CHAT SESSIONS =====
async function loadChatSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        if (data.sessions) {
            currentSessionId = data.current_session_id;
            renderChatSessions(data.sessions);
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

function renderChatSessions(sessions) {
    const list = document.getElementById('chatHistoryList');
    list.innerHTML = '';
    
    if (sessions.length === 0) {
        list.innerHTML = '<li class="history-empty">No chat history yet</li>';
        return;
    }
    
    sessions.forEach(s => {
        const li = document.createElement('li');
        li.className = `history-item ${s.id === currentSessionId ? 'active' : ''}`;
        li.onclick = () => loadSession(s.id);
        li.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>${escapeHtml(s.title)}</span>
            <button class="delete-session" onclick="event.stopPropagation(); deleteSession(${s.id})">✕</button>
        `;
        list.appendChild(li);
    });
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        const data = await response.json();
        
        if (data.messages) {
            currentSessionId = sessionId;
            
            // Hide welcome, show messages
            document.getElementById('welcomeScreen').style.display = 'none';
            document.getElementById('quickSuggestions').style.display = 'none';
            document.getElementById('messagesWrapper').classList.add('has-messages');
            
            // Move input to fixed bottom
            const bottomSection = document.getElementById('bottomSection');
            const chatMain = document.querySelector('.chat-main');
            if (bottomSection.parentElement.id === 'messagesWrapper') {
                chatMain.insertBefore(bottomSection, document.querySelector('.emergency-text-simple'));
                bottomSection.classList.add('fixed-bottom');
            }
            
            // Clear existing messages
            const wrapper = document.getElementById('messagesWrapper');
            wrapper.querySelectorAll('.message:not(.typing-indicator)').forEach(m => m.remove());
            
            // Add messages
            data.messages.forEach(msg => {
                addMessageToUI(msg.message, msg.sender === 'user' ? 'user' : 'sage');
            });
            
            loadChatSessions();
            toggleSidebar();
            scrollToBottom();
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

async function deleteSession(sessionId) {
    if (!confirm('Delete this conversation?')) return;
    
    try {
        await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
        if (sessionId === currentSessionId) startNewChat();
        loadChatSessions();
    } catch (error) {
        console.error('Error deleting session:', error);
    }
}

async function startNewChat() {
    try {
        await fetch('/api/new-chat', { method: 'POST' });
        currentSessionId = null;
        
        // Reset layout - move input back inside wrapper
        const bottomSection = document.getElementById('bottomSection');
        const wrapper = document.getElementById('messagesWrapper');
        const typingIndicator = document.getElementById('typingIndicator');
        
        // Clear messages
        wrapper.querySelectorAll('.message:not(.typing-indicator)').forEach(m => m.remove());
        
        // Move bottom section back inside wrapper after typing indicator
        wrapper.appendChild(bottomSection);
        bottomSection.classList.remove('fixed-bottom');
        wrapper.classList.remove('has-messages');
        
        // Show welcome screen
        document.getElementById('welcomeScreen').style.display = 'flex';
        document.getElementById('quickSuggestions').style.display = 'flex';
        
        loadChatSessions();
        toggleSidebar();
    } catch (error) {
        console.error('Error starting new chat:', error);
    }
}

// ===== SEND MESSAGE =====
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message && !selectedFile) return;
    
    // Hide welcome and add has-messages class for top alignment
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('quickSuggestions').style.display = 'none';
    document.getElementById('messagesWrapper').classList.add('has-messages');
    
    // Move input to fixed bottom position
    const bottomSection = document.getElementById('bottomSection');
    const chatMain = document.querySelector('.chat-main');
    if (bottomSection.parentElement.id === 'messagesWrapper') {
        chatMain.insertBefore(bottomSection, document.querySelector('.emergency-text-simple'));
        bottomSection.classList.add('fixed-bottom');
    }
    
    input.value = '';
    
    if (selectedFile) {
        const file = selectedFile;
        removeFile();
        addMessageToUI(`📎 ${file.name}: ${message || 'Analyze this'}`, 'user');
        showTypingIndicator();
        
        try {
            const data = await uploadFile(file, message);
            hideTypingIndicator();
            addMessageToUI(data.response, 'sage');
            loadChatSessions();
        } catch (error) {
            hideTypingIndicator();
            addMessageToUI("Sorry, couldn't process that file.", 'sage');
        }
    } else {
        addMessageToUI(message, 'user');
        showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            hideTypingIndicator();
            addMessageToUI(data.response, 'sage');
            loadChatSessions();
        } catch (error) {
            hideTypingIndicator();
            addMessageToUI("Connection error. Please try again.", 'sage');
        }
    }
}

function sendSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

function addMessageToUI(text, sender) {
    const wrapper = document.getElementById('messagesWrapper');
    const typingIndicator = document.getElementById('typingIndicator');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    
    if (sender === 'user') {
        div.innerHTML = `
            <div class="message-avatar"><span>U</span></div>
            <div class="message-content">
                <div class="message-bubble"><p>${escapeHtml(text)}</p></div>
                <span class="message-time">${time}</span>
            </div>
        `;
    } else {
        div.innerHTML = `
            <div class="message-avatar">
                <svg viewBox="0 0 50 50" width="32" height="32">
                    <rect x="18" y="8" width="14" height="34" rx="3" fill="#3dbda7"/>
                    <rect x="8" y="18" width="34" height="14" rx="3" fill="#3dbda7"/>
                    <ellipse cx="38" cy="12" rx="8" ry="5" fill="#2d8a7a" transform="rotate(45, 38, 12)"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-bubble"><p>${text}</p></div>
                <span class="message-time">${time}</span>
            </div>
        `;
    }
    
    wrapper.insertBefore(div, typingIndicator);
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== TYPING INDICATOR =====
function showTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'none';
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

// ===== FILE UPLOAD =====
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        alert('Please upload an image or PDF file.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File size should be less than 10MB.');
        return;
    }
    
    selectedFile = file;
    document.getElementById('fileName').textContent = `📎 ${file.name}`;
    document.getElementById('filePreview').style.display = 'block';
}

function removeFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').style.display = 'none';
}

async function uploadFile(file, message) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message', message || 'Please analyze this.');
    
    const response = await fetch('/api/upload', { method: 'POST', body: formData });
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
}

// ===== KEYBOARD =====
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ===== INITIALIZE =====
document.addEventListener('DOMContentLoaded', function() {
    
    loadChatSessions();
    document.getElementById('messageInput').focus();
});