try:
    from .llm_factory import OpenAILLMs
except ImportError:
    from evaluation_function.agents.llm_factory import OpenAILLMs
from langchain_core.messages import SystemMessage, RemoveMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END

from typing import Literal

# follow: 
# https://langchain-ai.github.io/langgraph/how-tos/memory/add-summary-conversation-history/
# https://langchain-ai.github.io/langgraph/how-tos/memory/delete-messages/

# We will add a `summary` attribute (in addition to `messages` key,
# which MessagesState already has)
class State(MessagesState):
    summary: str

class ChatbotAgent:
    def __init__(self, len_memory=10):
        chat_llm = OpenAILLMs()
        self.chat_llm = chat_llm.get_llm()
        summarisation_llm = OpenAILLMs()
        self.summarisation_llm = summarisation_llm.get_llm()
        self.memory = MemorySaver()
        self.len_memory = len_memory

        # Define a new graph for the conversation
        self.workflow = StateGraph(State)
        self.workflow_definition()
        # Finally, we compile it!
        self.app = self.workflow.compile(checkpointer=self.memory)


    def call_model(self, state: State) -> str:
        summary = state.get("summary", "")
        if summary:
            system_message = f"Summary of conversation earlier: {summary}"
            messages = [SystemMessage(content=system_message)] + state['messages']
        else:
            messages = state["messages"]

        valid_messages = self.check_for_valid_messages(messages)
        response = self.chat_llm.invoke(valid_messages)

        # We return a list, because this will get added to the existing list
        return {"messages": [response]}
    
    # We now define the logic for determining whether to end or summarize the conversation
    def should_continue(self, state: State) -> Literal["summarize_conversation", END]:
        """Return the next node to execute."""
        messages = state["messages"]
        valid_messages = self.check_for_valid_messages(messages)
        nr_messages = len(valid_messages)
        if "system" in valid_messages[-1].type:
            nr_messages -= 1
        # If there are more than X messages, then we summarize the conversation
        if nr_messages > self.len_memory:
            return "summarize_conversation"
        # Otherwise we can just end
        return END
    
    def summarize_conversation(self, state: State):
        # First, we summarize the conversation
        summary = state.get("summary", "")
        if summary:
            # If a summary already exists, we use a different system prompt
            # to summarize it than if one didn't
            summary_message = (
                f"This is summary of the conversation to date: {summary}\n\n"
                "Update the summary by taking into account the new messages above:"
            )
        else:
            # summary_message = "Create a summary of the conversation above:"
            summary_message = "Identify the key conversational preferences of the human user in the conversation above. Do not to focus on the details of the conversation:"

        messages = state["messages"] + [SystemMessage(content=summary_message)] # instead of HumanMessage
        valid_messages = self.check_for_valid_messages(messages)
        response = self.summarisation_llm.invoke(valid_messages)

        # We now need to delete messages that we no longer want to show up
        # I will delete all but the last two messages, but you can change this
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        return {"summary": response.content, "messages": delete_messages}
    
    def check_for_valid_messages(self, messages):
        # Removing the RemoveMessage() from the list of messages
        valid_messages = []
        for message in messages:
            if message.type != 'remove':
                valid_messages.append(message)
        return valid_messages
    
    def get_summary(self, config):
        return self.app.get_state(config).values['summary'] if 'summary' in self.app.get_state(config).values else [] 

    def workflow_definition(self):
        # Define the conversation node and the summarize node
        self.workflow.add_node("conversation", self.call_model)
        self.workflow.add_node(self.summarize_conversation)
        # Set the entrypoint as conversation
        self.workflow.add_edge(START, "conversation")

        # We now add a conditional edge
        self.workflow.add_conditional_edges(
            # First, we define the start node. We use `conversation`.
            # This means these are the edges taken after the `conversation` node is called.
            "conversation",
            # Next, we pass in the function that will determine which node is called next.
            self.should_continue,
        )

        # We now add a normal edge from `summarize_conversation` to END.
        # This means that after `summarize_conversation` is called, we end.
        self.workflow.add_edge("summarize_conversation", END)

    def print_update(self, update):
        for k, v in update.items():
            for m in v["messages"]:
                m.pretty_print()
            if "summary" in v:
                print(v["summary"])

    def pretty_response_value(self, event):
        # print(event["messages"][-1])
        return event["messages"][-1].content


if __name__ == "__main__":
    # TESTING
    chatbot_agent = ChatbotAgent()
    from IPython.display import Image, display

    try:
        display(Image(chatbot_agent.app.get_graph().draw_mermaid_png()))
    except Exception:
        # This requires some extra dependencies and is optional
        print("Could not display the graph.")
        pass

    config = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "q"]:
            print("Goodbye!")
            break

        events = chatbot_agent.app.stream(
            {"messages": [("user", user_input)]}, config, stream_mode="updates"
        )
        updates= chatbot_agent.app.get_state(config).values["messages"]
        print(f"DEBUGGING: {updates}")
        print(f"DEBUGGING: {chatbot_agent.get_summary(config)}")
        for event in events:
            chatbot_agent.print_update(event)
            # event["messages"][-1].pretty_print()

    # config = {"configurable": {"thread_id": "4"}}
    # input_message = HumanMessage(content="hi! I'm bob")
    # input_message.pretty_print()
    # for event in chatbot_agent.app.stream({"messages": [input_message]}, config, stream_mode="values"):
    #     print(f"Event: {event}")
    #     chatbot_agent.pretty_response_value(event)
    #     # chatbot_agent.print_update(event)

    # input_message = HumanMessage(content="what's my name?")
    # input_message.pretty_print()
    # for event in chatbot_agent.app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    #     chatbot_agent.print_update(event)

    # input_message = HumanMessage(content="i like the celtics!")
    # input_message.pretty_print()
    # for event in chatbot_agent.app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    #     chatbot_agent.print_update(event)

    # values = chatbot_agent.app.get_state(config).values
    # print(f"Final state: {values}")