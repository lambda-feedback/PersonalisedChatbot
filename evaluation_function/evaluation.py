from typing import Any
from langchain_core.messages import SystemMessage, RemoveMessage, HumanMessage, AIMessage
try:
    from .agents.chatbot_summarised_memory_agent import ChatbotAgent
    from .agents.profiling_agent import ProfilingAgent
    from .evaluation_response import Result, Params
except ImportError:
    from evaluation_function.agents.chatbot_summarised_memory_agent import ChatbotAgent
    from evaluation_function.agents.profiling_agent import ProfilingAgent
    from evaluation_function.evaluation_response import Result, Params
import time
import uuid

chatbot_agent = ChatbotAgent(len_memory=4)
profiling_agent = ProfilingAgent()

def evaluation_function(response: Any, answer: Any, params: Params) -> Result:
    """
    Function used to evaluate a student response.
    ---
    The handler function passes three arguments to evaluation_function():

    - `response` which are the answers provided by the student.
    - `answer` which are the correct answers to compare against.
    - `params` which are any extra parameters that may be useful,
        e.g., error tolerances.

    The output of this function is what is returned as the API response
    and therefore must be JSON-encodable. It must also conform to the
    response schema.

    Any standard python library may be used, as well as any package
    available on pip (provided it is added to requirements.txt).

    The way you wish to structure you code (all in this function, or
    split into many) is entirely up to you. All that matters are the
    return types and that evaluation_function() is the main function used
    to output the evaluation response.
    """

    result = Result(is_correct=True)
    include_test_data = False

    if "include_test_data" in params:
        include_test_data = params["include_test_data"]
    start_time = time.process_time()

    chatbot_response = invoke_simple_agent_with_retry(response, session_id=uuid.uuid4()) # TODO: to be replaced by Session ID set by web client
    # ########### TESTING
    # chatbot_response = {
    #     "input": response,
    #     "output": "I am a chatbot. I can help you with your queries.",
    #     "intermediate_steps": ["Number of messages sent: 0", "Number of remembered messages:0", "Number of total messages in the conversation: 0"]
    # }
    # ########### TESTING
    end_time = time.process_time()

    result._processing_time = end_time - start_time
    result.add_feedback("chatbot_response", chatbot_response["output"])
    result.add_metadata("summary", chatbot_response["intermediate_steps"])
    result.add_processing_time(end_time - start_time)

    return result.to_dict(include_test_data=include_test_data)

def invoke_simple_agent_with_retry(query: str, session_id: str):
    """Retry the simple agent if a tool fails to run.
    This can help when there are intermittent connection issues to external APIs.
    """
    print(f'in invoke_simple_agent_with_retry(), query = {query}, thread_id = {session_id}')
    config = {"configurable": {"thread_id": session_id}}
    response_events = chatbot_agent.app.invoke({"messages": [HumanMessage(content=query)]}, config=config, stream_mode="values") #updates
    # print(f'in invoke_simple_agent_with_retry(), response = {response_events}')
    pretty_printed_response = chatbot_agent.pretty_response_value(response_events) # for last event in the response
    # print(f'in invoke_simple_agent_with_retry(), pretty_printed_response = {pretty_printed_response}')

    summary = chatbot_agent.get_summary(config)
    nr_messages = len(chatbot_agent.app.get_state(config).values["messages"])
    nr_valid_messages = len([m for m in chatbot_agent.app.get_state(config).values["messages"] if m.type != "remove"])
    if "system" in chatbot_agent.app.get_state(config).values["messages"][-1].type:
        nr_valid_messages -= 1
    nr_human_messages = len([m for m in chatbot_agent.app.get_state(config).values["messages"] if m.type == "human"])
    # NOTE: intermediate_steps is expected to be a list
    intermediate_steps = ["Number of messages sent: "+ str(nr_human_messages), "Number of remembered messages:"+str(nr_valid_messages), "Number of total messages in the conversation: "+ str(nr_messages)]
    if summary:
        intermediate_steps.append("Summary: "+ str(summary))
    
    return {
        "input": query,
        "output": pretty_printed_response,
        "intermediate_steps": intermediate_steps
    }

def invoke_profiling_agent_with_retry(session_id: str):
    """Retry the profiling agent if a tool fails to run.
    This can help when there are intermittent connection issues to external APIs.
    """
    print(f'in invoke_profiling_agent_with_retry(), session_id = {session_id}')
    config = {"configurable": {"thread_id": session_id}}
    response_events = profiling_agent.app.invoke({"messages": []}, config=config, stream_mode="values") #updates

    pretty_printed_response = profiling_agent.pretty_response_value(response_events) # for last event in the response

    return {
        "input": "History of the conversation",
        "output": pretty_printed_response,
        "intermediate_steps": []
    }

# if __name__ == "__main__":
#     responses = [
#         "Hi, in one sentence tell me about London.",
#         "What can a tourist do there? Give me a list of activities in one sentence.",
#         "I am new to travelling and am concerned about my visit. Give me the top 5 things I should pack for the trip.",
#         "I am a foodie. What are the top 5 restaurants in London?",
#         "Give me a brief summary of what we have discussed so far. I want to remember the key points.",
#         "I do not understand you point, can you explain it in a different way?",
#     ]
#     for response in responses:
#         llm_response = evaluation_function(response, "", {"include_test_data": True})
#         print("AI: "+llm_response["feedback"])
#         print("Summary: ")
#         print(llm_response["metadata"]["summary"])
#         print("Processing time: " + str(llm_response["processing_time"]))
#         print("--------------------")