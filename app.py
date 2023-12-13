from openai import OpenAI
import time
import yfinance as yf
import json
import streamlit as st
import requests


def general_company_research(company_url, relevance_api_key):
    """
    Do general research on a company based on its website URL.

    Parameters:
    company_url (str): The URL of the company's website.
    api_key (str): API key for authentication.

    Returns:
    dict: The response data from the server.
    """
    # API endpoint URL
    api_url = "https://api-d7b62b.stack.tryrelevance.com/latest/studios/86c5000b-cac3-4f83-af04-fcb2eb1c6dd7/trigger_llm_friendly"

    # Headers for authentication
    headers = {
        "Authorization": relevance_api_key
    }

    # Request body
    body = {
        "company_url": company_url
    }

    # Make the POST request with headers and JSON body
    response = requests.post(api_url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response = response.json()
        response = response['output']['company_research_summary']
        return response
    else:
        return {"error": "Request failed", "status_code": response.status_code}

def find_person_in_company_by_role(company_name, role, relevance_api_key):
    """
    Find the name and LinkedIn profile of a person within a company by role.

    Parameters:
    company_name (str): The name of the company.
    role (str): The specific role to find in the company.
    relevance_api_key (str): API key for authentication.

    Returns:
    dict: The response data from the server.
    """
    # API endpoint URL
    api_url = "https://api-d7b62b.stack.tryrelevance.com/latest/studios/0af04d63-9df8-41c8-ad28-3e7091cf7af7/trigger_llm_friendly"

    # Headers for authentication
    headers = {
        "Authorization": relevance_api_key
    }

    # Request body
    body = {
        "company_name": company_name,
        "role": role
    }

    # Make the POST request with headers and JSON body
    response = requests.post(api_url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        output = response_data.get('output', {})

        # Extract name and LinkedIn URL and format them into a string
        name = output.get('name', 'Name not found')
        linkedin_url = output.get('linkedin', 'LinkedIn profile not found')

        return f"Name: {name}, LinkedIn Profile: {linkedin_url}"
    else:
        return {"error": "Request failed", "status_code": response.status_code}

def personalise_linkedin_connection_request(first_name, linkedin_url, product_context, my_company, relevance_api_key):
    """
    Personalize LinkedIn Connection Request based on user posts.

    Parameters:
    first_name (str): The first name of your prospect.
    linkedin_url (str): LinkedIn URL of your prospect.
    product_context (str): More context equals better tailored connection requests.
    my_company (str): The name of your company, whose products and services you're looking to sell.
    relevance_api_key (str): API key for authentication.

    Returns:
    dict: The response data from the server.
    """
    # API endpoint URL
    api_url = "https://api-d7b62b.stack.tryrelevance.com/latest/studios/26787101-7a5a-4fcf-becf-656217ee0471/trigger_llm_friendly"

    # Headers for authentication
    headers = {
        "Authorization": relevance_api_key
    }

    # Request body
    body = {
        "first_name": first_name,
        "linkedin_url": linkedin_url,
        "product_context": product_context,
        "my_company": my_company
    }

    print(f"this is the passed body: {body}")
    # Make the POST request with headers and JSON body
    response = requests.post(api_url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response = response.json()
        output = response['output']['personalised_opening_line']
        return f"Personalised Message: {output}"
    else:
        return {"error": "Request failed", "status_code": response.status_code}


class AssistantManager:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.assistant = None
        self.thread = None
        self.run = None

    def retrieve_assistant(self, assistant_id):
        self.assistant = self.client.beta.assistants.retrieve(assistant_id)

    def create_thread(self):
        self.thread = self.client.beta.threads.create()

    def add_message_to_thread(self, role, content):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=content
        )

    def run_assistant(self):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id= self.assistant.id
        )

    def wait_for_completion(self):
        while True:
            time.sleep(1)
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=self.run.id
            )
            # print(run_status.model_dump_json(indent=4))

            if run_status.status == 'completed':
                return self.process_messages()
                # break
            elif run_status.status == 'requires_action':
                print("Function Calling ...")
                print(run_status)
                self.call_required_functions(run_status.required_action.submit_tool_outputs.model_dump())
            else:
                print("Waiting for the Assistant to process...")

    def process_messages(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

        for msg in messages.data:
        # Check if the message is from the assistant
            if msg.role == "assistant":
                content = msg.content[0].text.value
                print(f"Assistant: {content}")
        return content

    def call_required_functions(self, required_actions):
        tool_outputs = []

        print(required_actions)

        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])
            print(arguments)

            if func_name == "general_company_research":
                output = general_company_research(company_url=arguments['company_url'], 
                                                  relevance_api_key="c716cd9c875d-4599-82d1-cf9e8f9fa22c:sk-NTY4ODVlOWUtNTRmMC00ZTk1LWI4YTgtYmU0ZjRhYjFjODdl")
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })
            elif func_name == "find_person_in_company_by_role":
                output = find_person_in_company_by_role(company_name=arguments['company_name'], 
                                                        role=arguments['role'], 
                                                        relevance_api_key="c716cd9c875d-4599-82d1-cf9e8f9fa22c:sk-MmYyMzkyZDQtYmM3Yy00NDY1LTk4OTctYzhjYmI2MDM1OTI4")
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })
            elif func_name == "personalise_linkedin_connection_request":
                output = personalise_linkedin_connection_request(first_name=arguments['first_name'], 
                                                                 linkedin_url=arguments['linkedin_url'],
                                                                 product_context="AI SalesMate, an innovative outbound sales copilot designed to enhance customer engagement and streamline sales processes.",
                                                                 my_company="NovaTech Solutions",
                                                                 relevance_api_key="c716cd9c875d-4599-82d1-cf9e8f9fa22c:sk-OTMxNTY4YzktMzQwNi00MmE0LTljYzEtYTBkYTYyNGM1YmJm")
                print(output)
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )


def main():
    api_key = st.secrets["OPENAI_API_KEY"]
    assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]
    manager = AssistantManager(api_key)

    # step 1: retrieve assistant
    manager.retrieve_assistant(assistant_id)

    # step 2: create a thread
    manager.create_thread()

    # Streamlit UI
    st.set_page_config(
    page_title="Outbound Sales Co-Pilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
    )

    st.markdown("<h1 style='text-align: center;'>Outbound Sales Co-Pilot 🚀</h1>", unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Message Outbound Sales Co-Pilot 💬"):

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create a combined prompt from chat history
        combined_prompt = str([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-20:]])
        # print(combined_prompt)

        manager.add_message_to_thread(role="user", content=combined_prompt)

         
        # Show spinner while processing the response
        with st.spinner("Generating response..."):
            manager.run_assistant()
            response = manager.wait_for_completion()

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
                    # st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    main()