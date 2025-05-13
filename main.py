import streamlit as st
from openai import AzureOpenAI
import os


# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT_se_gpt41"],
    api_key=st.secrets["AZURE_OPENAI_API_KEY_se_gpt41"],
    api_version="2024-12-01-preview"
)

# # Set page config
# st.set_page_config(
#     page_title="AI Chatbot",
#     page_icon="🤖",
#     layout="centered"
# )

# Display logo
# st.image("media/logo.png", width=200)

# Page configuration
st.set_page_config(
    page_title="algorithm.ai",
    page_icon="media/large_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.logo("media/large_logo.png", icon_image="media/large_logo.png", size="large")

# with st.sidebar:
#     st.header("Info")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Title
st.title("🤖 AI-консультант для сайта AlgoritmAI")

# Function to load and process knowledge base
def load_knowledge_base():
    knowledge = {}
    try:
        # Load system prompt
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            knowledge["system_prompt"] = f.read().strip()
        
        # Load all knowledge files from the knowledge directory
        knowledge_dir = "knowledge"
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(knowledge_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    knowledge[filename.replace(".txt", "")] = f.read().strip()
        
        # Format the system prompt with knowledge
        full_system_prompt = knowledge["system_prompt"].format(
            knowledge_base="\n\n".join([f"=== {k} ===\n{v}" for k, v in knowledge.items() if k != "system_prompt"])
        )
        
        return full_system_prompt
    except Exception as e:
        st.error(f"Ошибка загрузки базы знаний: {str(e)}")
        return None

# Display system prompt and knowledge in expanders
# Display chat completion parameters
with st.expander("Параметры чат-бота", expanded=False):
    st.markdown("""
    **Параметры генерации ответов:**
    - Temperature: 0.3 (низкая температура для более сфокусированных ответов)
    - Top P: 0.95 (высокое значение для естественных, но контролируемых ответов)
    - Frequency Penalty: 0.2 (легкий штраф для избежания повторений)
    - Presence Penalty: 0.2 (легкий штраф для поддержания контекста)
    """)

with st.expander("Системный промпт", expanded=False):
    try:
        system_prompt = open("system_prompt.txt").read().strip()
        st.text_area("Current System Prompt", system_prompt, height=300, label_visibility="hidden")
    except Exception as e:
        st.error(f"Could not load system prompt: {str(e)}")

st.subheader("База знаний")
st.markdown("**База знаний по страницам algorithm.ai:**")
for filename in sorted(os.listdir("knowledge")):
    if filename.endswith(".txt"):
        with st.expander(filename.replace(".txt", ""), expanded=False):
            try:
                content = open(os.path.join("knowledge", filename)).read().strip()
                st.text_area("Knowledge Content", content, height=300)
            except Exception as e:
                st.error(f"Could not load knowledge content: {str(e)}")

st.subheader("Чат-бот")

chat_container = st.container(border=True, height=300)

chat_container.markdown("...")

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
col1, col2 = st.columns([3, 1])  # 3:1 ratio for input:button
with col1:
    prompt = st.chat_input("Type your message here...")
with col2:
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    
    try:
        # Get response from OpenAI
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Load and process knowledge base
                    full_system_prompt = load_knowledge_base()
                    
                    if full_system_prompt:
                        response = client.chat.completions.create(
                            model="gpt-4.1",  # Azure OpenAI model name
                            messages=[
                                {"role": "system", "content": full_system_prompt}
                            ] + [
                                {"role": m["role"], "content": m["content"]} 
                                for m in st.session_state.messages
                            ],
                            temperature=0.3,  # Lower temperature for more focused responses
                            top_p=0.95,      # High top_p for natural but controlled responses
                            frequency_penalty=0.2,  # Mild penalty to avoid repetition
                            presence_penalty=0.2    # Mild penalty to maintain context
                        )
                        
                        # Add assistant response to chat history
                        assistant_response = response.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                        st.markdown(assistant_response)
                    else:
                        st.error("Не удалось загрузить базу знаний. Пожалуйста, проверьте файлы конфигурации.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure you have set up your Azure OpenAI credentials in Streamlit secrets")
