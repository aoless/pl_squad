I have created a simple and modern web application to interact with your Premier League Q&A agent.
Here's a summary of what I've done:

- **Web Framework**: I used FastAPI to create a robust backend.
- **Frontend**: I built a clean user interface with HTML, CSS, and JavaScript.
- **API**: An endpoint at `/api/ask` handles questions and communicates with the agent.
- **Easy to Run**: I've added a command to `pyproject.toml` to easily start the web server.

### How to run the application:

1.  **Create a `.env` file**:
    Create a file named `.env` in the root of the project and add your OpenAI API key and other settings. You can copy the example below:
    ```
    OPENAI_API_KEY="sk-..."
    OPENAI_MODEL="gpt-4o-mini"
    OPENAI_TEMPERATURE="0"
    ```

2.  **Install dependencies**:
    If you haven't installed the new dependencies, run:
    ```bash
    poetry install
    ```

3.  **Run the web server**:
    ```bash
    poetry run poe web
    ```
    This will start the server.

4.  **Open the application**:
    Open your web browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

You can now ask questions to your agent through the web interface.
Let me know if you have any other questions!
