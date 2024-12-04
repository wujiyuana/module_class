"""
csv智能分析助手
"""
#from langchain.memory import ConversationBufferMemory
import json
import pandas as pd
import streamlit as st
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_experimental.tools import PythonREPLTool
import matplotlib.pyplot as plt

PROMPT_TEMPLATE = """
你是一个精通CSV文件进行数据分析的数据分析师，你需要帮助用户对其上传的csv文件进行分析，
根据用户所提的问题进行回答，回答的格式取决于请求内容,请严格按照csv文件内容进行分析，不要捏造数据
情况1：用户的问题是普通文本问题
回答的json格式为：
{
"answer":"<你的答案写在这里>"
}
情况2：用户需要对数据筛选后用表格显示
回答的json格式为：
{
    "table": {
    "columns": ["column1", "column3",...], 
    "data": [[value1, value2, ...], [value1, value2, ...], ...]
    }
}
情况3：用户需要用柱状图展示数据分布
回答的json格式为：
{ 
    "bar": { 
    "Category": ["A", "B", "C", "D"], 
    "Values": [401, 133, 10, 1]
    }
}
输出格式为符合以上结构的JSON格式，即{<对应内容>}，一定不要输出```json```，同时不添加其它内容
你要处理的用户请求如下：
"""
#很奇妙，少了“即{<对应内容>}”这个之后生成柱状图会出现一点问题
# 回答，同时
def csv_agent(df,query):
    model = ChatTongyi(model="qwen-max",temperature=0)
    agent_executor = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        allow_dangerous_code=True,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors":True}
    )
    prompt = PROMPT_TEMPLATE+query
    response =  agent_executor.invoke({"input":prompt})
    print(response)
    response_dict = json.loads(response['output'])
    return response_dict

st.set_page_config(
    page_title="小鸢的数据分析助手",  # 标签页的名称
    page_icon="🚀"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"🚀
)
#添加一个标题
st.title('🌟CSV分析小助手')

#添加水平分割线
st.divider()

data = st.file_uploader("上传你的数据文件（CSV格式）:",type="csv")

if data:
    st.session_state["df"] = pd.read_csv(data)
    print(st.session_state["df"])
    with st.expander("点击查看数据"):
        st.dataframe(st.session_state["df"])
    query_user = st.text_input("请输入您的需求")
    if st.button("发送"):
        if query_user:
            response_dict_bot = csv_agent(st.session_state["df"],query_user)
            print(response_dict_bot)
            if 'answer' in response_dict_bot:
                st.write(response_dict_bot['answer'])
            elif 'table' in response_dict_bot:
                df1 = pd.DataFrame(response_dict_bot['table']['data'], columns=response_dict_bot['table']['columns'])
                st.dataframe(df1)
            elif 'bar' in response_dict_bot:
                df1 = pd.DataFrame(response_dict_bot['bar'])
                st.bar_chart(df1.set_index('Category')['Values'])
        else:
            st.write("请输入内容后提交")
#用来debug测试的代码
# df = pd.read_csv("iris.csv")
# #query1="将前10个鸢尾花挑选出来并且显示到表格中"
# #query1 = "鸢尾花有几类"
# query1 = "统计三个种类鸢尾花的数量并且用柱状图显示"
# a = csv_agent(df,query1)
# print(type(a))
# print(a)
# if 'bar' in a:
#     print('bar 是键')
#     print(a['bar'])
#     print(type(a['bar']))
#     df1 = pd.DataFrame(a['bar'])
#     plt.bar(df1["Category"],df1["Values"])
# if 'answer' in a:
#     print('answer 是键')
#     print(a['answer'])
#     print(type(a['answer']))




