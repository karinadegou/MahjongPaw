import os

def create_dir(dir_path):
    """创建目录，已存在则跳过"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"✅ 成功创建目录：{dir_path}")
    else:
        print(f"⚠️  目录已存在，跳过：{dir_path}")

def create_file(file_path):
    """创建空文件，已存在则跳过"""
    # 先确保文件所在目录存在
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建空文件
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            # 给__init__.py添加初始化注释
            if os.path.basename(file_path) == "__init__.py":
                f.write("# 模块初始化文件\n")
        print(f"✅ 成功创建文件：{file_path}")
    else:
        print(f"⚠️  文件已存在，跳过：{file_path}")

def main():
    # 项目根目录名称
    PROJECT_NAME = "ri_mahjong_helper_agent"
    project_root = os.path.join(os.getcwd(), PROJECT_NAME)
    print("=" * 50)
    print(f"开始创建【日麻小助手Agent】项目架构")
    print(f"项目根目录：{project_root}")
    print("=" * 50 + "\n")

    # 1. 定义所有需要创建的目录
    dir_list = [
        f"{PROJECT_NAME}/config",
        f"{PROJECT_NAME}/perception/cv_module",
        f"{PROJECT_NAME}/world_model/entities",
        f"{PROJECT_NAME}/decision/point_calculator",
        f"{PROJECT_NAME}/decision/hand_strategy",
        f"{PROJECT_NAME}/execution/llm_client",
        f"{PROJECT_NAME}/utils",
        f"{PROJECT_NAME}/models",
        f"{PROJECT_NAME}/img",
        f"{PROJECT_NAME}/tests"
    ]

    # 2. 定义所有需要创建的文件
    file_list = [
        f"{PROJECT_NAME}/README.md",
        f"{PROJECT_NAME}/requirements.txt",
        f"{PROJECT_NAME}/main.py",
        f"{PROJECT_NAME}/config/global_config.py",
        f"{PROJECT_NAME}/config/yolo_config.yaml",
        f"{PROJECT_NAME}/config/llm_prompt.py",
        f"{PROJECT_NAME}/perception/__init__.py",
        f"{PROJECT_NAME}/perception/data_input.py",
        f"{PROJECT_NAME}/perception/cv_module/__init__.py",
        f"{PROJECT_NAME}/perception/cv_module/screen_capture.py",
        f"{PROJECT_NAME}/perception/cv_module/yolo_detector.py",
        f"{PROJECT_NAME}/perception/cv_module/manual_correction.py",
        f"{PROJECT_NAME}/perception/cv_module/utils.py",
        f"{PROJECT_NAME}/world_model/__init__.py",
        f"{PROJECT_NAME}/world_model/game_frame.py",
        f"{PROJECT_NAME}/world_model/status_manager.py",
        f"{PROJECT_NAME}/world_model/entities/__init__.py",
        f"{PROJECT_NAME}/world_model/entities/mahjong_table.py",
        f"{PROJECT_NAME}/world_model/entities/player.py",
        f"{PROJECT_NAME}/world_model/entities/hand.py",
        f"{PROJECT_NAME}/world_model/entities/mahjong_tile.py",
        f"{PROJECT_NAME}/decision/__init__.py",
        f"{PROJECT_NAME}/decision/strategy_optimize.py",
        f"{PROJECT_NAME}/decision/point_calculator/__init__.py",
        f"{PROJECT_NAME}/decision/point_calculator/fan_fu_calc.py",
        f"{PROJECT_NAME}/decision/point_calculator/point_calc.py",
        f"{PROJECT_NAME}/decision/point_calculator/state_machine.py",
        f"{PROJECT_NAME}/decision/hand_strategy/__init__.py",
        f"{PROJECT_NAME}/decision/hand_strategy/hand_recommend.py",
        f"{PROJECT_NAME}/decision/hand_strategy/probability_tree.py",
        f"{PROJECT_NAME}/decision/hand_strategy/operation_guide.py",
        f"{PROJECT_NAME}/execution/__init__.py",
        f"{PROJECT_NAME}/execution/prompt_engineering.py",
        f"{PROJECT_NAME}/execution/llm_client/__init__.py",
        f"{PROJECT_NAME}/execution/llm_client/base_llm.py",
        f"{PROJECT_NAME}/execution/llm_client/openai_llm.py",
        f"{PROJECT_NAME}/utils/__init__.py",
        f"{PROJECT_NAME}/utils/log_utils.py",
        f"{PROJECT_NAME}/utils/data_utils.py",
        f"{PROJECT_NAME}/utils/ui_utils.py",
        f"{PROJECT_NAME}/models/yolov8_mahjong.pt",
        f"{PROJECT_NAME}/img/img.png",
        f"{PROJECT_NAME}/tests/__init__.py",
        f"{PROJECT_NAME}/tests/test_perception.py",
        f"{PROJECT_NAME}/tests/test_world_model.py",
        f"{PROJECT_NAME}/tests/test_decision.py",
        f"{PROJECT_NAME}/tests/test_execution.py"
    ]

    # 执行创建操作
    print("【第一步】创建目录结构...\n")
    for dir_path in dir_list:
        create_dir(dir_path)

    print("\n" + "=" * 30 + "\n")

    print("【第二步】创建空文件...\n")
    for file_path in file_list:
        create_file(file_path)

    print("\n" + "=" * 50)
    print("🎉 项目架构创建完成！")
    print(f"项目根目录：{project_root}")
    print("\n后续操作建议：")
    print("1. 打开 requirements.txt 添加项目依赖（yolov8、opencv-python 等）")
    print("2. 将 YOLO 权重文件放入 models 目录")
    print("3. 将流程图 img.png 放入 img 目录")
    print("4. 开始填充各模块业务代码")
    print("=" * 50)

if __name__ == "__main__":
    main()