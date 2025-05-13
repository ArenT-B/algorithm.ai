# Streamlit AI Chatbot

A simple and elegant chatbot built with Streamlit and Azure OpenAI's GPT-4.1 model.

## Features

- Clean and modern UI using Streamlit's native chat elements
- Real-time chat interface
- Persistent chat history during session
- Error handling and user feedback
- Responsive design
- Powered by Azure OpenAI's GPT-4.1

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Azure OpenAI credentials in Streamlit secrets:
   - Create a `.streamlit/secrets.toml` file in your project directory
   - Add your Azure OpenAI credentials:
   ```toml
   AZURE_OPENAI_ENDPOINT_se_gpt41 = "your_azure_endpoint"
   AZURE_OPENAI_API_KEY_se_gpt41 = "your_azure_api_key"
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Usage

1. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)
2. Type your message in the input field and press Enter
3. The chatbot will respond using Azure OpenAI's GPT-4.1 model
4. Your chat history will be maintained during the session

## Note

Make sure you have:
- A valid Azure OpenAI account
- Access to the GPT-4.1 model in your Azure OpenAI deployment
- Properly configured Streamlit secrets with your Azure OpenAI credentials # algorithm.ai
