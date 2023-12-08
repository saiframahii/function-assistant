from openai import OpenAI
import time
import yfinance as yf
import json
import streamlit as st


def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price


class AssistantManager:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.assistant = None
        self.thread = None
        self.run = None

    # def create_assistant(self, name, instructions, tools):
    #     self.assistant = self.client.beta.assistants.create(
    #         name=name,
    #         instructions=instructions,
    #         tools=tools,
    #         model=self.model
    #     )
    
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
                break
            elif run_status.status == 'requires_action':
                print("Function Calling ...")
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

        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name == "get_stock_price":
                output = get_stock_price(symbol=arguments['symbol'])
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
    api_key = "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"
    assistant_id = "asst_Y2RNxPUzSI7thEwCOH4kOVAL"
    manager = AssistantManager(api_key)

    # step 1: retrieve assistant
    manager.retrieve_assistant(assistant_id)

    # step 2: create a thread
    manager.create_thread()

    # Streamlit UI
    st.set_page_config(
    page_title="Stock GPT",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
    )

    st.markdown("<h1 style='text-align: center;'>Stock GPT 📈</h1>", unsafe_allow_html=True)
    # st.title("Stock GPT 📈")

    # Sidebar for additional controls or information
    with st.sidebar:
        st.info("Get real-time stock prices.")
        st.markdown("""
            ### Instructions
            - Enter the name or ticker symbol of a stock.
            - The assistant will provide the latest stock price.
            - View the conversation in the chat window.
        """)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Enter stock name ..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        manager.add_message_to_thread(role="user", content=prompt)
        manager.run_assistant()
        response = manager.wait_for_completion()

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})




if __name__ == '__main__':
    main()