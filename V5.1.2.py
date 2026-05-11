import sys
import os
import re
import csv
import json
import ctypes
import numpy as np
import cv2
import time
import pyautogui
try:
    import pyperclip
except Exception:
    pyperclip = None
import tifffile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QPushButton, QFileDialog, QLabel, QLineEdit, QTextEdit, QDialog,
                            QGroupBox, QSpinBox, QDoubleSpinBox, QMessageBox, QCheckBox, QDialogButtonBox,
                            QProgressBar, QScrollArea, QFrame, QComboBox, QColorDialog, QStackedWidget, QSizePolicy,
                            QListView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPointF, QLineF, QMutex, QMutexLocker, QWaitCondition, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QTextCursor, QIcon, QCursor

from pynput.keyboard import GlobalHotKeys
import traceback

if getattr(sys, "frozen", False):
    APP_RESOURCE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    APP_SETTINGS_DIR = os.path.dirname(sys.executable)
else:
    APP_RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_SETTINGS_DIR = APP_RESOURCE_DIR

APP_ICON_PATH = os.path.join(APP_RESOURCE_DIR, "icon.png")
APP_SETTINGS_PATH = os.path.join(APP_SETTINGS_DIR, "app_settings.json")

ZH_TO_EN = {
    "OptoStim2P v5.1.2": "OptoStim2P v5.1.2",
    "激活": "Stimulation",
    "刺激": "Stimulation",
    "检测": "Detection",
    "数据源配置": "Input Data",
    "输入数据": "Input Data",
    "校准参数": "Calibration Parameters",
    "程序控制": "Single-cell Control",
    "单细胞控制": "Single-cell Control",
    "实时预览与控制(单击左键校准，右键跳过)": "Interactive Alignment",
    "交互式对齐": "Interactive Alignment",
    "运行日志": "Log",
    "日志": "Log",
    "起始索引:": "Start Index:",
    "结束索引:": "End Index:",
    "ROI直径:": "ROI Diameter (px):",
    "ROI直径(px):": "ROI Diameter (px):",
    "延迟(s):": "Delay (s):",
    "显示状态": "View Status",
    "查看状态": "View Status",
    "单细胞校准": "Preview",
    "单细胞预览": "Single-cell Preview",
    "查看预览": "Preview",
    "预览": "Preview",
    "注册位置:X (Ctrl+1); Y (Ctrl+2); Stimulate (Ctrl+3)": "Register positions: X (Ctrl+1); Y (Ctrl+2); Stimulate (Ctrl+3)",
    "加载stat.npy": "stat.npy",
    "加载iscell.npy": "iscell.npy",
    "加载Suite2P图像": "Suite2p Reference Image",
    "加载显微镜图像": "Microscope Image",
    "stat.npy": "stat.npy",
    "iscell.npy": "iscell.npy",
    "Suite2p 参考图像": "Suite2p Reference Image",
    "显微镜图像": "Microscope Image",
    "未选择": "Not loaded",
    "未加载": "Not loaded",
    "未选择文件": "No file selected",
    "鼠标注册": "Mouse Registration",
    "鼠标位置注册状态": "Mouse registration status",
    "ROI坐标校准": "ROI Coordinate Calibration",
    "模糊Sigma:": "Sigma Blur:",
    "最大匹配:": "Max Matches:",
    "对比度阈值:": "Contrast Threshold:",
    "匹配比率:": "Match Ratio:",
    "补偿X:": "X Offset:",
    "补偿Y:": "Y Offset:",
    "X补偿(pix):": "X Offset (pix):",
    "Y补偿(pix):": "Y Offset (pix):",
    "计算校准": "Compute Calibration",
    "可视化校准": "Visualize Calibration",
    "清空校准": "Clear Calibration",
    "计算全局校准": "Compute Global Calibration",
    "可视化全局校准": "Visualize Global Calibration",
    "Z轴偏移检查": "Z-shift Check",
    "Z-stack Image": "Z-stack Image",
    "计算z轴偏移": "Compute Z-shift",
    "XY校准": "XY Calibration",
    "Z轴校准": "Z Calibration",
    "全局校准": "Global Calib.",
    "查看校准": "View Calib.",
    "Z轴偏移": "Z Calib.",
    "配准": "Registration",
    "XY配准": "XY Registration",
    "Z轴对齐": "Z Alignment",
    "计算配准": "Compute Registration",
    "查看对齐": "View Alignment",
    "估计Z偏移": "Estimate Z Shift",
    "清除配准": "Reset Registration",
    "更新Live图像": "Refresh Live Image",
    "准备就绪 | 左键微调，右键跳过": "Ready | Left click to adjust, right click to skip",
    "开始 (Ctrl+K)": "Start (Ctrl+K)",
    "暂停/继续(Ctrl+P)": "Pause/Resume (Ctrl+P)",
    "停止(Ctrl+Q)": "Stop (Ctrl+Q)",
    "跳过(Ctrl+/)": "Skip (Ctrl+/)",
    "未开始": "Not started",
    "进度": "Progress",
    "已暂停": "Paused",
    "已停止": "Stopped",
    "已完成": "Completed",
    "错误中断": "Interrupted",
    "已刺激": "Stimulated",
    "已跳过": "Skipped",
    "未注册": "Not registered",
    "已注册": "Registered",
    "保存偏移量": "Save Offsets",
    "平均刚性校准": "Average Rigid Calibration",
    "Live": "Live",
    "Reference": "Reference",
    "Live：左键校准，右键跳过 | Reference：仅供参考": "Live: left-click align, right-click skip | Reference: view only",
    "更多设置": "Settings",
    "Mask透明度:": "Mask Alpha:",
    "Patch Size (px):": "Patch Size (px):",
    "图像高斯模糊Kernel（奇数）:": "Gaussian Blur Kernel (odd):",
    "图像Gamma值:": "Image Gamma:",
    "Gamma变换阈值:": "Gamma Threshold:",
    "pyautogui 延迟 (ms):": "pyautogui Delay (ms):",
    "激活检测": "Activation Check",
    "检测通道:": "Detection Channel",
    "检测通道": "Detection Channel",
    "显示/图像": "Display / Image",
    "自动化": "Automation",
    "位置测试": "Position Test",
    "测试 X 输入": "Test X Input",
    "测试 Y 输入": "Test Y Input",
    "测试 X/Y 输入": "Test X/Y Input",
    "测试 Stimulate 点击": "Test Stimulate Click",
    "维护操作": "Maintenance",
    "保存文件后缀:": "Save Filename Suffix:",
    "保存日志和激活列表": "Save Log & Stimulated List",
    "重置已激活ROI列表": "Reset Stimulated ROI List",
    "重置校准": "Reset Calibration",
    "图像降噪模糊": "Image Denoise Blur",
    "导出界面截图": "Export UI Screenshot",
    "保存界面截图": "Save UI Screenshot",
    "界面截图已保存到:\n{file_path}": "UI screenshot saved to:\n{file_path}",
    "保存界面截图失败: {error}": "Failed to save UI screenshot: {error}",
    "自动保存": "Auto Save",
    "窗口置顶": "Always on Top",
    "保存": "Save",
    "取消": "Cancel",
    "Language": "Language",
    "语言": "Language",
    "中文": "中文",
    "English": "English",
    "错误": "Error",
    "警告": "Warning",
    "成功": "Success",
    "提示": "Info",
    "注意": "Notice",
    "完成": "Done",
    "参数说明 Tips": "Tips",
    "温馨提醒": "Reminder",
    "Post Check 详情图": "Post Check Details",
    "可视化选项": "Visualization",
    "热图颜色:": "Colormap:",
    "显示 ROI 位置": "Show ROI",
    "轮廓粗细:": "Outline Width:",
    "激活:": "Active:",
    "未激活:": "Inactive:",
    "热图 Min:": "Heatmap Min:",
    "热图 Max:": "Heatmap Max:",
    "保存校正后图像": "Save Corrected Image",
    "保存热图": "Save Heatmap",
    "导出ROI CSV": "Export ROI CSV",
    "选择颜色": "Choose Color",
    "没有可保存的校正后图像": "No corrected image available to save.",
    "图像已保存到:\n{file_path}": "Image saved to:\n{file_path}",
    "没有可保存的热图。": "No heatmap available to save.",
    "热图已保存到:\n{file_path}": "Heatmap saved to:\n{file_path}",
    "ROI CSV 已生成:\n{csv_path}": "ROI CSV generated:\n{csv_path}",
    "当前结果没有可导出的 ROI CSV。": "No ROI CSV is available for the current result.",
    "Post-stimulation (Corrected)": "Post-stimulation (Corrected)",
    "ROI Metric Histogram": "ROI Metric Histogram",
    "Fraction of cells": "Fraction of cells",
    "No ROI metrics": "No ROI metrics",
    "Heatmap": "Heatmap",
    "Post Check 工作台": "Post Check Workspace",
    "当前上下文：未带入主程序数据": "Current Context: no data imported from main window",
    "基础数据": "Input Data",
    "加载 stat.npy": "stat.npy",
    "加载 iscell.npy": "iscell.npy",
    "加载 Suite2P 图像": "Suite2p Reference Image",
    "加载激活前图像": "Pre-stimulation Image",
    "刺激前图像": "Pre-stimulation Image",
    "Post Check 输入": "Post Check Inputs",
    "加载激活后图像": "Post-stimulation Image",
    "刺激后图像": "Post-stimulation Image",
    "加载 ROI 子集文件": "Load ROI Subset File",
    "未选择 ROI 子集文件": "No ROI subset file selected",
    "检测参数": "Detection Parameters",
    "阈值(倍数):": "Threshold (fold):",
    "Fold Change阈值:": "Fold Change Threshold",
    "阈值(差值):": "Difference Threshold",
    "直径 (px):": "Diameter (px):",
    "细胞直径(px):": "Cell Diameter (px)",
    "激活后X位移": "Post X Shift",
    "激活后Y位移": "Post Y Shift",
    "X位移(Post)": "X Shift (Post)",
    "Y位移(Post)": "Y Shift (Post)",
    "自动校准位移": "Auto Shift Calibration",
    "估计位移": "Estimate Shift",
    "检测激活": "Evaluate Activation",
    "计算激活": "Compute Activation",
    "自动位移校准": "Auto Shift Calibration",
    "开始检测": "Start Detection",
    "方法:": "Method:",
    "ROI 直径 (pix):": "ROI Diameter (pix):",
    "后图 X 位移:": "Post X Shift:",
    "后图 Y 位移:": "Post Y Shift:",
    "检测摘要": "Detection Summary",
    "未检测": "Not evaluated",
    "已检测 ROI": "Evaluated ROI",
    "激活成功": "Activated",
    "成功率": "Success Rate",
    "方法": "Method",
    "阈值": "Threshold",
    "位移": "Shift",
    "结果操作": "Result Actions",
    "尚未完成检测": "Detection not completed yet",
    "查看详情图": "View Detail Plot",
    "检测完成": "Detection Complete",
    "Pixel-wise Fold Increase": "Pixel-wise Fold Increase",
    "ROI Mean Fold Change": "ROI Mean Fold Change",
    "Pixel-wise Difference (Post - Pre)": "Pixel-wise Difference (Post - Pre)",
    "ROI Mean Difference": "ROI Mean Difference",
    "Info": "Info",
    "No ROI coordinates loaded. Showing only the pixel-wise heatmap.": "No ROI coordinates loaded. Showing only the pixel-wise heatmap.",
    "输入无效": "Invalid input",
    "已加载": "Loaded",
    "手动加载": "Loaded manually",
    "已带入": "Imported",
    "未带入": "Not imported",
    "保存目录": "Save folder",
    "ROI 子集": "ROI subset",
    "启用": "enabled",
    "禁用": "disabled",
    "选择stat文件": "Select stat file",
    "选择iscell文件": "Select iscell file",
    "选择 stat 文件": "Select stat file",
    "选择 iscell 文件": "Select iscell file",
    "选择Suite2P图像": "Select Suite2P image",
    "选择 Suite2P 图像": "Select Suite2P image",
    "选择显微镜图像": "Select microscope image",
    "选择Live图像": "Select live image",
    "选择激活前图像": "Select pre-stimulation image",
    "选择激活后图像": "Select post-stimulation image",
    "选择 ROI 子集文件": "Select ROI subset file",
    "选择保存目录": "Select save folder",
    "ROI 列表 .npy": "ROI list .npy",
    "索引列表 txt/csv": "Index list txt/csv",
    "图像加载失败": "Failed to load image",
    "加载失败": "Load failed",
    "特征检测失败": "Feature detection failed",
    "匹配点不足": "Not enough matched points",
    "总匹配点不足": "Not enough total matched points",
    "单应性矩阵计算失败": "Failed to compute homography matrix",
    "单应性矩阵未计算": "Homography matrix has not been computed",
    "请先计算单应性矩阵": "Please compute the homography matrix first",
    "请先加载两幅图像": "Please load both images first",
    "请先加载suite2p图像": "Please load the Suite2P image first",
    "请检查加载的 stat/iscell 文件": "Please check the loaded stat/iscell files",
    "请先加载激活前和激活后图像": "Please load pre- and post-stimulation images first",
    "请先导入 Z-stack Image": "Please load the Z-stack image first",
    "未从 txt/csv 中解析到 ROI 编号": "No ROI IDs were parsed from the txt/csv file",
    "ROI 子集 .npy 为空": "ROI subset .npy is empty",
    "缺少基础 ROI 数据，请先加载 stat/iscell": "Base ROI data is missing. Please load stat/iscell first",
    "请先加载激活前图像": "Please load the pre-stimulation image first",
    "请先加载激活后图像": "Please load the post-stimulation image first",
    "请先导入 ROI 子集文件": "Please load the ROI subset file first",
    "ROI 子集文件中没有可用的有效 ROI": "No valid ROI is available in the ROI subset file",
    "格式提示": "Format Notice",
    "已清除单应性矩阵": "Cleared homography matrix",
    "别忘了把激光波长改回去！": "Remember to switch the laser wavelength back.",
    "已生成检测结果，可查看详情图。": "Detection result generated. Detail plot is available.",
    "当前状态：": "Current status:",
    "已带入当前 Live 图像": "Imported current live image",
    "已带入当前显微镜图像": "Imported current microscope image",
    "未加载图像，跳过坐标矫正": "No image loaded. Skipping coordinate correction",
    "生成cell mask预览图": "Generated cell mask preview",
    "已清除全局校准": "Cleared global registration",
    "已清除单细胞校准": "Cleared single-cell calibration",
    "已重置排除ROI列表": "Reset excluded ROI list",
    "自动化流程启动...": "Automation started...",
    "自动化已停止": "Automation stopped",
    "未找到有效ROI坐标": "No valid ROI coordinates found",
    "请注册X输入位置": "Please register the X input position",
    "请注册Y输入位置": "Please register the Y input position",
    "请注册stimulate按钮位置": "Please register the stimulate button position",
    "请先注册 X 输入位置": "Please register the X input position first",
    "请先注册 Y 输入位置": "Please register the Y input position first",
    "请先注册 Stimulate 按钮位置": "Please register the Stimulate button position first",
    "超出可跳过范围": "Skip target is out of range",
    "起始索引不能大于结束索引": "Start index cannot be greater than end index",
    "请先加载所有图像和坐标数据": "Please load all images and coordinate data first",
    "无效显微镜数据": "Invalid microscope data",
    "未找到校准数据": "No calibration data found",
    "显微镜与Suite2P patch数量不一致": "Microscope and Suite2P patch counts do not match",
    "无法在Suite2P参考图像中检测到特征点。": "No feature points were detected in the Suite2P reference image.",
    "无法在任何Z轴切片中找到有效的匹配。": "No valid match was found in any Z-stack slice.",
    "Z-stack 必须是多层图像": "Z-stack must be a multi-slice image",
    "日志和激活ROI列表已保存至: ": "Log and stimulated ROI list saved to: ",
    "日志和激活ROI列表已保存至: {log_path}": "Log and stimulated ROI list saved to: {log_path}",
    "输入完成": "Input completed",
    "已有任务运行中": "A task is already running",
    "自动化运行中，请先停止或完成后再进入检测页。": "Automation is running. Please stop it or wait until it finishes before entering Detection.",
    "窗口置顶状态: 启用": "Always-on-top: enabled",
    "窗口置顶状态: 禁用": "Always-on-top: disabled",
    "设置已保存：Mask透明度={alpha}，图像高斯模糊kernel = {kernel}，图像Gamma值={gamma}，ROI直径={roi_diameter}，延迟={delay}ms，模糊降噪={denoise}，自动保存={autosave}，后缀={suffix}": "Settings saved: mask alpha={alpha}, blur kernel={kernel}, gamma={gamma}, ROI diameter={roi_diameter}, delay={delay}ms, denoise={denoise}, autosave={autosave}, suffix={suffix}",
    "语言已保存，重启程序后生效。": "Language saved. Restart the app to apply changes.",
    "语言设置": "Language Setting",
    "PyAutoGUI 关键输入保护已启用": "PyAutoGUI critical input protection enabled",
}

EN_TO_ZH = {v: k for k, v in ZH_TO_EN.items()}

RUNTIME_PREFIX_ZH_TO_EN = {
    "加载 Suite2P 图像: ": "Loaded Suite2P image: ",
    "加载Suite2P图像: ": "Loaded Suite2P image: ",
    "加载显微镜图像: ": "Loaded microscope image: ",
    "加载/更新显微镜图像：": "Loaded/updated microscope image: ",
    "加载Live图像: ": "Loaded live image: ",
    "加载激活前图像: ": "Loaded pre-stimulation image: ",
    "加载激活后图像: ": "Loaded post-stimulation image: ",
    "上采样至": "resized to",
    "激活后图像已应用位移：": "Applied shift to post-stimulation image: ",
    "激活后图像已应用位移: ": "Applied shift to post-stimulation image: ",
    "检测页状态：": "Detection status: ",
    "保存目录 ": "Save path ",
    "激活前图像 ": "Pre image ",
    "ROI 子集 ": "ROI subset ",
    "已检测 ": "Evaluated ",
    "检测完成 (": "Detection complete (",
    "，共检测 ": ", evaluated ",
    "共检测 ": "Evaluated ",
    "成功激活 ": "activated ",
    "ROI metrics CSV saved: ": "ROI metrics CSV saved: ",
    "Failed to save ROI metrics CSV: ": "Failed to save ROI metrics CSV: ",
    "No ROI coordinates loaded. Showing only the pixel-wise heatmap. ROI metric = ": "No ROI coordinates loaded. Showing only the pixel-wise heatmap. ROI metric = ",
    "坐标转换失败: ": "Coordinate transform failed: ",
    "ROI提取错误: ": "ROI extraction error: ",
    "ROI 提取错误: ": "ROI extraction error: ",
    "ROI 子集文件解析失败: ": "ROI subset file parse failed: ",
    "加载失败: ": "Load failed: ",
    "stat 文件加载失败: ": "stat file load failed: ",
    "iscell 文件加载失败: ": "iscell file load failed: ",
    "自动位移校准失败: ": "Auto shift estimation failed: ",
    "自动位移校准失败: OpenCV 错误: ": "Auto shift estimation failed: OpenCV error: ",
    "发生未知错误: ": "Unknown error: ",
    "自动位移校准完成: ": "Auto shift estimation completed: ",
    "最佳位移": "best shift",
    "置信度": "confidence",
    "自动校准完成!\n计算出的位移 X: ": "Auto shift estimation completed.\nCalculated shift X: ",
    " 已更新。": " updated.",
    "开始自动位移校准...": "Starting auto shift estimation...",
    "已完成自动位移校准，当前位移 X ": "Auto shift estimation completed. Current shift X ",
    "保存目录设置为": "Save directory set to ",
    "提取到 ": "Extracted ",
    "提取到": "Extracted ",
    " 个有效ROI": " valid ROIs",
    "个有效ROI": " valid ROIs",
    " 个有效 ROI": " valid ROIs",
    "重置已激活ROI列表": "Reset stimulated ROI list",
    "成功加载 stat 文件": "Loaded stat file successfully",
    "成功加载 iscell 文件": "Loaded iscell file successfully",
    "成功加载 ": "Loaded ",
    " 文件": " file",
    "已导入 ROI 子集文件: ": "Loaded ROI subset file: ",
    "待基础 ROI 数据验证": "pending base ROI data validation",
    "，共 ": ", total ",
    "，有效 ": ", valid ",
    " 个编号": " IDs",
    " 个，无效 ": ", invalid ",
    " 个 ROI": " ROIs",
    " 个ROI": " ROIs",
    "个ROI": " ROIs",
    " 个，成功率 ": ", success rate ",
    "激活成功率：": "Activation success rate: ",
    "各象限特征点分布": "Feature distribution by quadrant",
    "象限": "Quadrant",
    "显微镜": "Microscope",
    "使用": "using ",
    "个匹配点": " matched points",
    "共发现": "Found ",
    "校准成功! 重投影误差: ": "Registration succeeded. Reprojection error: ",
    "像素": " px",
    "单应性矩阵": "Homography matrix",
    "已清除单应性矩阵": "Cleared homography matrix",
    "准备写入坐标 -> X:": "Preparing coordinates -> X:",
    "单细胞校准: ": "Single-cell calibration: ",
    "X输入位置未注册": "X input position is not registered",
    "Y输入位置未注册": "Y input position is not registered",
    "测试 X 输入：写入 ": "Test X input: wrote ",
    "测试 Y 输入：写入 ": "Test Y input: wrote ",
    "测试 X/Y 输入完成": "Test X/Y input completed",
    "Testing X input: moving to ": "Testing X input: moving to ",
    "Testing Y input: moving to ": "Testing Y input: moving to ",
    "Testing X input: wrote 100": "Testing X input: wrote 100",
    "Testing Y input: wrote 100": "Testing Y input: wrote 100",
    "Testing Stimulate click: moving to ": "Testing Stimulate click: moving to ",
    "Testing Stimulate click: clicked ": "Testing Stimulate click: clicked ",
    "鼠标已回到 Live 预览中心: ": "Mouse returned to Live preview center: ",
    "PyAutoGUI 关键输入保护不可用，继续执行: ": "PyAutoGUI critical input protection unavailable; continuing: ",
    "PyAutoGUI 关键输入保护释放失败: ": "Failed to release PyAutoGUI critical input protection: ",
    "如果点击无效，请确认设置窗口没有遮挡注册坐标。": "If the click has no effect, make sure the Settings window is not covering the registered position.",
    "测试 Stimulate 点击: ": "Test Stimulate click: ",
    "测试失败: ": "Test failed: ",
    " 已写入 ": " written: ",
    "跳过 ROI No.": "Skipped ROI No.",
    "跳过": "Skipped ",
    "激活": "Stimulated ",
    "启动自动化: 范围 no.": "Starting automation: range no.",
    "自动化即将启动：保持当前窗口状态，等待目标软件接收输入...": "Automation is about to start: keeping the current window state and waiting for the target software to receive input...",
    "自动化中出现未知错误": "Unknown error during automation",
    "已恢复": "Resumed",
    "已输入ROI ": "Entered ROI ",
    "输入操作失败: ": "Input operation failed: ",
    "点击处理错误: ": "Click handling error: ",
    "恢复 ROI No.": "Restored ROI No.",
    "注册 ": "Registered ",
    "窗口置顶状态: ": "Always-on-top: ",
    "启用": "enabled",
    "禁用": "disabled",
    "校准更新 #": "Calibration update #",
    "标记绘制失败: ": "Marker drawing failed: ",
    "下一个：no.": "Next: no.",
    "坐标转换失败，回退原始坐标: ": "Coordinate transform failed; using original coordinates: ",
    "无法聚焦到 X 输入框: ": "Failed to focus the X input box: ",
    "最佳匹配: slice no. ": "Best match: slice no. ",
    "已加载 Z-stack Image: ": "Loaded Z-stack image: ",
    "Z-stack加载失败: ": "Z-stack load failed: ",
    "特征匹配时发生错误: ": "Feature matching error: ",
    "处理切片时发生错误: ": "Slice processing error: ",
    "无法可视化Z轴校准: ": "Failed to visualize Z alignment: ",
    "OpenCV 错误": "OpenCV error",
    "未知错误": "unknown error",
    "保存失败: ": "Save failed: ",
    "请检查加载的.npy文件": "Please check the loaded .npy files",
    "图像处理失败: ": "Image processing failed: ",
    "日志和激活ROI列表已保存至: ": "Log and stimulated ROI list saved to: ",
    "Suite2P图像加载失败: ": "Suite2P image load failed: ",
    "更新显微镜图像：": "Updated microscope image: ",
    "Masks预览失败: ": "Masks preview failed: ",
    "生成cell mask预览图": "Generated cell mask preview",
    "当前上下文：stat ": "Current context: stat ",
    " | 保存目录 ": " | save folder ",
    " | 激活前图像 ": " | pre-stimulation image ",
    " | 主程序已刺激 ROI ": " | main stimulated ROI ",
    "已带入主程序 stat.npy": "Imported stat.npy from main window",
    "已从主程序带入 stat 数据": "Imported stat data from main window",
    "已带入主程序 iscell.npy": "Imported iscell.npy from main window",
    "已从主程序带入 iscell 数据": "Imported iscell data from main window",
    "已带入主程序 Suite2P 图像": "Imported Suite2P image from main window",
    "已从主程序带入 Suite2P 图像": "Imported Suite2P image from main window",
    "已带入主程序图像": "Imported image from main window",
    "设置已保存：Mask透明度=": "Settings saved: mask alpha=",
    "，图像高斯模糊kernel = ": ", Gaussian blur kernel = ",
    "，图像Gamma值=": ", image gamma=",
    "，ROI直径=": ", ROI diameter=",
    "px，延迟=": "px, delay=",
    "ms，激活检测=": "ms, activation check=",
    "，模糊降噪=": ", denoise=",
    "，自动保存=": ", autosave=",
    "，后缀=": ", suffix=",
    "应用全局校准": "Applied global registration",
    "已应用全局校准": "Applied global registration",
    "已应用单细胞校准": "Applied single-cell calibration",
    "已打开 post-check 界面": "Opened post-check page",
    "自动化流程": "Automation ",
    "已暂停": "paused",
    " 个": "",
    "：": ": ",
    "保存目录设置为": "Save folder set to ",
}

RUNTIME_PREFIX_EN_TO_ZH = {v: k for k, v in RUNTIME_PREFIX_ZH_TO_EN.items()}


def translate_literal(language, text):
    if not isinstance(text, str):
        return text
    if language == "zh":
        return EN_TO_ZH.get(text, text)
    return ZH_TO_EN.get(text, text)


def translate_runtime_text(language, text):
    if not isinstance(text, str):
        return text
    translated = translate_literal(language, text)
    if translated != text:
        return translated
    prefix_map = RUNTIME_PREFIX_ZH_TO_EN if language == "en" else RUNTIME_PREFIX_EN_TO_ZH
    replaced = text
    for source, target in sorted(prefix_map.items(), key=lambda item: len(item[0]), reverse=True):
        if source in replaced:
            replaced = replaced.replace(source, target)
    if replaced != text:
        return replaced
    for source, target in prefix_map.items():
        if text.startswith(source):
            return target + text[len(source):]
    return text


def infer_widget_language(widget):
    current = widget
    for _ in range(24):
        if current is None:
            break
        language = getattr(current, "language", None)
        if language in ("zh", "en"):
            return language
        try:
            current = current.parent()
        except Exception:
            break
    return "en"


def localize_dialog_text(parent, text):
    return translate_runtime_text(infer_widget_language(parent), text)


_ORIGINAL_QMESSAGEBOX_INFORMATION = QMessageBox.information
_ORIGINAL_QMESSAGEBOX_WARNING = QMessageBox.warning
_ORIGINAL_QMESSAGEBOX_CRITICAL = QMessageBox.critical
_ORIGINAL_QFILEDIALOG_GET_OPEN_FILE_NAME = QFileDialog.getOpenFileName
_ORIGINAL_QFILEDIALOG_GET_SAVE_FILE_NAME = QFileDialog.getSaveFileName
_ORIGINAL_QFILEDIALOG_GET_EXISTING_DIRECTORY = QFileDialog.getExistingDirectory


def _localized_information(parent, title, text, *args, **kwargs):
    return _ORIGINAL_QMESSAGEBOX_INFORMATION(
        parent,
        localize_dialog_text(parent, title),
        localize_dialog_text(parent, text),
        *args,
        **kwargs,
    )


def _localized_warning(parent, title, text, *args, **kwargs):
    return _ORIGINAL_QMESSAGEBOX_WARNING(
        parent,
        localize_dialog_text(parent, title),
        localize_dialog_text(parent, text),
        *args,
        **kwargs,
    )


def _localized_critical(parent, title, text, *args, **kwargs):
    return _ORIGINAL_QMESSAGEBOX_CRITICAL(
        parent,
        localize_dialog_text(parent, title),
        localize_dialog_text(parent, text),
        *args,
        **kwargs,
    )


def _localized_get_open_file_name(parent=None, caption="", directory="", filter="", *args, **kwargs):
    return _ORIGINAL_QFILEDIALOG_GET_OPEN_FILE_NAME(
        parent,
        localize_dialog_text(parent, caption),
        directory,
        filter,
        *args,
        **kwargs,
    )


def _localized_get_save_file_name(parent=None, caption="", directory="", filter="", *args, **kwargs):
    return _ORIGINAL_QFILEDIALOG_GET_SAVE_FILE_NAME(
        parent,
        localize_dialog_text(parent, caption),
        directory,
        filter,
        *args,
        **kwargs,
    )


def _localized_get_existing_directory(parent=None, caption="", directory="", *args, **kwargs):
    return _ORIGINAL_QFILEDIALOG_GET_EXISTING_DIRECTORY(
        parent,
        localize_dialog_text(parent, caption),
        directory,
        *args,
        **kwargs,
    )


QMessageBox.information = staticmethod(_localized_information)
QMessageBox.warning = staticmethod(_localized_warning)
QMessageBox.critical = staticmethod(_localized_critical)
QFileDialog.getOpenFileName = staticmethod(_localized_get_open_file_name)
QFileDialog.getSaveFileName = staticmethod(_localized_get_save_file_name)
QFileDialog.getExistingDirectory = staticmethod(_localized_get_existing_directory)


def load_app_settings_file():
    if not os.path.exists(APP_SETTINGS_PATH):
        return {"language": "en"}
    try:
        with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        language = data.get("language", "en")
        if language not in {"zh", "en"}:
            language = "en"
        return {"language": language}
    except Exception:
        return {"language": "en"}


def save_app_settings_file(settings):
    payload = {"language": settings.get("language", "en")}
    with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def apply_language_to_widget_tree(root, language):
    if hasattr(root, "setWindowTitle") and callable(getattr(root, "windowTitle", None)):
        title = root.windowTitle()
        translated = translate_runtime_text(language, title)
        if translated != title:
            root.setWindowTitle(translated)

    for widget in root.findChildren(QWidget):
        tooltip = widget.toolTip()
        translated_tooltip = translate_runtime_text(language, tooltip)
        if translated_tooltip != tooltip:
            widget.setToolTip(translated_tooltip)

        if isinstance(widget, QGroupBox):
            title = widget.title()
            translated = translate_runtime_text(language, title)
            if translated != title:
                widget.setTitle(translated)
        elif isinstance(widget, (QPushButton, QLabel, QCheckBox)):
            text = widget.text()
            translated = translate_runtime_text(language, text)
            if translated != text:
                widget.setText(translated)


