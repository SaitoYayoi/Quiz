import streamlit as st
import json
import random
import time

# 页面基础设置
st.set_page_config(page_title="医学刷题神器 v2.0", layout="centered")

# 定义加载数据的函数
def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# --- 初始化 Session State ---
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_q' not in st.session_state:
    st.session_state.current_q = None
if 'show_error' not in st.session_state:
    st.session_state.show_error = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 侧边栏：学科选择 ---
st.sidebar.title("📚 我的学科库")
# 这里你可以继续添加你的 5 个学科文件名
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json",
    "待添加学科3": "subject3.json",
    "待添加学科4": "subject4.json",
    "待添加学科5": "subject5.json"
}
selected_sub_name = st.sidebar.selectbox("选择要练习的学科", list(subject_map.keys()))

# 如果切换了学科，重新加载
if selected_sub_name != st.session_state.last_sub:
    st.session_state.questions = load_data(subject_map[selected_sub_name])
    if st.session_state.questions:
        st.session_state.current_q = random.choice(st.session_state.questions)
    st.session_state.last_sub = selected_sub_name
    st.session_state.show_error = False

# --- 主逻辑 ---
st.title(f"📖 {selected_sub_name}")

if not st.session_state.questions:
    st.warning("请检查 JSON 文件是否已正确上传。")
else:
    q = st.session_state.current_q
    
    st.divider()
    st.subheader(f"第 {q['id']} 题")
    st.write(q['question'])
    
    # 选项显示
    # 使用 key 来确保每次换题时单选框重置
    user_choice = st.radio(
        "选择你的答案：", 
        q['options'], 
        index=None, 
        key=f"radio_{q['id']}"
    )
    
    # 提交按钮
    if st.button("提交回答", type="primary"):
        if user_choice:
            correct_letter = q['answer'].strip().upper()
            if user_choice.startswith(correct_letter):
                # --- 情况1：选择正确 ---
                st.success("✅ 回答正确！正在进入下一题...")
                time.sleep(0.8)  # 短暂延迟，让你看清正确提示
                # 随机换下一题
                st.session_state.current_q = random.choice(st.session_state.questions)
                st.session_state.show_error = False
                st.rerun()
            else:
                # --- 情况2：选择错误 ---
                st.session_state.show_error = True
        else:
            st.warning("请先选择一个选项")
    
    # 错误反馈
    if st.session_state.show_error:
        st.error(f"❌ 答错了。正确答案是：{q['answer']}")
        st.info("你可以查看原题进行纠错，或者直接点击下方按钮跳过。")
        if st.button("强制下一道"):
            st.session_state.current_q = random.choice(st.session_state.questions)
            st.session_state.show_error = False
            st.rerun()
    
    # 进度提示
    st.sidebar.divider()
    st.sidebar.write(f"当前题库总数：{len(st.session_state.questions)}")