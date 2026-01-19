import streamlit as st
import json
import random
import time

# 页面基础设置
st.set_page_config(page_title="医学刷题宝", layout="centered")

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# --- 初始化状态 ---
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_q' not in st.session_state:
    st.session_state.current_q = None
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False

# --- 侧边栏 ---
st.sidebar.title("📚 学科模块")
# 如果你有新学科，在这里添加对应的文件名
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}
selected_sub_name = st.sidebar.selectbox("切换学科", list(subject_map.keys()))

# 切换学科逻辑
if selected_sub_name != st.session_state.last_sub:
    st.session_state.questions = load_data(subject_map[selected_sub_name])
    if st.session_state.questions:
        st.session_state.current_q = random.choice(st.session_state.questions)
    st.session_state.last_sub = selected_sub_name
    st.session_state.error_mode = False

# --- 主界面 ---
st.title(f"📖 {selected_sub_name}")

if not st.session_state.questions:
    st.warning("⚠️ 请确保 linjian.json 已经上传且格式正确。")
else:
    q = st.session_state.current_q
    
    st.divider()
    st.markdown(f"**第 {q['id']} 题**")
    st.markdown(f"#### {q['question']}")
    
    # 错误模式下禁用选项，防止重复触发
    is_disabled = st.session_state.error_mode
    
    # 单选框：选中即触发判断
    user_choice = st.radio(
        "请选择答案：", 
        q['options'], 
        index=None, 
        key=f"q_{q['id']}", 
        disabled=is_disabled
    )
    
    # --- 核心判断逻辑 ---
    if user_choice and not st.session_state.error_mode:
        correct_letter = q['answer'].strip().upper()
        
        if user_choice.startswith(correct_letter):
            # 答对了：直接显示绿色反馈，0.5秒后跳题
            st.success("✅ 正确！")
            time.sleep(0.5) 
            st.session_state.current_q = random.choice(st.session_state.questions)
            st.rerun()
        else:
            # 答错了：开启错误模式
            st.session_state.error_mode = True
            st.rerun()
    
    # --- 错误拦截提示 ---
    if st.session_state.error_mode:
        st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
        if st.button("下一题 ➔", type="primary"):
            st.session_state.error_mode = False
            st.session_state.current_q = random.choice(st.session_state.questions)
            st.rerun()
    
    # 底部统计
    st.sidebar.metric("题库总量", len(st.session_state.questions))