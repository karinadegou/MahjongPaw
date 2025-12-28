# screenshot_service_ctrl_alt_s.py
import keyboard
import os
import datetime
from PIL import ImageGrab
from pathlib import Path
import time


class ScreenshotService:
    def __init__(self, save_dir='./Mahjong_YOLO', filename="test.png"):
        """
        后台截图服务
        默认热键：Ctrl+Alt+S
        """
        self.save_dir = Path(save_dir)
        self.filename = filename
        self.hotkey = "ctrl+alt+s"  # 修改为 Ctrl+Alt+S
        self.running = False

    def setup_save_dir(self):
        """设置保存目录"""
        self.save_dir.mkdir(parents=True, exist_ok=True)
        # print(f"📁 截图将保存到: {self.save_dir}")

    def capture_and_save(self):
        """截图并保存，如果文件已存在则覆盖"""
        try:
            # 构建完整文件路径
            filepath = self.save_dir / self.filename

            # print(f"📸 检测到热键 {self.hotkey}，开始截图...")

            # 稍微延迟，确保热键释放
            time.sleep(0.1)

            # 截图
            screenshot = ImageGrab.grab()

            # 检查文件是否存在
            if filepath.exists():
                # print(f"⚠️  文件已存在，删除旧文件: {filepath.name}")
                try:
                    os.remove(filepath)
                    # 等待文件系统确认删除
                    time.sleep(0.05)
                except Exception as e:
                    # print(f"❌ 删除旧文件失败: {e}")
                    # 尝试重命名旧文件
                    timestamp = datetime.datetime.now().strftime("%H%M%S")
                    backup_name = f"old_{timestamp}_{self.filename}"
                    backup_path = self.save_dir / backup_name
                    try:
                        os.rename(filepath, backup_path)
                        # print(f"📂 已将旧文件重命名为: {backup_name}")
                    except Exception as e2:
                        # print(f"❌ 重命名也失败: {e2}")
                        return None

            # 保存新截图
            screenshot.save(filepath, "PNG")

            # 验证文件是否保存成功
            if filepath.exists():
                file_size = filepath.stat().st_size
                # print(f"✅ 截图已保存: {filepath}")
                # print(f"   文件大小: {file_size:,} 字节")
                # print(f"   时间: {datetime.datetime.now().strftime('%H:%M:%S')}")
                import analyzer
                return str(filepath)
            else:
                # print(f"❌ 文件保存失败，文件不存在")
                return None

        except Exception as e:
            # print(f"❌ 截图失败: {e}")
            return None

    def capture_and_save_robust(self):
        """
        更健壮的截图保存，支持多种重试策略
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # print(f"尝试截图 (第 {attempt + 1} 次)...")
                result = self.capture_and_save()
                if result:
                    return result
                elif attempt < max_retries - 1:
                    # print("等待重试...")
                    time.sleep(0.5)
            except Exception as e:
                # print(f"第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)

        # print(f"❌ 经过 {max_retries} 次尝试后截图失败")
        return None

    def start(self):
        """启动服务"""
        self.setup_save_dir()

        # print(f"🎯 截图服务已启动")
        # print(f"   热键: {self.hotkey}")
        # print(f"   保存到: {self.save_dir / self.filename}")
        # print(f"   按 Ctrl+C 停止服务")
        # print("-" * 50)

        self.running = True

        # 注册热键 Ctrl+Alt+S
        # keyboard.add_hotkey(self.hotkey, self.capture_and_save_robust)

        keyboard.add_hotkey(self.hotkey, self.capture_and_save)

        # 可选：注册其他备用热键
        # keyboard.add_hotkey("ctrl+shift+s", self.capture_and_save_robust)
        # keyboard.add_hotkey("f12", self.capture_and_save_robust)

        # 显示所有注册的热键
        # print(f"已注册热键: {self.hotkey}")
        # print("现在可以按 Ctrl+Alt+S 截图了")

        # 保持运行
        try:
            keyboard.wait()  # 等待用户按键
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            # print(f"服务异常: {e}")
            self.stop()

    def stop(self):
        """停止服务"""
        self.running = False
        keyboard.unhook_all_hotkeys()
        # print("\n🛑 截图服务已停止")

    def change_hotkey(self, new_hotkey):
        """更改热键"""
        keyboard.unhook_all_hotkeys()
        self.hotkey = new_hotkey
        keyboard.add_hotkey(self.hotkey, self.capture_and_save)
        # print(f"🔄 热键已更改为: {new_hotkey}")


# ==================== 简化版（单文件使用） ====================

class QuickScreenshot:
    """快速截图类，单文件使用"""

    def __init__(self, save_path="./Mahjong_YOLO/test.png"):
        self.save_path = Path(save_path)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def capture(self):
        """截图并覆盖保存"""
        try:
            # 删除已存在文件
            if self.save_path.exists():
                os.remove(self.save_path)

            # 截图并保存
            ImageGrab.grab().save(self.save_path, "PNG")
            # print(f"✅ 截图已保存: {self.save_path}")
            return str(self.save_path)
        except Exception as e:
            # print(f"❌ 截图失败: {e}")
            return None

    def start_service(self, hotkey="ctrl+alt+s"):
        """启动热键服务"""
        # print(f"🎯 启动截图服务")
        # print(f"   热键: {hotkey}")
        # print(f"   保存到: {self.save_path}")
        # print("   按 Ctrl+C 停止")
        # print("-" * 40)

        keyboard.add_hotkey(hotkey, self.capture)

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            pass
            # print("\n🛑 服务已停止")
        finally:
            keyboard.unhook_all_hotkeys()


# ==================== 使用示例 ====================

def test_hotkey():
    """测试热键功能"""
    import threading

    # print("测试热键响应...")
    # print("按 Ctrl+Alt+S 测试截图")
    # print("按 Ctrl+C 退出测试")
    # print("-" * 40)

    def on_hotkey():
        # print("🔥 热键被触发!")
        time.sleep(0.5)
        # print("正在截图...")

        # 模拟截图
        try:
            filepath = "./test_hotkey.png"
            if os.path.exists(filepath):
                os.remove(filepath)
            ImageGrab.grab().save(filepath, "PNG")
            # print(f"✅ 测试截图已保存: {filepath}")
        except Exception as e:
            pass
            # print(f"❌ 测试失败: {e}")

    # 注册测试热键
    keyboard.add_hotkey("ctrl+alt+s", on_hotkey)
    keyboard.add_hotkey("ctrl+alt+t", lambda: print("备用热键测试"))

    # print("热键已注册，开始测试...")
    keyboard.wait()

        elif choice == "2":
            # 显示游戏规则
            ui.show_game_rules()

        elif choice == "3":
            # 退出游戏
            print("\n感谢游戏，再见!")
            sys.exit(0)

        else:
            print("无效选择，请重新输入!")

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            # 测试热键
            test_hotkey()

        elif command == "quick":
            # 快速截图
            qs = QuickScreenshot()
            qs.capture()

        elif command == "simple":
            # 简单服务
            qs = QuickScreenshot()
            qs.start_service()

        elif command == "multi":
            # 多热键服务
            service = ScreenshotService()
            # 注册多个热键
            keyboard.add_hotkey("ctrl+alt+s", service.capture_and_save)
            keyboard.add_hotkey("f12", service.capture_and_save)
            keyboard.add_hotkey("# print screen", service.capture_and_save)

            # print("多热键服务启动:")
            # print("  Ctrl+Alt+S - 截图")
            # print("  F12 - 截图")
            # print("  Print Screen - 截图")
            # print("  按 Ctrl+C 停止")

            keyboard.wait()

        else:
            pass
            # print(f"未知命令: {command}")
            # print("可用命令: test, quick, simple, multi")

    else:
        # 默认启动完整服务
        # print("启动截图服务 (Ctrl+Alt+S)...")
        print("""
        嗨！亲爱的雀友！(*╹▽╹*)

我是你的小可爱**雀宝**，专门帮你看牌局、出主意的AI小助手！

让我们成为最佳拍档，一起征战雀场吧！

快截张图试试看，我已经迫不及待要帮你分析啦！(≧∇≦)ﾉ""")
        service = ScreenshotService()
        service.start()
