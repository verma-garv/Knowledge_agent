import streamlit as st
from langchain.messages import AIMessage, HumanMessage

from agent import agent, provider
from ui_helpers import describe_steps

MAX_HISTORY = 6

st.title("Notes assistant")
st.caption(f"Model provider: {provider}")

if "history" not in st.session_state:
    st.session_state.history  = [] #alternating HumanMessage / AIMessage

for m in st.session_state.history:
    role = "user" if isinstance(m, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(m.content)

question = st.chat_input("Ask about your notes, or about the web")
if question:
    with st.chat_message("user"):
        st.write(question)
    messages =  st.session_state.history[-MAX_HISTORY:] + [HumanMessage(content=question)]

    with st.chat_message("assistant"):
        with st.spinner("Thinking.."):
            result = agent.invoke(
                {"messages": messages},
                config={"recursion_limit": 10},
            )
        answer = result["messages"][-1].content

        if answer.startswith("[error]"):
            st.error(answer)
        else:
            st.write(answer)
            st.session_state.history.append(HumanMessage(content=question))
            st.session_state.history.append(AIMessage(content=answer))
        steps = describe_steps(result["messages"][len(messages):])
        if steps:
            with st.expander("show search steps"):
                for line in steps:
                    st.text(line)
