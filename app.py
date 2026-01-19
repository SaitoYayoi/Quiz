import streamlit as st
import json
import random
import time

# 1. 页面基础配置
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入核心 CSS：精准控制圆形填充颜色，并隔离功能按钮
st.markdown("""
    <style>
    /* --- 题号看板圆圈样式 --- */
    /* 答对、答错、未做的填充颜色设置 */
    .btn-wrap-correct button { background-color: #28a745 !important; color: white !important; }
    .btn-wrap-incorrect button { background-color: #dc3545 !important; color: white !important; }
    .btn-wrap-unattempted button { background-color: #f0f2f6 !important; color: #333 !important; }

    /* 强行将看板内的按钮变为圆形 */
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
        font-weight: bold !important;
    }
    
    /* --- 功能按钮样式隔离 --- */
    /* 恢复主界面的“下一题”和侧边栏按钮为标准长方形 */
    .main .stButton > button, 
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px !important;
        width: auto !important;
        height: auto !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 16px !important;
    }
    
    /* 消除多余空白 */
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
    st.session_state.results = {} # {原始题号索引: "correct" | "incorrect"}
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 4. 侧边栏：学科选择与数据预加载 ---
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}

with st.sidebar:
    st.title("⚙️ 刷题设置")
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))

# 关键：确保启动或切换时立即加载数据，不再显示空白看板
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        # 洗牌逻辑
        indices = list(range(len(data)))
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        # 重置当前状态
        st.session_state.current_idx_in_list = 0
        st.session_state.results = {}
        st.session_state.error_mode = False
        st.session_state.last_sub = selected_sub_name
        st.rerun() # 立即刷新以显示看板

total_q = len(st.session_state.all_questions)

# --- 5. 主界面布局 ---
main_col, board_col = st.columns([0.7, 0.3])

with main_col:
    if total_q == 0:
        st.info("👋 欢迎！请确保 JSON 数据文件已上传。")
    elif st.session_state.current_idx_in_list >= total_q:
        st.balloons()
        st.success("🏆 恭喜！你已完成本学科的所有题目！")
        if st.button("🔄 重新开始本课"):
            st.session_state.last_sub = ""
            st.rerun()
    else:
        # 当前题目逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"当前练习：第 {cur_list_idx + 1} 题 / 共 {total_q} 题 (书本序号: {actual_q_idx + 1})")
        st.divider()
        
        st.markdown(f"#### {q['question']}")
        
        user_choice = st.radio(
            "选择你的答案：", 
            q['options'], 
            index=None, 
            key=f"active_q_{actual_q_idx}",
            disabled=st.session_state.error_mode
        )
    
        # 答题判断
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
    
        # 错误拦截
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            if st.button("下一题 ➔", type="primary"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

# --- 6. 右侧看板：圆形颜色填充展示 ---
with board_col:
    with st.expander("📍 题目看板 (可滑动)", expanded=True):
        # 统计数据
        correct_n = list(st.session_state.results.values()).count("correct")
        incorrect_n = list(st.session_state.results.values()).count("incorrect")
        st.write(f"✅ {correct_n} | ❌ {incorrect_n} | ⚪ {total_q - correct_n - incorrect_n}")
        
        # 固定高度容器，解决网页过长问题
        with st.container(height=550):
            grid = st.columns(4) 
            for i in range(total_q):
                # 确定该题状态
                status = st.session_state.results.get(i, "unattempted")
                
                # 关键：使用 HTML 包装器 div 配合 CSS 实现颜色填充
                with grid[i % 4]:
                    st.markdown(f'<div class="btn-wrap-{status}">', unsafe_allow_html=True)
                    if st.button(f"{i+1}", key=f"btn_{i}"):
                        # 跳转逻辑
                        st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                        st.session_state.error_mode = False
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏底部重置
with st.sidebar:
    if total_q > 0:
        st.divider()
        if st.button("🔄 重置全课进度"):
            st.session_state.last_sub = ""
            st.rerun()