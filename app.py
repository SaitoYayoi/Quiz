import streamlit as st
import json
import random
import time

# 页面基础设置
st.set_page_config(page_title="医学刷题宝-进度统计版", layout="centered")

def load_data(filename):
    try:
        # 确保使用 utf-8 编码读取 JSON
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# --- 1. 初始化 Session State (核心逻辑) ---
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = [] # 原始题库
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = [] # 打乱后的索引序列
if 'current_idx_in_list' not in st.session_state:
    st.session_state.current_idx_in_list = 0 # 当前练习的进度指针
if 'stats' not in st.session_state:
    st.session_state.stats = {"correct": 0, "incorrect": 0} # 统计数据
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 2. 侧边栏：设置与统计 ---
st.sidebar.title("📊 练习统计")

# 你可以在这里继续添加你的其他 JSON 文件名
subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}
selected_sub_name = st.sidebar.selectbox("切换学科模块", list(subject_map.keys()))

# 切换学科或初始化时：执行一次洗牌 (Shuffle)
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        indices = list(range(len(data)))
        random.shuffle(indices) # 彻底打乱题目顺序
        st.session_state.shuffled_indices = indices
        st.session_state.current_idx_in_list = 0
        st.session_state.stats = {"correct": 0, "incorrect": 0}
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False

# 显示统计面板
total_q = len(st.session_state.all_questions)
if total_q > 0:
    done_q = st.session_state.current_idx_in_list
    progress = done_q / total_q
    
    st.sidebar.write(f"练习进度：{done_q} / {total_q}")
    st.sidebar.progress(progress)
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("正确", st.session_state.stats["correct"])
    col2.metric("错误", st.session_state.stats["incorrect"])
    
    # 计算实时正确率
    total_answered = st.session_state.stats["correct"] + st.session_state.stats["incorrect"]
    accuracy = (st.session_state.stats["correct"] / total_answered * 100) if total_answered > 0 else 0
    st.sidebar.write(f"当前正确率：{accuracy:.1f}%")
    
    st.sidebar.divider()
    if st.sidebar.button("🔄 重新开始本科练习"):
        st.session_state.last_sub = "" # 强制触发重新初始化
        st.rerun()

# --- 3. 主界面逻辑 ---
st.title(f"📖 {selected_sub_name}")

if not st.session_state.all_questions:
    st.warning("⚠️ 未检测到有效题库，请确认 linjian.json 文件已上传。")
elif st.session_state.current_idx_in_list >= total_q:
    st.balloons()
    st.success("🎉 太棒了！你已经完成了本学科的所有题目！")
    st.write(f"最终正确率：{accuracy:.1f}%")
else:
    # 获取当前随机序列中的题目
    actual_idx = st.session_state.shuffled_indices[st.session_state.current_idx_in_list]
    q = st.session_state.all_questions[actual_idx]
    
    st.divider()
    st.markdown(f"**随机序列：{st.session_state.current_idx_in_list + 1} / {total_q}** (原题号: {actual_idx + 1})")
    st.markdown(f"#### {q['question']}")
    
    # 根据是否答错锁定选项
    is_disabled = st.session_state.error_mode
    
    user_choice = st.radio(
        "请选择答案：", 
        q['options'], 
        index=None, 
        key=f"q_{actual_idx}", # 确保每道题的单选框是独立的
        disabled=is_disabled
    )
    
    # --- 自动判断逻辑 ---
    if user_choice and not st.session_state.error_mode:
        correct_letter = q['answer'].strip().upper()
        
        if user_choice.startswith(correct_letter):
            st.session_state.stats["correct"] += 1
            st.success("✅ 回答正确！")
            time.sleep(0.6) # 短暂延迟方便确认
            st.session_state.current_idx_in_list += 1
            st.rerun()
        else:
            st.session_state.stats["incorrect"] += 1
            st.session_state.error_mode = True
            st.rerun()
    
    # --- 错误拦截模式 ---
    if st.session_state.error_mode:
        st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
        if st.button("下一题 ➔", type="primary"):
            st.session_state.error_mode = False
            st.session_state.current_idx_in_list += 1
            st.rerun()