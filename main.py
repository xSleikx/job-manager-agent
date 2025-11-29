import os
import logging
from dotenv import load_dotenv

# Azure imports
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole

# Custom functions
from job_functions import user_functions

def setup_agent():
    # Load environment variables
    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    if not project_endpoint or not model_deployment:
        raise ValueError("Missing PROJECT_ENDPOINT or MODEL_DEPLOYMENT_NAME in .env file.")

    # Connect to Azure AgentsClient
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
    )

    # Define tools
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    agent_client.enable_auto_function_calls(toolset)

    # Create agent
    agent = agent_client.create_agent(
        model=model_deployment,
        name=" Job Manager",
        instructions="""You are proffesional Job Manager agent, which helps the user the mange his job applications.
                        You extract job info from pasted text. If the user provides a url extract job info with scrape_job_page function. 
                        First make a small summary of the Job, so you can add it to JSON later.
                        You also manage job applications. You can create, list, update job records using the local JSON functions.
                        You can also delete jobs by id or job_role, if the user wants to.

                        Important:
                        Save the job application direct to the .json without asking the user!
                        If the user provides the same job, notice him that the job is already saved and if he wants to add somthing new.""",
        toolset=toolset
    )

    # Create thread
    thread = agent_client.threads.create()
    print(f"Connected! You're chatting with: {agent.name} ({agent.id})")
    return agent_client, agent, thread

# Show conversation between agent and user for thread
def show_history(agent_client, thread):
    messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    print("\n--- Conversation History ---")
    for message in messages:
        if message.text_messages:
            role = message.role.capitalize()
            text = message.text_messages[-1].text.value
            print(f"{role}: {text}")
    print("--- End of History ---\n")

# Interactive loop to continuously accept user input and process requests through the agent
def chat_loop(agent_client, agent, thread):
    """Main chat loop for user interaction."""
    print("\nWelcome to the Job Support Agent!")
    print("Type your question or paste job details.")
    print("Commands: 'quit' to exit | 'history' to view conversation\n")

    while True:
        user_prompt = input("\nYou: ")
        if user_prompt.lower() == "quit":
            print("Goodbye!")
            break
        if user_prompt.lower() == "history":
            show_history(agent_client, thread)
            continue
        if not user_prompt.strip():
            print("Please enter a valid prompt.")
            continue

        print("Agent is processing your request...")
        message = agent_client.messages.create(thread_id=thread.id, role="user", content=user_prompt)
        run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            continue

        last_msg = agent_client.messages.get_last_message_text_by_role(thread_id=thread.id, role=MessageRole.AGENT)
        if last_msg:
            print(f"Agent: {last_msg.text.value}")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        agent_client, agent, thread = setup_agent()
        chat_loop(agent_client, agent, thread)
    finally:
        # Cleanup
        agent_client.delete_agent(agent.id)
        print("Deleted agent and closed session.")


if __name__ == '__main__':
    main()
