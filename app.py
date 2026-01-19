import streamlit as st
import json
import random

# 页面基础设置
st.set_page_config(page_title="医学刷题神器", layout="centered")

# 定义加载数据的函数
def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# 侧边栏：学科选择
st.sidebar.title("📚 我的学科库")
# 以后你有了新学科，只需在这里添加文件名即可
subject_options = {"临床检验基础": "linjian.json"}
selected_subject_name = st.sidebar.selectbox("选择要练习的学科", list(subject_options.keys()))

# 初始化题目状态
if 'current_question' not in st.session_state or st.session_state.get('last_sub') != selected_subject_name:
    data = load_data(subject_options[selected_subject_name])
    st.session_state.questions = data
    st.session_state.current_question = random.choice(data)
    st.session_state.last_sub = selected_subject_name
    st.session_state.answered = False
    st.session_state.user_choice = None

# 主界面显示
st.title(f"📖 {selected_subject_name}")
q = st.session_state.current_question

st.divider()
st.subheader(f"第 {q['id']} 题")
st.write(q['question'])

# 用户选择答案
choice = st.radio("请选择：", q['options'], index=None, key=f"q_{q['id']}")

if st.button("提交验证"):
    if choice:
        st.session_state.answered = True
        correct_letter = q['answer']
        if choice.startswith(correct_letter):
            st.success("✅ 太棒了，回答正确！")
        else:
            st.error(f"❌ 答错了。正确答案是：{correct_letter}")
    else:
        st.warning("请先选择一个选项")

if st.button("下一题"):
    st.session_state.current_question = random.choice(st.session_state.questions)
    st.session_state.answered = False
    st.rerun()