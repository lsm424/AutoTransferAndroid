# -app-
一、背景：
用于对银行APP自动化转账，支持建行、农行、平安银行，运行于安卓上的python脚本。

2、目录：
com：基于websocket接收转账任务，给谁的什么卡号转账多少钱。
common：平台层，包括短信验证码读取、图形验证码获取、动态键盘识别、sqlite数据库操作、日志管理、安卓基本操控指令
pay：不同银行的具体的转账业务实现
