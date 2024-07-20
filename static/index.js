document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start-button');
    const coverPage = document.getElementById('cover-page');
    const mainContent = document.getElementById('main-content');

    startButton.addEventListener('click', () => {
        coverPage.style.display = 'none';
        mainContent.style.display = 'block';
    });

    document.getElementById('send-btn').addEventListener('click', async () => {
        const prompt = document.getElementById('setup-textarea').value;

        if (prompt.trim() === "") return;
        const userSpeechBubble = document.createElement('div');
        userSpeechBubble.className = 'user-speech-bubble';
        userSpeechBubble.textContent = prompt;
        const chatContainer = document.getElementById('chat-container');
        chatContainer.appendChild(userSpeechBubble);
        document.getElementById('setup-textarea').value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();
        const girlImageUrl = document.getElementById('setup-container').dataset.girlImageUrl;
        const aiMessageContainer = document.createElement('div');
        aiMessageContainer.className = 'ai-message';
        const girlImage = document.createElement('img');
        girlImage.src = girlImageUrl;
        girlImage.className = 'girl-image';
        aiMessageContainer.appendChild(girlImage);
        const aiSpeechBubble = document.createElement('div');
        aiSpeechBubble.className = 'speech-bubble-ai';
        let responseText = data.response.replace(/\n/g, '<br>');
        aiSpeechBubble.innerHTML = `${responseText}`;
        console.log(data.response);
        aiMessageContainer.appendChild(aiSpeechBubble);
        const readAloudButton = document.createElement('button');
        readAloudButton.className = 'read-aloud-btn';
        readAloudButton.textContent = 'Read Aloud';
        readAloudButton.addEventListener('click', () => {
            readAloud(data.response);
        });
        aiMessageContainer.appendChild(readAloudButton);

        chatContainer.appendChild(aiMessageContainer);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    });

    async function readAloud(text) {
        try {
            const response = await fetch('/read_aloud', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error('Failed to read aloud');
            }

            const data = await response.json();
            console.log('Read aloud status:', data.status);
        } catch (error) {
            console.error('Error reading aloud:', error.message);
        }
    }
});