def get_app_icon():
    if os.path.exists(APP_ICON_PATH):
        return QIcon(APP_ICON_PATH)
    return QIcon()


class WheelFocusMixin:
    def _init_wheel_focus_guard(self):
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class GuardedSpinBox(WheelFocusMixin, QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_wheel_focus_guard()


class GuardedDoubleSpinBox(WheelFocusMixin, QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_wheel_focus_guard()


class GuardedComboBox(WheelFocusMixin, QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_wheel_focus_guard()
        popup_view = QListView(self)
        popup_view.setObjectName("comboPopupView")
        popup_view.setFrameShape(QFrame.NoFrame)
        popup_view.setLineWidth(0)
        popup_view.setMidLineWidth(0)
        popup_view.setUniformItemSizes(True)
        popup_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        popup_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        popup_view.viewport().setObjectName("comboPopupViewport")
        popup_view.setStyleSheet("""
            QListView#comboPopupView, QListView#comboPopupView::viewport {
                background-color: #18212b;
                border: 0px;
                outline: 0px;
            }
            QListView#comboPopupView::item {
                min-height: 24px;
                padding: 4px 8px;
                border: 0px;
                background-color: #18212b;
                color: #e8eef5;
            }
            QListView#comboPopupView::item:hover,
            QListView#comboPopupView::item:selected {
                background-color: #17354a;
                border: 0px;
                color: #e8eef5;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
                border: 0px;
            }
        """)
        self.setView(popup_view)


class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = ""
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setText(text)

    def setText(self, text):
        self._full_text = "" if text is None else str(text)
        super().setToolTip(self._full_text)
        self._apply_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_elided_text()

    def _apply_elided_text(self):
        if self.wordWrap():
            QLabel.setText(self, self._full_text)
            return

        available_width = max(0, self.contentsRect().width() - 8)
        if available_width <= 0:
            QLabel.setText(self, self._full_text)
            return

        elided = self.fontMetrics().elidedText(self._full_text, Qt.ElideMiddle, available_width)
        QLabel.setText(self, elided)

class InteractivePlotWindow(QWidget):
    def __init__(self, data, theme=None, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.language = getattr(parent, "language", "en")
        self.data = data
        self.theme = theme or {
            "bg": "#11161c",
            "panel": "#18212b",
            "border": "#2a3a4c",
            "text": "#e8eef5",
            "muted": "#8fa1b3",
        }
        self.setObjectName("auxWindow")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinMaxButtonsHint
            | Qt.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(self.tr_text("Post Check 详情图"))
        self.setGeometry(150, 150, 1400, 760)

        main_layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(12, 6), facecolor=self.theme["bg"])
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        main_layout.addWidget(self.toolbar)

        self.setup_controls()
        main_layout.addWidget(self.controls_group)
        self.initial_plot()
        apply_language_to_widget_tree(self, self.language)

    def tr_text(self, text):
        return translate_runtime_text(self.language, text)

    def set_button_role(self, button, role):
        button.setProperty("role", role)
        style = button.style()
        if style is not None:
            style.unpolish(button)
            style.polish(button)

    def style_matplotlib_figure(self):
        self.figure.patch.set_facecolor(self.theme["bg"])
        for ax in self.figure.axes:
            ax.set_facecolor(self.theme["panel"])
            ax.title.set_color(self.theme["text"])
            ax.xaxis.label.set_color(self.theme["muted"])
            ax.yaxis.label.set_color(self.theme["muted"])
            ax.tick_params(colors=self.theme["muted"])
            for spine in ax.spines.values():
                spine.set_color(self.theme["border"])

    def setup_controls(self):
        self.controls_group = QGroupBox(self.tr_text("可视化选项"))
        layout = QHBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel(self.tr_text("热图颜色:")))
        self.cmap_combo = GuardedComboBox()
        self.cmap_combo.addItems(["inferno", "viridis", "hot", "coolwarm", "jet", "gray_r"])
        self.cmap_combo.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(self.cmap_combo)

        self.show_rois_checkbox = QCheckBox(self.tr_text("显示 ROI 位置"))
        self.show_rois_checkbox.setChecked(True)
        self.show_rois_checkbox.stateChanged.connect(self.update_plot)
        layout.addWidget(self.show_rois_checkbox)

        layout.addWidget(QLabel(self.tr_text("轮廓粗细:")))
        self.linewidth_spinbox = GuardedDoubleSpinBox()
        self.linewidth_spinbox.setRange(0.2, 5.0)
        self.linewidth_spinbox.setSingleStep(0.2)
        self.linewidth_spinbox.setValue(0.8)
        self.linewidth_spinbox.valueChanged.connect(self.update_plot)
        layout.addWidget(self.linewidth_spinbox)

        layout.addWidget(QLabel(self.tr_text("激活:")))
        self.active_color_btn = self.create_color_button(QColor("#22c55e"))
        layout.addWidget(self.active_color_btn)

        layout.addWidget(QLabel(self.tr_text("未激活:")))
        self.inactive_color_btn = self.create_color_button(QColor("#ef4444"))
        layout.addWidget(self.inactive_color_btn)

        layout.addWidget(QLabel(self.tr_text("热图 Min:")))
        self.vmin_spinbox = GuardedDoubleSpinBox()
        self.vmin_spinbox.setDecimals(3)
        self.vmin_spinbox.setRange(-1e9, 1e9)
        self.vmin_spinbox.setValue(float(self.data["vmin"]))
        self.vmin_spinbox.valueChanged.connect(self.update_plot)
        layout.addWidget(self.vmin_spinbox)

        layout.addWidget(QLabel(self.tr_text("热图 Max:")))
        self.vmax_spinbox = GuardedDoubleSpinBox()
        self.vmax_spinbox.setDecimals(3)
        self.vmax_spinbox.setRange(-1e9, 1e9)
        self.vmax_spinbox.setValue(float(self.data["vmax"]))
        self.vmax_spinbox.valueChanged.connect(self.update_plot)
        layout.addWidget(self.vmax_spinbox)

        layout.addStretch()

        self.save_image_btn = QPushButton(self.tr_text("保存校正后图像"))
        self.set_button_role(self.save_image_btn, "secondary")
        self.save_image_btn.clicked.connect(self.save_corrected_image)
        layout.addWidget(self.save_image_btn)
        self.save_image_btn.setText(self.tr_text("保存热图"))

        self.export_csv_btn = QPushButton(self.tr_text("导出ROI CSV"))
        self.set_button_role(self.export_csv_btn, "secondary")
        self.export_csv_btn.clicked.connect(self.export_roi_csv)
        layout.addWidget(self.export_csv_btn)

        self.controls_group.setLayout(layout)

    def create_color_button(self, initial_color):
        button = QPushButton()
        button.setFixedSize(60, 24)
        button.setProperty("color", initial_color)
        button.setStyleSheet(
            f"background-color: {initial_color.name()}; border: none; border-radius: 6px;"
        )
        button.clicked.connect(lambda: self.on_color_pick(button))
        return button

    def on_color_pick(self, button):
        color = QColorDialog.getColor(button.property("color"), self, self.tr_text("选择颜色"))
        if color.isValid():
            button.setProperty("color", color)
            button.setStyleSheet(
                f"background-color: {color.name()}; border: none; border-radius: 6px;"
            )
            self.update_plot()

    def save_corrected_image(self):
        img = self.data.get("img_post_corrected")
        if img is None:
            QMessageBox.warning(self, self.tr_text("错误"), self.tr_text("没有可保存的校正后图像"))
            return

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(img, cmap="gray")
        ax.set_title(self.tr_text("Post-stimulation (Corrected)"))

        centers = self.data["centers"]
        radius = self.data["r"]
        color = self.active_color_btn.property("color").name()
        for x, y in centers:
            circle = plt.Circle((x, y), radius, fill=False, edgecolor=color, linewidth=self.linewidth_spinbox.value())
            ax.add_patch(circle)

        ax.set_aspect("equal")
        ax.axis("off")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr_text("保存校正后图像"),
            "",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*.*)" if self.language == "en" else "PNG 图像 (*.png);;JPEG 图像 (*.jpg *.jpeg);;所有文件 (*.*)",
        )
        if file_path:
            fig.savefig(file_path, bbox_inches="tight", dpi=300)
            QMessageBox.information(self, self.tr_text("成功"), self.tr_text("图像已保存到:\n{file_path}").format(file_path=file_path))
        plt.close(fig)

    def initial_plot(self):
        self.figure.clear()
        gs = self.figure.add_gridspec(1, 42, wspace=0.45)

        self.ax1 = self.figure.add_subplot(gs[0, 0:11])
        self.ax2 = self.figure.add_subplot(gs[0, 13:24])
        self.ax_hist = self.figure.add_subplot(gs[0, 31:42])

        self.ax1.set_aspect("equal", adjustable="box")
        self.ax2.set_aspect("equal", adjustable="box")
        self.ax_hist.set_box_aspect(1.0)
        self.artists = []

        self.ax1.imshow(self.data["img_post_corrected"], cmap="gray")
        self.ax1.set_title(self.tr_text("Post-stimulation (Corrected)"))

        self.im = self.ax2.imshow(
            self.data["display_map"],
            cmap=self.cmap_combo.currentText(),
            vmin=self.vmin_spinbox.value(),
            vmax=self.vmax_spinbox.value(),
        )
        self.ax2.set_title(self.data["plot_title"])
        self.ax_hist.set_title(self.tr_text("ROI Metric Histogram"))

        for ax in (self.ax1, self.ax2):
            ax.set_xticks([])
            ax.set_yticks([])

        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        cax = inset_axes(
            self.ax2,
            width="3.2%",
            height="100%",
            loc="lower left",
            bbox_to_anchor=(1.04, 0, 1, 1),
            bbox_transform=self.ax2.transAxes,
            borderpad=0,
        )
        self.cbar = self.figure.colorbar(self.im, cax=cax)

        from matplotlib.patches import Circle

        for idx in range(len(self.data["results"])):
            x, y = self.data["centers"][idx]
            radius = self.data["r"]
            for ax in (self.ax1, self.ax2):
                circle = Circle((float(x), float(y)), radius, facecolor="none")
                ax.add_patch(circle)
                self.artists.append(circle)

        self.update_plot()

    def update_plot(self):
        settings = {
            "cmap": self.cmap_combo.currentText(),
            "show_rois": self.show_rois_checkbox.isChecked(),
            "active_color": self.active_color_btn.property("color").name(),
            "inactive_color": self.inactive_color_btn.property("color").name(),
            "linewidth": self.linewidth_spinbox.value(),
            "vmin": self.vmin_spinbox.value(),
            "vmax": self.vmax_spinbox.value(),
        }

        self.im.set_cmap(settings["cmap"])
        self.im.set_clim(vmin=settings["vmin"], vmax=settings["vmax"])

        num_rois = len(self.data["results"])
        for i in range(num_rois):
            color = settings["active_color"] if self.data["results"][i] else settings["inactive_color"]

            circle_left = self.artists[i * 2]
            circle_left.set_edgecolor(color)
            circle_left.set_linewidth(settings["linewidth"])
            circle_left.set_visible(settings["show_rois"])

            circle_right = self.artists[i * 2 + 1]
            circle_right.set_edgecolor(color)
            circle_right.set_linewidth(settings["linewidth"])
            circle_right.set_visible(settings["show_rois"])

        self.ax_hist.clear()
        roi_metrics = np.asarray(self.data.get("roi_metrics", []), dtype=np.float32)
        finite_metrics = roi_metrics[np.isfinite(roi_metrics)]
        metric_label = self.data.get("metric_label", "ROI Metric")
        threshold = self.data.get("threshold")
        if finite_metrics.size:
            bin_count = min(30, max(10, int(np.sqrt(finite_metrics.size))))
            weights = np.full(finite_metrics.shape, 1.0 / finite_metrics.size, dtype=np.float32)
            self.ax_hist.hist(
                finite_metrics,
                bins=bin_count,
                weights=weights,
                color=self.theme.get("accent", "#38bdf8"),
                edgecolor=self.theme.get("border", "#2a3a4c"),
                alpha=0.9,
            )
            if threshold is not None and np.isfinite(threshold):
                self.ax_hist.axvline(
                    threshold,
                    color=self.theme.get("warning", "#f59e0b"),
                    linestyle="--",
                    linewidth=1.4,
                    label=f"{self.tr_text('阈值')} {threshold:.3f}",
                )
                self.ax_hist.legend(frameon=False, fontsize=9)
        else:
            self.ax_hist.text(0.5, 0.5, self.tr_text("No ROI metrics"), ha="center", va="center", color=self.theme["muted"])

        self.ax_hist.set_title(self.tr_text("ROI Metric Histogram"))
        self.ax_hist.set_xlabel(metric_label)
        self.ax_hist.set_ylabel(self.tr_text("Fraction of cells"))

        self.style_matplotlib_figure()
        self.canvas.draw_idle()

    def save_corrected_image(self):
        heatmap = self.data.get("display_map")
        if heatmap is None:
            QMessageBox.warning(self, self.tr_text("错误"), self.tr_text("没有可保存的热图。"))
            return

        fig, ax = plt.subplots(figsize=(8.6, 8))
        im = ax.imshow(
            heatmap,
            cmap=self.cmap_combo.currentText(),
            vmin=self.vmin_spinbox.value(),
            vmax=self.vmax_spinbox.value(),
        )
        ax.set_title(self.data.get("plot_title", self.tr_text("Heatmap")))

        if self.show_rois_checkbox.isChecked():
            centers = self.data.get("centers", [])
            radius = self.data.get("r", 0)
            results = self.data.get("results", [])
            active_color = self.active_color_btn.property("color").name()
            inactive_color = self.inactive_color_btn.property("color").name()
            line_width = self.linewidth_spinbox.value()
            for idx, (x, y) in enumerate(centers):
                is_active = results[idx] if idx < len(results) else False
                edge_color = active_color if is_active else inactive_color
                circle = plt.Circle((x, y), radius, fill=False, edgecolor=edge_color, linewidth=line_width)
                ax.add_patch(circle)

        ax.set_aspect("equal")
        ax.axis("off")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr_text("保存热图"),
            "",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*.*)" if self.language == "en" else "PNG 图片 (*.png);;JPEG 图片 (*.jpg *.jpeg);;所有文件 (*.*)",
        )
        if file_path:
            fig.savefig(file_path, bbox_inches="tight", dpi=300)
            QMessageBox.information(self, self.tr_text("成功"), self.tr_text("热图已保存到:\n{file_path}").format(file_path=file_path))
        plt.close(fig)

    def export_roi_csv(self):
        csv_path = self.data.get("csv_path")
        if csv_path and os.path.exists(csv_path):
            QMessageBox.information(self, self.tr_text("成功"), self.tr_text("ROI CSV 已生成:\n{csv_path}").format(csv_path=csv_path))
            return

        QMessageBox.information(self, self.tr_text("提示"), self.tr_text("当前结果没有可导出的 ROI CSV。"))


