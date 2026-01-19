import streamlit as st
import json
import random
import time

# 1. 页面配置：设为宽屏，默认收起侧边栏
st.set_page_config(page_title="医学刷题宝", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入 CSS：精准控制看板按钮的圆形填充，并隔离功能按钮
st.markdown("""
    <style>
    /* --- 看板按钮专属圆形样式 --- */
    .q-btn-box button {
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        font-weight: bold !important;
        margin: 4px !important;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
    }

    /* --- 精准颜色填充 --- */
    /* 正确：绿底白字 */
    .q-correct button { background-color: #28a745 !important; color: white !important; }
    /* 错误：红底白字 */
    .q-incorrect button { background-color: #dc3545 !important; color: white !important; }
    /* 未做：灰底黑字 */
    .q-none button { background-color: #f0f2f6 !important; color: #333 !important; }
    
    /* --- 功能按钮隔离 --- */
    /* 确保“下一题”、“重置进度”等长方形按钮不被变圆 */
    .stButton > button {
        border-radius: 8px;
        width: auto;
        height: auto;
    }
    
    /* 解决网页底部空白问题 */
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
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

# --- 4. 侧边栏及数据预加载 ---
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}

with st.sidebar:
    st.title("⚙️ 刷题设置")
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))

# 关键：一旦选择学科立即加载数据，确保看板不再空白
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
        st.rerun() # 强制刷新以立即渲染看板

total_q = len(st.session_state.all_questions)

# --- 5. 主界面布局 ---
main_col, board_col = st.columns([0.7, 0.3])

with main_col:
    if total_q == 0:
        st.info("👋 欢迎！请确保已上传数据文件。")
    elif st.session_state.current_idx_in_list >= total_q:
        st.balloons()
        st.success("🏆 恭喜通关本学科所有题目！")
    else:
        # 当前题目逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"随机练习：{cur_list_idx + 1} / {total_q} (原始序号: {actual_q_idx + 1})")
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
                st.success("✅ 回答正确！")
                time.sleep(0.6)
                st.session_state.current_idx_in_list += 1
                st.rerun()
            else:
                st.session_state.results[actual_q_idx] = "incorrect"
                st.session_state.error_mode = True
                st.rerun()
    
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            # 这里的按钮会恢复成标准长方形
            if st.button("下一题 ➔", type="primary", key="next_btn"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

# --- 6. 右侧看板：圆形颜色填充 ---
with board_col:
    with st.expander("📍 题目看板 (可滑动)", expanded=True):
        # 显示当前学科总题数统计
        st.write(f"总计: {total_q} 题")
        
        # 固定高度容器，防止页面被撑长
        with st.container(height=500):
            grid = st.columns(4) 
            for i in range(total_q):
                # 获取该题目的状态
                status = st.session_state.results.get(i, "none")
                
                # 核心改进：使用带类名的 div 包裹按钮，实现颜色填充
                with grid[i % 4]:
                    st.markdown(f'<div class="q-btn-box q-{status}">', unsafe_allow_html=True)
                    if st.button(f"{i+1}", key=f"btn_{i}"):
                        st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                        st.session_state.error_mode = False
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏重置进度按钮
with st.sidebar:
    if total_q > 0:
        st.divider()
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()