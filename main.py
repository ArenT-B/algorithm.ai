import streamlit as st
from openai import AzureOpenAI
import os
from datetime import datetime


# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT_se_gpt41"],
    api_key=st.secrets["AZURE_OPENAI_API_KEY_se_gpt41"],
    api_version="2024-12-01-preview"
)

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

# Initialize session state for collected contacts
if "collected_contacts" not in st.session_state:
    st.session_state.collected_contacts = []

# Initialize session state for showing contact form
if "show_contact_form" not in st.session_state:
    st.session_state.show_contact_form = False

# Initialize session state for selected question
if "selected_question" not in st.session_state:
    st.session_state.selected_question = "Выберите пример вопроса..."

# Initialize message counter
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

# Title
st.title("🤖 AI-консультант для сайта AlgoritmAI")

# Documentation sections
with st.expander("📋 О проекте", expanded=False):
    st.markdown("""
    ### Контекст проекта
    AI-консультант разработан для сайта AlgoritmAI с целью:
    - Отвечать на вопросы потенциальных клиентов
    - Собирать контакты для отдела продаж
    - Предоставлять информацию об услугах компании
    
    ### Основные ограничения
    - Консультант может говорить только об услугах, представленных на сайте
    - Не раскрывает информацию о своей природе как ИИ
    - Строго придерживается заданных рамок общения
    """)

with st.expander("🎯 Задачи консультанта", expanded=False):
    st.markdown("""
    ### Роль и задачи
    1. **Информационная поддержка**
       - Предоставление детальной информации об услугах
       - Ответы на вопросы о продуктах и кейсах
       - Объяснение преимуществ компании
    
    2. **Сбор контактов**
       - Вежливое предложение оставить контактные данные
       - Передача информации отделу продаж
    
    3. **Обработка запросов**
       - Четкие ответы по тематике компании
       - Корректная обработка вопросов "не по теме"
       - Поддержание профессионального тона общения
    """)

with st.expander("💡 Примеры взаимодействия", expanded=False):
    st.markdown("""
    ### Примеры вопросов для консультанта
    
    Вот примеры вопросов, которые вы можете задать:
    
    1. Какие услуги вы предоставляете в области разработки ПО?
    2. Как вы работаете с заказчиками из других стран?
    3. Расскажите о ваших последних проектах
    4. Какие технологии вы используете в разработке?
    5. Как происходит процесс разработки проекта?
    6. Какие гарантии вы предоставляете клиентам?
    7. Как вы обеспечиваете безопасность данных?
    8. Какие у вас условия оплаты?
    9. Как долго занимает разработка типового проекта?
    10. Предоставляете ли вы техническую поддержку после запуска?
    """)

with st.expander("🔍 Результаты тестирования текущего чат-бота", expanded=False):
    st.markdown("""    
    ⚠️ **Внимание**: На момент тестирования чат-бот на сайте algoritmai.com не функционирует.
    """)

with st.expander("🚀 Возможные улучшения", expanded=False):
    st.markdown("""
    ### Потенциальные улучшения системы
    
    1. **Расширение базы знаний**
       - Добавление большего количества примеров и кейсов
       - Включение FAQ по частым вопросам
       - Интеграция актуальной информации о проектах
    
    2. **Улучшение контекстного понимания**
       - Внедрение RAG (Retrieval-Augmented Generation)
       - Использование векторной базы данных для хранения знаний
       - Динамическая загрузка релевантной информации
    
    3. **Улучшение обработки запросов**
       - Внедрение Prompt Chaining для сложных сценариев
       - Использование разных промптов для разных типов вопросов
       - Оркестрация последовательности промптов для многошаговых задач
       - Автоматическое определение контекста и выбор соответствующего промпта
    """)

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
        
        # Add collected contacts to knowledge base if any exist
        if st.session_state.collected_contacts:
            contacts_info = "=== Собранные контакты ===\n"
            for i, contact in enumerate(st.session_state.collected_contacts, 1):
                contacts_info += f"Контакт #{i}:\n"
                contacts_info += f"Имя: {contact['name']}\n"
                contacts_info += f"Email: {contact['email']}\n"
                contacts_info += f"Телефон: {contact['phone']}\n"
                contacts_info += f"Компания: {contact['company']}\n"
                contacts_info += f"Сообщение: {contact['message']}\n"
                contacts_info += f"Время: {contact['timestamp']}\n\n"
            knowledge["collected_contacts"] = contacts_info
        
        # Format the system prompt with knowledge
        full_system_prompt = knowledge["system_prompt"].format(
            knowledge_base="\n\n".join([f"=== {k} ===\n{v}" for k, v in knowledge.items() if k != "system_prompt"])
        )
        
        return full_system_prompt
    except Exception as e:
        st.error(f"Ошибка загрузки базы знаний: {str(e)}")
        return None

st.subheader("Чат-бот")

