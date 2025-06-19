document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('question-form');
    const input = document.getElementById('question-input');
    const answerContainer = document.getElementById('answer-container');
    const answerText = document.getElementById('answer-text');
    const loading = document.getElementById('loading');

    const renderAnswer = (answer) => {
        answerText.innerHTML = ''; // Clear previous answer

        if (answer.includes('full squad')) {
            const parts = answer.split(/\n\n/);
            const intro = parts.shift();
            const introP = document.createElement('p');
            introP.textContent = intro;
            answerText.appendChild(introP);

            parts.forEach(playerInfo => {
                const playerCard = document.createElement('div');
                playerCard.className = 'player-card';

                const lines = playerInfo.split('\n').map(l => l.trim().replace(/^\d+\.\s*/, ''));

                const nameLine = lines.shift();
                const name = nameLine.replace(/\*\*/g, '');
                const nameH3 = document.createElement('h3');
                nameH3.textContent = name;
                playerCard.appendChild(nameH3);

                lines.forEach(line => {
                    const detailP = document.createElement('p');
                    const cleanLine = line.replace(/^- \*\*/, '').replace(/\*\* /g, ' ');
                    const [key, ...value] = cleanLine.split(':');
                    detailP.innerHTML = `<strong>${key}:</strong> ${value.join(':').trim()}`;
                    playerCard.appendChild(detailP);
                });

                answerText.appendChild(playerCard);
            });

        } else {
            // For other questions, just render with bold support
            answerText.innerHTML = answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) {
            return;
        }

        answerContainer.style.display = 'none';
        loading.style.display = 'block';

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) {
                throw new Error('Something went wrong');
            }

            const data = await response.json();
            renderAnswer(data.answer);
            answerContainer.style.display = 'block';

        } catch (error) {
            answerText.textContent = 'Error: ' + error.message;
            answerContainer.style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    });
});
