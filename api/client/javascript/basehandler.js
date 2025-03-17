document.addEventListener('DOMContentLoaded', () => {
    const prompt = document.getElementById('prompt');
    const send = document.getElementById('send');
    const chatMessages = document.getElementById('chat-messages');
    var history = [];

    send.addEventListener('click', () => {
        let promptText = prompt.value;

        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user');
        userMessage.innerHTML = `<div class="text">${promptText}</div>`;
        chatMessages.appendChild(userMessage);

        prompt.value = '';

        const aiMessage = document.createElement('div');
        aiMessage.classList.add('message', 'ai');
        aiMessage.innerHTML = `<div class="text"></div><button class="dislike-button">Dislike</button>`;
        chatMessages.appendChild(aiMessage);

        chatMessages.scrollTop = chatMessages.scrollHeight;

        const aiResponse = aiMessage.querySelector('.text');
        const dislikeButton = aiMessage.querySelector('.dislike-button');

        const eventSource = new EventSource(`/chat-api?prompt=${encodeURIComponent(promptText)}&history=${encodeURIComponent(JSON.stringify(history))}`);
        history.push('     PREVIOUS PROMPT FROM USER: ' + promptText);

        eventSource.onmessage = function(event) {
            aiResponse.innerHTML += event.data;
            aiResponse.classList.add('ai-text-loading');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        eventSource.onerror = function(error) {
            console.error('Error occurred while streaming:', error);
            console.error('EventSource readyState:', eventSource.readyState);
            eventSource.close();
        };

        dislikeButton.addEventListener('click', () => {
            console.log("Disliked message:", promptText);
            console.log("AI's response:", aiResponse.innerText);
            dislikeButton.disabled = true;
        });
    });
});
