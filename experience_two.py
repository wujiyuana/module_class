from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi
import streamlit as st
import time

from numpy.core.defchararray import title
from pydantic import BaseModel,Field,field_validator
#from streamlit import chat_message

class Wb(BaseModel):
    title: str=Field(...,description="微博标题")
    important_word: str=Field(...,
                              description="这篇微博的关键词,可以有多个",
                              examples=["#985大学生#🌟#超长寒假#","#春节#🚀#一票难求#🚀#春运#",
                                        "#中秋节#🌟#超级月亮#",
                                        "#徐克执导的金庸射雕和春节好适配#🐲#武侠是全球华人血脉觉醒的文化密码#"])
    content: str=Field(...,
                       description="微博的正文(主要内容)",
                       examples=["独属于中国的文化符号将再次唤醒每个华人心中的英雄情怀。由徐克执导的电影《射雕英雄传：侠之大者》定档2025年春节，戳视频↓↓四海同春，一步江湖！"])
    end: str=Field(...,
                   description="微博结尾")

user_output_parser = PydanticOutputParser(pydantic_object=Wb)
parser_instructions = user_output_parser.get_format_instructions()
#聊天提示词模板
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system","{parser_instructions}"),
        ("human","你长年在微博浏览各种帖子，经过多年的观察，你已经发现了撰写微博的套路，现在我高价聘用你做我的微博撰写小助手，你需要根据我给出的主题，写出一篇微博，并且输出的文本会根据用户要求的语言风格调整。主题:{theme}\n语言风格:{style}"),
    ]
)

#初始化客户端
# def weibo_solution(use_key,user_theme,user_style):
#     tongyi_chat = ChatTongyi(
#         model ="qwen-plus",
#         top_p = 1.0,
#         temperature=1.0,
#         api_key = use_key,
#     )
#     prompt_value = chat_prompt.invoke({"parser_instructions":parser_instructions,"theme":user_theme,"style":user_style})
#     response = tongyi_chat.invoke(prompt_value)
#     return response

#可以检验api是否正确等并给出错误原因
def weibo_solution(use_key, user_theme, user_style):
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
        #result = tongyi_chat.invoke(prompt_value)
        #response = user_output_parser.invoke(result)
        chain = chat_prompt | tongyi_chat | user_output_parser
        response  = chain.invoke({"parser_instructions": parser_instructions,"theme": user_theme,"style": user_style})
        print(f"模型返回结果: {response}")
        return response
    except Exception as e:
        print(f"模型调用失败: {e}")
        st.write(f"模型调用失败: {e},请修改对应错误后重新尝试")
        return False

#测试用例
# user_theme1 = "第一场雪"
# user_style1 = "浪漫"
# responses = weibo_solution(user_key,user_theme1,user_style1)
# print(responses)


st.set_page_config(
    page_title="小鸢的微博撰写小助手",  # 标签页的名称
    page_icon="🚀"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"🚀
)
#添加一个标题
st.title('🌟微博撰写小助手')

#添加水平分割线
st.divider()
#文本输入
user_input_theme = st.text_area("请输入你想要撰写的微博主题",height=100)
user_input_style = st.text_input("请输入你希望的文章风格")
st.divider()
with st.sidebar:
    st.write("用户管理")
    user_api = st.text_input("请输入你的api_key",type="password")

flag = 0


if st.button("提交") :
    if not user_input_theme.strip():  # 去掉首尾空格后判断
        st.write("主题输入不能为空，请输入内容！")
    if not user_api.strip():
        st.write("api_key输入不能空,请输入内容!")
    if not user_input_style.strip():
          st.write("文章风格输入不能为空,请输入内容！")
    if user_input_theme.strip() and user_api.strip() and user_input_style.strip():
        flag = 1
        st.write("提交成功")

if flag:
    ai_response = weibo_solution(user_api,user_input_theme,user_input_style)
    if ai_response:
        '小千-plus正在努力为你生成微博内容中✈️'
        # 添加一个占位符
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
     # 每次迭代更新进度条。
            latest_iteration.text(f'{i+1}%/100% ')
            bar.progress(i + 1)
            time.sleep(0.01)
        '小义plus完成这篇微博了！'
        st.divider()
        st.header(ai_response.title)
        st.write(ai_response.important_word)
        st.write(ai_response.content)
        st.write(ai_response.end)
        st.divider()
        flag = 0

