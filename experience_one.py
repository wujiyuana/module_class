from openai import OpenAI
import openai
import streamlit as st
import time

#初始化客户端
def text_correction(ai_prompt,user_input,api_key):
    client = OpenAI(
        # 文本纠错助手的 API KEY 将由用户提供，下行可替换为：api_key="sk-xxx"
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", )
    response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
    {'role': 'system', 'content': ai_prompt},
    {'role': 'user', 'content': user_input}
     ], )
    return response.choices[0].message.content

AI_prompt = """
    请你充当一个文本纠错助手，将所得到的文本进行纠错，分别指出文本中的语法错误，
    拼写错误，标点错误以及对应的修改建议,
    以下为输出格式:
    *语法错误:<语法错误的部分><修改建议>
    *拼写错误:<拼写错误的部分><修改建议>
    *标点错误:<标点错误的部分><修改建议>
    修改后的文本答案:<修改后的文本>
    """
st.set_page_config(
    page_title="小鸢的文本纠错助手",  # 标签页的名称
    page_icon="🐲"         # 标签页的图标，可以是 emoji 或 URL🐲"🌟"🚀
)
#添加一个标题
st.title('🌟文本纠错助手')

#添加水平分割线
st.divider()
#文本输入
user_input_content = st.text_area("请输入你需要进行纠错的文本",height=100)
st.divider()
with st.sidebar:
    st.write("用户管理")
    user_api = st.text_input("请输入你的api_key",type="password")
# 可以循环使用,暂时没用到？
count = 0
num = str(count)

flag = 0


if st.button("提交",key=num) :
    if not user_input_content.strip():  # 去掉首尾空格后判断
        st.write("文本输入不能为空，请输入内容！")
        count+=1
    if not user_api.strip():
        st.write("api_key输入不能空,请输入内容!")
        count+=1
    if user_input_content.strip() and user_api.strip():
        count += 1
        flag = 1
        st.write("提交成功")
else:
    count+=1
if flag :
    ai_response = text_correction(AI_prompt,user_input_content,user_api)
    '小千正在努力中✈️'
    # 添加一个占位符
    latest_iteration = st.empty()
    bar = st.progress(0)
    for i in range(100):
 # 每次迭代更新进度条。
        latest_iteration.text(f'{i+1}%/100% ')
        bar.progress(i + 1)
        time.sleep(0.01)
    '...现在我们完成了！'
    st.divider()
    st.text_area("🐲:结果输出",ai_response,height=100)
    flag = 0

