# Identify and summarize the key conversational preferences of the student based on the conversation above. Focus on high-level patterns, reasoning styles, and any notable preferences in how they approach learning, such as their tendency to explain their thought process, ask specific questions, or seek clarification. Do not include specific conversation details; instead, describe the student’s learning approach, areas of focus, and preferences for receiving explanations or corrections.

# Use concise sentences, objective language, and avoid assumptions about the student’s motivations. If no preference is clear, note "No preference observed."

# PROMPTS mainly generated by ChatGPT GPT-4o Nov 2024

conv_pref_prompt = """Analyze the student’s conversational style based on the interaction above. Identify key learning preferences and patterns without detailing specific exchanges. Focus on their reasoning style, approach to problem-solving, and preferences in receiving explanations or corrections, such as seeking step-by-step guidance, clarifications, or practical examples. Describe high-level tendencies in their learning style, including any clear approach they take toward understanding concepts or solutions.

**Guidelines:**
- Use concise, objective language.
- Note the student’s primary reasoning style, e.g., hands-on, conceptual, detail-oriented, etc.
- Note the student's goals, such as understanding foundational concepts, passing an exam, getting top marks, code implementation, or hands-on practice.
- Note any specific preferences in how they learn, such as asking detailed questions, seeking practical examples, requesting quizes, or requesting clarifications.
- Avoid assumptions about motivation; observe only patterns evident in the conversation.
- If no particular preference is detectable, state "No preference observed."

Examples:

Example 1:
**Conversation:**
Student: "I understand that the derivative gives us the slope of a function, but what if we want to know the rate of change over an interval? Do we still use the derivative?"
AI: "Good question! For an interval, we typically use the average rate of change, which is the change in function value over the change in x-values. The derivative gives the instantaneous rate of change at a specific point."

**Expected Answer:**
The student prefers in-depth conceptual understanding and asks thoughtful questions that differentiate between similar concepts. They seem comfortable discussing foundational ideas in calculus.

Example 2:
**Conversation:**
Student: "I’m trying to solve this physics problem: if I throw a ball upwards at 10 m/s, how long will it take to reach the top? I thought I could just divide by gravity, but I’m not sure."
AI: "You're on the right track! Since acceleration due to gravity is 9.8 m/s², you can divide the initial velocity by gravity to find the time to reach the peak, which would be around 1.02 seconds."

**Expected Answer:**
The student prefers practical problem-solving and is open to corrections. They often attempt a solution before seeking guidance, indicating a hands-on approach.

Example 3:
**Conversation:**
Student: "Can you explain the difference between meiosis and mitosis? I know both involve cell division, but I’m confused about how they differ."
AI: "Certainly! Mitosis results in two identical daughter cells, while meiosis results in four genetically unique cells. Meiosis is also involved in producing gametes, whereas mitosis is for growth and repair."

**Expected Answer:**
The student prefers clear, comparative explanations when learning complex biological processes. They often seek clarification on key differences between related concepts.

Example 4:
**Conversation:**
Student: "I wrote this Python code to reverse a string, but it’s not working. Here’s what I tried: `for char in string: new_string = char + new_string`."
AI: "You’re close! Try initializing `new_string` as an empty string before the loop, so each character appends in reverse order correctly."

**Expected Answer:**
The student prefers hands-on guidance with code, often sharing specific code snippets. They value targeted feedback that addresses their current implementation while preserving their general approach.

"""

update_conv_pref_prompt = """Based on the interaction above, analyse the student’s conversational style. Identify any shifts in their reasoning patterns, problem-solving approaches, or preferences for receiving explanations or corrections. Highlight any new tendencies or changes in their learning style that have emerged in contrast to the previous conversational style. If no significant changes are observed, repeat the previous conversational preferences without any alterations. 

**Guidelines:**
- Use concise, objective language.
- Note the student’s primary reasoning style, e.g., hands-on, conceptual, detail-oriented, etc.
- Note the student's goals, such as understanding foundational concepts, passing an exam, getting top marks, code implementation, hands-on practice, etc.
- Note any specific preferences in how they learn, such as asking detailed questions, seeking practical examples, requesting quizes, requesting clarifications, etc.
- Avoid assumptions about motivation; observe only patterns evident in the conversation.
- If no particular preference is detectable, state "No preference observed."

"""

summary_prompt = """
You are an AI assistant specializing in concise and accurate summarization. Your task is to summarize the previous conversation, capturing the main topics, key points, user questions, and your responses in a clear and organized format. Ensure the summary is:

Concise: Keep the summary brief while including all essential information.
Structured: Organize the summary into sections such as 'Topics Discussed,' 'Key Questions and Responses,' and 'Follow-Up Suggestions' if applicable.
Neutral and Accurate: Avoid adding interpretations or opinions; focus only on the content shared.
When summarizing:

If the conversation is technical, highlight significant concepts, solutions, and terminology.
If context involves problem-solving, detail the problem and the steps or solutions provided.
If the user asks for creative input, briefly describe the ideas presented.
Provide the summary in a bulleted format for clarity. Avoid redundant details while preserving the core intent of the discussion.
"""