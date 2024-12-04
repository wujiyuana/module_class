"""
pdf智能分析助手
"""
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatTongyi
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import streamlit as st


def get_chat_response(memory,uploaded_file,question):
    file_contents = uploaded_file.read()
    temp_file_path = "temp.pdf"
    with open(temp_file_path,"wb") as temp_file:
        temp_file.write(file_contents)
    loader = PyPDFLoader(temp_file_path)
    documents = loader.load()

    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""]
    )
    texts = text_splitter.split_documents(documents)

    # 初始化嵌入模型
    embeddings_model = DashScopeEmbeddings(model="text-embedding-v1", )

    # 创建向量数据库
    db = FAISS.from_documents(texts, embeddings_model)

    # 创建检索器
    retriever = db.as_retriever()

    # 初始化语言模型
    tongyi_model = ChatTongyi(model="qwen-plus")

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=tongyi_model,
        retriever=retriever,
        memory=memory
    )
    response = qa_chain.invoke({"chat_history":memory,"question":question})
    return response['answer']
st.set_page_config(
    page_title="小鸢的数据分析助手",  # 标签页的名称
    page_icon="🚀"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"🚀
)
#添加一个标题
st.title('🌟pdf智能小助手')
if "memory" not in st.session_state:
    st.session_state["memory"]=ConversationBufferMemory(
        return_messages=True, memory_key='chat_history', output_key='answer'
    )
pdf = st.file_uploader("请上传.pdf文件",type="pdf")
query = st.text_input("请输入您的问题")
if st.button("发送"):
    response1 = get_chat_response(st.session_state["memory"],pdf,query)
    st.write(response1)

# 用户输入
# query = "杂诗十二首的作者是谁？"

# # 生成响应
# response = qa_chain.invoke({"chat_history": memory, "question": query})
# print(f"Response: {response['answer']}")
#
# # 用户继续提问
# follow_up_query = "其中和岁月相关的诗句有哪些？"
# follow_up_response = qa_chain.invoke({"chat_history": memory, "question": follow_up_query})
# print(f"Follow-up Response: {follow_up_response['answer']}")
