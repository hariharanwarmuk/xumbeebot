import os
import json
from openai import OpenAI
from db_queries import get_case_info, search_knowledge_base_vector, assign_case_to_agent

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

FUNCTIONS = [
    {
        "name": "get_case_info",
        "description": "Get case details by case_id",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "integer"}
            },
            "required": ["case_id"]
        }
    },
    {
        "name": "search_knowledge_base_vector",
        "description": "Search the knowledge base using vector search with fuzzy matching. Use the case summary to generate a troubleshooting query and retrieve relevant solutions.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"}
            },
            "required": ["question"]
        }
    },
    {
        "name": "assign_case_to_agent",
        "description": "Assign a case to a specific agent",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "integer"},
                "agent_id": {"type": "integer"}
            },
            "required": ["case_id", "agent_id"]
        }
    }
]

def refine_final_answer(raw_answer, context=None):
    """
    Refine the raw final answer using the LLM. The context parameter (if provided)
    should include additional details, such as the full conversation history.
    """
    # Build a context string from provided context; if not provided, use an empty string.
    full_context = context if context else ""
    
    prompt = {
        "role": "system",
        "content": (
            "You are an assistant to a customer-service agent. Using the provided conversation history and additional context, "
            "please refine the following answer so that it is clear, concise, and actionable for the agent.\n\n"
            "Raw Answer:\n" + raw_answer + "\n\n"
            "Conversation History and Context:\n" + full_context
        )
    }
    messages = [prompt]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content
def message_to_str(msg):
    """
    Convert a message (dict or ChatCompletionMessage) into a string of the format 'role: content'.
    """
    if isinstance(msg, dict):
        role = msg.get("role", "")
        content = msg.get("content", "")
    else:
        # Assume it's a ChatCompletionMessage with attributes
        role = getattr(msg, "role", "")
        content = getattr(msg, "content", "")
    return f"{role}: {content}"

def call_openai_chat(messages):
    """
    Sends messages to GPT with function calling enabled.
    If GPT returns a function_call, executes it and feeds back the result.
    Once no function call remains, refines the final answer using the full conversation context.
    """
    while True:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            functions=FUNCTIONS,
            function_call="auto"
        )
        assistant_msg = response.choices[0].message

        if assistant_msg.function_call:
            print(f"Function call message \n: {assistant_msg}")
            fn_name = assistant_msg.function_call.name
            args_str = assistant_msg.function_call.arguments
            args = json.loads(args_str)

            if fn_name == "get_case_info":
                data = get_case_info(**args)
                tool_result = data if data else {"error": "No case found."}
            elif fn_name == "search_knowledge_base_vector":
                data = search_knowledge_base_vector(**args)
                tool_result = data if data else {"error": "No relevant knowledge found."}
            elif fn_name == "assign_case_to_agent":
                assign_case_to_agent(**args)
                tool_result = {"result": "Case assigned successfully."}
            else:
                tool_result = {"error": f"Unknown function {fn_name}"}

            messages.append(assistant_msg)
            messages.append({
                "role": "function",
                "name": fn_name,
                "content": json.dumps(tool_result)
            })
            print("Accumulated messages after function call:", messages)
        else:
            # Build full conversation context from all messages
            context_text = "\n".join([message_to_str(msg) for msg in messages if message_to_str(msg)])
            print(f"Context passed to refinement:\n{context_text}")
            refined = refine_final_answer(assistant_msg.content, context=context_text)
            print(f"Final refined answer \n: {refined}")
            return refined
