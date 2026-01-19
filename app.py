import streamlit as st
import json
import random
import time

# 1. 页面配置
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入精准 CSS：只针对“题目看板”内的按钮进行圆形处理
st.markdown("""
    <style>
    /* 重点：只让带有 [data-testid="stExpander"] 容器内的按钮变圆 */
    [data-testid="stExpander"] .stButton > button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0px !important;
        line-height: 40px !important;
        display: inline-block !important;
        margin: 4px !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    /* 鼠标悬停效果 */
    [data-testid="stExpander"] .stButton > button:hover {
        transform: scale(1.1);
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
    
    /* 保持主界面和侧边栏按钮（下一题、重置）为原始长方形 */
    .stButton > button {
        border-radius: 4px; /* 恢复默认微圆角 */
    }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# 3. 初始化状态
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = []
if 'current_idx_in_list' not in st.session_state:
    st.session_state.current_idx_in_list = 0
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 4. 左侧侧边栏 ---
with st.sidebar:
    st.title("⚙️ 设置")
    subject_map = {
        "临床检验基础": "linjian.json",
        "学科2": "subject2.json"
    }
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))
    
    st.divider()
    correct_count = list(st.session_state.results.values()).count("correct")
    incorrect_count = list(st.session_state.results.values()).count("incorrect")
    total_q = len(st.session_state.all_questions)
    
    if total_q > 0:
        st.metric("正确", f"{correct_count}")
        st.metric("错误", f"{incorrect_count}")
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()

# --- 5. 加载逻辑 ---
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        indices = list(range(len(data)))
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        st.session_state.current_idx_in_list = 0
        st.session_state.results = {}
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False

# --- 6. 主界面布局 ---
main_col, board_col = st.columns([0.7, 0.3])

with main_col:
    if not st.session_state.all_questions:
        st.info("👋 请确保数据文件已正确上传。")
    elif st.session_state.current_idx_in_list >= len(st.session_state.all_questions):
        st.balloons()
        st.success("🏆 恭喜通关所有题目！")
    else:
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"当前进度：{cur_list_idx + 1} / {total_q}")
        st.divider()
        
        st.markdown(f"#### {q['question']}")
        
        user_choice = st.radio(
            "选择答案：", 
            q['options'], 
            index=None, 
            key=f"active_q_{actual_q_idx}",
            disabled=st.session_state.error_mode
        )
    
        if user_choice and not st.session_state.error_mode:
            correct_letter = q['answer'].strip().upper()
            if user_choice.startswith(correct_letter):
                st.session_state.results[actual_q_idx] = "correct"
                st.success("✅ 正确！")
                time.sleep(0.7)
                st.session_state.current_idx_in_list += 1
                st.rerun()
            else:
                st.session_state.results[actual_q_idx] = "incorrect"
                st.session_state.error_mode = True
                st.rerun()
    
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            # 这里的“下一题”按钮现在会恢复成原始的长方形
            if st.button("下一题 ➔", type="primary"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

with board_col:
    # 这里的按钮会因为在 expander 内部而变成圆形
    with st.expander("📍 题目看板", expanded=True):
        grid_cols = st.columns(4) 
        for i in range(total_q):
            status = st.session_state.results.get(i)
            
            # 颜色定义
            if status == "correct":
                bg_color = "#28a745"
                txt_color = "white"
            elif status == "incorrect":
                bg_color = "#dc3545"
                txt_color = "white"
            else:
                bg_color = "#f0f2f6"
                txt_color = "#333"
    
            # 仅针对看板按钮注入独立背景颜色
            st.markdown(f"""
                <style>
                button[key="btn_{i}"] {{
                    background-color: {bg_color} !important;
                    color: {txt_color} !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            if grid_cols[i % 4].button(f"{i+1}", key=f"btn_{i}"):
                try:
                    st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                    st.session_state.error_mode = False
                    st.rerun()
                except ValueError:
                    pass