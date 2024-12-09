"""
final_experience:图标绘制助手
"""
import matplotlib.pyplot as plt
#from langchain.memory import ConversationBufferMemory
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.chat_models.tongyi import ChatTongyi
# from langchain_experimental.tools import PythonREPLTool
#需要在自己的电脑系统中用这两个字体
#确保中文能够显示
plt.rcParams['font.family'] = 'SimHei'
#正常显示负号
plt.rcParams['axes.unicode_minus'] = False
PROMPT_TEMPLATE = """
你是一个精通CSV文件以及xlsx文件并且能够进行数据分析的数据分析师，
你需要帮助用户对其上传的csv文件以及xlsx文件进行分析，
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
情况4：用户需要用折线图展示数据
回答的json格式为：
{ 
    "plt": { 
    "Category": ["A", "B", "C", "D"], 
    "Values": [401, 133, 10, 1]
    }
}
情况5：用户需要用扇形图展示数据
回答的json格式为：
{ 
    "fig": { 
    "Category": ["A", "B", "C", "D"], 
    "Values": [401, 133, 10, 1]
    }
}
情况6：用户需要用最小二乘法拟合对应的数据形成线性回归图，
那么此时你还需要给出原始数据存放在o_Category和o_Values中
回答的json格式为：
{ 
    "line": { 
    "o_Category":["A", "B", "C", "D"],
    "o_Values": [401, 133, 10, 1],
    "Category": ["A", "B", "C", "D"], 
    "Values": [401, 133, 10, 1]
    }
}
情况7:用户需要用散点图展示数据
回答的json格式为：
{ 
    "scatter": { 
    "Category": ["A", "B", "C", "D"], 
    "Values": [401, 133, 10, 1]
    },
    "graph":{
    "x":<x轴坐标名称>
    "y":<y轴坐标名称>
    }
}
情况8:用户需要用箱线图对数据异常值分析
回答的json格式为：
{ 
    "box": { 
    "Category":['A','A','B','C']
    "Values": [401, 133, 10, 1]
    }
}
情况9：用户的问题是生成以上图表之外的图表
回答的json格式为：
{
"answer":"很抱歉我暂时无法生成这种图表"
}
输出格式为符合以上结构的JSON格式，即{<对应内容>}，一定不要输出```json```，同时不添加其它内容
你要处理的用户请求如下：
"""
#很奇妙，少了“即{<对应内容>}”这个之后生成柱状图会出现一点问题
# 回答，同时
def csv_agent(df,query,use_key):
    try:
        print("尝试初始化 ChatTongyi...")
        tongyi_chat = ChatTongyi(
            model="qwen-plus",
            top_p=1.0,
            temperature=1.0,
            api_key=use_key,

        )
        print("ChatTongyi 初始化成功")
    except Exception as e:
        print(f"ChatTongyi 初始化失败: {e}")
        st.write(f"ChatTongyi 初始化失败: {e},请修改对应错误后重新尝试")
        return False
        #这里不需要
        # try:
        #     print("构造 Prompt...")
        #     prompt_value = chat_prompt.invoke({
        #         "parser_instructions": parser_instructions,
        #         "theme": user_theme,
        #         "style": user_style
        #     })
        #     print(f"Prompt 构造成功: {prompt_value}")
        # except Exception as e:
        #     print(f"Prompt 构造失败: {e}")
        #     st.write(f"Prompt 构造失败: {e},请修改对应错误后重新尝试")
        #     return False

    try:
        print("调用 ChatTongyi 模型...")
        agent_executor = create_pandas_dataframe_agent(
            llm=tongyi_chat,
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
    except Exception as e:
        print(f"模型调用失败: {e}")
        st.write(f"模型调用失败: {e},请修改对应错误后重新尝试")
        return False


st.set_page_config(
    page_title="图表绘制助手",  # 标签页的名称
    page_icon="🚀"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"
)
#添加一个标题
st.title('📄图表绘制助手')

#添加水平分割线
st.divider()
with st.sidebar:
    st.write("用户管理")
    user_api = st.text_input("请输入你的api_key",type="password")
#新增允许加入xlsx文件，利用后缀名进行分开处理
data = st.file_uploader("上传你的数据文件（CSV格式）:",type=["csv","xlsx"])
st.write("在上传您的文件后便可以进行提问")
if data:
    if data.name.endswith('.csv'):
        st.session_state["df"] = pd.read_csv(data)
    else:
        st.session_state["df"] = pd.read_excel(data,engine='openpyxl')
    print(st.session_state["df"])
    with st.expander("点击查看数据"):
        st.dataframe(st.session_state["df"])
    query_user = st.text_input("请输入您的需求")
    if st.button("发送🚀"):
        if not user_api.strip():
            st.write("api_key输入不能空,请输入内容!")
        if not query_user.strip():
            st.write("请您输入您的需求后再提交!")
        if query_user.strip() and user_api.strip():
            response_dict_bot = csv_agent(st.session_state["df"],
                                          query_user,
                                          user_api)
            if not response_dict_bot :
                st.write("模型调用失败")
            else:
                if 'answer' in response_dict_bot:
                    st.write(response_dict_bot['answer'])
                elif 'table' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['table']['data'],
                                       columns=response_dict_bot['table']['columns'])
                    st.dataframe(df1)
                elif 'bar' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['bar'])
                    st.bar_chart(df1.set_index('Category')['Values'])
                elif 'plt' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['plt'])
                    st.line_chart(df1.set_index('Category')['Values'])
                elif 'fig' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['fig'])
                    fig = go.Figure(data=[go.Pie(labels=df1['Category'],values=df1['Values'],hole=0.3)])
                    st.plotly_chart(fig)
                elif 'line' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['line'])
                    x = df1['o_Category']
                    y = df1['o_Values']
                    # 计算相关性系数
                    correlation_coefficient = np.corrcoef(x, y)[0, 1]
                    #最小二乘法拟合线性模型
                    slope,intercept = np.polyfit(x,y,1)
                    #回归方程
                    equation = f'y = {slope:.2f}x + {intercept:.2f}'
                    # 绘制数据点和回归线
                    fig, ax = plt.subplots()
                    ax.scatter(x, y, label="原始数据点", color='red')
                    ax.plot(x, slope * x + intercept, label=f"回归线: {equation}", color='blue')
                    # 添加标题和标签
                    ax.set_title("最小二乘法线性回归")
                    ax.set_xlabel("X 轴")
                    ax.set_ylabel("Y 轴")
                    # 显示图例
                    ax.legend()
                    # 在 Streamlit 中显示图表
                    st.pyplot(fig)
                    # 显示回归方程
                    st.write(f"回归方程: {equation}")
                    # 显示相关性系数
                    st.write(f"相关性系数: {correlation_coefficient:.2f}")
                    if -0.5<correlation_coefficient<0.5:
                        st.write(f"与y线性相关性较弱")
                    else:
                        st.write(f"x与y线性相关性较强")
                elif 'scatter' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['scatter'])
                    fig, ax = plt.subplots()
                    ax.scatter(df1['Category'], df1['Values'])
                    x_label,y_label = df1.keys()
                    # 添加标题和轴标签
                    ax.set_title('散点图')
                    ax.set_xlabel('X 轴')
                    ax.set_ylabel('Y 轴')
                    # 在Streamlit中显示图表
                    st.plotly_chart(fig)
                elif 'box' in response_dict_bot:
                    df1 = pd.DataFrame(response_dict_bot['box'])
                    # 创建箱线图
                    fig = px.box(df1, x='Category',y='Values',title='箱线图')
                    # 在Streamlit中显示图表
                    st.plotly_chart(fig)

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




