document.addEventListener('DOMContentLoaded', () => {
    console.log('InsideOut is ready.');

    // --- Feeling Page Logic ---
    window.fillFeeling = function (emotion) {
        const input = document.querySelector('input[name="feeling"]');
        if (input) {
            input.value = emotion;
            input.focus();
        }
    };

    // --- Reflection Page Chat Logic ---
    const chatContainer = document.getElementById('chat-container');
    const chatInput = document.getElementById('chat-input');
    const chatSubmit = document.getElementById('chat-submit');

    if (chatContainer) {
        // Initialize chat
        initializeChat();

        chatSubmit.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Focus input
        setTimeout(() => {
            chatInput.focus();
        }, 100);
    }

    function initializeChat() {
        // Check if we have initial feeling from server
        const initialMessage = chatContainer.querySelector('.message.user-message[data-feeling]');
        if (initialMessage) {
            const feeling = initialMessage.dataset.feeling;
            // Get AI response after a short delay
            setTimeout(() => {
                getAIResponse(feeling);
            }, 500);
        }
    }

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, 'user-message');
        chatInput.value = '';

        // Get AI response
        getAIResponse(text);
    }

    async function getAIResponse(feelingText) {
        // Show loading message
        const loadingMsg = addMessage('Echo is thinking...', 'ai-message loading');

        try {
            const response = await fetch('/api/reflect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feeling: feelingText })
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();

            // Remove loading message
            removeMessage(loadingMsg);

            // Handle response
            handleAIResponse(data);

        } catch (error) {
            console.error('Error:', error);
            removeMessage(loadingMsg);
            addMessage("I'm having some trouble connecting. Please try again.", 'ai-message');
        }
    }

    function handleAIResponse(data) {
        // Handle crisis response
        if (data.type === 'crisis') {
            addMessage(data.message, 'ai-message crisis');
            if (data.suggestion) {
                setTimeout(() => addMessage(data.suggestion, 'ai-message'), 800);
            }
            return;
        }

        // Handle normal response
        let delay = 0;

        if (data.message) {
            setTimeout(() => addMessage(data.message, 'ai-message'), delay);
            delay += 800;
        }

        if (data.suggestion) {
            setTimeout(() => addMessage(data.suggestion, 'ai-message'), delay);
            delay += 800;
        }

        if (data.follow_up) {
            setTimeout(() => addMessage(data.follow_up, 'ai-message'), delay);
        }

        if (data.new_pattern) {
            setTimeout(() => showNotification(data.new_pattern), delay + 500);
        }
    }

    function addMessage(text, className) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${className}`;

        // Add content
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = formatMessage(text);
        msgDiv.appendChild(contentDiv);

        // Add to chat
        chatContainer.appendChild(msgDiv);

        // Trigger animation
        setTimeout(() => {
            msgDiv.style.opacity = '1';
            msgDiv.style.transform = 'translateY(0)';
        }, 10);

        // Scroll to bottom
        scrollToBottom();

        // Return element for reference
        return msgDiv;
    }

    function formatMessage(text) {
        if (!text) return '';

        // Simple formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    function removeMessage(messageElement) {
        if (messageElement && messageElement.parentNode) {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translateY(-10px)';

            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 300);
        }
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }

    // --- Learning Hub Logic ---
    const modal = document.getElementById('topic-modal');
    const modalBody = document.getElementById('modal-body');
    const closeModal = document.querySelector('.close-modal');

    window.loadTopic = async function (topicSlug) {
        if (!modal) return;

        modalBody.innerHTML = '<p>Loading...</p>';
        modal.classList.remove('hidden');

        try {
            const response = await fetch(`/api/learn/${topicSlug}`);
            const data = await response.json();

            modalBody.innerHTML = `
                <h2>${data.title}</h2>
                <div class="learning-section">
                    <p><strong>Insight:</strong> ${data.explanation}</p>
                </div>
                <div class="learning-section">
                    <p><strong>Example:</strong> ${data.example}</p>
                </div>
                <div class="learning-section">
                    <p><strong>Reflection:</strong> ${data.reflection_question}</p>
                </div>
                <div class="learning-section">
                    <p><strong>Try This:</strong> ${data.action}</p>
                </div>
            `;
        } catch (error) {
            modalBody.innerHTML = '<p>Unable to load topic.</p>';
        }
    };

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            modal.classList.add('hidden');
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }

    // --- Notification Logic ---
    function showNotification(pattern) {
        const container = document.getElementById('notification-container');
        const message = document.getElementById('notification-message');

        if (!container || !message) return;

        message.textContent = `New pattern: ${pattern.name}`;
        container.classList.remove('hidden');

        // Auto-hide after 10 seconds
        setTimeout(() => {
            container.classList.add('hidden');
        }, 10000);
    }

    const closeNotif = document.querySelector('.close-notification');
    if (closeNotif) {
        closeNotif.addEventListener('click', () => {
            const container = document.getElementById('notification-container');
            if (container) container.classList.add('hidden');
        });
    }
});