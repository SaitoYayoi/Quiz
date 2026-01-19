import streamlit as st
import json
import random
import time

# 1. 页面配置
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入全局 CSS：精准隔离题号圆圈与功能按钮
st.markdown("""
    <style>
    /* --- 题号看板专属样式 --- */
    /* 仅针对看板容器内的按钮：强制变为圆形 */
    [data-testid="stExpander"] .stButton > button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0px !important;
        margin: 4px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
    }

    /* --- 功能按钮恢复样式 --- */
    /* 强制让主界面和侧边栏的长方形按钮恢复正常 */
    .main .stButton > button, 
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px !important;
        width: auto !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
        aspect-ratio: auto !important;
    }
    
    /* 优化整体布局间距 */
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

# --- 4. 侧边栏：学科选择 ---
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}

with st.sidebar:
    st.title("⚙️ 设置")
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))

# 数据加载逻辑：确保启动即加载
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

# --- 5. 主界面布局 ---
main_col, board_col = st.columns([0.7, 0.3])
total_q = len(st.session_state.all_questions)

with main_col:
    if total_q == 0:
        st.info("👋 欢迎！请确保已上传题库文件。")
    elif st.session_state.current_idx_in_list >= total_q:
        st.balloons()
        st.success("🏆 本学科已全部练习完毕！")
    else:
        # 当前题目逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"当前进度：{cur_list_idx + 1} / {total_q}")
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
            # 这里的“下一题”按钮现在会强制保持长方形
            if st.button("下一题 ➔", type="primary"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

# --- 6. 右侧看板：圆形颜色填充 ---
with board_col:
    with st.expander("📍 题目看板", expanded=True):
        if total_q > 0:
            # 批量生成样式并一次性注入
            style_content = ""
            for i in range(total_q):
                status = st.session_state.results.get(i)
                if status == "correct":
                    bg, txt = "#28a745", "white" # 绿
                elif status == "incorrect":
                    bg, txt = "#dc3545", "white" # 红
                else:
                    bg, txt = "#f0f2f6", "#333"  # 灰
                
                # 利用按钮生成的特定识别特征进行精准样式覆盖
                style_content += f'div[data-testid="stExpander"] .stButton > button[key="btn_{i}"] {{ background-color: {bg} !important; color: {txt} !important; }}\n'
            
            st.markdown(f"<style>{style_content}</style>", unsafe_allow_html=True)
    
            with st.container(height=550):
                grid = st.columns(4) 
                for i in range(total_q):
                    # 确保 key 与 CSS 匹配
                    if grid[i % 4].button(f"{i+1}", key=f"btn_{i}"):
                        st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                        st.session_state.error_mode = False
                        st.rerun()