@st.fragment
def render_chatbot():
    chat_container = st.container(border=True, height=300)

    chat_container.markdown("...")

    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Contact form
    if st.session_state.show_contact_form:
        with st.form("contact_form"):
            st.subheader("Оставьте ваши контакты")
            name = st.text_input("Ваше имя")
            email = st.text_input("Email")
            phone = st.text_input("Телефон")
            company = st.text_input("Компания")
            message = st.text_area("Дополнительная информация")
            
            if st.form_submit_button("Отправить"):
                contact_info = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "message": message,
                    "timestamp": str(datetime.now())
                }
                st.session_state.collected_contacts.append(contact_info)
                st.session_state.show_contact_form = False
                
                # Add a system message about the collected contact
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"Пользователь {name} ({email}) из компании {company} оставил контакты. Телефон: {phone}. Сообщение: {message}"
                })
                
                # Add assistant's response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Спасибо за предоставленную информацию! Наш менеджер свяжется с вами в ближайшее время."
                })
                st.rerun()

    # Chat input
    col1, col2, col3 = st.columns([1, 1, 1])  # 3:1:1 ratio for input:selectbox:button
    
    with col1:
        prompt = st.chat_input("Введите ваше сообщение...")
        # If a question is selected and no prompt is entered, use the selected question
        if prompt is None and st.session_state.selected_question != "Выберите пример вопроса...":
            prompt = st.session_state.selected_question
            st.session_state.selected_question = None  # Reset to None after use
            st.session_state.example_questions = None  # Reset the selectbox value
    
    # Add example questions selectbox
    example_questions = [
        "Какие услуги вы предоставляете в области разработки ПО?",
        "Как вы работаете с заказчиками из других стран?",
        "Расскажите о ваших последних проектах",
        "Какие технологии вы используете в разработке?",
        "Как происходит процесс разработки проекта?",
        "Какие гарантии вы предоставляете клиентам?",
        "Как вы обеспечиваете безопасность данных?",
        "Какие у вас условия оплаты?",
        "Как долго занимает разработка типового проекта?",
        "Предоставляете ли вы техническую поддержку после запуска?"
    ]
    
    with col2:
        selected_question = st.selectbox(
            "Примеры вопросов",
            example_questions,
            key="example_questions",
            index=None,
            on_change=lambda: setattr(st.session_state, "selected_question", st.session_state.example_questions),
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("🔄 Перезапустить", use_container_width=True):
            st.session_state.messages = []
            st.session_state.selected_question = "Выберите пример вопроса..."
            st.rerun()

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Increment user message counter
        st.session_state.user_message_count += 1
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        try:
            # Get response from OpenAI
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Думаю..."):
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
                            
                            # Check if the response suggests collecting contacts
                            contact_triggers = [
                                "оставьте ваши контакты",
                                "оставьте контакты",
                                "предоставьте контакты",
                                "свяжемся с вами",
                                "менеджер свяжется",
                                "оставьте заявку"
                            ]
                            
                            # Only show contact form if user has sent at least 3 messages
                            if st.session_state.user_message_count >= 3 and any(trigger in assistant_response.lower() for trigger in contact_triggers):
                                st.session_state.show_contact_form = True
                                st.rerun()
                        else:
                            st.error("Не удалось загрузить базу знаний. Пожалуйста, проверьте файлы конфигурации.")
                
        except Exception as e:
            st.error(f"Произошла ошибка: {str(e)}")
            st.info("Пожалуйста, убедитесь, что вы настроили учетные данные Azure OpenAI в секретах Streamlit")

render_chatbot()

# Display collected contacts
with st.expander("📊 Собранные контакты", expanded=False):
    if st.session_state.collected_contacts:
        for i, contact in enumerate(st.session_state.collected_contacts, 1):
            st.markdown(f"### Контакт #{i}")
            st.markdown(f"**Время:** {contact['timestamp']}")
            st.markdown(f"**Имя:** {contact['name']}")
            st.markdown(f"**Email:** {contact['email']}")
            st.markdown(f"**Телефон:** {contact['phone']}")
            st.markdown(f"**Компания:** {contact['company']}")
            st.markdown(f"**Сообщение:** {contact['message']}")
            st.markdown("---")
    else:
        st.info("Пока нет собранных контактов")

# Display system prompt and knowledge in expanders
# Display chat completion parameters
st.subheader("Основные параметры")
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
        st.text_area("Текущий системный промпт", system_prompt, height=300, label_visibility="hidden")
    except Exception as e:
        st.error(f"Не удалось загрузить системный промпт: {str(e)}")

st.subheader("База знаний")
st.markdown("**База знаний по страницам algorithm.ai:**")
for filename in sorted(os.listdir("knowledge")):
    if filename.endswith(".txt"):
        with st.expander(filename.replace(".txt", ""), expanded=False):
            try:
                content = open(os.path.join("knowledge", filename)).read().strip()
                st.text_area("Содержимое базы знаний", content, height=300)
            except Exception as e:
                st.error(f"Не удалось загрузить содержимое базы знаний: {str(e)}")
