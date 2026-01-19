import streamlit as st
import json
import random
import time

# 1. 页面配置：保持宽屏模式，默认收起左侧边栏
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入 CSS：精准控制看板圆圈和布局
st.markdown("""
    <style>
    /* 仅针对题目看板内部的按钮：变为圆形 */
    [data-testid="stExpander"] .stButton > button {
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0px !important;
        line-height: 38px !important;
        display: inline-block !important;
        margin: 3px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 13px !important;
    }
    
    /* 保持功能按钮（下一题、重置）为正常样式 */
    .stButton > button {
        border-radius: 6px;
    }
    
    /* 优化整体页面的背景和间距 */
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 95%;
    }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# --- 3. 初始化全局状态 ---
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
    st.title("⚙️ 设置与统计")
    subject_map = {
        "临床检验基础": "linjian.json",
        "待添加学科2": "subject2.json"
    }
    selected_sub_name = st.selectbox("当前选择学科", list(subject_map.keys()))
    
    st.divider()
    correct_count = list(st.session_state.results.values()).count("correct")
    incorrect_count = list(st.session_state.results.values()).count("incorrect")
    total_q = len(st.session_state.all_questions)
    
    if total_q > 0:
        st.metric("正确数量", f"{correct_count}")
        st.metric("错误数量", f"{incorrect_count}")
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()

# 数据加载逻辑
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

# --- 5. 主界面布局：左右分栏 ---
main_col, board_col = st.columns([0.7, 0.3])

with main_col:
    if not st.session_state.all_questions:
        st.info("👋 欢迎！请确保对应学科的 JSON 数据文件已上传。")
    elif st.session_state.current_idx_in_list >= len(st.session_state.all_questions):
        st.balloons()
        st.success("🏆 本学科已全部练习完毕！")
    else:
        # 当前题目内容
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"当前练习：第 {cur_list_idx + 1} 题 / 共 {total_q} 题")
        st.divider()
        
        st.markdown(f"#### {q['question']}")
        
        user_choice = st.radio(
            "选择你的答案：", 
            q['options'], 
            index=None, 
            key=f"active_q_{actual_q_idx}",
            disabled=st.session_state.error_mode
        )
    
        if user_choice and not st.session_state.error_mode:
            correct_letter = q['answer'].strip().upper()
            if user_choice.startswith(correct_letter):
                st.session_state.results[actual_q_idx] = "correct"
                st.success("✅ 正确！即将进入下一题...")
                time.sleep(0.7)
                st.session_state.current_idx_in_list += 1
                st.rerun()
            else:
                st.session_state.results[actual_q_idx] = "incorrect"
                st.session_state.error_mode = True
                st.rerun()
    
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            if st.button("下一题 ➔", type="primary"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

# --- 6. 右侧看板：解决长网页问题 ---
with board_col:
    with st.expander("📍 题目看板 (可滑动)", expanded=True):
        # 使用固定高度的容器解决网页过长问题
        with st.container(height=500):
            grid_cols = st.columns(4) 
            for i in range(total_q):
                status = st.session_state.results.get(i)
                
                # 动态颜色注入
                if status == "correct":
                    bg_color, txt_color = "#28a745", "white"
                elif status == "incorrect":
                    bg_color, txt_color = "#dc3545", "white"
                else:
                    bg_color, txt_color = "#f0f2f6", "#333"
    
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