class DetectionPage(QWidget):
    def __init__(self, theme=None, parent=None):
        super().__init__(parent)
        self.language = getattr(parent, "language", "en")
        self.theme = dict(theme) if theme is not None else {
            "bg": "#11161c",
            "surface": "#0f1720",
            "panel": "#18212b",
            "panel_alt": "#1d2a36",
            "border": "#2a3a4c",
            "text": "#e8eef5",
            "muted": "#8fa1b3",
            "accent": "#38bdf8",
            "success": "#22c55e",
        }
        self.setObjectName("auxWindow")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(self.tr_text("Post Check 工作台"))
        self.setMinimumSize(0, 0)

        self.stat_data = None
        self.iscell_data = None
        self.suite2p_img = None
        self.microscope_img = None
        self.pre_activation_img = None
        self.activation_img = None
        self.H = None
        self.centers = []
        self.valid = np.array([], dtype=int)
        self.valid_to_rel = {}
        self.default_savepath = None
        self.iscell_name = None
        self.stat_path = None
        self.iscell_path = None
        self.suite2p_img_path = None
        self.microscope_img_path = None
        self.stimulated_snapshot = set()

        self.roi_subset_source_path = None
        self.roi_subset_source_type = "Not loaded" if self.language == "en" else "未加载"
        self.roi_subset_raw_indices = []
        self.roi_subset_abs_indices = []
        self.roi_subset_invalid_indices = []
        self.roi_subset_duplicate_count = 0

        self.result_plot_data = None
        self.plot_window = None
        self.summary_state = {
            "total": None,
            "success": None,
            "rate": None,
            "method": None,
            "threshold": None,
            "shift_x": 0.0,
            "shift_y": 0.0,
        }
        self.context_source = {
            "stat": "未带入",
            "iscell": "未带入",
            "suite2p": "未带入",
            "pre": "未带入",
            "H": "未带入",
            "savepath": "未带入",
        }

        self.roi_subset_source_type = "未加载"
        self.context_source = {
            "stat": "Not loaded" if self.language == "en" else "未加载",
            "iscell": "Not loaded" if self.language == "en" else "未加载",
            "suite2p": "Not loaded" if self.language == "en" else "未加载",
            "pre": "Not loaded" if self.language == "en" else "未加载",
            "H": "Not loaded" if self.language == "en" else "未加载",
            "savepath": "Not loaded" if self.language == "en" else "未加载",
        }

        self.init_ui()
        self.update_threshold_settings()
        self.refresh_context_banner()
        self.refresh_roi_subset_status()
        self.refresh_summary()
        apply_language_to_widget_tree(self, self.language)
        self.apply_shared_data_from_parent()

    def tr_text(self, text):
        return translate_runtime_text(self.language, text)

    def label_full_text(self, label):
        return getattr(label, "_full_text", label.text())

    def set_shared_status_label(self, label, text, tooltip=None):
        if label is None:
            return
        label.setText(text)
        if tooltip:
            label.setToolTip(tooltip)

    def apply_shared_data_from_parent(self):
        parent = self.parent()
        if parent is None:
            return

        self.stat_data = getattr(parent, "stat_data", None)
        self.iscell_data = getattr(parent, "iscell_data", None)
        self.suite2p_img = getattr(parent, "suite2p_img", None)
        self.microscope_img = getattr(parent, "microscope_img", None)
        self.H = getattr(parent, "H", None)
        self.default_savepath = getattr(parent, "default_savepath", None)
        self.iscell_name = getattr(parent, "iscell_name", None)

        parent_valid = getattr(parent, "valid", None)
        if parent_valid is not None:
            self.valid = np.array(parent_valid, dtype=int)
            self.centers = list(getattr(parent, "centers", []) or [])
            self.valid_to_rel = {int(abs_idx): rel_idx for rel_idx, abs_idx in enumerate(self.valid.tolist())}
        elif self.stat_data is not None and self.iscell_data is not None:
            self.extract_roi_centers()

        shared_labels = [
            ("stat_label", "stat_path"),
            ("iscell_label", "iscell_path"),
            ("suite2p_img_label", "suite2p_img_path"),
            ("microscope_img_label", "microscope_img_path"),
        ]
        fallback = self.tr_text("未加载")
        for label_name, path_name in shared_labels:
            if not hasattr(self, label_name) or not hasattr(parent, label_name):
                continue
            parent_label = getattr(parent, label_name)
            text = self.label_full_text(parent_label) or fallback
            path = getattr(parent, path_name, None)
            self.set_shared_status_label(getattr(self, label_name), text, path)

    def push_shared_data_to_parent(self, source):
        parent = self.parent()
        if parent is not None and hasattr(parent, "apply_shared_data_from_detection"):
            parent.apply_shared_data_from_detection(source)

    def set_button_role(self, button, role):
        button.setProperty("role", role)
        style = button.style()
        if style is not None:
            style.unpolish(button)
            style.polish(button)

    def style_matplotlib_figure(self, fig):
        fig.patch.set_facecolor(self.theme["bg"])
        for ax in fig.axes:
            ax.set_facecolor(self.theme["panel"])
            ax.title.set_color(self.theme["text"])
            ax.xaxis.label.set_color(self.theme["muted"])
            ax.yaxis.label.set_color(self.theme["muted"])
            ax.tick_params(colors=self.theme["muted"])
            for spine in ax.spines.values():
                spine.set_color(self.theme["border"])

    def setup_status_label(self, label, object_name="fileStatus", word_wrap=False, minimum_height=28):
        label.setObjectName(object_name)
        label.setMinimumWidth(0)
        label.setMinimumHeight(minimum_height)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        label.setWordWrap(word_wrap)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def create_value_label(self, text="--"):
        label = QLabel(text)
        self.setup_status_label(label)
        return label

    def log(self, message):
        self.log_area.append(translate_runtime_text(self.language, message))
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_area.setTextCursor(cursor)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        self.context_info_label = QLabel("当前上下文：未带入主程序数据")
        self.setup_status_label(self.context_info_label, object_name="positionHint", word_wrap=True, minimum_height=54)
        main_layout.addWidget(self.context_info_label)

        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        left_layout.addWidget(self.create_basic_data_group())
        left_layout.addWidget(self.create_input_group())
        left_layout.addWidget(self.create_param_group())
        left_layout.addStretch()

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        right_layout.addWidget(self.create_summary_group())
        right_layout.addWidget(self.create_result_actions_group())
        right_layout.addStretch()

        left_widget.setMinimumWidth(480)
        center_layout.addWidget(left_widget, 3)
        center_layout.addWidget(right_widget, 2)
        main_layout.addLayout(center_layout, 1)

        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        self.log_area = QTextEdit()
        self.log_area.setObjectName("logArea")
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(170)
        log_layout.addWidget(self.log_area)
        main_layout.addWidget(log_group)

    def create_basic_data_group(self):
        group = QGroupBox("基础数据")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.post_stat_btn = QPushButton("stat.npy")
        self.post_iscell_btn = QPushButton("iscell.npy")
        self.post_suite2p_btn = QPushButton("Suite2p 参考图像")
        self.post_pre_btn = QPushButton("加载激活前图像")

        for button in (self.post_stat_btn, self.post_iscell_btn, self.post_suite2p_btn, self.post_pre_btn):
            self.set_button_role(button, "secondary")

        self.post_stat_label = ElidedLabel("未加载")
        self.post_iscell_label = ElidedLabel("未加载")
        self.post_suite2p_label = ElidedLabel("未加载")
        self.post_pre_label = ElidedLabel("未加载")
        for label in (self.post_stat_label, self.post_iscell_label, self.post_suite2p_label, self.post_pre_label):
            self.setup_status_label(label)

        grid.addWidget(self.post_stat_btn, 0, 0)
        grid.addWidget(self.post_stat_label, 0, 1)
        grid.addWidget(self.post_iscell_btn, 1, 0)
        grid.addWidget(self.post_iscell_label, 1, 1)
        grid.addWidget(self.post_suite2p_btn, 2, 0)
        grid.addWidget(self.post_suite2p_label, 2, 1)
        grid.addWidget(self.post_pre_btn, 3, 0)
        grid.addWidget(self.post_pre_label, 3, 1)

        self.post_stat_btn.clicked.connect(self.load_post_check_stat)
        self.post_iscell_btn.clicked.connect(self.load_post_check_iscell)
        self.post_suite2p_btn.clicked.connect(self.load_post_check_suite2p_image)
        self.post_pre_btn.clicked.connect(self.load_pre_activation_image)
        return group

    def create_input_group(self):
        group = QGroupBox("Post Check 输入")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.post_image_btn = QPushButton("加载激活后图像")
        self.roi_subset_btn = QPushButton("加载 ROI 子集文件")
        self.set_button_role(self.post_image_btn, "secondary")
        self.set_button_role(self.roi_subset_btn, "secondary")

        self.post_image_label = ElidedLabel("未加载")
        self.setup_status_label(self.post_image_label)
        self.roi_subset_label = QLabel("未选择 ROI 子集文件")
        self.setup_status_label(self.roi_subset_label, object_name="positionHint", word_wrap=True, minimum_height=54)

        grid.addWidget(self.post_image_btn, 0, 0)
        grid.addWidget(self.post_image_label, 0, 1)
        grid.addWidget(self.roi_subset_btn, 1, 0)
        grid.addWidget(self.roi_subset_label, 1, 1)

        self.post_image_btn.clicked.connect(self.load_activation_image)
        self.roi_subset_btn.clicked.connect(self.load_roi_subset_file)
        return group

    def create_param_group(self):
        group = QGroupBox("检测参数")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(10)

        self.eval_method_combo = GuardedComboBox()
        self.eval_method_combo.addItems(["Fold Increase", "Difference"])

        self.threshold_label = QLabel("阈值(倍数):")
        self.threshold_input = GuardedDoubleSpinBox()
        self.threshold_input.setDecimals(2)

        self.diameter_input = GuardedDoubleSpinBox()
        self.diameter_input.setRange(1, 100)
        self.diameter_input.setSingleStep(1)
        self.diameter_input.setValue(10)

        self.activation_correction_x = GuardedDoubleSpinBox()
        self.activation_correction_x.setRange(-200, 200)
        self.activation_correction_x.setDecimals(2)
        self.activation_correction_x.setSingleStep(0.1)

        self.activation_correction_y = GuardedDoubleSpinBox()
        self.activation_correction_y.setRange(-200, 200)
        self.activation_correction_y.setDecimals(2)
        self.activation_correction_y.setSingleStep(0.1)

        self.auto_correct_btn = QPushButton("自动位移校准")
        self.evaluate_btn = QPushButton("开始检测")
        self.set_button_role(self.auto_correct_btn, "secondary")
        self.set_button_role(self.evaluate_btn, "primary")

        grid.addWidget(QLabel("方法:"), 0, 0)
        grid.addWidget(self.eval_method_combo, 0, 1)
        grid.addWidget(self.threshold_label, 1, 0)
        grid.addWidget(self.threshold_input, 1, 1)
        grid.addWidget(QLabel("ROI 直径 (pix):"), 2, 0)
        grid.addWidget(self.diameter_input, 2, 1)
        grid.addWidget(QLabel("后图 X 位移:"), 3, 0)
        grid.addWidget(self.activation_correction_x, 3, 1)
        grid.addWidget(QLabel("后图 Y 位移:"), 4, 0)
        grid.addWidget(self.activation_correction_y, 4, 1)
        grid.addWidget(self.auto_correct_btn, 5, 0)
        grid.addWidget(self.evaluate_btn, 5, 1)

        self.eval_method_combo.currentIndexChanged.connect(self.update_threshold_settings)
        self.threshold_input.valueChanged.connect(self.sync_summary_parameters)
        self.activation_correction_x.valueChanged.connect(self.sync_summary_parameters)
        self.activation_correction_y.valueChanged.connect(self.sync_summary_parameters)
        self.auto_correct_btn.clicked.connect(self.auto_correct_drift)
        self.evaluate_btn.clicked.connect(self.evaluate_activation_success)
        return group

    def create_summary_group(self):
        group = QGroupBox("检测摘要")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.summary_total_label = self.create_value_label("未检测")
        self.summary_success_label = self.create_value_label("未检测")
        self.summary_rate_label = self.create_value_label("未检测")
        self.summary_method_label = self.create_value_label("未检测")
        self.summary_threshold_label = self.create_value_label("未检测")
        self.summary_shift_label = self.create_value_label("X 0.00 / Y 0.00")

        rows = [
            ("已检测 ROI", self.summary_total_label),
            ("激活成功", self.summary_success_label),
            ("成功率", self.summary_rate_label),
            ("方法", self.summary_method_label),
            ("阈值", self.summary_threshold_label),
            ("位移", self.summary_shift_label),
        ]

        for row, (title, label) in enumerate(rows):
            grid.addWidget(QLabel(title), row, 0)
            grid.addWidget(label, row, 1)

        return group

    def create_result_actions_group(self):
        group = QGroupBox("结果操作")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.result_status_label = QLabel("尚未完成检测")
        self.setup_status_label(self.result_status_label, object_name="positionHint", word_wrap=True, minimum_height=54)
        layout.addWidget(self.result_status_label)

        self.view_detail_btn = QPushButton("查看详情图")
        self.view_detail_btn.setEnabled(False)
        self.set_button_role(self.view_detail_btn, "secondary")
        self.view_detail_btn.clicked.connect(self.show_detail_plot)
        layout.addWidget(self.view_detail_btn)
        layout.addStretch()
        return group

    def refresh_context_banner(self):
        savepath_text = self.default_savepath if self.default_savepath else ("Not loaded" if self.language == "en" else "未加载")
        banner = (
            f"{'Detection status:' if self.language == 'en' else '检测页状态：'} stat {self.context_source['stat']} | "
            f"iscell {self.context_source['iscell']} | "
            f"H {self.context_source['H']} | "
            f"{'Save path' if self.language == 'en' else '保存目录'} {savepath_text}\n"
            f"Suite2P {self.context_source['suite2p']} | "
            f"{'Pre image' if self.language == 'en' else '激活前图像'} {self.context_source['pre']} | "
            f"{'ROI subset' if self.language == 'en' else 'ROI 子集'} {self.roi_subset_source_type}"
        )
        self.context_info_label.setText(banner)
        return
        savepath_text = self.default_savepath if self.default_savepath else "未带入"
        pre_text = self.context_source["pre"]
        banner = (
            f"当前上下文：stat {self.context_source['stat']} | "
            f"iscell {self.context_source['iscell']} | "
            f"H {self.context_source['H']} | "
            f"保存目录 {savepath_text}\n"
            f"Suite2P {self.context_source['suite2p']} | "
            f"激活前图像 {pre_text} | "
            f"主程序已刺激 ROI {len(self.stimulated_snapshot)} 个"
        )
        self.context_info_label.setText(banner)

    def refresh_summary(self):
        total = self.summary_state["total"]
        success = self.summary_state["success"]
        rate = self.summary_state["rate"]

        self.summary_total_label.setText(self.tr_text("未检测") if total is None else str(total))
        self.summary_success_label.setText(self.tr_text("未检测") if success is None else str(success))
        self.summary_rate_label.setText(self.tr_text("未检测") if rate is None else f"{rate:.2%}")
        self.summary_method_label.setText(self.summary_state["method"] or self.eval_method_combo.currentText())
        self.summary_threshold_label.setText(
            f"{self.summary_state['threshold']:.2f}"
            if self.summary_state["threshold"] is not None
            else f"{self.threshold_input.value():.2f}"
        )
        self.summary_shift_label.setText(
            f"X {self.summary_state['shift_x']:.2f} / Y {self.summary_state['shift_y']:.2f}"
        )

    def refresh_result_status(self, text=None):
        if text is None:
            if self.result_plot_data is None:
                text = self.tr_text("尚未完成检测")
            else:
                text = "Detection results ready. Open the detail plot." if self.language == "en" else "已生成检测结果，可查看详情图。"
        self.result_status_label.setText(text)

    def sync_summary_parameters(self):
        self.summary_state["method"] = self.eval_method_combo.currentText()
        self.summary_state["threshold"] = self.threshold_input.value()
        self.summary_state["shift_x"] = self.activation_correction_x.value()
        self.summary_state["shift_y"] = self.activation_correction_y.value()
        self.refresh_summary()

    def apply_context(self, context):
        if not context:
            return

        stat_data = context.get("stat_data")
        if stat_data is not None:
            self.stat_data = stat_data.copy()
            self.post_stat_label.setText("已带入主程序 stat.npy")
            self.post_stat_label.setToolTip("已从主程序带入 stat 数据")
            self.context_source["stat"] = "已带入"

        iscell_data = context.get("iscell_data")
        if iscell_data is not None:
            self.iscell_data = iscell_data.copy()
            self.post_iscell_label.setText("已带入主程序 iscell.npy")
            self.post_iscell_label.setToolTip("已从主程序带入 iscell 数据")
            self.context_source["iscell"] = "已带入"

        suite2p_img = context.get("suite2p_img")
        if suite2p_img is not None:
            self.suite2p_img = suite2p_img.copy()
            self.post_suite2p_label.setText("已带入主程序 Suite2P 图像")
            self.post_suite2p_label.setToolTip("已从主程序带入 Suite2P 图像")
            self.context_source["suite2p"] = "已带入"

        pre_activation_img = context.get("pre_activation_img")
        if pre_activation_img is not None:
            self.pre_activation_img = self.prepare_analysis_image(pre_activation_img)
            pre_source = context.get("pre_activation_source", "已带入主程序图像")
            self.post_pre_label.setText(pre_source)
            self.post_pre_label.setToolTip(pre_source)
            self.context_source["pre"] = pre_source

        homography = context.get("H")
        if homography is not None:
            self.H = homography.copy()
            self.context_source["H"] = "已带入"

        savepath = context.get("default_savepath")
        if savepath:
            self.default_savepath = savepath
            self.context_source["savepath"] = savepath

        roi_diameter = context.get("roi_diameter")
        if roi_diameter is not None:
            self.diameter_input.setValue(float(roi_diameter))

        stimulated = context.get("stimulated")
        if stimulated:
            self.stimulated_snapshot = set(stimulated)

        self.extract_roi_centers(log_success=False)

    def prepare_analysis_image(self, image):
        if image is None:
            return None

        result = image.copy()
        if result.ndim == 3:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        if result.shape != (1024, 1024):
            result = cv2.resize(result, (1024, 1024), interpolation=cv2.INTER_CUBIC)
        return result

    def load_analysis_image_from_path(self, title):
        path, _ = QFileDialog.getOpenFileName(
            self,
            title,
            self.default_savepath or "",
            "Images (*.png *.tif *.tiff *.jpg)",
        )
        if not path:
            return None, None, None

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            QMessageBox.warning(self, "错误", f"{title}失败")
            return None, None, None

        suffix = ""
        if image.shape != (1024, 1024):
            image = cv2.resize(image, (1024, 1024), interpolation=cv2.INTER_CUBIC)
            suffix = ", 上采样至(1024, 1024)"

        return path, image, suffix

    def load_post_check_stat(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 stat 文件",
            self.default_savepath or "",
            "Numpy Files (*.npy)",
        )
        if not path:
            return

        try:
            self.stat_data = np.load(path, allow_pickle=True)
            self.post_stat_label.setText(os.path.basename(path))
            self.post_stat_label.setToolTip(path)
            self.context_source["stat"] = "已加载"
            self.extract_roi_centers()
            self.log("成功加载 stat 文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"stat 文件加载失败: {e}")

    def load_post_check_iscell(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 iscell 文件",
            self.default_savepath or "",
            "Numpy Files (*.npy)",
        )
        if not path:
            return

        try:
            self.iscell_data = np.load(path, allow_pickle=True)
            self.default_savepath = os.path.dirname(path)
            self.iscell_name = os.path.splitext(os.path.basename(path))[0]
            self.post_iscell_label.setText(os.path.basename(path))
            self.post_iscell_label.setToolTip(path)
            self.context_source["iscell"] = "已加载"
            self.extract_roi_centers()
            self.log("成功加载 iscell 文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"iscell 文件加载失败: {e}")

    def load_post_check_suite2p_image(self):
        path, image, suffix = self.load_analysis_image_from_path("选择 Suite2P 图像")
        if image is None:
            return

        self.suite2p_img = image
        self.post_suite2p_label.setText(os.path.basename(path))
        self.post_suite2p_label.setToolTip(path)
        self.context_source["suite2p"] = "已加载"
        self.log(f"加载 Suite2P 图像: {os.path.basename(path)}{suffix}")
        self.refresh_context_banner()

    def load_pre_activation_image(self):
        path, image, suffix = self.load_analysis_image_from_path("选择激活前图像")
        if image is None:
            return

        self.pre_activation_img = image
        self.post_pre_label.setText(os.path.basename(path))
        self.post_pre_label.setToolTip(path)
        self.context_source["pre"] = "手动加载"
        self.log(f"加载激活前图像: {os.path.basename(path)}{suffix}")
        self.refresh_context_banner()

    def load_activation_image(self):
        path, image, suffix = self.load_analysis_image_from_path("选择激活后图像")
        if image is None:
            return

        self.activation_img = image
        self.post_image_label.setText(os.path.basename(path))
        self.post_image_label.setToolTip(path)
        self.log(f"加载激活后图像: {os.path.basename(path)}{suffix}")

    def extract_roi_centers(self, log_success=True):
        if self.stat_data is None or self.iscell_data is None:
            self.centers = []
            self.valid = np.array([], dtype=int)
            self.valid_to_rel = {}
            self.refresh_context_banner()
            self.refresh_roi_subset_status()
            return

        try:
            self.valid = np.where(self.iscell_data[:, 0] == 1)[0]
            self.centers = [self.stat_data[i]["med"][::-1] for i in self.valid]
            self.valid_to_rel = {int(abs_idx): rel_idx for rel_idx, abs_idx in enumerate(self.valid.tolist())}
            if log_success:
                self.log(f"提取到 {len(self.centers)} 个有效 ROI")
            self.refresh_context_banner()
            self.refresh_roi_subset_status()
        except Exception as e:
            self.centers = []
            self.valid = np.array([], dtype=int)
            self.valid_to_rel = {}
            self.log(f"ROI 提取错误: {e}")
            QMessageBox.warning(self, "警告", "请检查加载的 stat/iscell 文件")

    def update_threshold_settings(self):
        method = self.eval_method_combo.currentText()
        if method == "Fold Increase":
            self.threshold_label.setText("阈值(倍数):")
            self.threshold_input.setRange(0.1, 20.0)
            self.threshold_input.setSingleStep(0.1)
            if self.threshold_input.value() == 0.0:
                self.threshold_input.setValue(1.3)
        else:
            self.threshold_label.setText("阈值(差值):")
            self.threshold_input.setRange(-255.0, 255.0)
            self.threshold_input.setSingleStep(1.0)
            if self.threshold_input.value() == 0.0:
                self.threshold_input.setValue(20.0)

        self.summary_state["method"] = method
        self.summary_state["threshold"] = self.threshold_input.value()
        self.refresh_summary()

    def auto_correct_drift(self):
        if self.pre_activation_img is None or self.activation_img is None:
            QMessageBox.warning(self, "错误", "请先加载激活前和激活后图像")
            return

        self.log("开始自动位移校准...")
        try:
            pre_img_float = self.pre_activation_img.astype(np.float32)
            post_img_float = self.activation_img.astype(np.float32)
            shift, response = cv2.phaseCorrelate(pre_img_float, post_img_float)
            dx, dy = shift

            self.activation_correction_x.setValue(-dx)
            self.activation_correction_y.setValue(-dy)
            self.summary_state["shift_x"] = -dx
            self.summary_state["shift_y"] = -dy
            self.refresh_summary()

            self.log(f"自动位移校准完成: 最佳位移 X={dx:.2f}, Y={dy:.2f} (置信度: {response:.2f})")
            self.refresh_result_status(f"已完成自动位移校准，当前位移 X {-dx:.2f} / Y {-dy:.2f}")
        except cv2.error as e:
            error_message = f"自动位移校准失败: OpenCV 错误: {e}"
            self.log(error_message)
            QMessageBox.critical(self, "错误", error_message)
        except Exception as e:
            error_message = f"自动位移校准失败: {e}"
            self.log(error_message)
            QMessageBox.critical(self, "错误", error_message)

    def load_roi_subset_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 ROI 子集文件",
            self.default_savepath or "",
            "ROI Files (*.npy *.txt *.csv);;Numpy Files (*.npy);;Text Files (*.txt *.csv)",
        )
        if not path:
            return

        try:
            raw_indices, source_type = self.parse_roi_subset_file(path)
            unique_indices = []
            seen = set()
            duplicates = 0
            for idx in raw_indices:
                idx = int(idx)
                if idx in seen:
                    duplicates += 1
                    continue
                seen.add(idx)
                unique_indices.append(idx)

            self.roi_subset_source_path = path
            self.roi_subset_source_type = source_type
            self.roi_subset_raw_indices = unique_indices
            self.roi_subset_duplicate_count = duplicates
            self.refresh_roi_subset_status(log_result=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"ROI 子集文件解析失败: {e}")

    def parse_roi_subset_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".npy":
            data = np.load(path, allow_pickle=True)
            source_type = "stimulated.npy" if np.asarray(data).ndim >= 2 else "ROI 列表 .npy"
            return self.parse_roi_subset_npy(data), source_type

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        values = re.findall(r"-?\d+", content)
        if not values:
            raise ValueError("未从 txt/csv 中解析到 ROI 编号")
        return [int(v) for v in values], "索引列表 txt/csv"

    def parse_roi_subset_npy(self, data):
        array = np.asarray(data)

        if array.ndim >= 2 and array.shape[1] >= 1:
            first_col = np.asarray(array[:, 0]).astype(float)
            if np.all(np.isin(first_col, [0.0, 1.0])):
                return np.where(first_col > 0.5)[0].tolist()

        flat = np.asarray(array).ravel()
        if flat.size == 0:
            raise ValueError("ROI 子集 .npy 为空")

        if flat.dtype == np.bool_:
            return np.where(flat)[0].tolist()

        numeric = flat.astype(float)
        if np.all(np.isin(numeric, [0.0, 1.0])) and numeric.size > 4:
            return np.where(numeric > 0.5)[0].tolist()

        return [int(v) for v in numeric.tolist()]

    def refresh_roi_subset_status(self, log_result=False):
        if not self.roi_subset_source_path:
            self.roi_subset_abs_indices = []
            self.roi_subset_invalid_indices = []
            self.roi_subset_label.setText("未选择 ROI 子集文件")
            return

        base_name = os.path.basename(self.roi_subset_source_path)
        raw_count = len(self.roi_subset_raw_indices)

        if not self.valid_to_rel:
            self.roi_subset_abs_indices = []
            self.roi_subset_invalid_indices = []
            message = (
                f"{base_name} | {self.roi_subset_source_type}\n"
                f"已导入 {raw_count} 个 ROI，待基础 ROI 数据验证"
            )
            self.roi_subset_label.setText(message)
            if log_result:
                self.log(f"已导入 ROI 子集文件: {base_name}，共 {raw_count} 个编号，待基础 ROI 数据验证")
            return

        valid_indices = []
        invalid_indices = []
        for idx in self.roi_subset_raw_indices:
            if idx in self.valid_to_rel:
                valid_indices.append(idx)
            else:
                invalid_indices.append(idx)

        self.roi_subset_abs_indices = valid_indices
        self.roi_subset_invalid_indices = invalid_indices

        message = (
            f"{base_name} | {self.roi_subset_source_type}\n"
            f"有效 {len(valid_indices)} | 无效 {len(invalid_indices)}"
        )
        if self.roi_subset_duplicate_count:
            message += f" | 去重 {self.roi_subset_duplicate_count}"
        self.roi_subset_label.setText(message)
        self.roi_subset_label.setToolTip(self.roi_subset_source_path)

        if log_result:
            self.log(
                f"已导入 ROI 子集文件: {base_name}，有效 {len(valid_indices)} 个，无效 {len(invalid_indices)} 个"
            )

    def validate_detection_inputs(self):
        checks = [
            (self.stat_data is not None and self.iscell_data is not None and bool(self.centers), "缺少基础 ROI 数据，请先加载 stat/iscell"),
            (self.pre_activation_img is not None, "请先加载激活前图像"),
            (self.activation_img is not None, "请先加载激活后图像"),
            (bool(self.roi_subset_source_path), "请先导入 ROI 子集文件"),
            (bool(self.roi_subset_abs_indices), "ROI 子集文件中没有可用的有效 ROI"),
        ]

        for condition, message in checks:
            if not condition:
                QMessageBox.warning(self, "错误", message)
                return False
        return True

    def transform_roi_center(self, abs_idx):
        rel_idx = self.valid_to_rel.get(int(abs_idx))
        if rel_idx is None:
            raise ValueError(f"ROI {abs_idx} 不在当前有效 ROI 集合中")

        raw_x, raw_y = self.centers[rel_idx]
        points = np.array([[[raw_x * 2, raw_y * 2]]], dtype=np.float32)

        if self.H is not None:
            try:
                transformed = cv2.perspectiveTransform(points, self.H)
                return tuple(map(float, transformed[0][0]))
            except Exception as e:
                self.log(f"坐标转换失败，回退原始坐标: {e}")

        return tuple(map(float, points[0][0]))

    def evaluate_activation_success(self):
        if not self.validate_detection_inputs():
            return

        method = self.eval_method_combo.currentText()
        img_pre = self.pre_activation_img
        img_post = self.activation_img
        height, width = img_pre.shape
        radius = int(self.diameter_input.value() / 2)
        threshold = float(self.threshold_input.value())
        correction_x = float(self.activation_correction_x.value())
        correction_y = float(self.activation_correction_y.value())

        transform_matrix = np.float32([[1, 0, correction_x], [0, 1, correction_y]])
        img_post_corrected = cv2.warpAffine(img_post, transform_matrix, (width, height), borderValue=0)
        self.log(f"激活后图像已应用位移：X={correction_x:.2f}px, Y={correction_y:.2f}px")

        display_map = np.zeros((height, width), dtype=np.float32)
        results = []
        metric_values = []
        transformed_centers = []
        plot_title = "ROI Mean Fold Increase" if method == "Fold Increase" else "ROI Mean Difference (Post - Pre)"

        for abs_idx in self.roi_subset_abs_indices:
            x_aligned, y_aligned = self.transform_roi_center(abs_idx)
            transformed_centers.append((x_aligned, y_aligned))

            cx_aligned = int(round(x_aligned))
            cy_aligned = int(round(y_aligned))
            if not (radius < cx_aligned < width - radius and radius < cy_aligned < height - radius):
                results.append(False)
                continue

            mask = np.zeros((2 * radius + 1, 2 * radius + 1), dtype=np.uint8)
            cv2.circle(mask, (radius, radius), radius, 1, -1)
            roi_mask = mask == 1

            pre_patch = img_pre[cy_aligned - radius:cy_aligned + radius + 1, cx_aligned - radius:cx_aligned + radius + 1]
            post_patch = img_post_corrected[
                cy_aligned - radius:cy_aligned + radius + 1,
                cx_aligned - radius:cx_aligned + radius + 1,
            ]

            mean_pre = np.mean(pre_patch[roi_mask])
            mean_post = np.mean(post_patch[roi_mask])

            if method == "Fold Increase":
                mean_pre_safe = max(float(mean_pre), 1.0)
                metric = mean_post / mean_pre_safe
            else:
                metric = mean_post - mean_pre

            display_patch = display_map[
                cy_aligned - radius:cy_aligned + radius + 1,
                cx_aligned - radius:cx_aligned + radius + 1,
            ]
            display_patch[roi_mask] = metric
            metric_values.append(metric)
            results.append(metric >= threshold)

        if method == "Fold Increase":
            vmin = 1.0
            vmax = np.percentile(metric_values, 99.5) if metric_values else 1.0
            vmax = max(vmax, vmin + 1e-3)
        else:
            vmax = np.percentile(metric_values, 99.5) if metric_values else 1.0
            vmin = np.percentile(metric_values, 0.5) if metric_values else -1.0
            if np.isclose(vmin, vmax):
                vmax = vmin + 1e-3

        success_count = sum(1 for value in results if value)
        total_count = len(results)
        success_rate = (success_count / total_count) if total_count else 0.0

        self.summary_state.update(
            {
                "total": total_count,
                "success": success_count,
                "rate": success_rate,
                "method": method,
                "threshold": threshold,
                "shift_x": correction_x,
                "shift_y": correction_y,
            }
        )
        self.refresh_summary()

        self.result_plot_data = {
            "img_post_corrected": img_post_corrected,
            "display_map": display_map,
            "plot_title": plot_title,
            "vmin": vmin,
            "vmax": vmax,
            "results": results,
            "centers": transformed_centers,
            "r": radius,
            "roi_ids": list(self.roi_subset_abs_indices),
        }

        if self.plot_window is not None:
            self.plot_window.close()
            self.plot_window = None

        self.view_detail_btn.setEnabled(True)
        self.refresh_result_status(f"已检测 {total_count} 个 ROI，成功 {success_count} 个，成功率 {success_rate:.2%}")
        self.log(
            f"检测完成 ({method})，共检测 {total_count} 个 ROI，成功激活 {success_count} 个，成功率 {success_rate:.2%}"
        )
        QMessageBox.information(
            self,
            "检测完成",
            f"方法: {method}\n共检测 {total_count} 个 ROI，激活成功 {success_count} 个\n激活成功率：{success_rate:.2%}",
        )

    def show_detail_plot(self):
        if self.result_plot_data is None:
            return

        if self.plot_window is not None:
            try:
                if self.plot_window.isVisible():
                    self.plot_window.raise_()
                    self.plot_window.activateWindow()
                    return
            except RuntimeError:
                self.plot_window = None

        self._open_plot_window()

    def _clear_plot_window_reference(self, *args):
        self.plot_window = None

    def _close_existing_plot_window(self):
        if self.plot_window is None:
            return
        try:
            self.plot_window.close()
        except RuntimeError:
            pass
        self.plot_window = None

    def _open_plot_window(self):
        self._close_existing_plot_window()
        self.plot_window = InteractivePlotWindow(self.result_plot_data, theme=self.theme, parent=self)
        self.plot_window.destroyed.connect(self._clear_plot_window_reference)
        self.plot_window.show()
        self.plot_window.raise_()
        self.plot_window.activateWindow()

    # Legacy standalone post-check layout and workflow overrides
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        self.create_file_selection(main_layout)
        self.create_calibration_params(main_layout)
        self.create_QC(main_layout)
        self.create_log_area(main_layout)

    def create_file_selection(self, layout):
        group = QGroupBox("输入数据")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.stat_btn = QPushButton("stat.npy")
        self.iscell_btn = QPushButton("iscell.npy")
        self.suite2p_img_btn = QPushButton("Suite2p 参考图像")
        self.microscope_img_btn = QPushButton("显微镜图像")
        for button in (
            self.stat_btn,
            self.iscell_btn,
            self.suite2p_img_btn,
            self.microscope_img_btn,
        ):
            self.set_button_role(button, "secondary")

        self.stat_label = ElidedLabel("未加载")
        self.iscell_label = ElidedLabel("未加载")
        self.suite2p_img_label = ElidedLabel("未加载")
        self.microscope_img_label = ElidedLabel("未加载")
        for label in (
            self.stat_label,
            self.iscell_label,
            self.suite2p_img_label,
            self.microscope_img_label,
        ):
            self.setup_status_label(label, minimum_height=32)
            label.setAlignment(Qt.AlignCenter)

        grid.addWidget(self.stat_btn, 0, 0)
        grid.addWidget(self.stat_label, 0, 1)
        grid.addWidget(self.iscell_btn, 0, 2)
        grid.addWidget(self.iscell_label, 0, 3)
        grid.addWidget(self.suite2p_img_btn, 1, 0)
        grid.addWidget(self.suite2p_img_label, 1, 1)
        grid.addWidget(self.microscope_img_btn, 1, 2)
        grid.addWidget(self.microscope_img_label, 1, 3)
        for col in range(4):
            grid.setColumnStretch(col, 1)

        self.stat_btn.clicked.connect(lambda: self.load_npy_file("stat"))
        self.iscell_btn.clicked.connect(lambda: self.load_npy_file("iscell"))
        self.suite2p_img_btn.clicked.connect(self.load_suite2p_image)
        self.microscope_img_btn.clicked.connect(self.load_microscope_image)
        layout.addWidget(group)

    def create_calibration_params(self, layout):
        group = QGroupBox("配准")
        main_vbox = QVBoxLayout(group)
        params_grid = QGridLayout()
        params_grid.setHorizontalSpacing(10)
        params_grid.setVerticalSpacing(8)

        params_grid.addWidget(QLabel("模糊Sigma:"), 0, 0)
        self.set_sigma = GuardedDoubleSpinBox()
        self.set_sigma.setRange(0, 10)
        self.set_sigma.setDecimals(2)
        self.set_sigma.setValue(3.0)
        params_grid.addWidget(self.set_sigma, 0, 1)

        params_grid.addWidget(QLabel("对比度阈值:"), 0, 2)
        self.contrast_spin = GuardedDoubleSpinBox()
        self.contrast_spin.setRange(0.005, 0.1)
        self.contrast_spin.setDecimals(3)
        self.contrast_spin.setSingleStep(0.005)
        self.contrast_spin.setValue(0.01)
        params_grid.addWidget(self.contrast_spin, 0, 3)

        params_grid.addWidget(QLabel("补偿X:"), 0, 4)
        self.compensation_x = GuardedDoubleSpinBox()
        self.compensation_x.setRange(-500, 500)
        self.compensation_x.setDecimals(2)
        self.compensation_x.setValue(0.0)
        params_grid.addWidget(self.compensation_x, 0, 5)

        params_grid.addWidget(QLabel("最大匹配:"), 1, 0)
        self.max_matches_spin = GuardedSpinBox()
        self.max_matches_spin.setRange(1, 30)
        self.max_matches_spin.setValue(20)
        params_grid.addWidget(self.max_matches_spin, 1, 1)

        params_grid.addWidget(QLabel("匹配比率:"), 1, 2)
        self.ratio_spin = GuardedDoubleSpinBox()
        self.ratio_spin.setRange(0.5, 0.95)
        self.ratio_spin.setDecimals(2)
        self.ratio_spin.setSingleStep(0.05)
        self.ratio_spin.setValue(0.80)
        params_grid.addWidget(self.ratio_spin, 1, 3)

        params_grid.addWidget(QLabel("补偿Y:"), 1, 4)
        self.compensation_y = GuardedDoubleSpinBox()
        self.compensation_y.setRange(-500, 500)
        self.compensation_y.setDecimals(2)
        self.compensation_y.setValue(0.0)
        params_grid.addWidget(self.compensation_y, 1, 5)
        for col in (1, 3, 5):
            params_grid.setColumnStretch(col, 1)
        for col in (0, 2, 4):
            params_grid.setColumnStretch(col, 0)
        self.calibration_param_holder = QWidget(group)
        self.calibration_param_holder.setLayout(params_grid)
        self.calibration_param_holder.hide()
        for index in range(params_grid.count()):
            item = params_grid.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.calibrate_btn = QPushButton("计算配准")
        self.visualize_btn = QPushButton("查看对齐")
        self.clear_btn = QPushButton("清除配准")
        self.tips_btn = QPushButton("Tips")
        self.set_button_role(self.calibrate_btn, "primary")
        self.set_button_role(self.visualize_btn, "secondary")
        self.set_button_role(self.clear_btn, "warning")
        self.set_button_role(self.tips_btn, "secondary")
        for button in (self.calibrate_btn, self.visualize_btn, self.clear_btn, self.tips_btn):
            button.setMinimumWidth(110)
            btn_layout.addWidget(button)

        self.calibrate_btn.clicked.connect(self.compute_homography)
        self.visualize_btn.clicked.connect(self.visualize_calibration)
        self.clear_btn.clicked.connect(self.clearH)
        self.tips_btn.clicked.connect(self.show_tips)

        main_vbox.addLayout(btn_layout)
        layout.addWidget(group)

    def create_QC(self, layout):
        qc_container_widget = QWidget()
        qc_main_layout = QVBoxLayout(qc_container_widget)
        qc_main_layout.setContentsMargins(0, 0, 0, 0)
        qc_main_layout.setSpacing(6)

        content_box = QGroupBox("")
        grid = QGridLayout(content_box)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.eval_method_combo = GuardedComboBox()
        self.eval_method_combo.addItems(["Fold Increase", "Difference"])
        parent_method = getattr(self.parent(), "detection_method", "Fold Increase")
        method_index = self.eval_method_combo.findText(parent_method)
        if method_index >= 0:
            self.eval_method_combo.setCurrentIndex(method_index)
        self.detection_channel_combo = GuardedComboBox()
        self.detection_channel_combo.addItems(["PAGFP", "PAmCherry"])
        parent_channel = getattr(self.parent(), "detection_channel", "PAGFP")
        channel_index = self.detection_channel_combo.findText(parent_channel)
        if channel_index >= 0:
            self.detection_channel_combo.setCurrentIndex(channel_index)

        self.load_pre_btn = QPushButton("刺激前图像")
        self.load_post_btn = QPushButton("刺激后图像")
        self.set_button_role(self.load_pre_btn, "secondary")
        self.set_button_role(self.load_post_btn, "secondary")
        detection_image_tip = "Supports png/jpg/tif/tiff; single-frame grayscale tif/tiff is recommended."
        self.load_pre_btn.setToolTip(detection_image_tip)
        self.load_post_btn.setToolTip(detection_image_tip)
        grid.addWidget(self.load_pre_btn, 0, 0, 1, 2)
        grid.addWidget(self.load_post_btn, 0, 2, 1, 2)

        self.pre_activation_label = ElidedLabel("未选择文件")
        self.post_activation_label = ElidedLabel("未选择文件")
        for label in (self.pre_activation_label, self.post_activation_label):
            self.setup_status_label(label, minimum_height=32)
            label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.pre_activation_label, 1, 0, 1, 2)
        grid.addWidget(self.post_activation_label, 1, 2, 1, 2)

        grid.addWidget(QLabel("激活检测"), 2, 0)
        grid.addWidget(self.eval_method_combo, 2, 1)

        grid.addWidget(QLabel("检测通道:"), 2, 2)
        grid.addWidget(self.detection_channel_combo, 2, 3)

        grid.addWidget(QLabel("细胞直径(px):"), 3, 0)
        self.diameter_input = GuardedDoubleSpinBox()
        self.diameter_input.setRange(1, 100)
        self.diameter_input.setDecimals(2)
        self.diameter_input.setValue(12.0)
        grid.addWidget(self.diameter_input, 3, 1)

        self.threshold_label = QLabel("Fold Change阈值:")
        grid.addWidget(self.threshold_label, 3, 2)
        self.threshold_input = GuardedDoubleSpinBox()
        self.threshold_input.setDecimals(2)
        self.threshold_input.setValue(1.3)
        grid.addWidget(self.threshold_input, 3, 3)

        grid.addWidget(QLabel("X位移(Post)"), 4, 0)
        self.activation_correction_x = GuardedDoubleSpinBox()
        self.activation_correction_x.setRange(-50, 50)
        self.activation_correction_x.setDecimals(2)
        self.activation_correction_x.setSingleStep(0.1)
        self.activation_correction_x.setValue(0.0)
        grid.addWidget(self.activation_correction_x, 4, 1)

        grid.addWidget(QLabel("Y位移(Post)"), 4, 2)
        self.activation_correction_y = GuardedDoubleSpinBox()
        self.activation_correction_y.setRange(-50, 50)
        self.activation_correction_y.setDecimals(2)
        self.activation_correction_y.setSingleStep(0.1)
        self.activation_correction_y.setValue(0.0)
        grid.addWidget(self.activation_correction_y, 4, 3)

        for widget in (
            self.eval_method_combo,
            self.detection_channel_combo,
            self.diameter_input,
            self.threshold_input,
            self.activation_correction_x,
            self.activation_correction_y,
        ):
            widget.setMinimumWidth(0)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for col in (1, 3):
            grid.setColumnStretch(col, 1)
        for col in (0, 2):
            grid.setColumnStretch(col, 0)

        self.auto_correct_btn = QPushButton("估计位移")
        self.evaluate_btn = QPushButton("计算激活")
        self.set_button_role(self.auto_correct_btn, "secondary")
        self.set_button_role(self.evaluate_btn, "primary")
        action_button_layout = QHBoxLayout()
        action_button_layout.setSpacing(10)
        action_button_layout.addWidget(self.auto_correct_btn)
        action_button_layout.addWidget(self.evaluate_btn)
        grid.addLayout(action_button_layout, 5, 0, 1, 4)

        self.load_pre_btn.clicked.connect(self.load_pre_activation_image)
        self.load_post_btn.clicked.connect(self.load_activation_image)
        self.eval_method_combo.currentIndexChanged.connect(self.update_threshold_settings)
        self.eval_method_combo.currentIndexChanged.connect(self.sync_detection_controls_to_parent)
        self.detection_channel_combo.currentIndexChanged.connect(self.sync_detection_controls_to_parent)
        self.auto_correct_btn.clicked.connect(self.auto_correct_drift)
        self.evaluate_btn.clicked.connect(self.evaluate_activation_success)
        self.sync_detection_controls_to_parent()

        qc_main_layout.addWidget(content_box)
        layout.addWidget(qc_container_widget)

    def create_log_area(self, layout):
        group = QGroupBox("日志")
        vbox = QVBoxLayout(group)
        vbox.setContentsMargins(8, 12, 8, 8)
        self.log_area = QTextEdit()
        self.log_area.setObjectName("logArea")
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(180)
        self.log_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox.addWidget(self.log_area)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(group, 1)

    def refresh_context_banner(self):
        return

    def refresh_roi_subset_status(self, log_result=False):
        return

    def refresh_summary(self):
        return

    def refresh_result_status(self, text=None):
        return

    def sync_summary_parameters(self):
        return

    def sync_detection_controls_to_parent(self):
        parent = self.parent()
        if parent is not None:
            parent.detection_method = self.eval_method_combo.currentText()
            parent.detection_channel = self.detection_channel_combo.currentText()

    def log(self, message):
        self.log_area.append(translate_runtime_text(self.language, message))
        QApplication.processEvents()

    def show_tips(self):
        if self.language == "en":
            tip_text = (
                "1. Sigma Blur controls smoothing before feature extraction.\n"
                "2. Max Matches limits the retained matches in each quadrant.\n"
                "3. Lower Contrast Threshold makes SIFT detect weaker features.\n"
                "4. Lower Match Ratio is stricter; values near 0.80 are a good start.\n"
                "5. X/Y offsets apply manual adjustments to the registration result.\n"
                "6. If matches are insufficient, increase Sigma, increase Match Ratio, or lower the Contrast Threshold."
            )
        else:
            tip_text = (
                "1. 模糊Sigma用于控制特征提取前的平滑程度。\n"
                "2. 最大匹配限制每个象限保留的匹配点数量。\n"
                "3. 对比度阈值越低，SIFT更容易检出弱特征。\n"
                "4. 匹配比率越小越严格，通常优先在0.80附近调整。\n"
                "5. X/Y补偿用于对校准结果做手动微调。\n"
                "6. 如果匹配点不足，优先尝试增大Sigma、提高匹配比率，或适当降低对比度阈值。"
            )
        QMessageBox.information(self, self.tr_text("参数说明 Tips"), tip_text)

    def load_npy_file(self, file_type):
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"选择{file_type}文件",
            self.default_savepath or "",
            "Numpy Files (*.npy)",
        )
        if not path:
            return

        try:
            data = np.load(path, allow_pickle=True)
            self.default_savepath = os.path.dirname(path)
            if file_type == "stat":
                self.stat_data = data
                self.stat_path = path
                self.stat_label.setText(os.path.basename(path))
                self.stat_label.setToolTip(path)
            elif file_type == "iscell":
                self.iscell_data = data
                self.iscell_name = os.path.splitext(os.path.basename(path))[0]
                self.iscell_path = path
                self.iscell_label.setText(os.path.basename(path))
                self.iscell_label.setToolTip(path)
            self.extract_roi_centers()
            self.log(f"成功加载 {file_type} 文件")
            self.push_shared_data_to_parent(file_type)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {e}")

    def extract_roi_centers(self):
        if self.stat_data is None or self.iscell_data is None:
            self.valid = np.array([], dtype=int)
            self.centers = []
            return

        try:
            self.valid = np.where(self.iscell_data[:, 0] == 1)[0]
            self.centers = [self.stat_data[i]["med"][::-1] for i in self.valid]
            self.valid_to_rel = {int(abs_idx): rel_idx for rel_idx, abs_idx in enumerate(self.valid.tolist())}
            self.log(f"提取到 {len(self.centers)} 个有效ROI")
        except Exception as e:
            self.valid = np.array([], dtype=int)
            self.centers = []
            self.valid_to_rel = {}
            self.log(f"ROI提取错误: {e}")
            QMessageBox.warning(self, "警告", "请检查加载的 stat/iscell 文件")

    def load_suite2p_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Suite2P图像",
            self.default_savepath or "",
            "Images (*.png *.jpg *.tif *.tiff)",
        )
        if not path:
            return

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            QMessageBox.critical(self, "错误", "图像加载失败")
            return

        original_shape = image.shape
        original_dtype = image.dtype
        suffix = ""
        if image.shape != (1024, 1024):
            image = cv2.resize(image, (1024, 1024), interpolation=cv2.INTER_CUBIC)
            suffix = ", 上采样至(1024, 1024)"

        self.suite2p_img = image
        self.suite2p_img_path = path
        self.suite2p_img_label.setText(os.path.basename(path))
        self.suite2p_img_label.setToolTip(path)
        self.log(f"加载Suite2P图像: {original_shape}, {original_dtype}{suffix}")
        self.push_shared_data_to_parent("suite2p")

    def load_microscope_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择显微镜图像",
            self.default_savepath or "",
            "Images (*.png *.jpg *.tif *.tiff)",
        )
        if not path:
            return

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            QMessageBox.critical(self, "错误", "图像加载失败")
            return

        original_shape = image.shape
        original_dtype = image.dtype
        suffix = ""
        if image.shape != (1024, 1024):
            image = cv2.resize(image, (1024, 1024), interpolation=cv2.INTER_CUBIC)
            suffix = ", 上采样至(1024, 1024)"

        self.microscope_img = image
        self.microscope_img_path = path
        self.microscope_img_label.setText(os.path.basename(path))
        self.microscope_img_label.setToolTip(path)
        self.log(f"加载显微镜图像: {original_shape}, {original_dtype}{suffix}")
        self.push_shared_data_to_parent("microscope")

    def update_threshold_settings(self):
        method = self.eval_method_combo.currentText()
        if method == "Fold Increase":
            self.threshold_label.setText(self.tr_text("Fold Change阈值:"))
            self.threshold_input.setRange(0.1, 20.0)
            self.threshold_input.setSingleStep(0.1)
            self.threshold_input.setValue(1.3)
        else:
            self.threshold_label.setText(self.tr_text("阈值(差值):"))
            self.threshold_input.setRange(-255.0, 255.0)
            self.threshold_input.setSingleStep(1.0)
            self.threshold_input.setValue(20.0)

    def auto_correct_drift(self):
        if self.pre_activation_img is None or self.activation_img is None:
            QMessageBox.warning(self, "错误", "请先加载激活前和激活后图像")
            return

        self.log("开始自动位移校准...")
        try:
            pre_img_float = self.pre_activation_img.astype(np.float32)
            post_img_float = self.activation_img.astype(np.float32)
            shift, response = cv2.phaseCorrelate(pre_img_float, post_img_float)
            dx, dy = shift

            self.activation_correction_x.setValue(-dx)
            self.activation_correction_y.setValue(-dy)
            self.log(f"自动位移校准完成: 最佳位移 X={dx:.2f}, Y={dy:.2f} (置信度 {response:.2f})")
            QMessageBox.information(
                self,
                "成功",
                f"自动校准完成!\n计算出的位移 X: {dx:.2f}, Y: {dy:.2f} 已更新。",
            )
        except cv2.error as e:
            error_message = f"自动位移校准失败: OpenCV 错误: {e}"
            self.log(error_message)
            QMessageBox.critical(self, "错误", error_message)
        except Exception as e:
            error_message = f"发生未知错误: {e}"
            self.log(error_message)
            QMessageBox.critical(self, "错误", error_message)

    def detect_features_with_quadrants(self):
        if self.suite2p_img is None or self.microscope_img is None:
            QMessageBox.critical(self, "错误", "请先加载两幅图像")
            return False

        quadrant_size = 341
        quadrants = []
        for i in range(3):
            for j in range(3):
                x_start, y_start = j * quadrant_size, i * quadrant_size
                x_end = (j + 1) * quadrant_size if j < 2 else 1024
                y_end = (i + 1) * quadrant_size if i < 2 else 1024
                quadrants.append((i, j, x_start, y_start, x_end, y_end))

        sift = cv2.SIFT_create(
            nfeatures=0,
            nOctaveLayers=3,
            contrastThreshold=self.contrast_spin.value(),
            edgeThreshold=10,
            sigma=float(self.set_sigma.value()),
        )

        self.kp1, self.des1 = [], None
        mask = np.zeros_like(self.suite2p_img)
        for region in quadrants:
            i, j, xs, ys, xe, ye = region
            mask.fill(0)
            mask[ys:ye, xs:xe] = 255
            kp, des = sift.detectAndCompute(self.suite2p_img, mask)
            if des is not None and len(kp) > 0:
                self.kp1.extend(kp)
                self.des1 = des if self.des1 is None else np.vstack((self.des1, des))

        self.kp2, self.des2 = [], None
        mask = np.zeros_like(self.microscope_img)
        for region in quadrants:
            i, j, xs, ys, xe, ye = region
            mask.fill(0)
            mask[ys:ye, xs:xe] = 255
            kp, des = sift.detectAndCompute(self.microscope_img, mask)
            if des is not None and len(kp) > 0:
                self.kp2.extend(kp)
                self.des2 = des if self.des2 is None else np.vstack((self.des2, des))

        self.log_feature_distribution(quadrant_size)
        if self.des1 is None or self.des2 is None:
            QMessageBox.critical(self, "错误", "特征检测失败")
            return False

        flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
        matches = flann.knnMatch(self.des1, self.des2, k=2)
        self.matches = []
        for pair in matches:
            if len(pair) < 2:
                continue
            m, n = pair
            if m.distance < self.ratio_spin.value() * n.distance:
                pt1 = self.kp1[m.queryIdx].pt
                pt2 = self.kp2[m.trainIdx].pt
                if np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) <= 50:
                    self.matches.append(m)

        if len(self.matches) < 15:
            QMessageBox.critical(self, "错误", "匹配点不足")
            return False

        self.matches = sorted(self.matches, key=lambda item: item.distance)
        return True

    def log_feature_distribution(self, quadrant_size):
        suite2p_counts = np.zeros((3, 3), dtype=int)
        for kp in self.kp1:
            x, y = kp.pt
            i, j = int(y // quadrant_size), int(x // quadrant_size)
            suite2p_counts[min(i, 2), min(j, 2)] += 1

        micro_counts = np.zeros((3, 3), dtype=int)
        for kp in self.kp2:
            x, y = kp.pt
            i, j = int(y // quadrant_size), int(x // quadrant_size)
            micro_counts[min(i, 2), min(j, 2)] += 1

        self.log("\n各象限特征点分布:")
        for i in range(3):
            for j in range(3):
                self.log(f"象限({i},{j}): Suite2P={suite2p_counts[i, j]} | 显微镜={micro_counts[i, j]}")

    def compute_homography(self):
        if not self.detect_features_with_quadrants():
            return

        quadrant_size = 341
        quadrant_dict = {(i, j): [] for i in range(3) for j in range(3)}
        for match in self.matches:
            x, y = self.kp1[match.queryIdx].pt
            i, j = int(y // quadrant_size), int(x // quadrant_size)
            quadrant_dict[(min(i, 2), min(j, 2))].append(match)

        selected_matches = []
        for quadrant, matches in quadrant_dict.items():
            matches = sorted(matches, key=lambda item: item.distance)
            count = min(self.max_matches_spin.value(), len(matches))
            selected_matches.extend(matches[:count])
            self.log(f"象限{quadrant}: 使用{count}/{len(matches)}个匹配点")

        if len(selected_matches) < 15:
            QMessageBox.critical(self, "错误", "总匹配点不足")
            return

        self.log(f"共发现{len(selected_matches)}个匹配点")
        src_pts = np.float32([self.kp1[m.queryIdx].pt for m in selected_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.kp2[m.trainIdx].pt for m in selected_matches]).reshape(-1, 1, 2)
        self.H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if self.H is None:
            QMessageBox.critical(self, "错误", "单应性矩阵计算失败")
            return

        self.H[0, 2] += self.compensation_x.value()
        self.H[1, 2] += self.compensation_y.value()
        error = self.calculate_reprojection_error(src_pts, dst_pts)
        self.log(f"校准成功! 重投影误差: {error:.2f}像素")
        H_str = np.array2string(
            self.H,
            formatter={"float_kind": lambda value: f"{value:12.8f}"},
            suppress_small=True,
        ).replace("[", " ").replace("]", " ")
        self.log(f"单应性矩阵:\n{H_str}")

    def calculate_reprojection_error(self, src, dst):
        transformed = cv2.perspectiveTransform(src, self.H)
        return np.mean(np.linalg.norm(dst - transformed, axis=2))

    def visualize_calibration(self):
        if self.H is None:
            QMessageBox.critical(self, "错误", "请先计算单应性矩阵")
            return

        grid_size = 64
        x_coords = np.arange(0, 1024, grid_size)
        y_coords = np.arange(0, 1024, grid_size)
        grid = np.array([[x, y] for y in y_coords for x in x_coords], dtype=np.float32).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(grid, self.H)

        fig, axes = plt.subplots(1, 2, figsize=(18, 5))
        fig.patch.set_facecolor(self.theme["bg"])
        matched_img = cv2.drawMatches(
            self.suite2p_img,
            self.kp1,
            self.microscope_img,
            self.kp2,
            self.matches[:300],
            None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        axes[0].imshow(matched_img)
        axes[0].set_title("Feature Matching", color=self.theme["text"])
        axes[0].axis("off")

        ax = axes[1]
        all_x = np.concatenate([grid[:, 0, 0], transformed[:, 0, 0]])
        all_y = np.concatenate([grid[:, 0, 1], transformed[:, 0, 1]])
        max_range = max(np.ptp(all_x), np.ptp(all_y)) * 1.1
        mid_x = (np.max(all_x) + np.min(all_x)) / 2
        mid_y = (np.max(all_y) + np.min(all_y)) / 2
        ax.set_facecolor(self.theme["panel"])
        ax.set_aspect("equal")
        ax.set_xlim(mid_x - max_range / 2, mid_x + max_range / 2)
        ax.set_ylim(mid_y + max_range / 2, mid_y - max_range / 2)
        ax.scatter(grid[:, 0, 0], grid[:, 0, 1], c="#38bdf8", s=10, label="Suite2P", alpha=0.6)
        ax.scatter(transformed[:, 0, 0], transformed[:, 0, 1], c="#ef4444", s=10, label="Microscope", alpha=0.6)
        for i in range(1, 3):
            ax.axhline(i * 341, c=self.theme["border"], ls="--", lw=0.5, alpha=0.6)
            ax.axvline(i * 341, c=self.theme["border"], ls="--", lw=0.5, alpha=0.6)
        ax.legend()
        ax.set_title("Correction Map", color=self.theme["text"])
        ax.tick_params(colors=self.theme["muted"])
        for spine in ax.spines.values():
            spine.set_color(self.theme["border"])

        plt.tight_layout()
        plt.show()

    def clearH(self):
        if self.H is not None:
            self.H = None
            self.log("已清除单应性矩阵")

    def transform_coordinates(self, points):
        if self.H is None:
            raise ValueError("单应性矩阵未计算")
        return cv2.perspectiveTransform(points, self.H)

    def transform_centers(self, idx):
        raw_x, raw_y = self.centers[idx]
        points = np.array([[[raw_x * 2, raw_y * 2]]], dtype=np.float32)
        if self.H is not None:
            try:
                transformed = self.transform_coordinates(points)
                final_x, final_y = transformed[0][0]
            except Exception as e:
                self.log(f"坐标转换失败: {e}")
                final_x, final_y = points[0][0]
        else:
            final_x, final_y = points[0][0]
        return int(final_x), int(final_y)

    def _convert_detection_image_to_grayscale(self, image):
        if image.ndim == 2:
            return image

        if image.ndim != 3:
            raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")

        if image.shape[-1] in (3, 4):
            color_image = image[..., :3]
        elif image.shape[0] in (3, 4):
            color_image = np.moveaxis(image[:3], 0, -1)
        else:
            raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")

        gray = np.mean(color_image.astype(np.float32), axis=-1)
        if np.issubdtype(image.dtype, np.integer):
            info = np.iinfo(image.dtype)
            gray = np.clip(np.rint(gray), info.min, info.max).astype(image.dtype)
        else:
            gray = gray.astype(np.float32)
        return gray

    def _read_detection_image(self, path):
        ext = os.path.splitext(path)[1].lower()
        notes = []
        warning = None

        if ext in {".png", ".jpg", ".jpeg"}:
            warning = "PNG/JPG is supported, but single-frame grayscale tif/tiff is recommended for stable quantification."

        if ext in {".tif", ".tiff"}:
            with tifffile.TiffFile(path) as tif:
                if not tif.series:
                    raise ValueError("Failed to load image.")
                series = tif.series[0]
                raw_shape = tuple(series.shape)
                squeezed_shape = tuple(dim for dim in raw_shape if dim != 1)
                axes = getattr(series, "axes", "")

                if len(squeezed_shape) > 3:
                    raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")
                if len(squeezed_shape) == 3:
                    channel_like = (
                        squeezed_shape[-1] in (3, 4)
                        or squeezed_shape[0] in (3, 4)
                        or any(axis in axes for axis in ("S", "C"))
                    )
                    stack_like = any(axis in axes for axis in ("Z", "I", "T", "Q"))
                    if stack_like or not channel_like:
                        raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")

                image = series.asarray()
        else:
            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if image is None:
                raise ValueError("Failed to load image.")

        image = np.squeeze(image)
        if image.ndim > 3:
            raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")

        source_shape = tuple(image.shape)
        source_dtype = str(image.dtype)

        if image.ndim == 3:
            image = self._convert_detection_image_to_grayscale(image)
            notes.append("Converted to grayscale")

        if image.ndim != 2:
            raise ValueError("Detection supports only single-frame 2D images. Export a single frame first.")

        if image.shape != (1024, 1024):
            image = cv2.resize(image, (1024, 1024), interpolation=cv2.INTER_CUBIC)
            notes.append("Resized to (1024, 1024)")

        metadata = {
            "source_shape": source_shape,
            "source_dtype": source_dtype,
            "notes": notes,
            "warning": warning,
        }
        return image, metadata

    def load_pre_activation_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择激活前图像",
            self.default_savepath or "",
            "Images (*.png *.jpg *.jpeg *.tif *.tiff)",
        )
        if not path:
            return

        try:
            image, metadata = self._read_detection_image(path)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            return

        self.pre_activation_img = image
        self.pre_activation_label.setText(os.path.basename(path))
        self.pre_activation_label.setToolTip(path)
        note_text = ""
        if metadata["notes"]:
            note_text = " | " + "; ".join(metadata["notes"])
        self.log(
            f"加载激活前图像: {os.path.basename(path)} | {metadata['source_shape']}, {metadata['source_dtype']}{note_text}"
        )
        if metadata["warning"]:
            self.log(metadata["warning"])
            QMessageBox.information(self, "格式提示", metadata["warning"])

    def load_activation_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择激活后图像",
            self.default_savepath or "",
            "Images (*.png *.jpg *.jpeg *.tif *.tiff)",
        )
        if not path:
            return

        try:
            image, metadata = self._read_detection_image(path)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            return

        self.activation_img = image
        self.post_activation_label.setText(os.path.basename(path))
        self.post_activation_label.setToolTip(path)
        note_text = ""
        if metadata["notes"]:
            note_text = " | " + "; ".join(metadata["notes"])
        self.log(
            f"加载激活后图像: {os.path.basename(path)} | {metadata['source_shape']}, {metadata['source_dtype']}{note_text}"
        )
        if metadata["warning"]:
            self.log(metadata["warning"])
            QMessageBox.information(self, "格式提示", metadata["warning"])

    def get_roi_metrics_csv_path(self, method):
        metric_tag = "fold" if method == "Fold Increase" else "difference"
        channel = getattr(self, "detection_channel_combo", None)
        channel_tag = channel.currentText() if channel is not None else getattr(self.parent(), "detection_channel", "PAGFP")
        channel_tag = re.sub(r"[^A-Za-z0-9_-]+", "_", channel_tag).strip("_") or "channel"
        base_dir = self.default_savepath or os.getcwd()
        base_name = self.iscell_name or "post_check"
        return os.path.join(base_dir, f"{base_name}_post_check_{channel_tag}_{metric_tag}_roi_metrics.csv")

    def save_roi_metrics_csv(self, method, roi_rows):
        csv_path = self.get_roi_metrics_csv_path(method)
        fieldnames = [
            "roi_no",
            "suite2p_index",
            "method",
            "metric_label",
            "metric_value",
            "post_pre_ratio",
            "pre_mean",
            "post_mean",
            "activated",
            "in_bounds",
            "center_x",
            "center_y",
        ]
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(roi_rows)
        return csv_path

    def evaluate_activation_success(self):
        if self.pre_activation_img is None or self.activation_img is None:
            QMessageBox.warning(self, "错误", "请先加载激活前和激活后图像")
            return

        method = self.eval_method_combo.currentText()
        img_pre = self.pre_activation_img.astype(np.float32)
        img_post = self.activation_img.astype(np.float32)
        height, width = img_pre.shape
        radius = int(self.diameter_input.value() / 2)
        threshold = self.threshold_input.value()
        correction_x = self.activation_correction_x.value()
        correction_y = self.activation_correction_y.value()
        transform_matrix = np.float32([[1, 0, correction_x], [0, 1, correction_y]])
        img_post_corrected = cv2.warpAffine(img_post, transform_matrix, (width, height), borderValue=0)
        self.log(f"激活后图像已应用位移: X={correction_x:.2f}px, Y={correction_y:.2f}px")

        safe_pre = img_pre + 1e-6
        if method == "Fold Increase":
            display_map = img_post_corrected / safe_pre
            plot_title = self.tr_text("Pixel-wise Fold Increase")
            metric_label = self.tr_text("ROI Mean Fold Change")
            display_values = display_map[np.isfinite(display_map)]
            vmin = 1.0
            vmax = np.percentile(display_values, 99.5) if display_values.size else 1.0
            vmax = max(vmax, vmin + 1e-3)
        else:
            display_map = img_post_corrected - img_pre
            plot_title = self.tr_text("Pixel-wise Difference (Post - Pre)")
            metric_label = self.tr_text("ROI Mean Difference")
            display_values = display_map[np.isfinite(display_map)]
            vmax = np.percentile(display_values, 99.5) if display_values.size else 1.0
            vmin = np.percentile(display_values, 0.5) if display_values.size else -1.0
            if np.isclose(vmin, vmax):
                vmax = vmin + 1e-3

        results = []
        roi_metrics = []
        roi_rows = []
        transformed_centers = []
        suite2p_indices = []

        for idx in range(len(self.centers)):
            x_aligned, y_aligned = self.transform_centers(idx)
            transformed_centers.append((x_aligned, y_aligned))
            suite2p_index = int(self.valid[idx]) if idx < len(self.valid) else idx
            suite2p_indices.append(suite2p_index)
            cx_aligned, cy_aligned = int(round(x_aligned)), int(round(y_aligned))
            if not (radius < cx_aligned < width - radius and radius < cy_aligned < height - radius):
                roi_metrics.append(np.nan)
                results.append(False)
                roi_rows.append(
                    {
                        "roi_no": idx,
                        "suite2p_index": suite2p_index,
                        "method": method,
                        "metric_label": metric_label,
                        "metric_value": np.nan,
                        "post_pre_ratio": np.nan,
                        "pre_mean": np.nan,
                        "post_mean": np.nan,
                        "activated": False,
                        "in_bounds": False,
                        "center_x": float(x_aligned),
                        "center_y": float(y_aligned),
                    }
                )
                continue

            mask = np.zeros((2 * radius + 1, 2 * radius + 1), dtype=np.uint8)
            cv2.circle(mask, (radius, radius), radius, 1, -1)
            roi_mask = mask == 1
            pre_patch = img_pre[cy_aligned - radius:cy_aligned + radius + 1, cx_aligned - radius:cx_aligned + radius + 1]
            post_patch = img_post_corrected[
                cy_aligned - radius:cy_aligned + radius + 1,
                cx_aligned - radius:cx_aligned + radius + 1,
            ]

            mean_pre = np.mean(pre_patch[roi_mask])
            mean_post = np.mean(post_patch[roi_mask])
            if method == "Fold Increase":
                metric = mean_post / (float(mean_pre) + 1e-6)
            else:
                metric = mean_post - mean_pre

            metric_value = float(metric)
            is_active = bool(metric >= threshold)
            roi_metrics.append(metric_value)
            results.append(is_active)
            roi_rows.append(
                {
                    "roi_no": idx,
                    "suite2p_index": suite2p_index,
                    "method": method,
                    "metric_label": metric_label,
                    "metric_value": metric_value,
                    "post_pre_ratio": metric_value if method == "Fold Increase" else np.nan,
                    "pre_mean": float(mean_pre),
                    "post_mean": float(mean_post),
                    "activated": is_active,
                    "in_bounds": True,
                    "center_x": float(x_aligned),
                    "center_y": float(y_aligned),
                }
            )

        total = len(results)
        success_count = sum(1 for result in results if result)
        success_rate = success_count / total if total > 0 else 0.0
        csv_path = None
        if roi_rows:
            try:
                csv_path = self.save_roi_metrics_csv(method, roi_rows)
                self.log(f"ROI metrics CSV saved: {csv_path}")
            except Exception as e:
                self.log(f"Failed to save ROI metrics CSV: {e}")

        if total == 0:
            self.log(f"No ROI coordinates loaded. Showing only the pixel-wise heatmap. ROI metric = {metric_label}.")
            QMessageBox.information(self, self.tr_text("Info"), self.tr_text("No ROI coordinates loaded. Showing only the pixel-wise heatmap."))
        else:
            QMessageBox.information(
                self,
                self.tr_text("检测完成"),
                f"Method: {method}\nHeatmap: {plot_title}\nROI metric: {metric_label}\nTotal ROI: {total}\nActivated: {success_count}\nSuccess rate: {success_rate:.2%}\nCSV: {csv_path or 'not saved'}" if self.language == "en" else
                f"方法: {method}\n热图: {plot_title}\nROI指标: {metric_label}\nROI总数: {total}\n激活成功: {success_count}\n成功率: {success_rate:.2%}\nCSV: {csv_path or '未保存'}",
            )
            self.log(
                f"Detection complete ({method}); heatmap={plot_title}; ROI metric={metric_label}; total ROI={total}; activated={success_count}; success rate={success_rate:.2%}; csv={csv_path or 'not saved'}"
            )

        self.result_plot_data = {
            "img_post_corrected": img_post_corrected,
            "display_map": display_map,
            "plot_title": plot_title,
            "vmin": vmin,
            "vmax": vmax,
            "results": results,
            "centers": transformed_centers,
            "r": radius,
            "roi_metrics": roi_metrics,
            "metric_label": metric_label,
            "threshold": float(threshold),
            "suite2p_indices": suite2p_indices,
            "csv_path": csv_path,
            "roi_rows": roi_rows,
        }

        self._open_plot_window()
class AutomationThread(QThread):
    progress = pyqtSignal(int, int, float, float, int)
    progress_state = pyqtSignal(int, int, int, int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    preview = pyqtSignal(np.ndarray, np.ndarray, int)
    paused = pyqtSignal(bool)
    log_message = pyqtSignal(str)  # 新的信号


    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.running = True
        self._paused = False
        self._lock = QMutex()
        self._pause_cond = QWaitCondition()
        self._just_skipped = False

        self.start_idx = parent.start_spin.value()
        self.end_idx = parent.end_spin.value()
        self.delay = parent.delay_spin.value()
        bounded_end = min(self.end_idx, len(parent.centers)-1) if parent.centers else self.end_idx
        self.total_count = max(0, bounded_end - self.start_idx + 1)
        self.processed_count = 0
        self.stimulated_count = 0
        self.skipped_count = 0
        self.preview.connect(parent.update_preview, Qt.QueuedConnection)

    def log(self, message):
        self.log_message.emit(message)

    def signal_user_skip(self):
        with QMutexLocker(self._lock):
            self._just_skipped = True

    def emit_progress_state(self, status):
        self.progress_state.emit(
            self.processed_count,
            self.total_count,
            self.stimulated_count,
            self.skipped_count,
            status
        )
    

    def run(self):
        centers = self.parent.centers
        removed = self.parent.removed
        if not centers:
            self.error.emit("未找到有效ROI坐标")
            self.finished.emit()
            return
        
        try:

            start, end = self.start_idx, min(self.end_idx, len(centers)-1)
            self.total_count = max(0, end - start + 1)
            idx = start

            while idx <= end and self.running:
                abs_idx = self.parent.valid[idx]
                # 跳过
                if abs_idx in removed:
                    self.log(f"跳过 ROI No.{idx}")
                    self.processed_count += 1
                    self.skipped_count += 1
                    self.emit_progress_state("running")
                    idx += 1
                    continue

                # 预览下一个
                next_idx = idx + 1
                while next_idx <= end and self.parent.valid[next_idx] in removed:
                    next_idx += 1
               
                if next_idx <= len(centers)-1:
                    abs_next = self.parent.valid[next_idx]
                    self.emit_preview(abs_next)

                with QMutexLocker(self._lock):
                    while self._paused and self.running:
                        self._pause_cond.wait(self._lock)

                if not self.running:
                    break

                temp_x, temp_y = centers[idx]
                raw_x = temp_x * 2
                raw_y = temp_y * 2

                if self.parent.H is not None:
                    try:
                        transformed = self.parent.transform_coordinates(
                            np.array([[[raw_x, raw_y]]], dtype=np.float32)
                        )
                        base_x, base_y = transformed[0][0]
                    except Exception as e:
                        self.log(f"坐标转换失败: {str(e)}") 
                else:
                    base_x, base_y = raw_x, raw_y
                    
                current_comp_x = self.parent.compensation_x.value()
                current_comp_y = self.parent.compensation_y.value()

                offset = self.parent.offsets.get(abs_idx, (0,0))
                x = int(base_x + current_comp_x + offset[0])
                y = int(base_y + current_comp_y + offset[1])

                preview_offset = self.parent.preview_offset.get(abs_idx,(0,0))
                diameter = int(self.parent.roi_diameter)
                final_x = int(x + preview_offset[0]-diameter*0.5)
                final_y = int(y + preview_offset[1]-diameter*0.5)

                if getattr(self.parent, "debug_coordinate_logging", False):
                    self.log(
                        f"Coordinate breakdown ROI {abs_idx}: "
                        f"raw_center=({raw_x:.1f},{raw_y:.1f}) -> "
                        f"registered_center=({base_x:.1f},{base_y:.1f}) -> "
                        f"comp=({current_comp_x:.1f},{current_comp_y:.1f}) -> "
                        f"single_offset=({offset[0]:.1f},{offset[1]:.1f}) -> "
                        f"preview_offset=({preview_offset[0]:.1f},{preview_offset[1]:.1f}) -> "
                        f"diameter={diameter} -> final_top_left=({final_x},{final_y})"
                    )
                    self.log(f"单细胞校准: x: {offset[0]:.1f} + {preview_offset[0]:.1f} y: {offset[1]:.1f} + {preview_offset[1]:.1f}")

                try:
                    self.input_coordinates(final_x, final_y)
                except Exception as e:
                    self.error.emit(f"输入操作失败: {e}")
                    self.running = False
                    break

                self.processed_count += 1
                self.stimulated_count += 1
                self.emit_progress_state("running")
                self.progress.emit(idx, self.end_idx, final_x, final_y, self.parent.valid[idx])
                idx += 1

                # —— 可响应的“睡眠” —— #
                total_ms = int(self.delay * 1000)
                interval = 100          # 每 100ms 检查一次
                slept = 0

                while slept < total_ms and self.running:
                    with QMutexLocker(self._lock):
                        # 如果暂停，就在条件上等待
                        while self._paused and self.running:
                            self._pause_cond.wait(self._lock)
                        
                        if self._just_skipped:
                            slept = 0  # 刷新延迟时间
                            self._just_skipped = False # 立刻重置标志，防止重复增加

                    QThread.msleep(interval)
                    slept += interval

                if not self.running:
                    break

        except Exception as e:
                self.log(f" {str(e)}") 
                self.error.emit("自动化中出现未知错误")

        self.finished.emit()

    def toggle_pause(self):
        """切换暂停/继续：暂停时线程会阻塞在 wait 上，继续时唤醒它"""
        with QMutexLocker(self._lock):
            self._paused = not self._paused
            self.paused.emit(self._paused)
            self.emit_progress_state("paused" if self._paused else "running")
            if not self._paused:
                # 从暂停状态恢复时，唤醒线程
                self._pause_cond.wakeAll()


    def input_coordinates(self, x, y):
        previous_pause = pyautogui.PAUSE
        previous_clipboard = None
        should_restore_clipboard = False
        protected = False
        pyautogui.PAUSE = self.parent.automation_input_pause
        stim_pause = self.parent.pyautogui_delay / 1000.0
        self.log(f"准备写入坐标 -> X:{int(x)} Y:{int(y)}")

        try:
            if pyperclip is not None:
                try:
                    previous_clipboard = pyperclip.paste()
                    should_restore_clipboard = True
                except Exception:
                    previous_clipboard = None
                    should_restore_clipboard = False

            protected = self.parent.begin_pyautogui_critical_section(log_func=self.log)
            self.parent.write_registered_field_value('x_pos', x, "X", log_func=self.log, restore_clipboard=False)
            self.parent.write_registered_field_value('y_pos', y, "Y", log_func=self.log, restore_clipboard=False)

            if 'stimulate_pos' in self.parent.registered_pos:
                pyautogui.click(*self.parent.registered_pos['stimulate_pos'])
                time.sleep(stim_pause)
                self.parent.move_mouse_to_live_preview_center(log_func=self.log)
        finally:
            if should_restore_clipboard and pyperclip is not None:
                try:
                    pyperclip.copy(previous_clipboard)
                except Exception:
                    pass
            if protected:
                self.parent.end_pyautogui_critical_section(log_func=self.log)
            pyautogui.PAUSE = previous_pause

    def emit_preview(self, abs_i):
        """生成并发送预览图像"""
        rel_i = list(self.parent.valid).index(abs_i)
        x0, y0 = self.parent.centers[rel_i]
        raw_x, raw_y = int(x0*2), int(y0*2)

        if self.parent.H is not None:
            try:
                transformed = self.parent.transform_coordinates(
                    np.array([[[raw_x, raw_y]]], dtype=np.float32)
                )
                base_x, base_y = transformed[0][0]
            except Exception as e:
                self.log(f"坐标转换失败: {str(e)}")
                
        else:
            base_x, base_y = raw_x, raw_y
            
        current_comp_x = self.parent.compensation_x.value()
        current_comp_y = self.parent.compensation_y.value()

        offset = self.parent.offsets.get(abs_i, (0,0))
        x = int(base_x + current_comp_x + offset[0])
        y = int(base_y + current_comp_y + offset[1])

        if self.parent.live_img is not None:
            temp_microscope_image = self.parent.live_img
        else: temp_microscope_image = self.parent.microscope_img


        if len(temp_microscope_image.shape) == 2:
            micro_color = cv2.cvtColor(temp_microscope_image, cv2.COLOR_GRAY2BGR)
        else:
            micro_color = temp_microscope_image.copy()

        micro = self.parent.extract_single_patch(image=micro_color,
                center_x=x,
                center_y=y,
                patch_size=self.parent.patch_size,
                denoise=True)
        
        if len(self.parent.suite2p_img.shape) == 2:
            suite2p_color = cv2.cvtColor(self.parent.suite2p_img, cv2.COLOR_GRAY2BGR)
        else:
            suite2p_color = self.parent.suite2p_img.copy()
        
        suite2p = self.parent.extract_single_patch_withmask(image=suite2p_color,
                center_x=raw_x,
                center_y=raw_y,
                patch_size=self.parent.patch_size,
                denoise=True,
                abs_index = abs_i)
        

        self.preview.emit(micro, suite2p, rel_i)

    

class AdvancedCalibrationGUI(QWidget):
    position_registered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.position_registered.connect(self.refresh_position_lights)
        self.app_settings = self.load_app_settings()
        self.language = self.app_settings.get("language", "en")
        self.setWindowTitle(self.tr_text("OptoStim2P v5.1.2"))
        self.setWindowIcon(get_app_icon())
        self.setGeometry(100, 100, 960, 780)
        self.setObjectName("mainWindow")
        
        self.suite2p_img = None
        self.microscope_img = None
        self.live_img = None
        self.suite2p_img_withmask = None
        self.suite2p_mask_preview_window = None
        self.iscell_data = None
        self.stat_data = None
        self.H = None
        self.centers = []
        self.registered_pos = {}
        self.automation_thread = None
        self.kp1 = None
        self.kp2 = None
        self.matches = None
        self.current_index = None
        self.valid = None
        self.patches = []
        self.offsets = {}
        self.removed = set()
        self.stimulated = set()
        self.post_check_window = None
        self.restore_topmost_after_automation = False
        self.restore_window_after_automation = False
        self.automation_start_pending = False
        self.automation_input_pause = 0.005
        self.field_focus_pause = 0.025
        self.field_clear_pause = 0.008
        self.double_click_interval = 0.035
        self.debug_coordinate_logging = False
        self._pyautogui_input_blocked = False
        self._pyautogui_blockinput_warned = False
        self._block_input_func = None
        self._file_load_in_progress = False
        

        self.default_savepath = None
        self.iscell_name = None
        self.stat_path = None
        self.iscell_path = None
        self.suite2p_img_path = None
        self.microscope_img_path = None
        self.z_stack = None
        self.z_stack_path = None

        self.roi_diameter = 10
        self.pyautogui_delay = 40 # 单位：ms
        self.detection_method = "Fold Increase"
        self.detection_channel = "PAGFP"
        self.patch_size = 40
        self.set_alpha = 0.3
        self.set_gamma = 1.6
        self.set_gammathres = 40
        self.ifdenoise = True
        self.autosave = True
        self.set_patchkernel = 9
        self.suffix = ""
        self.theme = {
            "bg": "#11161c",
            "surface": "#0f1720",
            "panel": "#18212b",
            "panel_alt": "#1d2a36",
            "border": "#2a3a4c",
            "text": "#e8eef5",
            "muted": "#8fa1b3",
            "accent": "#38bdf8",
            "accent_soft": "#17354a",
            "warning": "#f59e0b",
            "warning_soft": "#433114",
            "danger": "#ef4444",
            "danger_soft": "#3a171c",
            "success": "#22c55e",
        }


        self.preview_offset={}

        self.preview_label  = QLabel()   # 左侧：显微镜
        self.s2p_preview_label  = QLabel()   # 右侧：Suite2P（只读）
        self.preview_label.setFixedSize(180, 180)

        self.current_preview_index = -1  # 当前预览的细胞索引
        self.preview_click_enabled = True
        self.progress_state = {
            "processed": 0,
            "total": 0,
            "stimulated": 0,
            "skipped": 0,
            "status": "idle",
        }
        
        self.init_ui()
        self.apply_language_to_ui()
        self.apply_theme()
        self.init_hotkeys()

    def init_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        mode_bar = QFrame()
        mode_bar.setObjectName("modeBar")
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(12, 10, 12, 10)
        mode_layout.setSpacing(10)

        self.activation_mode_btn = QPushButton("刺激")
        self.detection_mode_btn = QPushButton("检测")
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("settingsButton")
        self.activation_mode_btn.setMinimumWidth(92)
        self.detection_mode_btn.setMinimumWidth(92)
        self.settings_btn.setFixedSize(36, 36)
        self.activation_mode_btn.clicked.connect(lambda: self.switch_mode("activation"))
        self.detection_mode_btn.clicked.connect(lambda: self.switch_mode("detection"))
        self.settings_btn.clicked.connect(self.show_advanced_settings)
        mode_layout.addWidget(self.activation_mode_btn)
        mode_layout.addWidget(self.detection_mode_btn)
        mode_layout.addStretch()
        mode_layout.addWidget(self.settings_btn)
        outer_layout.addWidget(mode_bar)

        self.page_stack = QStackedWidget()
        self.page_stack.setObjectName("pageStack")
        outer_layout.addWidget(self.page_stack, 1)

        self.activation_page = QScrollArea()
        self.activation_page.setObjectName("pageScrollArea")
        self.activation_page.setWidgetResizable(True)
        self.activation_page.setFrameShape(QScrollArea.NoFrame)
        self.activation_page.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        activation_content = QWidget()
        activation_content.setObjectName("scrollContent")
        main_layout = QVBoxLayout(activation_content)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        self.create_file_selection(main_layout)
        self.create_calibration_params(main_layout)
        self.create_main_controls(main_layout)
        self.create_preview_section(main_layout)
        self.create_log_area(main_layout)
        self.activation_page.setWidget(activation_content)
        self.page_stack.addWidget(self.activation_page)

        self.detection_page = DetectionPage(theme=self.theme, parent=self)
        self.detection_page_scroll = QScrollArea()
        self.detection_page_scroll.setObjectName("pageScrollArea")
        self.detection_page_scroll.setWidgetResizable(True)
        self.detection_page_scroll.setFrameShape(QScrollArea.NoFrame)
        self.detection_page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.detection_page_scroll.setWidget(self.detection_page)
        self.page_stack.addWidget(self.detection_page_scroll)

        self.setLayout(outer_layout)
        self.current_mode = "activation"
        self.switch_mode("activation", force=True)
        self.update_mode_switch_state()

    def tr_text(self, text):
        return translate_runtime_text(self.language, text)

    def load_app_settings(self):
        return load_app_settings_file()

    def save_app_settings(self):
        self.app_settings["language"] = self.language
        save_app_settings_file(self.app_settings)

    def apply_language_to_ui(self):
        apply_language_to_widget_tree(self, self.language)
        if hasattr(self, "detection_page"):
            self.detection_page.language = self.language
            apply_language_to_widget_tree(self.detection_page, self.language)

    def set_button_role(self, button, role):
        button.setProperty("role", role)
        style = button.style()
        if style is not None:
            style.unpolish(button)
            style.polish(button)

    def mark_file_status(self, label):
        label.setObjectName("fileStatus")
        label.setMinimumWidth(0)
        label.setMinimumHeight(28)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        label.setAlignment(Qt.AlignCenter)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def label_full_text(self, label):
        return getattr(label, "_full_text", label.text())

    def set_file_status_text(self, label, text, tooltip=None):
        if label is None:
            return
        label.setText(text)
        if tooltip:
            label.setToolTip(tooltip)

    def sync_shared_data_to_detection(self):
        detection_page = getattr(self, "detection_page", None)
        if detection_page is None:
            return
        if hasattr(detection_page, "apply_shared_data_from_parent"):
            detection_page.apply_shared_data_from_parent()

    def apply_shared_data_from_detection(self, source):
        detection_page = getattr(self, "detection_page", None)
        if detection_page is None:
            return

        if source == "stat":
            self.stat_data = detection_page.stat_data
            self.stat_path = getattr(detection_page, "stat_path", None)
            self.set_file_status_text(
                self.stat_label,
                self.label_full_text(detection_page.stat_label),
                self.stat_path,
            )
        elif source == "iscell":
            self.iscell_data = detection_page.iscell_data
            self.iscell_name = getattr(detection_page, "iscell_name", None)
            self.default_savepath = getattr(detection_page, "default_savepath", None)
            self.iscell_path = getattr(detection_page, "iscell_path", None)
            self.set_file_status_text(
                self.iscell_label,
                self.label_full_text(detection_page.iscell_label),
                self.iscell_path,
            )
        elif source == "suite2p":
            self.suite2p_img = detection_page.suite2p_img
            self.suite2p_img_path = getattr(detection_page, "suite2p_img_path", None)
            self.set_file_status_text(
                self.suite2p_img_label,
                self.label_full_text(detection_page.suite2p_img_label),
                self.suite2p_img_path,
            )
        elif source == "microscope":
            self.microscope_img = detection_page.microscope_img
            self.live_img = self.microscope_img.copy() if self.microscope_img is not None else None
            self.microscope_img_path = getattr(detection_page, "microscope_img_path", None)
            self.set_file_status_text(
                self.microscope_img_label,
                self.label_full_text(detection_page.microscope_img_label),
                self.microscope_img_path,
            )

        if source in {"stat", "iscell"}:
            self.extract_roi_centers()
            self.stimulated = set()
            self.log("重置已激活ROI列表")

        if source in {"stat", "iscell", "suite2p"} and (
            self.suite2p_img is not None and self.stat_data is not None and self.iscell_data is not None
        ):
            try:
                self._update_suite2p_overlay()
            except Exception as e:
                self.log(f"Masks预览失败: {e}")

        self.sync_shared_data_to_detection()

    def apply_theme(self):
        app = QApplication.instance()
        if app is None:
            return

        app.setStyle("Fusion")
        app.setStyleSheet(self.build_stylesheet())

    def build_stylesheet(self):
        return """
        QWidget {{
            color: {text};
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 12px;
        }}
        QWidget#mainWindow, QWidget#auxWindow, QDialog, QMessageBox {{
            background-color: {bg};
        }}
        QWidget#scrollContent, QStackedWidget#pageStack, QScrollArea#pageScrollArea {{
            background-color: {bg};
        }}
        QStackedWidget#pageStack > QWidget {{
            background-color: {bg};
        }}
        QScrollArea#pageScrollArea > QWidget > QWidget {{
            background-color: {bg};
        }}
        QScrollArea#pageScrollArea QScrollBar:vertical,
        QScrollArea#pageScrollArea QScrollBar:horizontal {{
            background-color: {panel};
        }}
        QFrame#modeBar {{
            background-color: {panel};
            border-bottom: none;
        }}
        QGroupBox {{
            background-color: {panel};
            border: none;
            border-radius: 12px;
            margin-top: 10px;
            padding: 8px 8px 8px 8px;
        }}
        QGroupBox[plainSection="true"] {{
            margin-top: 0px;
            padding: 0px;
            border-radius: 12px;
            border: none;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 2px 8px;
            border: none;
            border-radius: 10px;
            background-color: {panel_alt};
            color: {text};
            font-weight: 600;
        }}
        QGroupBox[centerTitle="true"]::title {{
            subcontrol-position: top center;
            left: 0px;
            padding: 2px 10px;
        }}
        QLabel {{
            background: transparent;
        }}
        QLabel#fileStatus {{
            background-color: {surface};
            border: none;
            border-radius: 9px;
            padding: 5px 9px;
            color: {muted};
        }}
        QLabel#positionHint {{
            background-color: {surface};
            border: none;
            border-radius: 10px;
            padding: 6px 9px;
            color: {muted};
        }}
        QFrame#positionSignalPanel {{
            background-color: {surface};
            border: none;
            border-radius: 10px;
        }}
        QLabel[positionLight="true"] {{
            border: none;
            border-radius: 5px;
            min-width: 10px;
            max-width: 10px;
            min-height: 10px;
            max-height: 10px;
        }}
        QLabel[positionSignalText="true"] {{
            color: {muted};
            background: transparent;
            border: none;
        }}
        QLabel#previewInfo {{
            background-color: {surface};
            border: none;
            border-radius: 10px;
            padding: 8px 12px;
            color: {accent};
            font-weight: 600;
        }}
        QFrame#previewImage {{
            background-color: #0b1117;
            border: none;
            border-radius: 14px;
        }}
        QFrame#suite2pPreview {{
            background-color: #0b1117;
            border: none;
            border-radius: 14px;
        }}
        QLabel#previewImageContent, QLabel#suite2pPreviewContent {{
            background: transparent;
            border: none;
        }}
        QLabel[previewPanelTitle="true"] {{
            color: {muted};
            background: transparent;
            border: none;
            font-weight: 600;
            padding: 0px 0px 4px 2px;
        }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background-color: {surface};
            border: none;
            border-radius: 10px;
            padding: 5px 9px;
            selection-background-color: {accent};
            selection-color: {bg};
        }}
        QComboBox {{
            background-color: {surface};
            border: none;
            border-radius: 10px;
            padding: 5px 9px;
            min-height: 22px;
            color: {text};
        }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
            border: none;
            background-color: #13202a;
        }}
        QComboBox:focus, QComboBox:hover {{
            border: none;
            background-color: #13202a;
        }}
        QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QTextEdit:disabled {{
            background-color: #151d26;
            border: none;
            color: {muted};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 22px;
            background: transparent;
        }}
        QComboBox QAbstractItemView {{
            background-color: {panel};
            alternate-background-color: {panel};
            color: {text};
            border: none;
            outline: 0;
            padding: 4px 0px;
            selection-background-color: {accent_soft};
            selection-color: {text};
        }}
        QListView#comboPopupView {{
            background-color: {panel};
            color: {text};
            border: none;
            outline: 0;
            padding: 4px 0px;
        }}
        QListView#comboPopupView::viewport {{
            background-color: {panel};
            border: none;
            outline: 0;
        }}
        QListView#comboPopupView::item {{
            min-height: 24px;
            padding: 4px 8px;
            border: none;
            background-color: {panel};
        }}
        QListView#comboPopupView::item:hover,
        QListView#comboPopupView::item:selected {{
            background-color: {accent_soft};
            color: {text};
            border: none;
        }}
        QListView#comboPopupView QScrollBar:horizontal {{
            height: 0px;
            background: transparent;
            border: none;
        }}
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            width: 18px;
            border: none;
            background: transparent;
        }}
        QPushButton {{
            background-color: #1d2833;
            border: none;
            border-radius: 10px;
            padding: 5px 9px;
            min-height: 30px;
            color: {text};
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #243342;
        }}
        QPushButton:pressed {{
            background-color: #13202a;
        }}
        QPushButton:disabled {{
            background-color: #141b22;
            color: {muted};
        }}
        QPushButton[role="secondary"] {{
            background-color: #1d2833;
        }}
        QPushButton[role="primary"] {{
            background-color: {accent_soft};
            color: #f1fbff;
            font-weight: 600;
        }}
        QPushButton[role="primary"]:hover {{
            background-color: #1c4660;
        }}
        QPushButton[role="warning"] {{
            background-color: {warning_soft};
            color: #fff7e6;
            font-weight: 600;
        }}
        QPushButton[role="warning"]:hover {{
            background-color: #5b4319;
        }}
        QPushButton[role="danger"] {{
            background-color: {danger_soft};
            color: #fff1f2;
            font-weight: 600;
        }}
        QPushButton[role="danger"]:hover {{
            background-color: #531d25;
        }}
        QPushButton#settingsButton {{
            background-color: #1d2833;
            border: none;
            border-radius: 10px;
            padding: 0px;
            min-height: 36px;
            min-width: 36px;
            font-size: 18px;
            font-weight: 600;
        }}
        QPushButton#settingsButton:hover {{
            background-color: #243342;
        }}
        QPushButton#settingsButton:pressed {{
            background-color: #13202a;
        }}
        QCheckBox {{
            spacing: 8px;
            color: {text};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: none;
            background-color: {surface};
        }}
        QCheckBox::indicator:hover {{
            background-color: #13202a;
        }}
        QCheckBox::indicator:checked {{
            background-color: {accent};
            border: none;
        }}
        QTextEdit#logArea {{
            background-color: #0b1117;
            border: none;
            border-radius: 12px;
            padding: 10px 12px;
            color: #d7e6f4;
            font-family: "Cascadia Mono", "Consolas", "Microsoft YaHei UI";
            font-size: 11px;
        }}
        QToolBar {{
            background-color: {panel};
            border: none;
            border-radius: 10px;
            padding: 4px;
            spacing: 4px;
        }}
        QProgressBar#progressBar {{
            background-color: {surface};
            border: none;
            border-radius: 11px;
            color: {text};
            min-height: 24px;
            text-align: center;
            font-weight: 600;
        }}
        QProgressBar#progressBar::chunk {{
            background-color: {accent};
            border-radius: 9px;
            margin: 2px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 4px 0 4px 0;
        }}
        QScrollBar::handle:vertical {{
            background: {border};
            min-height: 28px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {accent};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
            height: 0px;
        }}
        QToolTip {{
            background-color: {panel_alt};
            color: {text};
            border: none;
            padding: 6px 8px;
        }}
        """.format(**self.theme)

    def style_matplotlib_figure(self, fig):
        fig.patch.set_facecolor(self.theme["bg"])
        for ax in fig.axes:
            ax.set_facecolor(self.theme["panel"])
            ax.title.set_color(self.theme["text"])
            ax.xaxis.label.set_color(self.theme["muted"])
            ax.yaxis.label.set_color(self.theme["muted"])
            ax.tick_params(colors=self.theme["muted"])
            for spine in ax.spines.values():
                spine.set_color(self.theme["border"])

            legend = ax.get_legend()
            if legend is not None:
                frame = legend.get_frame()
                frame.set_facecolor(self.theme["panel"])
                frame.set_edgecolor(self.theme["border"])
                frame.set_alpha(0.96)
                for text in legend.get_texts():
                    text.set_color(self.theme["text"])

    def format_progress_text(self):
        status = self.progress_state["status"]
        processed = self.progress_state["processed"]
        total = self.progress_state["total"]
        stimulated = self.progress_state["stimulated"]
        skipped = self.progress_state["skipped"]

        if status == "idle" or total <= 0:
            return self.tr_text("未开始")

        prefix_map = {
            "running": self.tr_text("进度"),
            "paused": self.tr_text("已暂停"),
            "stopped": self.tr_text("已停止"),
            "finished": self.tr_text("已完成"),
            "error": self.tr_text("错误中断"),
        }
        prefix = prefix_map.get(status, self.tr_text("进度"))
        return f"{prefix} {processed}/{total} | {self.tr_text('已刺激')} {stimulated} | {self.tr_text('跳过')} {skipped}"

    def update_progress_ui(self, processed=None, total=None, stimulated=None, skipped=None, status=None):
        if processed is not None:
            self.progress_state["processed"] = max(0, int(processed))
        if total is not None:
            self.progress_state["total"] = max(0, int(total))
        if stimulated is not None:
            self.progress_state["stimulated"] = max(0, int(stimulated))
        if skipped is not None:
            self.progress_state["skipped"] = max(0, int(skipped))
        if status is not None:
            self.progress_state["status"] = status

        total_value = self.progress_state["total"]
        processed_value = min(self.progress_state["processed"], total_value) if total_value > 0 else 0
        self.progress_state["processed"] = processed_value

        if hasattr(self, "progress_bar"):
            self.progress_bar.setRange(0, max(1, total_value))
            self.progress_bar.setValue(processed_value)
            self.progress_bar.setFormat(self.format_progress_text())

    def reset_progress_ui(self):
        self.update_progress_ui(processed=0, total=0, stimulated=0, skipped=0, status="idle")

    def set_progress_status(self, status):
        self.update_progress_ui(status=status)

    def handle_progress_state(self, processed, total, stimulated, skipped, status):
        next_status = status
        if self.progress_state["status"] in {"stopped", "error"} and status in {"running", "paused"}:
            next_status = self.progress_state["status"]
        self.update_progress_ui(
            processed=processed,
            total=total,
            stimulated=stimulated,
            skipped=skipped,
            status=next_status,
        )

    def handle_pause_state(self, is_paused):
        if self.progress_state["status"] in {"stopped", "error", "finished", "idle"}:
            return
        self.set_progress_status("paused" if is_paused else "running")


    def create_preview_section(self, layout):
        group = QGroupBox("交互式对齐")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(12)
        preview_panel_size = 188
        preview_panel_height = 208
        preview_image_size = 168

        self.preview_label = QLabel()
        self.preview_label.setMouseTracking(True)
        self.preview_label.setFixedSize(preview_image_size, preview_image_size)
        self.preview_label.setObjectName("previewImageContent")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_info = QLabel("准备就绪 | 左键微调，右键跳过")
        self.preview_info.setObjectName("previewInfo")
        self.preview_info.setAlignment(Qt.AlignCenter)
        self.preview_info.setWordWrap(True)
        self.preview_info.hide()

        self.preview_panel = QFrame()
        self.preview_panel.setObjectName("previewImage")
        self.preview_panel.setFixedSize(preview_panel_size, preview_panel_height)
        preview_panel_layout = QVBoxLayout(self.preview_panel)
        preview_panel_layout.setContentsMargins(10, 7, 10, 10)
        preview_panel_layout.setSpacing(2)
        self.preview_panel_title = QLabel("Live")
        self.preview_panel_title.setProperty("previewPanelTitle", True)
        self.preview_panel_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        preview_panel_layout.addWidget(self.preview_panel_title)
        preview_panel_layout.addWidget(self.preview_label, 0, Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.setSpacing(8)
        vbox.addWidget(self.preview_panel, 0, Qt.AlignCenter)
        vbox.addStretch()

        s2p_box = QVBoxLayout()
        s2p_box.setSpacing(8)
        self.s2p_preview_label.setAlignment(Qt.AlignCenter)
        self.s2p_preview_label.setObjectName("suite2pPreviewContent")
        self.s2p_preview_label.setFixedSize(preview_image_size, preview_image_size)
        self.s2p_preview_panel = QFrame()
        self.s2p_preview_panel.setObjectName("suite2pPreview")
        self.s2p_preview_panel.setFixedSize(preview_panel_size, preview_panel_height)
        s2p_panel_layout = QVBoxLayout(self.s2p_preview_panel)
        s2p_panel_layout.setContentsMargins(10, 7, 10, 10)
        s2p_panel_layout.setSpacing(2)
        self.s2p_preview_panel_title = QLabel("Reference")
        self.s2p_preview_panel_title.setProperty("previewPanelTitle", True)
        self.s2p_preview_panel_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        s2p_panel_layout.addWidget(self.s2p_preview_panel_title)
        s2p_panel_layout.addWidget(self.s2p_preview_label, 0, Qt.AlignCenter)
        s2p_box.addWidget(self.s2p_preview_panel, 0, Qt.AlignCenter)
        s2p_box.addStretch()

        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(8)
        self.start_btn = QPushButton("开始 (Ctrl+K)")
        self.pause_btn = QPushButton("暂停/继续(Ctrl+P)")
        self.stop_btn = QPushButton("停止(Ctrl+Q)")
        self.skip_btn = QPushButton("跳过(Ctrl+/)")
        for b in [self.start_btn, self.pause_btn,self.stop_btn,self.skip_btn]:
            ctrl_layout.addWidget(b)
        self.set_button_role(self.start_btn, "primary")
        self.set_button_role(self.pause_btn, "secondary")
        self.set_button_role(self.stop_btn, "danger")
        self.set_button_role(self.skip_btn, "warning")
        ctrl_layout.addStretch()

        self.start_btn.clicked.connect(self.start_automation)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop_automation)
        self.skip_btn.clicked.connect(self.skip_current_cell)

        main_layout.addLayout(vbox,   50)
        main_layout.addLayout(s2p_box,50)      
        main_layout.addLayout(ctrl_layout,30)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        group_layout.addLayout(main_layout)
        group_layout.addWidget(self.progress_bar)
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.reset_progress_ui()
        # 初始化点击事件
        self.preview_label.mousePressEvent = self.on_preview_click  # 重写鼠标事件

    def skip_current_cell(self):

        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.signal_user_skip()

        
        max_idx = self.end_spin.value()
        idx = self.current_preview_index
        abs_idx = self.valid[idx]
        if idx < 0 or idx > len(self.centers)-1:
            self.log("超出可跳过范围")
            return

        # 记录跳过
        self.removed.add(abs_idx)
        self.log(f"跳过 ROI No.{abs_idx}: no.{idx}/{max_idx}")

        # 找到下一个有效的索引
        next_idx = idx + 1
        
        while next_idx <= max_idx and next_idx in self.removed:
            next_idx += 1

        if next_idx <= len(self.centers)-1:

            # 如果有自动化线程在跑，就用它来 preview
            if self.automation_thread and self.automation_thread.isRunning():
                with QMutexLocker(self.automation_thread._lock):
                    self.automation_thread._pause_cond.wakeAll()

                abs_next = self.valid[next_idx]  
                self.automation_thread.emit_preview(abs_next)
            else:
                # 否则直接用 update_preview 来手动更新界面
                if 0 <= next_idx < len(self.patches):
                    micro_patch, suite2p_patch, _ = self.patches[next_idx - self.start_spin.value()]
                    self.update_preview(micro_patch, suite2p_patch, next_idx)
        
        else: self.log("超出可跳过范围")

    def on_preview_click(self, event):
        """
        在自动化暂停时，点击显微镜预览图叠加校准偏移到当前细胞，
        并唤醒自动化线程继续执行。增加了详细日志以帮助调试。
        """
        # # 1) 检查线程和暂停状态
        # if not self.automation_thread:
        #     return
      
        # 2) 获取当前预览索引
        idx = self.current_preview_index
        if idx < 0:
            return

        # 3) 获取 pixmap 和 label 大小
        if event.button() == Qt.LeftButton:
                
            pixmap = self.preview_label.pixmap()
            if pixmap is None:
                return
            img_w, img_h = pixmap.width(), pixmap.height()
            lbl_w, lbl_h = self.preview_label.width(), self.preview_label.height()
    

            # 4) 计算点击相对图像的位置
            x_off = (lbl_w - img_w) // 2
            y_off = (lbl_h - img_h) // 2
            click_x = event.x() - x_off
            click_y = event.y() - y_off
        

            if click_x < 0 or click_y < 0 or click_x >= img_w or click_y >= img_h:
                return

            # 5) 映射到 40x40 patch 坐标系
            patch_size = max(1.0, float(getattr(self, "patch_size", 40)))
            patch_center = patch_size / 2.0
            scale_x = img_w / patch_size
            scale_y = img_h / patch_size
            rel_x = click_x / scale_x
            rel_y = click_y / scale_y
            dx = rel_x - patch_center
            dy = rel_y - patch_center

            # 6) 刷新已有 offset
            abs_i = self.valid[idx] 
            self.preview_offset[abs_i] = (dx, dy)

            self.log(f"校准更新 #{idx}: Δ({dx:.1f}, {dy:.1f})")

            # 7) 在界面上画标记
            self.show_preview_marker(dx, dy)
            

     
        elif event.button() == Qt.RightButton:
          
            self.skip_current_cell()
            

        else: return

    def create_file_selection(self, layout):
        group = QGroupBox("输入数据")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        
        self.stat_btn = QPushButton("stat.npy")
        self.stat_btn.clicked.connect(lambda: self.load_npy_file('stat'))
        self.stat_label = ElidedLabel("未加载")
        self.mark_file_status(self.stat_label)
        
        self.iscell_btn = QPushButton("iscell.npy")
        self.iscell_btn.clicked.connect(lambda: self.load_npy_file('iscell'))
        self.iscell_label = ElidedLabel("未加载")
        self.mark_file_status(self.iscell_label)
        
        self.suite2p_img_label = ElidedLabel("未加载")
        self.microscope_img_label = ElidedLabel("未加载")
        self.mark_file_status(self.suite2p_img_label)
        self.mark_file_status(self.microscope_img_label)

        self.suite2p_img_btn = QPushButton("Suite2p 参考图像")
        self.suite2p_img_btn.clicked.connect(self.load_suite2p_image)
        self.microscope_img_btn = QPushButton("显微镜图像")
        self.microscope_img_btn.clicked.connect(self.load_microscope_image)
        for btn in [self.stat_btn, self.iscell_btn, self.suite2p_img_btn, self.microscope_img_btn]:
            self.set_button_role(btn, "secondary")
        
        
        grid.addWidget(self.stat_btn, 0, 0)
        grid.addWidget(self.stat_label, 0, 1)
        grid.addWidget(self.iscell_btn, 0, 2)
        grid.addWidget(self.iscell_label, 0, 3)

        # 第二行：图像文件
       
        grid.addWidget(self.suite2p_img_btn, 1, 0)
        grid.addWidget(self.suite2p_img_label, 1, 1)
        grid.addWidget(self.microscope_img_btn, 1, 2)
        grid.addWidget(self.microscope_img_label, 1, 3)

        # 设置列宽比例
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 2)  # 原3改为2
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 0)
        grid.setColumnStretch(5, 0)
        grid.setColumnStretch(2, 1)

        group.setLayout(grid)
        layout.addWidget(group)

    def create_calibration_params(self, layout):
        group = QGroupBox("配准")
        main_vbox = QVBoxLayout()  # 改用垂直布局

        # 参数部分使用紧凑网格布局
        params_grid = QGridLayout()
        params_grid.setHorizontalSpacing(10)
        params_grid.setVerticalSpacing(8)
        
        # 第一列：分象限参数
        params_grid.addWidget(QLabel("模糊Sigma:"), 0, 0)
        self.set_sigma = GuardedDoubleSpinBox()
        self.set_sigma.setRange(0, 10)
        params_grid.addWidget(self.set_sigma, 0, 1)
        
        params_grid.addWidget(QLabel("最大匹配:"), 1, 0)
        self.max_matches_spin = GuardedSpinBox()
        self.max_matches_spin.setRange(1, 30)
        params_grid.addWidget(self.max_matches_spin, 1, 1)

        # 第二列：特征参数
        params_grid.addWidget(QLabel("对比度阈值:"), 0, 2)
        self.contrast_spin = GuardedDoubleSpinBox()
        self.contrast_spin.setRange(0.005, 0.1)
        self.contrast_spin.setDecimals(3)
        params_grid.addWidget(self.contrast_spin, 0, 3)
        
        params_grid.addWidget(QLabel("匹配比率:"), 1, 2)
        self.ratio_spin = GuardedDoubleSpinBox()
        self.ratio_spin.setRange(0.5, 0.95)
        params_grid.addWidget(self.ratio_spin, 1, 3)

        # 第三列：补偿参数
        params_grid.addWidget(QLabel("X补偿(pix):"), 0, 4)
        self.compensation_x = GuardedDoubleSpinBox()
        self.compensation_x.setRange(-500, 500)
        params_grid.addWidget(self.compensation_x, 0, 5)
        
        params_grid.addWidget(QLabel("Y补偿(pix):"), 1, 4)
        self.compensation_y = GuardedDoubleSpinBox()
        self.compensation_y.setRange(-500, 500)
        params_grid.addWidget(self.compensation_y, 1, 5)

        for spin in (
            self.set_sigma,
            self.max_matches_spin,
            self.contrast_spin,
            self.ratio_spin,
            self.compensation_x,
            self.compensation_y,
        ):
            spin.setMinimumWidth(0)
            spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for col in (1, 3, 5):
            params_grid.setColumnStretch(col, 1)
        for col in (0, 2, 4):
            params_grid.setColumnStretch(col, 0)
        self.calibration_param_holder = QWidget(group)
        self.calibration_param_holder.setLayout(params_grid)
        self.calibration_param_holder.hide()
        for index in range(params_grid.count()):
            item = params_grid.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
        
        calibration_actions_layout = QHBoxLayout()
        calibration_actions_layout.setSpacing(14)
        xy_group = QGroupBox("XY配准")
        xy_group.setProperty("centerTitle", True)
        xy_layout = QVBoxLayout(xy_group)
        xy_layout.setContentsMargins(12, 18, 12, 12)
        xy_layout.setSpacing(8)
        z_group = QGroupBox("Z轴对齐")
        z_group.setProperty("centerTitle", True)
        z_layout = QVBoxLayout(z_group)
        z_layout.setContentsMargins(12, 18, 12, 12)
        z_layout.setSpacing(8)
        xy_button_row = QHBoxLayout()
        xy_button_row.setSpacing(10)
        z_button_row = QHBoxLayout()
        z_button_row.setSpacing(10)
       
        self.calibrate_btn = QPushButton("计算配准")
        self.visualize_btn = QPushButton("查看对齐")
        
        self.zstack_btn = QPushButton("Z-stack Image")
        self.zcalib_btn = QPushButton("估计Z偏移")
        
        self.calibrate_btn.clicked.connect(self.compute_homography)
        self.visualize_btn.clicked.connect(self.visualize_calibration)
        
        self.zstack_btn.clicked.connect(self.load_z_stack_image)
        self.zcalib_btn.clicked.connect(self.show_zcalib)
        for button in (self.calibrate_btn, self.visualize_btn, self.zstack_btn, self.zcalib_btn):
            button.setMinimumWidth(150)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.set_button_role(self.calibrate_btn, "primary")
        self.set_button_role(self.zstack_btn, "secondary")
        self.set_button_role(self.zcalib_btn, "secondary")
        self.set_button_role(self.visualize_btn, "secondary")
        
        


        xy_button_row.addWidget(self.calibrate_btn)
        xy_button_row.addWidget(self.visualize_btn)
        z_button_row.addWidget(self.zstack_btn)
        z_button_row.addWidget(self.zcalib_btn)
        xy_layout.addLayout(xy_button_row)
        z_layout.addLayout(z_button_row)
        calibration_actions_layout.addWidget(xy_group, 1)
        calibration_actions_layout.addWidget(z_group, 1)
       

        # 组合布局
        main_vbox.addLayout(calibration_actions_layout)
        main_vbox.setSpacing(12)  # 参数区与按钮区间距

        self.set_sigma.setValue(3)   
        self.max_matches_spin.setValue(20)   
        self.contrast_spin.setValue(0.01)    
        self.ratio_spin.setValue(0.8)       
        self.compensation_x.setValue(0.0)   
        self.compensation_y.setValue(0.0)
        
        group.setLayout(main_vbox)
        layout.addWidget(group)

        # 在create_calibration_params方法中添加按钮
        

    def show_tips(self):
        if self.language == "en":
            tip_text = (
                "\n1. Load stat.npy and iscell.npy to get ROI IDs and coordinates. Load the Suite2p reference image and microscope image.\n\n"
                "2. Compute registration. If default parameters produce fewer than 50 matches, increase Match Ratio up to 0.9 and Sigma Blur up to 5. If alignment is inaccurate, try Match Ratio 0.7, Sigma Blur 1.6, and Contrast Threshold 0.02.\n\n"
                "3. Set Start Index and End Index. A group of 30-50 ROIs is usually practical.\n\n"
                "4. Preview shows the current stimulation point on the live/microscope image and the target cell from Suite2p masks. Left-click the live image to update the stimulation coordinate; right-click to exclude or restore the ROI.\n\n"
                "5. Register the X input, Y input, and Stimulate button positions with shortcuts. After each Stimulate click, the mouse returns to the Live preview center. Set delay slightly longer than the stimulation duration.\n\n"
                "6. Click Start. The preview shows the next stimulation point and target cell. Use buttons or shortcuts to skip the next ROI when needed.\n\n"
                "7. After one ROI group is complete, reload the newly acquired microscope image through Input Data and use Preview to check or fine-tune offsets before continuing.\n\n"
                "8. After one cell class is complete, load a new iscell.npy to get a new ROI set.\n"
            )
        else:
            tip_text = (
                "\n1. 依次加载stat.npy, iscell.npy，获取ROI编号和坐标。加载suite2p图像（推荐使用mean_img）时获得预览图。加载显微镜图像\n\n"
                "2. 计算全局校准：若默认参数获得匹配点少于50，尝试增加“匹配比率”至最高0.9，增加“模糊Sigma”至最高5。若匹配不准确，尝试降低“匹配比率”至0.7，降低“模糊Sigma”至1.6，提高对比度阈值至0.02\n\n"
                "3. 设置起始和结束索引。推荐30-50个一组\n\n"
                "4. 单细胞校准：每个ROI周围区域，当前的激活点（左）和目标细胞（右）（来自suite2P的cell masks）分别显示在显微镜图像（或Live图像）和suite2p图像上。对于每个ROI，左键单击左侧图像的位置可以生成更新的激活坐标，右键单击将该ROI排除或恢复。所有ROI校准后，若点击“保存偏移量”，更新的激活坐标会直径应用到各自对应的ROI；若点击“平均刚性校准”，会将平均后的偏移量更新到刚性校准的“X补偿”和“Y补偿”上。一般计算全局校准后不需要进行“平均刚性校准”\n\n"
                "5. 用快捷键注册输入 X、输入 Y 和 Stimulate 按钮的鼠标位置。每次点击 Stimulate 后，鼠标会回到 Live 预览框中心。设置延迟建议略长于刺激持续时间。\n\n"
                "6. 点击“开始”。预览图象会显示下一个激活点（左）和目标细胞（右）。在左侧图像上单击左键可以更新激活坐标，单击右键可以跳过。可以使用按钮或快捷键跳过下一个激活点\n\n"
                "7. 一组ROI激活完成后，建议检查激活结果，通过“输入数据”中的“显微镜图像”重新导入新拍摄的图像。点击“单细胞校准”，若有整体偏移，校准1-3个细胞后应用“平均刚性校准”。再次点击“单细胞校准”检查并校准每个ROI。注册鼠标位置后开始\n\n"
                "8. 一类细胞激活完成后，可直接导入新的iscell.npy文件，获得新的ROI编号和坐标\n"
            )
        QMessageBox.information(self, self.tr_text("参数说明 Tips"), tip_text)

    def show_preview_marker(self, dx, dy):
        """在底图上画单个 marker，而且每次都从底图复制"""
        try:
            # 1) 确保我们有底图
            if not hasattr(self, '_base_preview_pixmap'):
                return
            base = self._base_preview_pixmap.copy()

            painter = QPainter(base)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor(255, 0, 0), 2))

            # 2) 计算缩放与中心
            img_w = base.width()
            img_h = base.height()
            patch_size = max(1.0, float(getattr(self, "patch_size", 40)))
            patch_center = patch_size / 2.0
            scale_x = img_w / patch_size
            scale_y = img_h / patch_size

            # 3) 中心坐标 = (20 + dx, 20 + dy) 映射到显示坐标
            cx = (patch_center + dx) * scale_x
            cx = (patch_center + dx) * scale_x
            cy = (patch_center + dy) * scale_y

            # 4) 画十字
            length = min(img_w, img_h) * 0.1
            painter.drawLine(
                QLineF(QPointF(cx - length, cy), QPointF(cx + length, cy))
            )
            painter.drawLine(
                QLineF(QPointF(cx, cy - length), QPointF(cx, cy + length))
            )
            painter.end()

            # 5) 更新 QLabel
            self.preview_label.setPixmap(base)

        except Exception as e:
            print(f"{e}")
            self.log(f"标记绘制失败: {e}")
    
    def update_preview(self, micro_patch, suite2p_patch, index):
        """更新实时预览：左侧显微镜可交互，右侧Suite2P只读"""
        self.current_preview_index = index

        # —— 左侧：显微镜 patch —— #
        if micro_patch is None or micro_patch.size == 0:
            self.preview_info.setText("无效显微镜数据")
        else:
            # BGR->RGB
            rgb = (cv2.cvtColor(micro_patch, cv2.COLOR_BGR2RGB)
                if micro_patch.shape[2] == 3 else micro_patch)
            rgb = np.ascontiguousarray(rgb)
            h, w = rgb.shape[:2]
            qimg = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
            if qimg.isNull():
                self.preview_info.setText("显微镜图像转换失败")
            else:
                pm = QPixmap.fromImage(qimg).scaled(
                    self.preview_label.width(),
                    self.preview_label.height(),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation
                )
                self._base_preview_pixmap = pm  # 新增：保存底图
                self.preview_label.setPixmap(pm)
                self.preview_info.setText(f"下一个：no.{index}/{self.end_spin.value()}")

            # 叠加偏移标记
            self.show_preview_marker(0, 0)

        # —— 右侧：Suite2P patch —— #
        if suite2p_patch is None or suite2p_patch.size == 0:
            # 清空或显示占位文字
            self.s2p_preview_label.clear()
        else:
            rgb2 = (cv2.cvtColor(suite2p_patch, cv2.COLOR_BGR2RGB)
                    if suite2p_patch.shape[2] == 3 else suite2p_patch)
            rgb2 = np.ascontiguousarray(rgb2)
            h2, w2 = rgb2.shape[:2]
            qimg2 = QImage(rgb2.data, w2, h2, 3*w2, QImage.Format_RGB888)
            if qimg2.isNull():
                # 出错可忽略
                pass
            else:
                pm2 = QPixmap.fromImage(qimg2).scaled(
                    self.s2p_preview_label.width(),
                    self.s2p_preview_label.height(),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation
                )
                self.s2p_preview_label.setPixmap(pm2)
    
    def extract_cell_patches(self):

        if self.microscope_img is None or self.suite2p_img_withmask is None or not self.centers:
            QMessageBox.critical(self, "错误", "请先加载所有图像和坐标数据")
            return
        
        # 获取索引范围
        start_idx = self.start_spin.value()
        end_idx = self.end_spin.value()
        if start_idx > end_idx:
            QMessageBox.critical(self, "错误", "起始索引不能大于结束索引")
            return
        abs_idxs = self.valid[start_idx:end_idx+1]

        # 创建独立的存储结构
        self.micro_patches = []  # 存储显微镜图像patch
        self.suite2p_patches = []  # 存储suite2p图像patch
        self.patch_coordinates = []  # 存储对应坐标

        # 转换后的有效中心点（已应用补偿）
        valid_centers = self.centers[start_idx:end_idx+1]
        patch_size = int(getattr(self, "patch_size", 40))
        patch_center = patch_size // 2
        
        # 预处理suite2p图像
        if len(self.suite2p_img.shape) == 2:
            suite2p_color = cv2.cvtColor(self.suite2p_img, cv2.COLOR_GRAY2BGR)
        else:
            suite2p_color = self.suite2p_img.copy()

        # 提取suite2p patch
        for idx, (x, y) in enumerate(valid_centers):
            x, y = int(x) * 2 , int(y) * 2
            abs_i = abs_idxs[idx]
                
            patch = self.extract_single_patch_withmask(image=suite2p_color,
                                                       center_x=x,
                                                       center_y=y,
                                                       patch_size=patch_size,
                                                       denoise=self.ifdenoise,
                                                       abs_index=abs_i)
            
            # 标记中心点并存储
            cv2.circle(patch, (patch_center, patch_center), 1, (0,0,255), -1)
            self.suite2p_patches.append(patch)


        if self.live_img is not None:
            temp_microscope_image = self.live_img
        else: temp_microscope_image = self.microscope_img
        
        # 预处理显微镜图像
        if len(temp_microscope_image.shape) == 2:
            micro_color = cv2.cvtColor(temp_microscope_image, cv2.COLOR_GRAY2BGR)
        else:
            micro_color = temp_microscope_image.copy()

        # 提取显微镜 patch
        for rel_i, (x0, y0) in enumerate(self.centers[start_idx:end_idx+1]):
            abs_i = abs_idxs[rel_i]  # 绝对编号

        # 计算 raw_x, raw_y, homography, 全局补偿
            raw_x, raw_y = int(x0*2), int(y0*2)
            # 应用坐标转换（如果有）
            if self.H is not None:
                try:
                    transformed = self.transform_coordinates(
                        np.array([[[raw_x, raw_y]]], dtype=np.float32)
                    )
                    base_x, base_y = transformed[0][0]
                except Exception as e:
                    self.log(f"坐标转换失败: {str(e)}")
                    continue
            else:
                base_x, base_y = raw_x, raw_y
                
            current_comp_x = self.compensation_x.value()
            current_comp_y = self.compensation_y.value()

            offset = self.offsets.get(abs_i, (0,0))
            x = int(base_x + current_comp_x + offset[0])
            y = int(base_y + current_comp_y + offset[1])

                
            micro_patch = self.extract_single_patch(
                image=micro_color,
                center_x=x,
                center_y=y,
                patch_size=patch_size,
                denoise=self.ifdenoise
            )

            
            # 标记中心点并存储
            cv2.circle(micro_patch, (patch_center, patch_center), 1, (0,0,255), -1)
            self.micro_patches.append(micro_patch)
            self.patch_coordinates.append((x, y))

        # 验证两个列表长度一致
        if len(self.micro_patches) != len(self.suite2p_patches):
            QMessageBox.warning(self, "警告", "显微镜与Suite2P patch数量不一致")
            return

        # 组合成原有结构（兼容旧代码）
        self.patches = [
        (self.micro_patches[i], self.suite2p_patches[i], abs_idxs[i])
        for i in range(len(abs_idxs))
        ]

        self.show_patch_grid()
        micro, suite2p, _ = self.patches[0]
        self.update_preview(micro, suite2p, start_idx)

    def extract_single_patch(self, image, center_x, center_y, patch_size=40, denoise=True):
        """通用patch提取方法"""

        try: 
            y1 = max(0, center_y - patch_size//2)
            y2 = min(image.shape[0], center_y + patch_size//2)
            x1 = max(0, center_x - patch_size//2)
            x2 = min(image.shape[1], center_x + patch_size//2)
            
            # 创建空patch
            patch = np.zeros((patch_size, patch_size, 3), dtype=np.uint8)
            
            # 裁剪图像区域
            crop = image[y1:y2, x1:x2]
            ph, pw = crop.shape[:2]
            
            # 居中填充
            patch[
                (patch_size//2 - ph//2):(patch_size//2 + ph//2 + ph%2),
                (patch_size//2 - pw//2):(patch_size//2 + pw//2 + pw%2)
            ] = crop
            

            # def adjust_gamma(image, gamma=1.0):
            #     invGamma = 1.0 / gamma
            #     table = np.array([((i / 255.0) ** invGamma) * 255
            #     for i in np.arange(0, 256)]).astype("uint8")
            #     return cv2.LUT(image, table)

            # patch = adjust_gamma(patch, gamma=self.set_gamma)


            # 3) 第一次归一化（保证后面 LUT 在 [0,255] 内）
            patch = cv2.normalize(patch, None, 0, 255, cv2.NORM_MINMAX)   
            invGamma = 1.0 / self.set_gamma
    
            table = np.array([((i / 255.0) ** invGamma) * 255
                            if i > 20 else i  # 保留最暗部（小于10）不变
                            for i in np.arange(0, 256)]).astype("uint8")
            patch = cv2.LUT(patch, table)

            # 2. CLAHE 细致增强局部对比度
            # clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
            # lab = cv2.cvtColor(patch, cv2.COLOR_BGR2LAB)
            # l, a, b = cv2.split(lab)
            # l2 = clahe.apply(l)
            # lab2 = cv2.merge((l2, a, b))
            # patch = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

                                                

            # def log_transform(image, c=1):
            #     """
            #     对图像进行对数变换以增强暗部细节。
            #     c 是一个常数，用于调整变换的强度。
            #     """
            #     log_image = c * (np.log1p(image.astype(float)) / np.log1p(255))
            #     normalized_log = cv2.normalize(log_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            #     return normalized_log

            # # 在你的 extract_single_patch_withmask 函数中替换标准化处理
            # patch = log_transform(patch, c=1) # 调整 c 的值以获得最佳效果

            # 标准化处理

            # 锐化处理
            if denoise:
                blur = cv2.GaussianBlur(patch, (self.set_patchkernel, self.set_patchkernel), 0)
                patch = cv2.addWeighted(blur, 1.5, blur, -0.5, 0)
                #patch = blur

            patch = cv2.normalize(patch, None, 0, 255, cv2.NORM_MINMAX) 


            return patch
        
        finally:
            # 显式释放中间变量
            if 'crop' in locals(): del crop
            if 'blur' in locals(): del blur

    def show_patch_grid(self):
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        self.temp_offset = {}

        if hasattr(self, 'patch_win'):
            self.patch_win.close()
            self.patch_win.deleteLater()
            del self.patch_win

        self.patch_win = QWidget()
        self.patch_win.setObjectName("auxWindow")
        self.patch_win.setWindowTitle(self.tr_text("单细胞预览"))
        layout = QVBoxLayout(self.patch_win)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        hint_label = QLabel(self.tr_text("Live：左键校准，右键跳过 | Reference：仅供参考"))
        hint_label.setObjectName("positionHint")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        num_pairs = len(self.patches)
        pairs_per_row = 4
        rows = max(1, int(np.ceil(num_pairs / pairs_per_row)))
        fig = Figure(figsize=(13.2, max(3.2, rows * 2.85)), facecolor=self.theme["bg"])
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumSize(1180, int(max(320, rows * 270)))

        scroll_area = QScrollArea()
        scroll_area.setObjectName("pageScrollArea")
        scroll_area.setWidgetResizable(False)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(canvas)
        layout.addWidget(scroll_area, 1)

        fig.subplots_adjust(
            left=0.025, right=0.985,
            bottom=0.04, top=0.96,
            wspace=0.28, hspace=0.50
        )
        outer_grid = fig.add_gridspec(rows, pairs_per_row, wspace=0.36, hspace=0.48)

        self.ax_mapping = {}
        start_idx = self.start_spin.value()
        end_idx   = self.end_spin.value()
        self.abs_idxs = self.valid[start_idx : end_idx+1]  

        text_color = self.theme.get("text", "#e8eef5")
        muted_color = self.theme.get("muted", "#8fa1b3")
        skipped_color = self.theme.get("danger", "#ef4444")
        card_color = self.theme.get("panel_alt", "#1d2a36")
        card_title_color = self.theme.get("accent", "#38bdf8")

        def as_rgb(patch):
            return cv2.cvtColor(patch, cv2.COLOR_BGR2RGB) if patch.shape[2] == 3 else patch

        def roi_title(rel_i, actual_idx, dxdy=None):
            status = f" | {self.tr_text('已跳过')}" if actual_idx in self.removed else ""
            title = f"ROI {actual_idx} | no.{rel_i + start_idx}/{end_idx}{status}"
            if dxdy is not None and actual_idx not in self.removed:
                dx, dy = dxdy
                title += f" | dx {dx:.1f}, dy {dy:.1f}"
            return title

        def draw_card_header(ax, rel_i, dxdy=None):
            _, _, actual_idx = self.patches[rel_i]
            ax.clear()
            ax.set_facecolor(card_color)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            color = skipped_color if actual_idx in self.removed else card_title_color
            ax.text(
                0.5,
                0.5,
                roi_title(rel_i, actual_idx, dxdy=dxdy),
                transform=ax.transAxes,
                ha="center",
                va="center",
                color=color,
                fontsize=9,
                fontweight="bold",
            )

        def draw_live_patch(ax, rel_i, dxdy=None):
            micro_patch, _, actual_idx = self.patches[rel_i]
            ax.clear()
            ax.axis("off")
            ax.set_facecolor(card_color)
            ax.set_title(self.tr_text("Live"), fontsize=9, fontweight="bold", color=text_color, pad=4)
            if actual_idx in self.removed:
                gray = cv2.cvtColor(micro_patch, cv2.COLOR_BGR2GRAY)
                gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                ax.imshow(gray, alpha=0.3)
            else:
                ax.imshow(as_rgb(micro_patch))
                if dxdy is not None:
                    patch_size = micro_patch.shape[0]
                    dx, dy = dxdy
                    ax.scatter(
                        patch_size // 2 + dx,
                        patch_size // 2 + dy,
                        s=44,
                        edgecolors="red",
                        facecolors="none",
                        linewidths=1.2,
                    )

        def draw_reference_patch(ax, rel_i):
            _, suite2p_patch, _ = self.patches[rel_i]
            ax.clear()
            ax.axis("off")
            ax.set_facecolor(card_color)
            ax.set_title(self.tr_text("Reference"), fontsize=9, fontweight="bold", color=muted_color, pad=4)
            ax.imshow(as_rgb(suite2p_patch))

        card_axes = {}
        for rel_i in range(num_pairs):
            row = rel_i // pairs_per_row
            col = rel_i % pairs_per_row

            card_spec = outer_grid[row, col]
            card_bg = fig.add_subplot(card_spec)
            card_bg.set_facecolor(card_color)
            card_bg.set_xticks([])
            card_bg.set_yticks([])
            for spine in card_bg.spines.values():
                spine.set_visible(False)
            card_bg.set_zorder(0)

            inner = card_spec.subgridspec(2, 2, height_ratios=[0.20, 1.0], wspace=0.16, hspace=0.22)
            ax_title = fig.add_subplot(inner[0, :])
            ax_left = fig.add_subplot(inner[1, 0])
            ax_right = fig.add_subplot(inner[1, 1])
            ax_title.set_zorder(2)
            ax_left.set_zorder(2)
            ax_right.set_zorder(2)

            self.ax_mapping[ax_left] = rel_i
            card_axes[rel_i] = (ax_title, ax_left, ax_right)
            draw_card_header(ax_title, rel_i)
            draw_live_patch(ax_left, rel_i)
            draw_reference_patch(ax_right, rel_i)

        def onclick(event):
            if event.inaxes not in self.ax_mapping:
                return

            if event.button == 1:
                rel_i = self.ax_mapping[event.inaxes]
                micro_patch, _, actual_idx = self.patches[rel_i]
                ax = event.inaxes

                if actual_idx in self.removed:
                    return

                try:
                    xdata, ydata = event.xdata, event.ydata
                    if xdata is None or ydata is None:
                        return
                    patch_size = micro_patch.shape[0]

                    dx = xdata - patch_size//2
                    dy = ydata - patch_size//2
                    self.temp_offset[actual_idx] = (dx, dy)
                    title_ax, _, _ = card_axes[rel_i]
                    draw_card_header(title_ax, rel_i, dxdy=(dx, dy))
                    draw_live_patch(ax, rel_i, dxdy=(dx, dy))
                    canvas.draw_idle()

                except Exception as e:
                    print(f"点击处理错误: {str(e)}")
                    traceback.print_exc()

            elif event.button == 3:

                rel_i = self.ax_mapping[event.inaxes]
                _, _, actual_idx = self.patches[rel_i]
                ax = event.inaxes

                if actual_idx in self.removed:
                    self.removed.remove(actual_idx)
                    self.log(f"恢复 ROI No.{actual_idx}")
                else:
                    self.removed.add(actual_idx)
                    self.log(f"跳过 ROI No.{actual_idx}")

                title_ax, _, _ = card_axes[rel_i]
                draw_card_header(title_ax, rel_i)
                draw_live_patch(ax, rel_i)
                canvas.draw_idle()

            else:
                return

        canvas.mpl_connect('button_press_event', onclick)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_save = QPushButton(self.tr_text("保存偏移量"))
        btn_save.clicked.connect(lambda _: (self.save_offsets(), self.patch_win.close()))
        self.set_button_role(btn_save, "primary")

        btn_globalcalib = QPushButton(self.tr_text("平均刚性校准"))
        btn_globalcalib.clicked.connect(lambda _: (self.globalcalib(), self.patch_win.close()))
        self.set_button_role(btn_globalcalib, "secondary")

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_globalcalib)

        layout.addLayout(btn_layout)

        screen_size = QApplication.primaryScreen().availableGeometry()
        max_width = screen_size.width() * 0.86
        max_height = screen_size.height() * 0.86
        self.patch_win.resize(int(min(1280, max_width)), int(min(860, max_height)))

        self.patch_win.canvas = canvas
        self.patch_win.fig = fig
        self.style_matplotlib_figure(fig)
        canvas.draw_idle()
        self.patch_win.show()
       

    def save_offsets(self):
            # 如果已有该细胞偏移，则叠加，否则新增
            for abs_idx, (dx, dy) in self.temp_offset.items():
                prev_dx, prev_dy = self.offsets.get(abs_idx, (0, 0))
                self.offsets[abs_idx] = (prev_dx + dx, prev_dy + dy)
            self.temp_offset.clear()
            self.log("已应用单细胞校准")

    def globalcalib (self):
        if not self.temp_offset:
            QMessageBox.warning(self, "警告", "未找到校准数据")
            return None
        
        # 收集有效偏移量
        valid_dx = []
        valid_dx = []
        valid_dy = []

        for idx in self.temp_offset:
            dx, dy = self.temp_offset[idx]
            if isinstance(dx, (int, float, np.integer, np.floating)) and isinstance(dy, (int, float, np.integer, np.floating)):
                valid_dx.append(float(dx))
                valid_dy.append(float(dy))

        if not valid_dx or not valid_dy:
            QMessageBox.warning(self, "警告", "未找到有效校准数据")
            return None

        mean_dx = int(round(np.mean(valid_dx)))
        mean_dy = int(round(np.mean(valid_dy)))
        set_x = self.compensation_x.value() + mean_dx
        set_y = self.compensation_y.value() + mean_dy
        self.compensation_x.setValue(set_x)   
        self.compensation_y.setValue(set_y)

        self.log(f"已应用全局校准({self.compensation_x.value()},{self.compensation_y.value()})")

    def create_position_signal_panel(self):
        panel = QFrame()
        panel.setObjectName("positionSignalPanel")
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(10, 6, 10, 6)
        panel_layout.setSpacing(12)

        title_label = QLabel("PyAutoGUI Control")
        title_label.setProperty("positionSignalText", True)
        title_label.setToolTip("PyAutoGUI control registration status")
        panel_layout.addWidget(title_label)

        self.position_lights = {}
        self.position_signal_labels = {}
        signal_items = [
            ("x_pos", "Stim sites X pos (Ctrl+1)", "Stim sites X pos"),
            ("y_pos", "Stim sites Y pos (Ctrl+2)", "Stim sites Y pos"),
            ("stimulate_pos", "Stim Button (Ctrl+3)", "Stim Button"),
        ]

        for pos_type, label_text, tooltip_name in signal_items:
            item = QFrame()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(5)

            light = QLabel()
            light.setProperty("positionLight", True)
            light.setFixedSize(10, 10)

            text = QLabel(label_text)
            text.setProperty("positionSignalText", True)
            text.setToolTip(f"{tooltip_name} {self.tr_text('未注册')}")

            item_layout.addWidget(light)
            item_layout.addWidget(text)
            panel_layout.addWidget(item)

            self.position_lights[pos_type] = light
            self.position_signal_labels[pos_type] = (text, tooltip_name)

        panel_layout.addStretch(1)
        self.refresh_position_lights()
        return panel

    def set_position_light(self, pos_type, active):
        light = getattr(self, "position_lights", {}).get(pos_type)
        if light is None:
            return
        color = "#E2A528" if active else "#3b4652"
        light.setStyleSheet(f"background-color: {color}; border: none; border-radius: 5px;")

    def refresh_position_lights(self):
        if not hasattr(self, "position_lights"):
            return
        for pos_type, light in self.position_lights.items():
            active = pos_type in self.registered_pos
            self.set_position_light(pos_type, active)
            label_info = getattr(self, "position_signal_labels", {}).get(pos_type)
            if label_info is None:
                continue
            text, tooltip_name = label_info
            if active:
                tooltip = f"{tooltip_name} {self.tr_text('已注册')}: {self.registered_pos[pos_type]}"
                text.setToolTip(tooltip)
                light.setToolTip(tooltip)
            else:
                tooltip = f"{tooltip_name} {self.tr_text('未注册')}"
                text.setToolTip(tooltip)
                light.setToolTip(tooltip)

    def create_main_controls(self, layout):
        group = QGroupBox("单细胞控制")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.position_signal_panel = self.create_position_signal_panel()

        self.start_spin = GuardedSpinBox()
        self.end_spin = GuardedSpinBox()
        self.roi_diameter_spin = GuardedSpinBox()
        self.delay_spin = GuardedDoubleSpinBox()

        self.roi_diameter_spin.setRange(1, 200)
        self.roi_diameter_spin.setValue(int(getattr(self, "roi_diameter", 10)))
        self.delay_spin.setValue(4.0)
        for spin in [self.start_spin, self.end_spin, self.roi_diameter_spin, self.delay_spin]:
            spin.setFixedWidth(80)

        grid.addWidget(QLabel("起始索引:"), 0, 0)
        grid.addWidget(self.start_spin, 0, 1)
        grid.addWidget(QLabel("结束索引:"), 0, 2)
        grid.addWidget(self.end_spin, 0, 3)
        grid.addWidget(QLabel("ROI直径(px):"), 0, 4)
        grid.addWidget(self.roi_diameter_spin, 0, 5)
        grid.addWidget(QLabel("延迟(s):"), 0, 6)
        grid.addWidget(self.delay_spin, 0, 7)
        for col in (1, 3, 5, 7):
            grid.setColumnStretch(col, 1)
        for col in (0, 2, 4, 6):
            grid.setColumnStretch(col, 0)
        grid.addWidget(self.position_signal_panel, 2, 0, 1, 8)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.print_status_btn = QPushButton("查看状态")
        self.crop_btn = QPushButton("预览")
        for btn in [self.print_status_btn, self.crop_btn]:
            btn.setMinimumWidth(88)
            self.set_button_role(btn, "secondary")
        btn_layout.addWidget(self.crop_btn, 1)
        btn_layout.addWidget(self.print_status_btn, 1)
        self.crop_btn.clicked.connect(self.extract_cell_patches)
        grid.addLayout(btn_layout, 1, 0, 1, 8)

        self.print_status_btn.clicked.connect(self.print_status)

        group.setLayout(grid)
        layout.addWidget(group)

    def request_high_res_screenshot(self, owner_dialog=None):
        default_path = os.path.join(APP_SETTINGS_DIR, "OptoStim2P_UI_3x.png")
        path, _ = QFileDialog.getSaveFileName(
            owner_dialog or self,
            self.tr_text("保存界面截图"),
            default_path,
            "PNG Image (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"

        if owner_dialog is not None:
            owner_dialog.reject()

        QTimer.singleShot(250, lambda save_path=path: self.save_high_res_screenshot(save_path))

    def save_high_res_screenshot(self, path, scale=3, dpi=300):
        painter = None
        error_message = None
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        try:
            size = self.size()
            image = QImage(size.width() * scale, size.height() * scale, QImage.Format_ARGB32)
            image.fill(QColor(self.theme["bg"]))
            dots_per_meter = int(dpi / 0.0254)
            image.setDotsPerMeterX(dots_per_meter)
            image.setDotsPerMeterY(dots_per_meter)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.scale(scale, scale)
            self.render(painter)
            painter.end()
            painter = None

            if not image.save(path, "PNG"):
                raise IOError(path)

            self.log(self.tr_text("界面截图已保存到:\n{file_path}").format(file_path=path))
        except Exception as e:
            error_message = self.tr_text("保存界面截图失败: {error}").format(error=e)
        finally:
            if painter is not None:
                painter.end()
            QApplication.restoreOverrideCursor()
            QApplication.processEvents()

        if error_message:
            QMessageBox.critical(self, self.tr_text("错误"), error_message)

    def show_advanced_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr_text("更多设置"))
        dlg.resize(380, 680)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        settings_scroll = QScrollArea(dlg)
        settings_scroll.setObjectName("pageScrollArea")
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QScrollArea.NoFrame)
        settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        settings_content = QWidget()
        settings_content.setObjectName("scrollContent")
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(8)

        def create_settings_group(title):
            group = QGroupBox(self.tr_text(title))
            grid = QGridLayout(group)
            grid.setContentsMargins(10, 14, 10, 10)
            grid.setHorizontalSpacing(10)
            grid.setVerticalSpacing(8)
            grid.setColumnStretch(1, 1)
            return group, grid

        def add_setting_row(grid, row, label_text, widget):
            grid.addWidget(QLabel(self.tr_text(label_text)), row, 0)
            grid.addWidget(widget, row, 1)

        display_group, display_grid = create_settings_group("显示/图像")
        self.set_alpha_input = QLineEdit(str(getattr(self, 'set_alpha', 0.3)))
        self.patch_size_input = GuardedSpinBox()
        self.patch_size_input.setRange(16, 256)
        self.patch_size_input.setSingleStep(2)
        self.patch_size_input.setValue(int(getattr(self, "patch_size", 40)))
        self.patchkernel_input = QLineEdit(str(getattr(self, 'set_patchkernel', 9)))
        self.set_gamma_input = QLineEdit(str(getattr(self, 'set_gamma', 1.6)))
        self.set_gammathres_input = QLineEdit(str(getattr(self, 'set_gammathres', 40)))
        self.language_combo = GuardedComboBox()
        self.language_combo.addItem(self.tr_text("中文"), "zh")
        self.language_combo.addItem(self.tr_text("English"), "en")
        current_index = self.language_combo.findData(self.language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        self.enable_denoise_click_cb = QCheckBox(self.tr_text("图像降噪模糊"))
        self.enable_denoise_click_cb.setChecked(getattr(self, 'ifdenoise', True))
        self.export_screenshot_btn = QPushButton(self.tr_text("导出界面截图"))
        self.set_button_role(self.export_screenshot_btn, "secondary")
        self.export_screenshot_btn.clicked.connect(lambda: self.request_high_res_screenshot(owner_dialog=dlg))
        add_setting_row(display_grid, 0, "Mask透明度:", self.set_alpha_input)
        add_setting_row(display_grid, 1, "Patch Size (px):", self.patch_size_input)
        add_setting_row(display_grid, 2, "图像高斯模糊Kernel（奇数）:", self.patchkernel_input)
        add_setting_row(display_grid, 3, "图像Gamma值:", self.set_gamma_input)
        add_setting_row(display_grid, 4, "Gamma变换阈值:", self.set_gammathres_input)
        add_setting_row(display_grid, 5, "Language", self.language_combo)
        display_grid.addWidget(self.enable_denoise_click_cb, 6, 0, 1, 2)
        display_grid.addWidget(self.export_screenshot_btn, 7, 0, 1, 2)
        settings_layout.addWidget(display_group)

        calibration_group, calibration_grid = create_settings_group("校准参数")
        self.settings_sigma_spin = GuardedDoubleSpinBox()
        self.settings_sigma_spin.setRange(0, 10)
        self.settings_sigma_spin.setDecimals(2)
        self.settings_sigma_spin.setSingleStep(0.1)
        self.settings_sigma_spin.setValue(float(self.set_sigma.value()))

        self.settings_max_matches_spin = GuardedSpinBox()
        self.settings_max_matches_spin.setRange(1, 30)
        self.settings_max_matches_spin.setValue(int(self.max_matches_spin.value()))

        self.settings_contrast_spin = GuardedDoubleSpinBox()
        self.settings_contrast_spin.setRange(0.005, 0.1)
        self.settings_contrast_spin.setDecimals(3)
        self.settings_contrast_spin.setSingleStep(0.005)
        self.settings_contrast_spin.setValue(float(self.contrast_spin.value()))

        self.settings_ratio_spin = GuardedDoubleSpinBox()
        self.settings_ratio_spin.setRange(0.5, 0.95)
        self.settings_ratio_spin.setDecimals(2)
        self.settings_ratio_spin.setSingleStep(0.05)
        self.settings_ratio_spin.setValue(float(self.ratio_spin.value()))

        self.settings_compensation_x = GuardedDoubleSpinBox()
        self.settings_compensation_x.setRange(-500, 500)
        self.settings_compensation_x.setDecimals(2)
        self.settings_compensation_x.setValue(float(self.compensation_x.value()))

        self.settings_compensation_y = GuardedDoubleSpinBox()
        self.settings_compensation_y.setRange(-500, 500)
        self.settings_compensation_y.setDecimals(2)
        self.settings_compensation_y.setValue(float(self.compensation_y.value()))

        add_setting_row(calibration_grid, 0, "模糊Sigma:", self.settings_sigma_spin)
        add_setting_row(calibration_grid, 1, "最大匹配:", self.settings_max_matches_spin)
        add_setting_row(calibration_grid, 2, "对比度阈值:", self.settings_contrast_spin)
        add_setting_row(calibration_grid, 3, "匹配比率:", self.settings_ratio_spin)
        add_setting_row(calibration_grid, 4, "X补偿(pix):", self.settings_compensation_x)
        add_setting_row(calibration_grid, 5, "Y补偿(pix):", self.settings_compensation_y)
        settings_layout.addWidget(calibration_group)

        automation_group, automation_grid = create_settings_group("自动化")
        self.delay_input = QLineEdit(str(int(getattr(self, 'pyautogui_delay', 60))))
        self.enable_topmost_cb = QCheckBox(self.tr_text("窗口置顶"))
        self.enable_topmost_cb.setChecked(bool(self.windowFlags() & Qt.WindowStaysOnTopHint))
        self.enable_autosave_cb = QCheckBox(self.tr_text("自动保存"))
        self.enable_autosave_cb.setChecked(getattr(self, "autosave", True))
        self.set_suffix_input = QLineEdit(str(getattr(self, 'suffix', "")))
        add_setting_row(automation_grid, 0, "pyautogui 延迟 (ms):", self.delay_input)
        automation_grid.addWidget(self.enable_topmost_cb, 1, 0, 1, 2)
        automation_grid.addWidget(self.enable_autosave_cb, 2, 0, 1, 2)
        add_setting_row(automation_grid, 3, "保存文件后缀:", self.set_suffix_input)
        automation_grid.addWidget(QLabel(self.tr_text("位置测试")), 4, 0, 1, 2)
        position_test_frame = QFrame()
        position_test_frame.setObjectName("settingsInlinePanel")
        position_test_layout = QGridLayout(position_test_frame)
        position_test_layout.setContentsMargins(0, 0, 0, 0)
        position_test_layout.setHorizontalSpacing(8)
        position_test_layout.setVerticalSpacing(8)
        position_test_layout.setColumnStretch(0, 1)
        position_test_layout.setColumnStretch(1, 1)
        self.test_x_input_btn = QPushButton(self.tr_text("测试 X 输入"))
        self.test_y_input_btn = QPushButton(self.tr_text("测试 Y 输入"))
        self.test_xy_input_btn = QPushButton(self.tr_text("测试 X/Y 输入"))
        self.test_stimulate_click_btn = QPushButton(self.tr_text("测试 Stimulate 点击"))
        self.test_x_input_btn.clicked.connect(self.test_x_input_position)
        self.test_y_input_btn.clicked.connect(self.test_y_input_position)
        self.test_xy_input_btn.clicked.connect(self.test_xy_input_positions)
        self.test_stimulate_click_btn.clicked.connect(self.test_stimulate_position_click)
        for button in (
            self.test_x_input_btn,
            self.test_y_input_btn,
            self.test_xy_input_btn,
            self.test_stimulate_click_btn,
        ):
            self.set_button_role(button, "secondary")
        self.set_button_role(self.test_stimulate_click_btn, "warning")
        position_test_layout.addWidget(self.test_x_input_btn, 0, 0)
        position_test_layout.addWidget(self.test_y_input_btn, 0, 1)
        position_test_layout.addWidget(self.test_xy_input_btn, 1, 0, 1, 2)
        position_test_layout.addWidget(self.test_stimulate_click_btn, 2, 0, 1, 2)
        automation_grid.addWidget(position_test_frame, 5, 0, 1, 2)
        settings_layout.addWidget(automation_group)

        maintenance_group = QGroupBox(self.tr_text("维护操作"))
        maintenance_layout = QVBoxLayout(maintenance_group)
        maintenance_layout.setContentsMargins(10, 14, 10, 10)
        maintenance_layout.setSpacing(8)
        self.save_btn = QPushButton(self.tr_text("保存日志和激活列表"))
        self.reset_stimulated_btn = QPushButton(self.tr_text("重置已激活ROI列表"))
        self.clear_btn = QPushButton(self.tr_text("重置校准"))
        self.tips_btn = QPushButton("Tips")

        
        self.tips_btn.clicked.connect(self.show_tips)
        self.save_btn.clicked.connect(self.save_log)
        self.reset_stimulated_btn.clicked.connect(self.reset_stimulated)
        self.clear_btn.clicked.connect(self.clearH)
        self.set_button_role(self.save_btn, "secondary")
        self.set_button_role(self.reset_stimulated_btn, "warning")
        self.set_button_role(self.clear_btn, "danger")
        self.set_button_role(self.tips_btn, "secondary")
        for button in (self.save_btn, self.reset_stimulated_btn, self.clear_btn, self.tips_btn):
            maintenance_layout.addWidget(button)
        settings_layout.addWidget(maintenance_group)
        settings_layout.addStretch(1)
        settings_scroll.setWidget(settings_content)
        layout.addWidget(settings_scroll, 1)

        # 5. 保存 / 取消按钮
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        save_button = btns.button(QDialogButtonBox.Save)
        cancel_button = btns.button(QDialogButtonBox.Cancel)
        if save_button is not None:
            save_button.setText(self.tr_text("保存"))
        if cancel_button is not None:
            cancel_button.setText(self.tr_text("取消"))
        layout.addWidget(btns)

        if dlg.exec_() == QDialog.Accepted:
            try:
                # 保存输入结果到 self
                self.roi_diameter = int(self.roi_diameter_spin.value())
                self.pyautogui_delay = int(self.delay_input.text())
                if hasattr(self, "detection_page") and hasattr(self.detection_page, "eval_method_combo"):
                    self.detection_method = self.detection_page.eval_method_combo.currentText()
                if hasattr(self, "detection_page") and hasattr(self.detection_page, "detection_channel_combo"):
                    self.detection_channel = self.detection_page.detection_channel_combo.currentText()
                self.patch_size = int(self.patch_size_input.value())
                self.set_sigma.setValue(float(self.settings_sigma_spin.value()))
                self.max_matches_spin.setValue(int(self.settings_max_matches_spin.value()))
                self.contrast_spin.setValue(float(self.settings_contrast_spin.value()))
                self.ratio_spin.setValue(float(self.settings_ratio_spin.value()))
                self.compensation_x.setValue(float(self.settings_compensation_x.value()))
                self.compensation_y.setValue(float(self.settings_compensation_y.value()))
                if hasattr(self, "detection_page"):
                    for attr, value in (
                        ("set_sigma", float(self.settings_sigma_spin.value())),
                        ("max_matches_spin", int(self.settings_max_matches_spin.value())),
                        ("contrast_spin", float(self.settings_contrast_spin.value())),
                        ("ratio_spin", float(self.settings_ratio_spin.value())),
                        ("compensation_x", float(self.settings_compensation_x.value())),
                        ("compensation_y", float(self.settings_compensation_y.value())),
                    ):
                        widget = getattr(self.detection_page, attr, None)
                        if widget is not None:
                            widget.setValue(value)
                if hasattr(self, "detection_page") and hasattr(self.detection_page, "eval_method_combo"):
                    self.detection_page.update_threshold_settings()
                self.ifdenoise = self.enable_denoise_click_cb.isChecked()
                self.autosave = self.enable_autosave_cb.isChecked()
                desired_topmost = self.enable_topmost_cb.isChecked()
                selected_language = self.language_combo.currentData()
                self.set_alpha = float(self.set_alpha_input.text())
                self.set_gamma = float(self.set_gamma_input.text())
                self.set_gammathres = int(self.set_gammathres_input.text())
                self.set_patchkernel = int(self.patchkernel_input.text())
                self.suffix = str(self.set_suffix_input.text())
                if desired_topmost != bool(self.windowFlags() & Qt.WindowStaysOnTopHint):
                    self.toggle_topmost()
                language_changed = selected_language in {"zh", "en"} and selected_language != self.language
                if selected_language in {"zh", "en"}:
                    self.language = selected_language
                    self.save_app_settings()

                if self.language == "en":
                    self.log(
                        f"Settings saved: mask alpha={self.set_alpha}, blur kernel={self.set_patchkernel}, gamma={self.set_gamma}, "
                        f"ROI diameter={self.roi_diameter}, patch size={self.patch_size}px, delay={self.pyautogui_delay}ms, detection method={self.detection_method}, denoise={'enabled' if self.ifdenoise else 'disabled'}, "
                        f"autosave={'enabled' if self.autosave else 'disabled'}, suffix={self.suffix}"
                    )
                else:
                    self.log(f"设置已保存：Mask透明度={self.set_alpha}，图像高斯模糊kernel = {self.set_patchkernel}，图像Gamma值={self.set_gamma}，ROI直径={self.roi_diameter}，"
                            f"Patch Size={self.patch_size}px，延迟={self.pyautogui_delay}ms，激活检测={self.detection_method}，模糊降噪={'启用' if self.ifdenoise else '关闭'}，自动保存={'启用' if self.autosave else '关闭'}，后缀={self.suffix}")
                if language_changed:
                    QMessageBox.information(self, self.tr_text("语言设置"), self.tr_text("语言已保存，重启程序后生效。"))
            except ValueError as e:
                self.log(self.tr_text("输入无效"))

    def load_z_stack_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择Z-stack.tiff，建议2um步进，范围20um（start：-10um， end： 10um）", "", "Images (*.tif)")
        if not path:
            return

        try:
            z_stack = tifffile.imread(path)
            if z_stack.ndim < 3:
                raise ValueError("Z-stack 必须是多层图像")
            self.z_stack = z_stack
            self.z_stack_path = path
            self.log(f"已加载 Z-stack Image: {os.path.basename(path)} | shape={z_stack.shape}, dtype={z_stack.dtype}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"Z-stack加载失败: {e}")
            return

    def show_zcalib(self):
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        import matplotlib.gridspec as gridspec

        if self.z_stack is None:
            QMessageBox.warning(self, "警告", "请先导入 Z-stack Image")
            return

        if self.suite2p_img is None:
            QMessageBox.critical(self, "错误", "请先加载suite2p图像")
            return

        z_stack = self.z_stack
        no_slices = z_stack.shape[0]

        # --- SIFT and FLANN Initialization ---
        sift = cv2.SIFT_create(contrastThreshold=0.005, sigma=3)
        FLANN_INDEX_KDTREE = 1
        flann = cv2.FlannBasedMatcher(
            dict(algorithm=FLANN_INDEX_KDTREE, trees=5),
            dict(checks=50)
        )

        # --- Process Reference Image ---
        suite2p_img_8bit = cv2.normalize(self.suite2p_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        kp_suite2p, des_suite2p = sift.detectAndCompute(suite2p_img_8bit, None)

        if des_suite2p is None:
            QMessageBox.warning(self, "注意", "无法在Suite2P参考图像中检测到特征点。")
            return

        # --- Matching Loop ---
        best_slice_index = -1
        best_match_count = -1
        all_match_counts = []
        
        try:
            for i in range(no_slices):
                current_slice = z_stack[i]
                slice_8bit = cv2.normalize(current_slice, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                kp_slice, des_slice = sift.detectAndCompute(slice_8bit, None)

                if des_slice is None or len(kp_slice) < 2:
                    self.log(f"Slice {i+1}: No features detected.")
                    continue

                matches = flann.knnMatch(des_suite2p, des_slice, k=2)
                
                good_matches = []
                # 🛡️ Crash-Safe Check: Ensure each match has two neighbors
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < 0.7 * n.distance:
                            good_matches.append(m)
                
                num_good_matches = len(good_matches)

                all_match_counts.append(num_good_matches)
                self.log(f"Slice no. {i+1}: {num_good_matches}个匹配点")
                
                if num_good_matches > best_match_count:
                    best_match_count = num_good_matches
                    best_slice_index = i # Use 0-based index internally

        except cv2.error as e:
            QMessageBox.critical(self, "OpenCV 错误", f"特征匹配时发生错误: {e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "未知错误", f"处理切片时发生错误: {e}")
            return

        # --- Report Results ---
        if best_slice_index != -1:
            self.log(f"最佳匹配: slice no. {best_slice_index + 1} ")
            QMessageBox.information(self, "完成", f"最佳匹配: slice no. {best_slice_index + 1} \n{best_match_count}个匹配点")
        else:
            QMessageBox.critical(self, "错误", "无法在任何Z轴切片中找到有效的匹配。")

        # --- Visualization Window ---
        if hasattr(self, 'z_patch_win'):
            self.z_patch_win.close()
            self.z_patch_win.deleteLater()

        try:

            self.z_patch_win = QWidget()
            self.z_patch_win.setObjectName("auxWindow")
            self.z_patch_win.setWindowTitle("Z-Stack Patch Visualization")
            layout = QVBoxLayout(self.z_patch_win)
            layout.setContentsMargins(12, 12, 12, 12)

            patch_centers = [(256, 256), (768, 256), (256, 768), (768, 768), (512, 512)]
            patch_size = 60  
            half_patch = patch_size // 2
            num_locations = len(patch_centers)
            
            fig = Figure(figsize=(2.5 * (no_slices + 1), 2.5 * num_locations), facecolor=self.theme["bg"])
            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            
            # ✨ Use GridSpec for better layout control
            gs = gridspec.GridSpec(num_locations, no_slices + 2, figure=fig, width_ratios=[1, 0.2] + [1]*no_slices)
            fig.suptitle("Suite2P_img vs. Z-Slices", fontsize=16)

            for row_idx, (cx, cy) in enumerate(patch_centers):
                y1, y2 = cy - half_patch, cy + half_patch
                x1, x2 = cx - half_patch, cx + half_patch

                if self.H is not None:
                    try:
                        transformed = self.transform_coordinates(
                            np.array([[[cx, cy]]], dtype=np.float32)
                        )
                        cx_live, cy_live = transformed[0][0]
                        self.log("应用全局校准")

                    except Exception as e:
                        self.log(f"坐标转换失败: {str(e)}")
                        continue
                else:
                    cx_live, cy_live = cx, cy

                y3, y4 = int(cy_live - half_patch), int(cy_live + half_patch)
                x3, x4 = int(cx_live - half_patch), int(cx_live + half_patch)


                # Display reference patch in the first column
                ax_ref = fig.add_subplot(gs[row_idx, 0])
                ref_patch = self.suite2p_img[y1:y2, x1:x2]
                ref_patch_8bit = cv2.normalize(ref_patch, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                
                blur_ref = cv2.GaussianBlur(ref_patch_8bit, (self.set_patchkernel, self.set_patchkernel), 0)
                patch_ref = cv2.addWeighted(blur_ref, 1.5, blur_ref, -0.5, 0)
                patch_ref = cv2.normalize(patch_ref, None, 0, 255, cv2.NORM_MINMAX)
                
                
                ax_ref.imshow(cv2.cvtColor(patch_ref, cv2.COLOR_GRAY2RGB))
                ax_ref.set_title(f"Ref @({cx},{cy})", fontsize=8)
                ax_ref.axis('off')

                # Display Z-stack patches starting from the third column (index 2)
                for slice_idx in range(no_slices):
                    ax_slice = fig.add_subplot(gs[row_idx, slice_idx + 2])
                    slice_patch = z_stack[slice_idx, y3:y4, x3:x4]

                    patch_8bit = cv2.normalize(slice_patch, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

                    invGamma = 1.0 / self.set_gamma
                    table = np.array([((i / 255.0) ** invGamma) * 255
                                if i > 20 else i  # 保留最暗部（小于10）不变
                                for i in np.arange(0, 256)]).astype("uint8")
                    patch_gamma = cv2.LUT(patch_8bit, table)

                    # Apply sharpening
                    blur = cv2.GaussianBlur(patch_gamma, (self.set_patchkernel, self.set_patchkernel), 0)
                    patch = cv2.addWeighted(blur, 1.5, blur, -0.5, 0)
                    patch = cv2.normalize(patch, None, 0, 255, cv2.NORM_MINMAX) 
                    
                    ax_slice.imshow(cv2.cvtColor(patch, cv2.COLOR_GRAY2RGB))
                    ax_slice.axis('off')

                    if row_idx == 0:
                        match_count = all_match_counts[slice_idx]
                        ax_slice.set_title(f"slice no. {slice_idx+1}\n{match_count} matches\n{((slice_idx+1)-((no_slices+1)/2))*2}um", fontsize=8)

            self.style_matplotlib_figure(fig)
            fig.tight_layout(rect=[0, 0, 1, 0.96])
            self.z_patch_win.show()
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法可视化Z轴校准: {str(e)}")
            print(e)
        

    def create_log_area(self, layout):
        group = QGroupBox("日志")
        vbox = QVBoxLayout()
        vbox.setContentsMargins(8, 12, 8, 8)
        self.log_area = QTextEdit()
        self.log_area.setObjectName("logArea")
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(180)
        self.log_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox.addWidget(self.log_area)
        group.setLayout(vbox)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(group, 1)

    def save_log(self):
        try:
            iscell_temp = self.iscell_data.copy()
            stimulated_path = os.path.join(self.default_savepath, f"{self.iscell_name}_stimulated{self.suffix}.npy")
            log_path = os.path.join(self.default_savepath, f"auto_log{self.suffix}.txt")

            stimulated_indices = sorted(list(self.stimulated))
            iscell_temp[:,0] = 0
            iscell_temp[stimulated_indices,0] = 1

        
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(self.log_area.toPlainText())
            np.save(stimulated_path, iscell_temp)
            self.log(self.tr_text("日志和激活ROI列表已保存至: {log_path}").format(log_path=log_path))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def toggle_topmost(self):
        current = self.windowFlags() & Qt.WindowStaysOnTopHint
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not current)
        self.show()
        self.log("窗口置顶状态: " + ("启用" if not current else "禁用"))

    def prepare_for_automation_input(self):
        self.restore_topmost_after_automation = False
        self.restore_window_after_automation = False
        QApplication.processEvents()

    def restore_after_automation_input(self):
        self.restore_topmost_after_automation = False
        self.restore_window_after_automation = False

    def _get_block_input_func(self):
        if os.name != "nt":
            raise RuntimeError("Windows BlockInput is only available on Windows")
        if self._block_input_func is None:
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            block_input = user32.BlockInput
            block_input.argtypes = [ctypes.c_bool]
            block_input.restype = ctypes.c_bool
            self._block_input_func = block_input
        return self._block_input_func

    def begin_pyautogui_critical_section(self, log_func=None):
        logger = log_func or self.log
        if self._pyautogui_input_blocked:
            return True
        try:
            block_input = self._get_block_input_func()
            if not block_input(True):
                raise ctypes.WinError(ctypes.get_last_error())
            self._pyautogui_input_blocked = True
            return True
        except Exception as e:
            if not self._pyautogui_blockinput_warned:
                logger(f"PyAutoGUI 关键输入保护不可用，继续执行: {e}")
                self._pyautogui_blockinput_warned = True
            return False

    def end_pyautogui_critical_section(self, log_func=None):
        if not self._pyautogui_input_blocked:
            return
        logger = log_func or self.log
        try:
            block_input = self._get_block_input_func()
            if not block_input(False):
                raise ctypes.WinError(ctypes.get_last_error())
        except Exception as e:
            logger(f"PyAutoGUI 关键输入保护释放失败: {e}")
        finally:
            self._pyautogui_input_blocked = False

    def launch_automation_thread(self):
        self.automation_start_pending = False
        if self.automation_thread is None or self.automation_thread.isRunning():
            return

        self.automation_thread.start()
        self.log("自动化流程启动...")

    def write_registered_field_value(self, pos_type, value, axis_name, log_func=None, restore_clipboard=True):
        missing_messages = {
            'x_pos': "X输入位置未注册",
            'y_pos': "Y输入位置未注册",
        }
        if pos_type not in self.registered_pos:
            raise ValueError(missing_messages.get(pos_type, f"{pos_type} is not registered"))

        pyautogui.PAUSE = self.automation_input_pause
        focus_pause = self.field_focus_pause
        clear_pause = self.field_clear_pause
        type_interval = self.automation_input_pause
        text_value = str(int(value))
        pos = self.registered_pos[pos_type]
        logger = log_func or self.log

        pyautogui.moveTo(*pos)
        pyautogui.click(clicks=2, interval=self.double_click_interval, button='left')
        time.sleep(focus_pause)
        pyautogui.press('f2')
        time.sleep(clear_pause)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(clear_pause)
        pyautogui.press('backspace')
        time.sleep(clear_pause)
        if pyperclip is not None:
            previous_clipboard = None
            if restore_clipboard:
                try:
                    previous_clipboard = pyperclip.paste()
                except Exception:
                    previous_clipboard = None
            try:
                pyperclip.copy(text_value)
                time.sleep(clear_pause)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(clear_pause)
                if restore_clipboard and previous_clipboard is not None:
                    pyperclip.copy(previous_clipboard)
            except Exception:
                pyautogui.write(text_value, interval=type_interval)
        else:
            pyautogui.write(text_value, interval=type_interval)
        time.sleep(clear_pause)
        pyautogui.press('enter')
        time.sleep(focus_pause)
        logger(f"{axis_name} 已写入 {int(value)}")
        return pos

    def warn_missing_registration(self, pos_type):
        messages = {
            'x_pos': "请先注册 X 输入位置",
            'y_pos': "请先注册 Y 输入位置",
            'stimulate_pos': "请先注册 Stimulate 按钮位置",
        }
        msg = messages.get(pos_type, f"{pos_type} is not registered")
        self.log(msg)
        QMessageBox.warning(self, self.tr_text("警告"), translate_runtime_text(self.language, msg))

    def write_registered_field_value_for_test(self, pos_type, value, axis_name):
        if pos_type not in self.registered_pos:
            self.warn_missing_registration(pos_type)
            return False

        pos = self.registered_pos[pos_type]
        text_value = str(int(value))
        self.log(f"Testing {axis_name} input: moving to {pos}")

        move_pause = 0.30
        focus_pause = 0.40
        step_pause = 0.18
        double_click_interval = 0.22
        type_interval = 0.05

        pyautogui.PAUSE = 0.10
        pyautogui.moveTo(*pos, duration=0.10)
        time.sleep(move_pause)
        pyautogui.click(clicks=2, interval=double_click_interval, button='left')
        time.sleep(focus_pause)
        pyautogui.press('f2')
        time.sleep(step_pause)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(step_pause)
        pyautogui.press('backspace')
        time.sleep(step_pause)
        if pyperclip is not None:
            try:
                previous_clipboard = pyperclip.paste()
            except Exception:
                previous_clipboard = None
            try:
                pyperclip.copy(text_value)
                time.sleep(step_pause)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(step_pause)
                if previous_clipboard is not None:
                    pyperclip.copy(previous_clipboard)
            except Exception:
                pyautogui.write(text_value, interval=type_interval)
        else:
            pyautogui.write(text_value, interval=type_interval)
        time.sleep(step_pause)
        pyautogui.press('enter')
        time.sleep(focus_pause)
        self.log(f"Testing {axis_name} input: wrote {int(value)}")
        return True

    def test_registered_input(self, pos_type, value, axis_name):
        if pos_type not in self.registered_pos:
            self.warn_missing_registration(pos_type)
            return False
        try:
            return self.write_registered_field_value_for_test(pos_type, value, axis_name)
        except Exception as e:
            self.log(f"测试失败: {e}")
            QMessageBox.warning(self, self.tr_text("警告"), translate_runtime_text(self.language, f"测试失败: {e}"))
            return False

    def test_x_input_position(self):
        self.test_registered_input('x_pos', 100, "X")

    def test_y_input_position(self):
        self.test_registered_input('y_pos', 100, "Y")

    def test_xy_input_positions(self):
        if not self.test_registered_input('x_pos', 100, "X"):
            return
        if not self.test_registered_input('y_pos', 100, "Y"):
            return
        self.log("测试 X/Y 输入完成")

    def test_stimulate_position_click(self):
        if 'stimulate_pos' not in self.registered_pos:
            self.warn_missing_registration('stimulate_pos')
            return
        pos = self.registered_pos['stimulate_pos']
        self.log(f"Testing Stimulate click: moving to {pos}")
        pyautogui.moveTo(*pos, duration=0.10)
        time.sleep(0.30)
        pyautogui.click(*pos)
        time.sleep(0.25)
        self.log(f"Testing Stimulate click: clicked {pos}")
        self.log("如果点击无效，请确认设置窗口没有遮挡注册坐标。")

    def move_mouse_to_live_preview_center(self, log_func=None):
        logger = log_func or self.log
        if not hasattr(self, "preview_label") or self.preview_label is None:
            return None
        center = self.preview_label.rect().center()
        global_center = self.preview_label.mapToGlobal(center)
        x, y = int(global_center.x()), int(global_center.y())
        pyautogui.moveTo(x, y)
        logger(f"Mouse returned to Live preview center: Point(x={x}, y={y})")
        return x, y

    def init_hotkeys(self):
        self.hotkeys = GlobalHotKeys({
            '<ctrl>+p': lambda *args: self.toggle_pause(),
            '<ctrl>+/': self.skip_current_cell,
            '<ctrl>+1': lambda: self.register_position('x_pos'),
            '<ctrl>+2': lambda: self.register_position('y_pos'),
            '<ctrl>+3': lambda: self.register_position('stimulate_pos'),
            '<ctrl>+k': self.start_automation,
            '<ctrl>+q': self.stop_automation,
        })
        self.hotkeys.start()

    def log(self, message):
        self.log_area.append(translate_runtime_text(self.language, message))
        cursor = self.log_area.textCursor()  # 获取光标
        cursor.movePosition(QTextCursor.End)  # 移动光标到末尾
        self.log_area.setTextCursor(cursor)  # 应用光标位置
        QApplication.processEvents()

    # 核心功能方法 479

    def _file_load_busy_message(self):
        return "File loading is already in progress. Please wait." if self.language == "en" else "文件正在加载，请稍候。"

    def _begin_file_load(self):
        if self._file_load_in_progress:
            self.log(self._file_load_busy_message())
            return False
        self._file_load_in_progress = True
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        return True

    def _end_file_load(self):
        self._file_load_in_progress = False
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def refresh_suite2p_overlay_if_ready(self, show_preview=False):
        if self.suite2p_img is None or self.stat_data is None or self.iscell_data is None:
            self.suite2p_img_withmask = None
            return False
        try:
            self._update_suite2p_overlay()
            if show_preview:
                self.show_suite2p_mask_preview()
            return True
        except Exception as e:
            self.suite2p_img_withmask = None
            message = f"Mask preview generation failed: {e}" if self.language == "en" else f"Masks预览生成失败: {e}"
            self.log(message)
            return False

    def _clear_suite2p_mask_preview_window(self, *args):
        self.suite2p_mask_preview_window = None

    def show_suite2p_mask_preview(self):
        if self.suite2p_img_withmask is None:
            return

        rgb = np.ascontiguousarray(self.suite2p_img_withmask)
        h, w = rgb.shape[:2]
        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)

        if self.suite2p_mask_preview_window is None:
            win = QWidget(self)
            win.setObjectName("auxWindow")
            win.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
            win.setAttribute(Qt.WA_DeleteOnClose, True)
            title = "Suite2P ROI Mask Preview" if self.language == "en" else "Suite2P ROI Mask 预览"
            win.setWindowTitle(title)
            win.setWindowIcon(get_app_icon())

            layout = QVBoxLayout(win)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(8)

            label = QLabel()
            label.setObjectName("suite2pPreview")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(512, 512)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(label)

            win.preview_label = label
            win.destroyed.connect(self._clear_suite2p_mask_preview_window)
            self.suite2p_mask_preview_window = win

        preview_label = self.suite2p_mask_preview_window.preview_label
        preview_label.setPixmap(pixmap.scaled(900, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.suite2p_mask_preview_window.resize(940, 940)
        self.suite2p_mask_preview_window.show()
        self.suite2p_mask_preview_window.raise_()
        self.suite2p_mask_preview_window.activateWindow()
    
    def load_npy_file(self, file_type):
        path, _ = QFileDialog.getOpenFileName(
            self, f"选择{file_type}文件", "", "Numpy Files (*.npy)")
        if not path:
            return

        if not self._begin_file_load():
            return

        try:
            data = np.load(path, allow_pickle=True)
            if file_type == 'stat':
                self.stat_data = data
                self.stat_path = path
                self.stat_label.setText(os.path.basename(path))
                self.stat_label.setToolTip(path)
                self.extract_roi_centers()
            elif file_type == 'iscell':
                self.default_savepath = os.path.dirname(path)
                self.iscell_name = os.path.splitext(os.path.basename(path))[0]
                self.iscell_data = data
                self.iscell_path = path
                self.iscell_label.setText(os.path.basename(path))
                self.iscell_label.setToolTip(path)
                self.extract_roi_centers()
                self.log(f"保存目录设置为{self.default_savepath}")

            self.log(f"成功加载 {file_type} 文件")
            self.refresh_suite2p_overlay_if_ready(show_preview=True)
            self.stimulated = set()
            self.log("重置已激活ROI列表")
            self.sync_shared_data_to_detection()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")
        finally:
            self._end_file_load()


    def extract_roi_centers(self):
        if hasattr(self, 'stat_data') and self.stat_data is not None and \
       hasattr(self, 'iscell_data') and self.iscell_data is not None:
            try:
                self.valid = np.where(self.iscell_data[:, 0] == 1)[0]
                self.centers = [self.stat_data[i]['med'][::-1] for i in self.valid]
                self.start_spin.setMaximum(len(self.centers)-1)
                self.end_spin.setMaximum(len(self.centers)-1)
                self.end_spin.setValue(len(self.centers)-1)
                self.log(f"提取到 {len(self.centers)} 个有效ROI")
                self.log(f"{self.valid}")
                self.offsets = {}
                self.preview_offset = {}
                self.removed = set()

            except Exception as e:
                error = f"ROI提取错误: {str(e)}"
                self.log(error)
                QMessageBox.warning(self, "警告", "请检查加载的.npy文件")

    def load_suite2p_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Suite2P图像", "", "Images (*.png *.jpg *.tif)")
        if not path:
            return

        if not self._begin_file_load():
            return

        try:

            img0 = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img0 is None:
                raise ValueError("图像加载失败")
            orig_shape = img0.shape  
            bit_depth = img0.dtype

    
            self.suite2p_img_label.setText(os.path.basename(path))
            self.suite2p_img_label.setToolTip(path)
            self.log(f"加载Suite2P图像: {orig_shape}, {bit_depth}")

            target_size = (1024, 1024)
            img_up  = cv2.resize(img0,     target_size, interpolation=cv2.INTER_CUBIC)
            self.log(f"上采样至 {target_size}")
            self.suite2p_img = img_up
            self.suite2p_img_path = path

            self.refresh_suite2p_overlay_if_ready(show_preview=True)
            self.sync_shared_data_to_detection()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"图像处理失败: {e}")
            self.log(f"Suite2P图像加载失败: {e}")
        finally:
            self._end_file_load()


    def extract_single_patch_withmask(self, image, center_x, center_y, abs_index=None, patch_size=40, denoise=True):
        """
        通用patch提取方法，根据中心坐标提取图像区域，并叠加对应细胞的mask，处理视野边缘情况。
        """
        try:
            y1_patch_orig = max(0, center_y - patch_size // 2)
            y2_patch_orig = min(image.shape[0], center_y + patch_size // 2)
            x1_patch_orig = max(0, center_x - patch_size // 2)
            x2_patch_orig = min(image.shape[1], center_x + patch_size // 2)

            # 实际裁剪区域
            crop = image[y1_patch_orig:y2_patch_orig, x1_patch_orig:x2_patch_orig]
            ph, pw = crop.shape[:2]

            # 创建空白 patch
            patch = np.zeros((patch_size, patch_size, 3), dtype=np.uint8)

            # 计算 crop 在 patch 中的起始位置
            start_y = patch_size // 2 - ph // 2
            start_x = patch_size // 2 - pw // 2

            # 将 crop 填充到 patch 中心
            patch[start_y:start_y + ph, start_x:start_x + pw] = crop

            # 提取对应细胞的 mask 并叠加到 patch 上
            if self.stat_data is not None and abs_index is not None and 0 <= abs_index < len(self.stat_data):
                cell = self.stat_data[abs_index]
                ypix = cell.get('ypix')
                xpix = cell.get('xpix')

                if ypix is not None and xpix is not None:
                    # 计算 mask 在原始 1024x1024 图像中的坐标
                    ypix_1024 = ypix * 2
                    xpix_1024 = xpix * 2

                    # 创建一个与 patch 大小相同的 mask (单通道)
                    mask_patch = np.zeros((patch_size, patch_size), dtype=np.uint8)

                    # 计算 mask 像素相对于原始裁剪区域左上角 (y1_patch_orig, x1_patch_orig) 的偏移量
                    relative_y_orig = ypix_1024 - y1_patch_orig
                    relative_x_orig = xpix_1024 - x1_patch_orig

                    # 找到位于原始裁剪区域内的 mask 像素
                    mask_in_crop_y = np.logical_and(relative_y_orig >= 0, relative_y_orig < ph)
                    mask_in_crop_x = np.logical_and(relative_x_orig >= 0, relative_x_orig < pw)
                    valid_mask_indices = np.where(np.logical_and(mask_in_crop_y, mask_in_crop_x))[0]

                    if valid_mask_indices.size > 0:
                        # 计算这些 mask 像素在 patch 中的坐标
                        patch_y = start_y + relative_y_orig[valid_mask_indices]
                        patch_x = start_x + relative_x_orig[valid_mask_indices]

                        # 确保这些坐标在 patch 的有效范围内 (理论上应该在)
                        valid_patch_y = np.logical_and(patch_y >= 0, patch_y < patch_size)
                        valid_patch_x = np.logical_and(patch_x >= 0, patch_x < patch_size)
                        final_valid_indices = np.where(np.logical_and(valid_patch_y, valid_patch_x))[0]

                        if final_valid_indices.size > 0:
                            mask_patch[patch_y[final_valid_indices], patch_x[final_valid_indices]] = 255

                    # 将单通道 mask 转换为三通道并叠加到 patch 上 (蓝色)
                    mask_color = np.zeros_like(patch)
                    mask_color[:, :, 2] = mask_patch
                    patch = cv2.addWeighted(patch, 1, mask_color, self.set_alpha, 0)

            # 锐化处理
            if denoise:
                blur = cv2.GaussianBlur(patch, (self.set_patchkernel, self.set_patchkernel), 0)
                patch = cv2.addWeighted(blur, 1.5, blur, -0.5, 0)

            # 标准化处理
            patch = cv2.normalize(patch, None, 0, 255, cv2.NORM_MINMAX)

        
            return patch

        finally:
            if 'crop' in locals(): del crop
            if 'blur' in locals(): del blur
            if 'mask_color' in locals(): del mask_color
            if 'mask_patch' in locals(): del mask_patch

    

    def _update_suite2p_overlay(self):
        """
        用已有的 self.suite2p_img (1024×1024) + self.stat_data + self.iscell_data
        来生成半透明的 self.suite2p_img_withmask。
        """
        img_up = self.suite2p_img
        h, w = img_up.shape

        # 1) 在原始 512×512 上构建 mask，再统一 resize 到 1024×1024
        #    注意：我们假设 stat_data 中的 ypix/xpix 已是相对于 512×512 的坐标
        #    因此先反推回 512×512 mask，再放大到 1024×1024。
        cell_mask0 = np.zeros((h//2, w//2), dtype=np.uint8)
        arr = self.iscell_data
        flags = (arr[:,0] == 1) if arr.ndim == 2 else (arr == 1)

        for idx, cell in enumerate(self.stat_data):
            if not flags[idx]:
                continue
            ypix = cell.get('ypix')
            xpix = cell.get('xpix')
            if ypix is None or xpix is None:
                continue
            cell_mask0[ypix, xpix] = 255

        mask_up = cv2.resize(cell_mask0, (w, h), interpolation=cv2.INTER_NEAREST)

        # 2) 叠加
        base = cv2.cvtColor(img_up, cv2.COLOR_GRAY2BGR)
        overlay = np.zeros_like(base)
        overlay[..., 0] = mask_up
        alpha = self.set_alpha
        self.suite2p_img_withmask = cv2.addWeighted(base, 1.0, overlay, alpha, 0)

        self.log("生成cell mask预览图")
        # 如果需要立即刷新预览，可在这里发信号或直接调用 update_preview()

    def load_microscope_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择显微镜图像", "", "Images (*.png *.jpg *.tif)")
        if path:
            if not self._begin_file_load():
                return
            had_microscope_image = self.microscope_img is not None
            try:
                self.microscope_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if self.microscope_img is None:
                    QMessageBox.critical(self, "错误", "图像加载失败")
                    return
                microscope_img_shape = self.microscope_img.shape
                miscroscope_img_bit = self.microscope_img.dtype
                Temp_log = ""

                if self.microscope_img.shape != (1024,1024):
                    self.microscope_img = cv2.resize(
                        self.microscope_img, 
                        (1024,1024),
                        interpolation=cv2.INTER_CUBIC
                        )
                    Temp_log = ", 上采样至(1024, 1024)"

                if self.microscope_img is not None:
                    self.live_img = self.microscope_img.copy()
                    self.microscope_img_label.setText(os.path.basename(path))  # 新增文件名显示
                    self.microscope_img_label.setToolTip(path)
                    self.microscope_img_path = path
                    self.log(f"加载/更新显微镜图像：{microscope_img_shape}, {miscroscope_img_bit}{Temp_log}")
                    self.sync_shared_data_to_detection()
                    if had_microscope_image:
                        reminder = "Reminder: switch the laser wavelength back." if self.language == "en" else "温馨提醒：别忘了把激光波长改回去！"
                        self.log(reminder)
                else:
                    QMessageBox.critical(self, "错误", "图像加载失败")
            finally:
                self._end_file_load()

    def load_live(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Live图像", "", "Images (*.png *.jpg *.tif)")
        if path:
            self.live_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            live_img_shape = self.microscope_img.shape
            live_img_bit = self.microscope_img.dtype
            Temp_log = ""

            if self.live_img.shape != (1024,1024):
                self.live_img = cv2.resize(
                    self.live_img, 
                    (1024,1024),
                    interpolation=cv2.INTER_CUBIC
                    )
                Temp_log = ", 上采样至(1024, 1024)"
            if self.live_img is not None:
                self.log(f"更新显微镜图像：{live_img_shape}, {live_img_bit}{Temp_log}")
            else:
                QMessageBox.critical(self, "错误", "图像加载失败")

        tip_text = (
        "别忘了把激光波长改回去！"
        )
        QMessageBox.information(self, "温馨提醒", tip_text)

    def detect_features_with_quadrants(self):
        """分象限特征检测"""
        if self.suite2p_img is None or self.microscope_img is None:
            QMessageBox.critical(self, "错误", "请先加载两幅图像")
            return False
        
        quadrant_size = 341
        quadrants = []
        for i in range(3):
            for j in range(3):
                x_start = j * quadrant_size
                y_start = i * quadrant_size
                x_end = (j+1)*quadrant_size if j<2 else 1024
                y_end = (i+1)*quadrant_size if i<2 else 1024
                quadrants.append((i, j, x_start, y_start, x_end, y_end))
        
        sift = cv2.SIFT_create(
            nfeatures=0,
            nOctaveLayers=3,
            contrastThreshold=self.contrast_spin.value(),
            edgeThreshold=10,
            sigma=float(self.set_sigma.value())
        )
        
        # Suite2P图像特征检测
        self.kp1 = []
        self.des1 = None
        mask = np.zeros_like(self.suite2p_img)
        for region in quadrants:
            i, j, xs, ys, xe, ye = region
            mask.fill(0)
            mask[ys:ye, xs:xe] = 255
            kp, des = sift.detectAndCompute(self.suite2p_img, mask)
            if des is not None and len(kp) > 0:
                self.kp1.extend(kp)
                self.des1 = des if self.des1 is None else np.vstack((self.des1, des))
        
        # 显微镜图像特征检测
        self.kp2 = []
        self.des2 = None
        mask = np.zeros_like(self.microscope_img)
        for region in quadrants:
            i, j, xs, ys, xe, ye = region
            mask.fill(0)
            mask[ys:ye, xs:xe] = 255
            kp, des = sift.detectAndCompute(self.microscope_img, mask)
            if des is not None and len(kp) > 0:
                self.kp2.extend(kp)
                self.des2 = des if self.des2 is None else np.vstack((self.des2, des))
        
        # 统计特征点分布
        self.log_feature_distribution(quadrant_size)
        
        if self.des1 is None or self.des2 is None:
            QMessageBox.critical(self, "错误", "特征检测失败")
            return False
        
        # 特征匹配
        FLANN_INDEX_KDTREE = 1
        flann = cv2.FlannBasedMatcher(
            dict(algorithm=FLANN_INDEX_KDTREE, trees=5),
            dict(checks=50))
        matches = flann.knnMatch(self.des1, self.des2, k=2)
        
        # 筛选优质匹配
        self.matches = []
        for m, n in matches:
            if m.distance < self.ratio_spin.value() * n.distance:
                pt1 = self.kp1[m.queryIdx].pt  # 在 suite2p_img 中的点
                pt2 = self.kp2[m.trainIdx].pt  # 在 microscope_img 中的点
                dx = pt1[0] - pt2[0]
                dy = pt1[1] - pt2[1]
                dist = np.sqrt(dx**2 + dy**2)
                if dist <= 50:
                    self.matches.append(m)
        
        if len(self.matches) < 15:
            QMessageBox.critical(self, "错误", "匹配点不足")
            return False
        
        self.matches = sorted(self.matches, key=lambda x: x.distance)
        return True

    def log_feature_distribution(self, quadrant_size):
        """记录特征点分布信息"""
        # Suite2P特征分布
        suite2p_counts = np.zeros((3,3), dtype=int)
        for kp in self.kp1:
            x, y = kp.pt
            i, j = int(y//quadrant_size), int(x//quadrant_size)
            suite2p_counts[min(i,2), min(j,2)] += 1
        
        # 显微镜特征分布
        micro_counts = np.zeros((3,3), dtype=int)
        for kp in self.kp2:
            x, y = kp.pt
            i, j = int(y//quadrant_size), int(x//quadrant_size)
            micro_counts[min(i,2), min(j,2)] += 1
        
        self.log("\n各象限特征点分布:")
        for i in range(3):
            for j in range(3):
                self.log(f"象限({i},{j}): Suite2P={suite2p_counts[i,j]} | 显微镜={micro_counts[i,j]}")

    def compute_homography(self):
        if not self.detect_features_with_quadrants():
            return
        
        # 分象限选择匹配点
        quadrant_size = 341
        quadrant_dict = {(i,j):[] for i in range(3) for j in range(3)}
        for m in self.matches:
            x, y = self.kp1[m.queryIdx].pt
            i, j = int(y//quadrant_size), int(x//quadrant_size)
            quadrant_dict[(min(i,2), min(j,2))].append(m)
        
        selected_matches = []
        for q in quadrant_dict:
            matches = sorted(quadrant_dict[q], key=lambda x: x.distance)
            n = min(self.max_matches_spin.value(), 
                   max(0, len(matches)))
            selected_matches.extend(matches[:n])
            self.log(f"象限{q}: 使用{n}/{len(matches)}个匹配点")
        
        if len(selected_matches) < 15:
            QMessageBox.critical(self, "错误", "总匹配点不足")
            return
        
        self.log(f"共发现{len(selected_matches)}个匹配点")
        
        # 计算单应性矩阵
        src_pts = np.float32([self.kp1[m.queryIdx].pt for m in selected_matches]).reshape(-1,1,2)
        dst_pts = np.float32([self.kp2[m.trainIdx].pt for m in selected_matches]).reshape(-1,1,2)
        
        self.H, mask = cv2.findHomography(
            src_pts, dst_pts, cv2.RANSAC, 
            ransacReprojThreshold=3.0,
            maxIters=5000,
            confidence=0.999
        )
        
        if self.H is None:
            QMessageBox.critical(self, "错误", "单应性矩阵计算失败")
            return
        
        # 应用手动补偿
        # self.H[0, 2] += self.compensation_x.value()
        # self.H[1, 2] += self.compensation_y.value()
        
        # 计算误差
        error = self.calculate_reprojection_error(src_pts, dst_pts)
        self.log(f"校准成功! 重投影误差: {error:.2f}像素")
        H_str = np.array2string(
            self.H,
            formatter={
                'float_kind': lambda x: f"{x:12.8f}"  # 固定小数点显示，保留8位小数
            },
            suppress_small=True  # 抑制极小数的科学计数法
        ).replace('[', ' ').replace(']', ' ')  # 保持矩阵对齐
        self.log(f"单应性矩阵:\n{H_str}")
        self.sync_shared_data_to_detection()

    def calculate_reprojection_error(self, src, dst):
        transformed = cv2.perspectiveTransform(src, self.H)
        return np.mean(np.linalg.norm(dst - transformed, axis=2))

    def visualize_calibration(self):
        if self.H is None:
            QMessageBox.critical(self, "错误", "请先计算单应性矩阵")
            return
        
        # 生成网格点
        grid_size = 64
        x = np.arange(0, 1024, grid_size)
        y = np.arange(0, 1024, grid_size)
        grid = np.array([[xi, yi] for yi in y for xi in x], dtype=np.float32).reshape(-1,1,2)
        
        # 转换网格点
        transformed = cv2.perspectiveTransform(grid, self.H)
        
        # 绘制匹配点
        fig = plt.figure(figsize=(18, 5), facecolor=self.theme["bg"])
        matched_img = cv2.drawMatches(
            self.suite2p_img, self.kp1,
            self.microscope_img, self.kp2,
            self.matches[:300], None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        ax_match = fig.add_subplot(121)
        ax_match.imshow(matched_img)
        ax_match.set_title("Feature matching")
        ax_match.axis('off')
        
        # 子图2：网格变形可视化
        ax = fig.add_subplot(122)
        
        # 计算坐标范围
        all_x = np.concatenate([grid[:,0,0], transformed[:,0,0]])
        all_y = np.concatenate([grid[:,0,1], transformed[:,0,1]])
        max_range = max(np.ptp(all_x), np.ptp(all_y)) * 1.1
        mid_x = (np.max(all_x) + np.min(all_x)) / 2
        mid_y = (np.max(all_y) + np.min(all_y)) / 2
        
        # 设置相同比例
        ax.set_aspect('equal')
        ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
        ax.set_ylim(mid_y + max_range/2, mid_y - max_range/2)  # 反转Y轴
        
        # 绘制内容
        ax.scatter(grid[:,0,0], grid[:,0,1], c=self.theme["accent"], s=10, label='Suite2p Reference', alpha=0.75)
        ax.scatter(transformed[:,0,0], transformed[:,0,1], c=self.theme["danger"], s=10, label='Microscope Image', alpha=0.75)
        
        # 绘制分界线
        for i in range(1,3):
            ax.axhline(i*341, c=self.theme["muted"], ls='--', lw=0.5, alpha=0.5)
            ax.axvline(i*341, c=self.theme["muted"], ls='--', lw=0.5, alpha=0.5)
        
        ax.legend()
        ax.set_title("Correction Map")
        self.style_matplotlib_figure(fig)
        fig.tight_layout()
        plt.show()

    def reset_stimulated(self):
            self.stimulated = set()
            self.log("重置已激活ROI列表")

    def clearH(self):
        if self.H is not None:
            self.H = None
            self.log("已清除单应性矩阵")
        if self.compensation_x is not None or self.compensation_y is not None:
            self.compensation_y.setValue(0)
            self.compensation_x.setValue(0)
            self.log("已清除全局校准")
        self.offsets = {}
        self.preview_offset = {}
        self.log("已清除单细胞校准")
        self.removed = set()
        self.log("已重置排除ROI列表")
        self.sync_shared_data_to_detection()

    def transform_coordinates(self, points):
        if self.H is None:
            raise ValueError("单应性矩阵未计算")
        return cv2.perspectiveTransform(points, self.H)

    def register_position(self, pos_type):
        pos = pyautogui.position()
        self.registered_pos[pos_type] = pos
        self.position_registered.emit()
        self.log(f"注册 {pos_type}: {pos}")

    def validate_inputs(self):
        check_roi = [
            (bool(self.centers), "未找到有效ROI坐标"),
            ('x_pos' in self.registered_pos, "请注册X输入位置"),
            ('y_pos' in self.registered_pos, "请注册Y输入位置"),
            ('stimulate_pos' in self.registered_pos, "请注册stimulate按钮位置"),
        ]
        for condition, msg in check_roi:
            if not condition:
                QMessageBox.critical(self, "错误", msg)
                return False
            
        if self.suite2p_img is None or self.microscope_img is None or self.H is None:
            self.log("未加载图像，跳过坐标矫正")
            return True
                    
        return True

    def switch_mode(self, mode, force=False):
        if mode == "detection" and not force:
            if self.automation_start_pending or (self.automation_thread and self.automation_thread.isRunning()):
                QMessageBox.information(self, "提示", "自动化运行中，请先停止或完成后再进入检测页。")
                self.update_mode_switch_state()
                return

        if mode == "detection":
            self.page_stack.setCurrentWidget(self.detection_page_scroll)
            self.current_mode = "detection"
        else:
            self.page_stack.setCurrentWidget(self.activation_page)
            self.current_mode = "activation"

        self.update_mode_buttons()

    def update_mode_buttons(self):
        activation_role = "primary" if self.current_mode == "activation" else "secondary"
        detection_role = "primary" if self.current_mode == "detection" else "secondary"
        self.set_button_role(self.activation_mode_btn, activation_role)
        self.set_button_role(self.detection_mode_btn, detection_role)

    def update_mode_switch_state(self):
        detection_locked = self.automation_start_pending or (
            self.automation_thread is not None and self.automation_thread.isRunning()
        )
        self.detection_mode_btn.setEnabled(not detection_locked)
        if detection_locked and getattr(self, "current_mode", "activation") != "activation":
            self.switch_mode("activation", force=True)
        else:
            self.update_mode_buttons()
    
    def print_status(self):
        removed_str = ", ".join(map(str, sorted(list(self.removed))))
        if self.language == "en":
            self.log("Current status:")
            self.log(f"Save directory set to {self.default_savepath}")
            self.log(f"Extracted {len(self.centers)} valid ROIs")
            self.log(f"Skipped {len(self.removed)} ROIs: {{{removed_str}}}")
            self.log(f"Stimulated {len(self.stimulated)} ROIs: {self.stimulated}")
        else:
            self.log("当前状态：")
            self.log(f"保存目录设置为{self.default_savepath}")
            self.log(f"提取到 {len(self.centers)} 个有效ROI")
            self.log(f"跳过 {len(self.removed)} 个ROI：{{{removed_str}}}")
            self.log(f"激活 {len(self.stimulated)} 个ROI：{self.stimulated}")

    def build_post_check_context(self):
        pre_activation_img = None
        pre_activation_source = "未带入"
        if self.live_img is not None:
            pre_activation_img = self.live_img.copy()
            pre_activation_source = "已带入当前 Live 图像"
        elif self.microscope_img is not None:
            pre_activation_img = self.microscope_img.copy()
            pre_activation_source = "已带入当前显微镜图像"

        context = {
            "stat_data": self.stat_data.copy() if self.stat_data is not None else None,
            "iscell_data": self.iscell_data.copy() if self.iscell_data is not None else None,
            "suite2p_img": self.suite2p_img.copy() if self.suite2p_img is not None else None,
            "pre_activation_img": pre_activation_img,
            "pre_activation_source": pre_activation_source,
            "H": self.H.copy() if self.H is not None else None,
            "default_savepath": self.default_savepath,
            "roi_diameter": self.roi_diameter,
            "stimulated": set(self.stimulated),
        }
        return context

    def open_post_check_window(self):
        self.switch_mode("detection")
        return
        if self.post_check_window is not None and self.post_check_window.isVisible():
            self.post_check_window.raise_()
            self.post_check_window.activateWindow()
            return

        self.post_check_window = DetectionPage(theme=self.theme, parent=self)
        self.post_check_window.destroyed.connect(lambda *_: setattr(self, "post_check_window", None))
        self.post_check_window.show()
        self.post_check_window.raise_()
        self.post_check_window.activateWindow()
        self.log("已打开 post-check 界面")


    
    def start_automation(self):
        if not self.validate_inputs():
            return

        if self.automation_thread and (self.automation_thread.isRunning() or self.automation_start_pending):
            QMessageBox.warning(self, "警告", "已有任务运行中")
            return

        self.log(
            f"启动自动化: 范围 no.{self.start_spin.value()} -> no.{self.end_spin.value()} | "
            f"x={self.registered_pos.get('x_pos')} y={self.registered_pos.get('y_pos')} "
            f"stim={self.registered_pos.get('stimulate_pos')}"
        )
        self.automation_thread = AutomationThread(self)
        self.automation_thread.log_message.connect(self.log)
        self.automation_thread.progress.connect(self.handle_progress)
        self.automation_thread.progress_state.connect(self.handle_progress_state)
        self.automation_thread.finished.connect(self.handle_finish)
        self.automation_thread.error.connect(self.handle_error)
        self.automation_thread.paused.connect(self.handle_pause_state)
        self.automation_thread.preview.connect(
            lambda micro, suite2p, idx: self.update_preview(micro, suite2p, idx)
        )
        self.update_progress_ui(
            processed=0,
            total=self.automation_thread.total_count,
            stimulated=0,
            skipped=0,
            status="running",
        )
        self.prepare_for_automation_input()
        self.automation_start_pending = True
        self.switch_mode("activation", force=True)
        self.update_mode_switch_state()
        self.log("自动化即将启动：保持当前窗口状态，等待目标软件接收输入...")
        self.log("PyAutoGUI 关键输入保护已启用")
        QTimer.singleShot(250, self.launch_automation_thread)


    def toggle_pause(self):
        """切换暂停状态"""
        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.toggle_pause()
            status = "已暂停" if self.automation_thread._paused else "已恢复"
            self.log(f"自动化流程{status}")

    def stop_automation(self, status="stopped"):
        self.automation_start_pending = False
        if self.automation_thread is not None:
            if status in {"stopped", "error"}:
                self.set_progress_status(status)
            self.automation_thread.running = False
            self.automation_thread._pause_cond.wakeAll()  # 如果线程在暂停中
            self.automation_thread.wait()  # 等待线程完全退出
            self.automation_thread = None
            self.restore_after_automation_input()
            if status == "stopped":
                self.log("自动化已停止")
        elif status in {"stopped", "error"} and self.progress_state["status"] not in {"idle", "finished"}:
            self.set_progress_status(status)
            self.restore_after_automation_input()
        self.update_mode_switch_state()

    def handle_progress(self, idx, total, x, y, current):
        self.log(f"已输入ROI {current}: no.{idx}/{total} __ X:{x:.1f}, Y:{y:.1f}")
        self.stimulated.add(current)
        

    def handle_finish(self):
        self.automation_start_pending = False
        self.automation_thread = None
        self.restore_after_automation_input()
        self.update_mode_switch_state()
        if self.progress_state["status"] in {"stopped", "error"}:
            return

        total = self.progress_state["total"]
        self.update_progress_ui(processed=total, status="finished")

        self.log(f"输入完成")
        iscell_temp = self.iscell_data.copy()
        stimulated_path = os.path.join(self.default_savepath, f"{self.iscell_name}_stimulated{self.suffix}.npy")
        log_path = os.path.join(self.default_savepath, f"auto_log{self.suffix}.txt")

        stimulated_indices = sorted(list(self.stimulated))
        iscell_temp[:,0] = 0
        iscell_temp[stimulated_indices,0] = 1

        if self.autosave:
            np.save(stimulated_path, iscell_temp)
            
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_area.toPlainText())
                self.log(self.tr_text("日志和激活ROI列表已保存至: {log_path}").format(log_path=log_path))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")


    def handle_error(self, msg):
        self.set_progress_status("error")
        self.restore_after_automation_input()
        self.update_mode_switch_state()
        QMessageBox.critical(self, "错误", msg)
        self.stop_automation(status="error")

    def closeEvent(self, event):
        self.stop_automation()
        self.hotkeys.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedCalibrationGUI()
    window.show()
    sys.exit(app.exec_())
