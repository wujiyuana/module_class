from langchain.chains.conversation.base import ConversationChain
from langchain.chains.question_answering.map_reduce_prompt import system_template
#from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_models import ChatTongyi
from langchain.memory import ConversationBufferMemory
import streamlit as st


#memory = ConversationBufferMemory(return_messages=True)

# 心理咨询聊天机器人
system_template_text="""
你是一个从世界顶级学校的心理专业毕业的博士生，你已经掌握了很多基本的心理专业相关知识，并且在多家心理咨询所实习过，
现在你需要用十分温柔耐心，且带一点点幽默的语言，和一些有心理问题或者有一些心理困扰的人进行聊天沟通，来帮助他解决
他的心理问题，走出难关，除了聊天之外，你有时也可以为他提出一些解决他的问题的建议。希望你能够顺利为他们解决他们的
心理问题,但同时也希望你的安慰能够更多一些，而非仅仅只是提建议，一定要对找你沟通聊天的用户保持充足的耐心和温柔哦！
"""



# 输入
AI_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_template_text),
        MessagesPlaceholder(variable_name="history"),
        ("human","{input}"),
    ]
)

#范围回答，同时一定程度上有容错，避免api输入错误报错或者内容为空报错
def get_chat_response(user_input_text, memory1, api_key):
    if not api_key.strip():
        return False
    try:
        print("尝试初始化 ChatTongyi...")
        model = ChatTongyi(
            model="qwen-max",
            top_p=1.0,
            temperature=1.0,
            api_key=api_key,
        )
        print("ChatTongyi 初始化成功")
    except Exception as e:
        print(f"ChatTongyi 初始化失败: {e}")
        return False
    try:
        print("调用 ChatTongyi 模型...")
        # result = tongyi_chat.invoke(prompt_value)
        # response = user_output_parser.invoke(result)
        chain = ConversationChain(llm=model,memory=memory1,prompt=AI_prompt)
        result = chain.invoke(input=user_input_text,history=AI_history)#插入到prompt
        print(f"模型返回结果: {result}")
        return result["response"]
    except Exception as e:
        print(f"模型调用失败: {e}")
        #st.write(f"模型调用失败: {e},请修改对应错误后重新尝试")
        return False


# streamlit 界面设计
st.set_page_config(
    page_title="小鸢的心理咨询聊天",  # 标签页的名称
    page_icon="🌟"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"🚀
)
#添加一个标题
st.title('🕊️小鸢心理咨询师')

#添加水平分割线
st.divider()

with st.sidebar:
    st.write("用户管理")
    user_api = st.text_input("请输入你的api_key",type="password")


if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    st.session_state.messages = [{"role":"assistant","content":"你好，我是心理咨询师小鸢，很高兴能够和你聊天！"}]

AI_history =  st.session_state.memory.load_memory_variables({})["history"]

# 显示所有会话的历史记录
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

#内容赋值给prompt
if prompt :=st.chat_input("请输入您的内容"):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role":"user","content":prompt})
    response = get_chat_response(user_input_text=prompt,memory1= st.session_state.memory,api_key=user_api)
    with st.chat_message("assistant"):
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role":"assistant","content":response})
        else:
            st.markdown("请你重新确认api_key正确后再和我聊天哦！")
            st.session_state.messages.append({"role": "assistant", "content":"请你重新确认api_key正确后再和我聊天哦！" })


