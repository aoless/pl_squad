document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('question-form');
    const input = document.getElementById('question-input');
    const answerContainer = document.getElementById('answer-container');
    const answerText = document.getElementById('answer-text');
    const loading = document.getElementById('loading');

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
            answerText.textContent = data.answer;
            answerContainer.style.display = 'block';

        } catch (error) {
            answerText.textContent = 'Error: ' + error.message;
            answerContainer.style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    });
});
