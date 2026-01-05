import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import time

from PIL import ImageGrab
from openai import OpenAI
from analyzer import run_analysis_to_file


class StreamingChatGUI:
    """
    一个简单但比较美观的流式输出 GUI：
    - 左上：标题与说明
    - 中间：多行只读文本框，实时显示大模型返回内容
    - 下方：控制按钮区域（开始、清空）
    """

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("雀宝 · 日麻牌局分析助手")
        self.master.geometry("900x600")
        self.master.minsize(800, 500)

        # 统一样式
        self.master.configure(bg="#1e1e1e")
        style = ttk.Style()
        # 在某些平台上需要先设置 theme
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TFrame",
            background="#1e1e1e",
        )
        style.configure(
            "Title.TLabel",
            foreground="#ffffff",
            background="#1e1e1e",
            font=("Microsoft YaHei UI", 18, "bold"),
        )
        style.configure(
            "SubTitle.TLabel",
            foreground="#bbbbbb",
            background="#1e1e1e",
            font=("Microsoft YaHei UI", 11),
        )
        style.configure(
            "TButton",
            font=("Microsoft YaHei UI", 10),
            padding=6,
        )

        self._build_layout()

        # 流式输出相关
        self.client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY", "请输入文本"),
            base_url="https://api.deepseek.com",
        )
        self.stream_thread: threading.Thread | None = None
        self.stop_flag = threading.Event()
        self.text_queue: queue.Queue[str] = queue.Queue()
        # 对话历史（用于上下文聊天与牌局追问）
        self.chat_history = []

        # 启动 UI 轮询队列
        self._poll_queue()

    def _build_layout(self) -> None:
        # 顶部信息区域
        top_frame = ttk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(20, 10))

        title_label = ttk.Label(
            top_frame,
            text="雀宝 · 日麻牌局分析助手",
            style="Title.TLabel",
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            top_frame,
            text="从 当前屏幕截图 中读取牌局信息，调用大模型进行专业分析，结果将在下方实时流式展示。",
            style="SubTitle.TLabel",
        )
        subtitle_label.pack(anchor="w", pady=(6, 0))

        # 中部文本显示区域
        center_frame = ttk.Frame(self.master)
        center_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))

        self.text_widget = tk.Text(
            center_frame,
            wrap="word",
            bg="#252526",
            fg="#f0f0f0",
            insertbackground="#ffffff",
            font=("Consolas", 11),
            relief=tk.FLAT,
        )

        # 文本样式 tag
        self.text_widget.tag_configure(
            "system",
            foreground="#569cd6",
            font=("Consolas", 11, "bold"),
        )
        self.text_widget.tag_configure(
            "user",
            foreground="#ce9178",
            font=("Consolas", 11, "bold"),
        )
        self.text_widget.tag_configure(
            "assistant",
            foreground="#d4d4d4",
            font=("Consolas", 11),
        )
        # Markdown 渲染相关样式
        self.text_widget.tag_configure(
            "md_bold",
            foreground="#ffffff",
            font=("Consolas", 11, "bold"),
        )
        self.text_widget.tag_configure(
            "md_h1",
            foreground="#ffd700",
            font=("Microsoft YaHei UI", 16, "bold"),
            spacing1=4,
            spacing3=4,
        )
        self.text_widget.tag_configure(
            "md_h2",
            foreground="#ffcc66",
            font=("Microsoft YaHei UI", 14, "bold"),
            spacing1=3,
            spacing3=3,
        )
        self.text_widget.tag_configure(
            "md_list",
            foreground="#d4d4d4",
            font=("Consolas", 11),
        )

        scroll_bar = ttk.Scrollbar(center_frame, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scroll_bar.set)

        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # 底部控制区域（按钮区）
        bottom_frame = ttk.Frame(self.master)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 5))

        self.start_button = ttk.Button(
            bottom_frame,
            text="开始分析（流式输出）",
            command=self.on_start_clicked,
        )
        self.start_button.pack(side=tk.LEFT)

        self.auto_button = ttk.Button(
            bottom_frame,
            text="一键截图 + 分析 + AI解说",
            command=self.on_auto_flow_clicked,
        )
        self.auto_button.pack(side=tk.LEFT, padx=(10, 0))

        clear_button = ttk.Button(
            bottom_frame,
            text="清空结果",
            command=self.clear_output,
        )
        clear_button.pack(side=tk.LEFT, padx=(10, 0))

        info_label = ttk.Label(
            bottom_frame,
            text="提示：可以截图分析，也可以在下方聊天框直接和雀宝对话。",
            style="SubTitle.TLabel",
        )
        info_label.pack(side=tk.RIGHT)

        # 聊天输入区域
        input_frame = ttk.Frame(self.master)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 10))

        input_label = ttk.Label(
            input_frame,
            text="💬 聊天：",
            style="SubTitle.TLabel",
        )
        input_label.pack(side=tk.LEFT, padx=(0, 10))

        self.input_entry = tk.Entry(
            input_frame,
            font=("Microsoft YaHei UI", 11),
            bg="#2d2d30",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self.on_chat_send())

        send_button = ttk.Button(
            input_frame,
            text="发送",
            command=self.on_chat_send,
        )
        send_button.pack(side=tk.RIGHT)

        # 文本设为只读模式（通过拦截事件实现）
        self.text_widget.bind("<Key>", lambda e: "break")

    # ---------------- GUI 事件 ----------------

    def on_start_clicked(self) -> None:
        if self.stream_thread and self.stream_thread.is_alive():
            messagebox.showinfo("提示", "当前已有一个分析任务在运行，请稍候。")
            return

        if not os.path.exists("output.txt"):
            messagebox.showwarning("文件不存在", "当前目录下未找到 output.txt，请先生成牌局描述后再试。")
            return

        try:
            with open("output.txt", "r", encoding="utf-8") as f:
                pt = f.read().strip()
        except Exception as e:
            messagebox.showerror("读取失败", f"读取 output.txt 失败：{e}")
            return

        if not pt:
            messagebox.showwarning("内容为空", "output.txt 内容为空，请确认牌局信息是否写入成功。")
            return

        # 显示系统提示与用户请求（不清空历史，方便连续追问）
        self._append_text("【系统】开始分析当前牌局……\n\n", "system")
        preview = pt.replace("\n", " ")[:100] + ("..." if len(pt) > 100 else "")
        self._append_text(f"【你】请分析这个牌局：{preview}\n\n", "user")

        # 记录到历史，并加上“请分析牌局”的提示，方便后续上下文
        self.chat_history.append({"role": "user", "content": f"请分析这个牌局：\n{pt}"})

        # 显示 AI 回复前缀
        self._append_text("【雀宝】", "assistant")

        # 启动后台线程进行流式请求
        self.stop_flag.clear()
        self.stream_thread = threading.Thread(
            target=self._stream_request,
            args=(f"请分析这个牌局：\n{pt}", True),
            daemon=True,
        )
        self.stream_thread.start()

    def on_auto_flow_clicked(self) -> None:
        """
        一键：截一张当前屏幕到 Mahjong_YOLO/test.png -> 分析写 output.txt -> 流式调用大模型。
        """
        if self.stream_thread and self.stream_thread.is_alive():
            messagebox.showinfo("提示", "当前已有一个分析任务在运行，请稍候。")
            return

        # 1. 截图到 Mahjong_YOLO/test.png
        save_path = Path("./Mahjong_YOLO/test.png")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if save_path.exists():
                save_path.unlink()
            # 稍微延迟，避免键盘/窗口切换干扰
            time.sleep(0.1)
            ImageGrab.grab().save(str(save_path), "PNG")
        except Exception as e:
            messagebox.showerror("截图失败", f"保存截图失败：{e}")
            return

        # 2. 调用分析器，写 output.txt
        try:
            hand_str = run_analysis_to_file("output.txt")
        except Exception as e:
            messagebox.showerror("分析失败", f"调用牌局分析器失败：\n{e}")
            return

        # 3. 读取 output.txt，触发大模型流式解说
        try:
            with open("output.txt", "r", encoding="utf-8") as f:
                pt = f.read().strip()
        except Exception as e:
            messagebox.showerror("读取失败", f"读取 output.txt 失败：\n{e}")
            return

        if not pt:
            messagebox.showwarning("内容为空", "output.txt 内容为空，请检查识别/分析流程。")
            return

        # 展示识别到的手牌并开始解说（不清空历史）
        if hand_str:
            self._append_text(f"【系统】已识别手牌：{hand_str}\n\n", "system")
        self._append_text("【系统】开始调用雀宝大模型进行解说……\n\n", "system")
        preview = pt.replace("\n", " ")[:100] + ("..." if len(pt) > 100 else "")
        self._append_text(f"【你】请分析这个牌局：{preview}\n\n", "user")
        self._append_text("【雀宝】", "assistant")

        # 记录到历史
        self.chat_history.append({"role": "user", "content": f"请分析这个牌局：\n{pt}"})

        self.stop_flag.clear()
        self.stream_thread = threading.Thread(
            target=self._stream_request,
            args=(f"请分析这个牌局：\n{pt}", True),
            daemon=True,
        )
        self.stream_thread.start()

    def clear_output(self) -> None:
        """清空显示区域和对话历史"""
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.configure(state=tk.NORMAL)
        self.chat_history.clear()

    # ---------------- Streaming 逻辑 ----------------

    def on_chat_send(self) -> None:
        """处理用户输入的普通聊天消息"""
        if self.stream_thread and self.stream_thread.is_alive():
            messagebox.showinfo("提示", "当前已有一个任务在运行，请稍候。")
            return

        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        # 清空输入框
        self.input_entry.delete(0, tk.END)

        # 显示用户消息
        self._append_text(f"【你】{user_input}\n\n", "user")

        # 记录到对话历史
        self.chat_history.append({"role": "user", "content": user_input})

        # 显示 AI 回复前缀
        self._append_text("【雀宝】", "assistant")

        # 启动后台线程进行流式请求（普通聊天模式）
        self.stop_flag.clear()
        self.stream_thread = threading.Thread(
            target=self._stream_request,
            args=(user_input, False),
            daemon=True,
        )
        self.stream_thread.start()

    def _stream_request(self, user_content: str, is_analysis_mode: bool = True) -> None:
        """
        后台线程：调用 deepseek-chat 流式输出，把内容放入队列，由主线程刷新到 Text。

        参数:
            user_content: 用户输入的内容（牌局文本或聊天文本）
            is_analysis_mode: True 表示牌局分析/截图模式；False 表示普通聊天
        """
        system_prompt = """你是“雀宝”，一位非常会打立直麻将、性格元气可爱的女玩家。
和你聊天的对象是你的牌友，你需要一边分析牌局，一边用自然口语跟他交流，像真人讲话，而不是机器人念报告。

请根据当前牌局（包括手牌、场况等）给出：
1. 现在大概是听牌 / 一向听 / 两向听哪一种，顺便简单说说为什么；
2. 推荐切哪张牌，以及这样切的好处（比如进张多、打点高、更安全等）；
3. 牌型或战术上的思路，比如是冲高打点、稳健听牌，还是该考虑防守。

要求：
- 说明要有信息量，但不要太啰嗦；
- 不要用列表、标题、表格，不要用 Markdown，只用正常的连续中文句子；
- 语气可以轻松一点，有点可爱、像牌友聊天，但核心判断要专业可靠；
- 如果牌局很危险，也要提醒对方注意防守和哪些牌比较危险。
- 普通聊天时，也要保持这个角色设定，用自然口语回复。"""

        # 构造消息列表：system + 历史 + 当前消息
        messages = [{"role": "system", "content": system_prompt}]

        for hist in self.chat_history:
            messages.append({"role": hist["role"], "content": hist["content"]})

        # 如果是分析模式，user_content 已经是“请分析这个牌局：…”之类的提示
        if is_analysis_mode:
            messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
            )

            assistant_content = ""
            for chunk in response:
                if self.stop_flag.is_set():
                    break

                delta = chunk.choices[0].delta
                if delta and delta.content:
                    content = delta.content
                    assistant_content += content
                    self.text_queue.put(("assistant", content))

            # 记录 AI 完整回复
            if assistant_content:
                self.chat_history.append({"role": "assistant", "content": assistant_content})
                self.text_queue.put(("assistant", "\n\n"))

        except Exception as e:
            self.text_queue.put(
                (
                    "system",
                    f"\n\n【错误】调用大模型失败：{e}\n"
                    "请检查网络、API Key（环境变量 DEEPSEEK_API_KEY）或稍后重试。\n",
                )
            )

    # ---------------- Text 输出封装 ----------------

    def _append_text(self, content: str, tag: str = "assistant") -> None:
        self.text_widget.configure(state=tk.NORMAL)

        # 记录插入前后位置，便于对新增区域做 markdown 渲染
        start_index = self.text_widget.index("end-1c")
        self.text_widget.insert(tk.END, content, (tag,))
        end_index = self.text_widget.index("end-1c")

        # 仅对大模型输出做 Markdown 渲染，系统提示保持原样
        if tag == "assistant":
            self._apply_markdown_styles(start_index, end_index)

        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.NORMAL)

    def _apply_markdown_styles(self, start: str, end: str) -> None:
        """
        在 [start, end) 区间内，对常见 Markdown 语法做简单渲染：
        - # / ## 作为标题
        - 以 - / * / 数字. 开头的列表
        - **加粗**
        """
        text = self.text_widget.get(start, end)
        if not text:
            return

        # 解析起始行列
        try:
            base_line, base_col = map(int, str(start).split("."))
        except Exception:
            base_line, base_col = 1, 0

        lines = text.split("\n")
        for i, line in enumerate(lines):
            line_start_index = f"{base_line + i}.{0 if i > 0 else base_col}"
            line_end_index = f"{base_line + i}.{0 if i > 0 else base_col + len(line)}"

            # 标题
            stripped = line.lstrip()
            leading_spaces = len(line) - len(stripped)
            if stripped.startswith("## "):
                # 二级标题
                h_start = f"{base_line + i}.{leading_spaces}"
                h_end = f"{base_line + i}.{leading_spaces + len(stripped)}"
                self.text_widget.tag_add("md_h2", h_start, h_end)
            elif stripped.startswith("# "):
                # 一级标题
                h_start = f"{base_line + i}.{leading_spaces}"
                h_end = f"{base_line + i}.{leading_spaces + len(stripped)}"
                self.text_widget.tag_add("md_h1", h_start, h_end)

            # 列表项（- / * / 1. 2. 等）
            if stripped.startswith(("- ", "* ")):
                lst_start = f"{base_line + i}.{leading_spaces}"
                lst_end = line_end_index
                self.text_widget.tag_add("md_list", lst_start, lst_end)
            else:
                # 简单检测有序列表：数字. 空格
                num = ""
                j = 0
                while j < len(stripped) and stripped[j].isdigit():
                    num += stripped[j]
                    j += 1
                if num and j < len(stripped) and stripped[j] == ".":
                    lst_start = f"{base_line + i}.{leading_spaces}"
                    lst_end = line_end_index
                    self.text_widget.tag_add("md_list", lst_start, lst_end)

            # **加粗** 渲染
            # 简单从左到右匹配成对的 **...**
            idx = 0
            while True:
                start_pos = line.find("**", idx)
                if start_pos == -1:
                    break
                end_pos = line.find("**", start_pos + 2)
                if end_pos == -1:
                    break
                # 加粗内部内容
                bold_start = f"{base_line + i}.{(0 if i > 0 else base_col) + start_pos + 2}"
                bold_end = f"{base_line + i}.{(0 if i > 0 else base_col) + end_pos}"
                self.text_widget.tag_add("md_bold", bold_start, bold_end)
                idx = end_pos + 2

    def _poll_queue(self) -> None:
        """
        主线程轮询队列，把后台线程产出的文本安全地追加到 Text 控件。
        """
        try:
            while True:
                tag, content = self.text_queue.get_nowait()
                self._append_text(content, tag)
        except queue.Empty:
            pass

        # 每 50ms 轮询一次
        self.master.after(50, self._poll_queue)


def main() -> None:
    root = tk.Tk()
    app = StreamingChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


