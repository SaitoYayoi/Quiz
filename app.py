import streamlit as st
import json
import random
import time

# 1. 页面基础配置：设为宽屏
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入全局 CSS：确保样式美观且按钮圆润
st.markdown("""
    <style>
    /* 仅针对题目看板内部的按钮：变为圆形 */
    [data-testid="stExpander"] .stButton > button {
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0px !important;
        margin: 4px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        border: 1px solid #ddd !important;
    }
    /* 保持主界面的“下一题”和侧边栏按钮为长方形样式 */
    .stButton > button { border-radius: 6px; }
    /* 优化整体间距 */
    .main .block-container { padding-top: 1.5rem; }
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

# --- 4. 关键：数据预加载逻辑 (放在渲染之前) ---
# 先定义学科映射
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}

# 在侧边栏选择学科
with st.sidebar:
    st.title("⚙️ 刷题控制台")
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))

# 如果切换了学科或第一次打开，立即加载数据
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        # 生成并打乱索引
        indices = list(range(len(data)))
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        # 重置所有状态
        st.session_state.current_idx_in_list = 0
        st.session_state.results = {}
        st.session_state.error_mode = False
        st.session_state.last_sub = selected_sub_name
        st.rerun() # 加载完数据后强制刷新，确保看板立即显示

# --- 5. 布局：左侧答题，右侧看板 ---
main_col, board_col = st.columns([0.7, 0.3])

# 获取统计数据
total_q = len(st.session_state.all_questions)
correct_count = list(st.session_state.results.values()).count("correct")
incorrect_count = list(st.session_state.results.values()).count("incorrect")

with main_col:
    if total_q == 0:
        st.info("👋 欢迎！请确保已上传数据文件。")
    elif st.session_state.current_idx_in_list >= total_q:
        st.balloons()
        st.success("🏆 通关！本学科所有题目已练习完毕。")
    else:
        # 答题逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"随机进度：{cur_list_idx + 1} / {total_q}")
        st.divider()
        st.markdown(f"#### {q['question']}")
        
        user_choice = st.radio("选择答案：", q['options'], index=None, key=f"active_q_{actual_q_idx}", disabled=st.session_state.error_mode)
    
        if user_choice and not st.session_state.error_mode:
            correct_letter = q['answer'].strip().upper()
            if user_choice.startswith(correct_letter):
                st.session_state.results[actual_q_idx] = "correct"
                st.success("✅ 正确！")
                time.sleep(0.6)
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

with board_col:
    # 右侧看板：显示统计和题号网格
    with st.expander("📍 题目看板 (点击跳转)", expanded=True):
        st.write(f"✅ 正确: {correct_count} | ❌ 错误: {incorrect_count}")
        
        # 使用固定高度容器，防止网页过长
        with st.container(height=550):
            grid = st.columns(4) 
            for i in range(total_q):
                status = st.session_state.results.get(i)
                
                # 使用 Emoji 颜色图标作为题号标识，这在 iOS 上非常醒目且稳定
                # 🟢=正确, 🔴=错误, ⚪=未做
                if status == "correct":
                    label = f"🟢\n{i+1}"
                elif status == "incorrect":
                    label = f"🔴\n{i+1}"
                else:
                    label = f"⚪\n{i+1}"
                
                # 点击跳转逻辑
                if grid[i % 4].button(label, key=f"btn_{i}"):
                    # 找到该原始题号在随机序列中的索引
                    st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                    st.session_state.error_mode = False
                    st.rerun()

# 侧边栏重置按钮
with st.sidebar:
    if total_q > 0:
        st.divider()
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()