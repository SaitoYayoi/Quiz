import streamlit as st
import json
import random
import time

# 1. 页面配置
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入核心 CSS：精准控制圆形样式
st.markdown("""
    <style>
    /* 仅让右侧看板容器内的按钮变圆 */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] .stButton > button {
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
    
    /* 保持主界面功能按钮（下一题、重置）为标准长方形 */
    [data-testid="stSidebar"] .stButton > button, 
    .main .stButton > button[key*="next"] {
        border-radius: 6px !important;
        width: auto !important;
        height: auto !important;
        padding: 0.25rem 1rem !important;
    }
    
    /* 整体布局优化 */
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

# --- 4. 侧边栏与数据预加载 ---
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}

with st.sidebar:
    st.title("⚙️ 刷题设置")
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))
    
    # 如果切换学科，立即加载并洗牌
    if selected_sub_name != st.session_state.last_sub:
        data = load_data(subject_map[selected_sub_name])
        if data:
            st.session_state.all_questions = data
            indices = list(range(len(data)))
            random.shuffle(indices)
            st.session_state.shuffled_indices = indices
            st.session_state.current_idx_in_list = 0
            st.session_state.results = {}
            st.session_state.error_mode = False
            st.session_state.last_sub = selected_sub_name
            st.rerun()
    
    # 统计数据
    total_q = len(st.session_state.all_questions)
    correct_count = list(st.session_state.results.values()).count("correct")
    incorrect_count = list(st.session_state.results.values()).count("incorrect")
    
    if total_q > 0:
        st.divider()
        st.metric("正确", correct_count)
        st.metric("错误", incorrect_count)
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()

# --- 5. 主界面布局 ---
main_col, board_col = st.columns([0.7, 0.3])

with main_col:
    if total_q == 0:
        st.info("👋 欢迎！请确保已上传题库文件。")
    elif st.session_state.current_idx_in_list >= total_q:
        st.balloons()
        st.success("🏆 恭喜！本学科已通关。")
    else:
        # 当前题目逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"当前练习：{cur_list_idx + 1} / {total_q}")
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
                time.sleep(0.6)
                st.session_state.current_idx_in_list += 1
                st.rerun()
            else:
                st.session_state.results[actual_q_idx] = "incorrect"
                st.session_state.error_mode = True
                st.rerun()
    
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            if st.button("下一题 ➔", type="primary", key="next_btn"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

# --- 6. 右侧看板：圆形颜色填充逻辑 ---
with board_col:
    with st.expander("📍 题目看板", expanded=True):
        if total_q > 0:
            # A. 批量生成颜色样式代码 (一次性注入，不占网页空间)
            style_str = ""
            for i in range(total_q):
                status = st.session_state.results.get(i)
                if status == "correct":
                    bg, txt = "#28a745", "white" # 绿底白字
                elif status == "incorrect":
                    bg, txt = "#dc3545", "white" # 红底白字
                else:
                    bg, txt = "#f0f2f6", "#333"  # 灰底黑字
                style_str += f'button[key="btn_{i}"] {{ background-color: {bg} !important; color: {txt} !important; }}\n'
            
            st.markdown(f"<style>{style_str}</style>", unsafe_allow_html=True)
    
            # B. 渲染固定高度的滚动容器
            with st.container(height=550):
                grid = st.columns(4) 
                for i in range(total_q):
                    if grid[i % 4].button(f"{i+1}", key=f"btn_{i}"):
                        st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                        st.session_state.error_mode = False
                        st.rerun()