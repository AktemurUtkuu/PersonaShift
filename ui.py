import os
import sys
import cv2
import time
import psycopg2
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QSlider, QMessageBox, QComboBox,
                             QWidget, QHBoxLayout, QPushButton, QCheckBox, 
                             QGroupBox, QDialog, QScrollArea, QGridLayout, 
                             QFrame, QStackedWidget, QLineEdit, QGraphicsOpacityEffect)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QTimer
from dotenv import load_dotenv
from engine import VideoThread

# Uygulamanın olduğu dizini tespit et
base_path = os.path.dirname(os.path.abspath(__file__))
# .env dosyasının yolunu oraya sabitle
env_path = os.path.join(base_path, '.env')

# load_dotenv'i bu yolla çağır
load_dotenv(dotenv_path=env_path)

# Kontrol etmek için ekle:
if not os.path.exists(env_path):
    print(f"HATA: .env dosyası bulunamadı! Aranan yol: {env_path}")

if getattr(sys, 'frozen', False):
    sys.path.append(os.path.join(sys._MEIPASS, 'basicsr'))
    sys.path.append(os.path.join(sys._MEIPASS, 'gfpgan'))

COLORS = {
    "void": "#0b0e12",
    "carbon": "#181a1d",
    "graphite": "#1f2124",
    "slate": "#303235",
    "fog": "#5d5e61",
    "steel": "#818284",
    "ash": "#a3a4a5",
    "silver": "#bababb",
    "bone": "#dedede",
    "accent": "#00d892",
    "teal": "#002923",
    "teal_hover": "#005441",
    "error": "#9f3f53",
    "violet": "#c58aff",
    "coral": "#ff6285",
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "xxl": 24,
    "section": 40,
}

RADIUS = {
    "none": 0,
    "sm": 1,
    "md": 4,
}

TYPOGRAPHY = {
    "body_family": "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif",
    "mono_family": "'Consolas', 'JetBrains Mono', 'IBM Plex Mono', monospace",
    "caption": 11,
    "body": 14,
    "button": 12,
    "title": 18,
    "heading": 26,
}

COMPONENT_STYLES = {
    "label": f"color: {COLORS['ash']}; font-size: 13px; border: none;",
    "form_input": (
        f"background-color: {COLORS['carbon']}; border: 1px solid {COLORS['slate']}; "
        f"border-radius: {RADIUS['sm']}px; padding: 10px; color: {COLORS['bone']}; font-size: 14px;"
    ),
    "profile_readonly": (
        f"background-color: {COLORS['carbon']}; border: 1px solid {COLORS['slate']}; "
        f"border-radius: {RADIUS['sm']}px; padding: 0 10px; color: {COLORS['steel']};"
    ),
    "profile_editable": (
        f"background-color: {COLORS['graphite']}; border: 1px solid {COLORS['accent']}; "
        f"border-radius: {RADIUS['sm']}px; padding: 0 10px; color: {COLORS['bone']};"
    ),
    "camera_viewport": (
        f"background-color: {COLORS['void']}; border: 1px solid {COLORS['slate']}; "
        f"border-radius: {RADIUS['sm']}px;"
    ),
}

GLOBAL_STYLE = f"""
    QMainWindow, QDialog {{
        background-color: {COLORS['void']};
    }}
    QWidget {{
        color: {COLORS['silver']};
        font-family: {TYPOGRAPHY['body_family']};
        font-size: {TYPOGRAPHY['body']}px;
        font-weight: 400;
        selection-background-color: {COLORS['teal']};
        selection-color: {COLORS['accent']};
    }}
    QLabel {{
        color: {COLORS['silver']};
        border: none;
    }}
    QLabel#app_brand {{
        color: {COLORS['bone']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 18px;
        padding-bottom: {SPACING['md']}px;
        letter-spacing: 1px;
    }}
    QLabel#brand_mark {{
        color: {COLORS['accent']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 20px;
        padding: 0px;
    }}
    QLabel#brand_name {{
        color: {COLORS['bone']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 14px;
        letter-spacing: 1px;
    }}
    QLabel#brand_caption {{
        color: {COLORS['steel']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
    }}
    QLabel#page_title {{
        color: {COLORS['bone']};
        font-size: 17px;
        padding-left: {SPACING['md']}px;
    }}
    QLabel#page_context {{
        color: {COLORS['steel']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
        padding-left: {SPACING['md']}px;
    }}
    QLabel#screen_title, QLabel#dialog_title {{
        color: {COLORS['bone']};
        font-size: {TYPOGRAPHY['title']}px;
    }}
    QLabel#screen_heading {{
        color: {COLORS['bone']};
        font-size: {TYPOGRAPHY['heading']}px;
    }}
    QLabel#screen_caption, QLabel#muted_label, QLabel#face_name_label {{
        color: {COLORS['ash']};
        font-size: 13px;
    }}
    QLabel#metric_title, QLabel#form_label {{
        color: {COLORS['ash']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 12px;
    }}
    QLabel#metric_value {{
        color: {COLORS['bone']};
        font-size: 20px;
    }}
    QLabel#card_title {{
        color: {COLORS['ash']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 11px;
        letter-spacing: 1px;
    }}
    QLabel#card_value {{
        color: {COLORS['bone']};
        font-size: 19px;
    }}
    QLabel#card_context, QLabel#field_hint, QLabel#support_body {{
        color: {COLORS['ash']};
        font-size: 13px;
    }}
    QLabel#field_value {{
        color: {COLORS['bone']};
        font-size: 14px;
    }}
    QLabel#payment_brand {{
        color: {COLORS['accent']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
    }}
    QLabel#payment_number {{
        color: {COLORS['bone']};
        font-size: 18px;
    }}
    QLabel#payment_meta, QLabel#payment_holder, QLabel#plan_feature {{
        color: {COLORS['ash']};
        font-size: 13px;
    }}
    QLabel#support_code {{
        color: {COLORS['steel']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
    }}
    QLabel#plan_title {{
        color: {COLORS['ash']};
        font-size: 20px;
    }}
    QLabel#plan_title[status="premium"] {{
        color: {COLORS['accent']};
    }}
    QLabel#plan_price {{
        color: {COLORS['bone']};
        font-size: 28px;
    }}
    QLabel#status_label {{
        color: {COLORS['accent']};
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 10px;
    }}
    QLabel#status_label[status="info"] {{
        color: {COLORS['ash']};
        border-left: 2px solid {COLORS['ash']};
    }}
    QLabel#status_label[status="success"] {{
        color: {COLORS['accent']};
        border-left: 2px solid {COLORS['accent']};
    }}
    QLabel#status_label[status="warning"] {{
        color: {COLORS['bone']};
        border-left: 2px solid {COLORS['error']};
    }}
    QLabel#status_label[status="error"] {{
        color: {COLORS['error']};
        border-left: 2px solid {COLORS['error']};
    }}
    QLabel#camera_placeholder_title {{
        color: {COLORS['bone']};
        font-size: 18px;
    }}
    QLabel#camera_placeholder_meta {{
        color: {COLORS['steel']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 11px;
        letter-spacing: 1px;
    }}
    QLabel#camera_viewport {{
        background-color: {COLORS['void']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        color: {COLORS['steel']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 12px;
        letter-spacing: 1px;
    }}
    QLabel#camera_viewport[state="running"] {{
        border-color: {COLORS['accent']};
    }}
    QLabel#control_label {{
        color: {COLORS['ash']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 11px;
        letter-spacing: 1px;
    }}
    QLabel#selected_face_value {{
        color: {COLORS['bone']};
        background-color: {COLORS['graphite']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 10px;
    }}
    QLabel#restriction_text {{
        color: {COLORS['ash']};
        font-size: 13px;
    }}
    QLabel#face_empty_state {{
        color: {COLORS['steel']};
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 18px;
    }}
    QLabel#error_label {{
        color: {COLORS['error']};
        font-size: 12px;
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 8px;
    }}
    QLabel#error_label[visibleState="empty"] {{
        color: {COLORS['fog']};
        background-color: transparent;
        border: 1px solid transparent;
    }}
    QLabel#login_kicker, QLabel#section_title {{
        color: {COLORS['accent']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
    }}
    QLabel#login_title {{
        color: {COLORS['bone']};
        font-size: 26px;
    }}
    QLabel#login_helper {{
        color: {COLORS['ash']};
        font-size: 13px;
    }}
    QLabel#user_name_label {{
        color: {COLORS['bone']};
        font-size: 13px;
    }}
    QLabel#user_status_label, QLabel#status_badge {{
        color: {COLORS['accent']};
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 4px 8px;
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 10px;
        letter-spacing: 1px;
    }}
    QLabel#card_icon {{
        color: {COLORS['ash']};
        background-color: {COLORS['graphite']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 8px 12px;
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 12px;
    }}
    QLabel#card_info {{
        background: transparent;
        border: none;
        margin-left: 10px;
    }}
    QLabel#face_thumbnail {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QLabel#face_thumbnail:hover {{
        border-color: {COLORS['ash']};
    }}
    QLabel#face_thumbnail[selected="true"] {{
        border: 2px solid {COLORS['accent']};
        background-color: {COLORS['teal']};
    }}

    QFrame#sidebar {{
        background-color: {COLORS['void']};
        border-right: 1px solid {COLORS['slate']};
    }}
    QFrame#sidebar_header {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#sidebar_footer {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#top_bar {{
        background-color: {COLORS['void']};
        border-bottom: 1px solid {COLORS['slate']};
    }}
    QFrame#content_container {{
        background-color: {COLORS['void']};
    }}
    QFrame#page_header {{
        background-color: transparent;
        border: none;
    }}
    QFrame#card_frame {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#stat_card, QFrame#plan_card, QFrame#info_card, QFrame#form_panel, QFrame#payment_card, QFrame#support_tile {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#camera_preview_panel, QFrame#camera_controls_panel, QFrame#camera_status_bar, QFrame#restriction_panel, QFrame#face_picker_item {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#camera_preview_panel[state="running"], QFrame#face_picker_item[selected="true"] {{
        border-left: 2px solid {COLORS['accent']};
    }}
    QFrame#restriction_panel[status="locked"] {{
        border-left: 2px solid {COLORS['error']};
    }}
    QFrame#restriction_panel[status="unlocked"] {{
        border-left: 2px solid {COLORS['accent']};
    }}
    QFrame#stat_card[status="success"], QFrame#plan_card[status="active"], QFrame#info_card[status="success"], QFrame#payment_card[preferred="true"], QFrame#support_tile[status="success"] {{
        border-left: 2px solid {COLORS['accent']};
    }}
    QFrame#stat_card[status="info"], QFrame#info_card[status="info"], QFrame#support_tile[status="info"] {{
        border-left: 2px solid {COLORS['ash']};
    }}
    QFrame#stat_card[status="premium"], QFrame#info_card[status="premium"], QFrame#support_tile[status="premium"] {{
        border-left: 2px solid {COLORS['violet']};
    }}
    QFrame#info_card[status="warning"], QFrame#support_tile[status="warning"] {{
        border-left: 2px solid {COLORS['error']};
    }}
    QFrame#form_row {{
        background-color: {COLORS['graphite']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#payment_card[preferred="false"] {{
        border-left: 2px solid {COLORS['slate']};
    }}
    QFrame#alert_box {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QFrame#alert_box[status="success"] {{
        border-left: 2px solid {COLORS['accent']};
    }}
    QFrame#alert_box[status="error"] {{
        border-left: 2px solid {COLORS['error']};
    }}
    QFrame#alert_box[status="confirm"] {{
        border-left: 2px solid {COLORS['ash']};
    }}

    QGroupBox {{
        color: {COLORS['bone']};
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding-top: 20px;
        font-size: 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {COLORS['ash']};
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: 12px;
    }}
    QGroupBox#payment_card[preferred="true"] {{
        color: {COLORS['accent']};
        border: 1px solid {COLORS['accent']};
    }}

    QPushButton {{
        background-color: {COLORS['graphite']};
        color: {COLORS['silver']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 8px 12px;
        font-family: {TYPOGRAPHY['mono_family']};
        font-size: {TYPOGRAPHY['button']}px;
    }}
    QPushButton:hover {{
        color: {COLORS['bone']};
        border-color: {COLORS['ash']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['carbon']};
        color: {COLORS['fog']};
        border-color: {COLORS['slate']};
    }}
    QPushButton#action_btn, QPushButton[variant="primary"] {{
        background-color: {COLORS['teal']};
        color: {COLORS['accent']};
        border: 1px solid {COLORS['teal']};
    }}
    QPushButton#action_btn:hover, QPushButton[variant="primary"]:hover {{
        background-color: {COLORS['teal_hover']};
        border-color: {COLORS['teal_hover']};
    }}
    QPushButton#action_btn[variant="success"] {{
        background-color: {COLORS['teal']};
        color: {COLORS['accent']};
        border-color: {COLORS['accent']};
    }}
    QPushButton#action_btn[variant="danger"] {{
        background-color: {COLORS['carbon']};
        color: {COLORS['error']};
        border-color: {COLORS['error']};
    }}
    QPushButton#action_btn[variant="subtle"], QPushButton#action_btn:disabled {{
        background-color: {COLORS['graphite']};
        color: {COLORS['fog']};
        border-color: {COLORS['slate']};
    }}
    QPushButton[variant="success"] {{
        background-color: {COLORS['teal']};
        color: {COLORS['accent']};
        border-color: {COLORS['accent']};
    }}
    QPushButton[variant="danger"] {{
        background-color: {COLORS['carbon']};
        color: {COLORS['error']};
        border-color: {COLORS['error']};
    }}
    QPushButton[variant="ghost"] {{
        background-color: {COLORS['carbon']};
        color: {COLORS['ash']};
        border-color: {COLORS['ash']};
    }}
    QPushButton[variant="subtle"] {{
        background-color: {COLORS['graphite']};
        color: {COLORS['silver']};
        border-color: {COLORS['slate']};
    }}
    QPushButton#menu_toggle_btn {{
        background-color: transparent;
        color: {COLORS['ash']};
        font-size: 16px;
        border: 1px solid {COLORS['slate']};
        padding: 0px;
    }}
    QPushButton#menu_toggle_btn:hover {{
        background-color: {COLORS['graphite']};
        color: {COLORS['bone']};
    }}
    QPushButton#nav_btn {{
        background-color: transparent;
        color: {COLORS['ash']};
        text-align: left;
        padding-left: 12px;
        font-size: 12px;
        font-family: {TYPOGRAPHY['mono_family']};
        border: 1px solid transparent;
        letter-spacing: 1px;
    }}
    QPushButton#nav_btn:hover {{
        background-color: {COLORS['carbon']};
        color: {COLORS['bone']};
        border-color: {COLORS['slate']};
    }}
    QPushButton#nav_btn:checked {{
        background-color: {COLORS['carbon']};
        color: {COLORS['accent']};
        border: 1px solid {COLORS['slate']};
        border-left: 2px solid {COLORS['accent']};
    }}

    QCheckBox {{
        font-size: 13px;
        color: {COLORS['silver']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['teal']};
        border-color: {COLORS['accent']};
    }}

    QLineEdit, QComboBox {{
        background-color: {COLORS['carbon']};
        border: 1px solid {COLORS['slate']};
        border-radius: {RADIUS['sm']}px;
        padding: 8px;
        color: {COLORS['bone']};
    }}
    QLineEdit[role="loginInput"] {{
        background-color: {COLORS['void']};
        padding: 11px;
        font-size: 14px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {COLORS['accent']};
    }}
    QLineEdit:read-only {{
        color: {COLORS['steel']};
        background-color: {COLORS['carbon']};
    }}
    QComboBox::drop-down {{
        border-left: 1px solid {COLORS['slate']};
        width: 22px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['carbon']};
        color: {COLORS['silver']};
        border: 1px solid {COLORS['slate']};
        selection-background-color: {COLORS['teal']};
        selection-color: {COLORS['accent']};
    }}

    QSlider::groove:horizontal {{
        height: 4px;
        background: {COLORS['slate']};
        border: none;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        border: 1px solid {COLORS['teal']};
        width: 12px;
        margin: -5px 0;
        border-radius: {RADIUS['sm']}px;
    }}
    QSlider::sub-page:horizontal {{
        background: {COLORS['teal']};
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    QStackedWidget#pages {{
        background-color: {COLORS['void']};
        border: none;
    }}
    QScrollBar:vertical {{
        background: {COLORS['void']};
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['slate']};
        min-height: 30px;
        border-radius: {RADIUS['sm']}px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: none;
        border: none;
    }}
    QListWidget, QTableWidget {{
        background-color: {COLORS['carbon']};
        color: {COLORS['silver']};
        border: 1px solid {COLORS['slate']};
        gridline-color: {COLORS['slate']};
        selection-background-color: {COLORS['teal']};
        selection-color: {COLORS['accent']};
    }}
"""

def refresh_style(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

def set_style_state(widget, **properties):
    for name, value in properties.items():
        widget.setProperty(name, value)
    refresh_style(widget)

def create_nav_button(text):
    button = QPushButton(text)
    button.setObjectName("nav_btn")
    button.setCheckable(True)
    button.setMinimumHeight(38)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button

def create_section_title(text):
    label = QLabel(text.upper())
    label.setObjectName("section_title")
    return label

def create_card_frame():
    frame = QFrame()
    frame.setObjectName("card_frame")
    return frame

def create_status_badge(text):
    badge = QLabel(text.upper())
    badge.setObjectName("status_badge")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return badge

def create_action_button(text, variant="subtle", width=None, height=38):
    button = QPushButton(text)
    button.setMinimumHeight(height)
    if width:
        button.setFixedWidth(width)
    if variant in ("primary", "success"):
        button.setObjectName("action_btn")
    set_style_state(button, variant=variant)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button

def create_info_card(title, value, context="", status="info"):
    card = QFrame()
    card.setObjectName("info_card")
    card.setProperty("status", status)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(8)

    title_label = QLabel(title.upper())
    title_label.setObjectName("card_title")
    value_label = QLabel(value)
    value_label.setObjectName("card_value")
    layout.addWidget(title_label)
    layout.addWidget(value_label)

    if context:
        context_label = QLabel(context)
        context_label.setObjectName("card_context")
        context_label.setWordWrap(True)
        layout.addWidget(context_label)

    layout.addStretch()
    return card

def create_form_row(label_text, default_value, readonly=True):
    row = QFrame()
    row.setObjectName("form_row")
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(14, 10, 14, 10)
    row_layout.setSpacing(14)

    label = QLabel(label_text)
    label.setObjectName("form_label")
    label.setFixedWidth(170)

    field = QLineEdit(default_value)
    field.setReadOnly(readonly)
    field.setMinimumHeight(36)
    field.setStyleSheet(COMPONENT_STYLES["profile_readonly"] if readonly else COMPONENT_STYLES["profile_editable"])

    row_layout.addWidget(label)
    row_layout.addWidget(field)
    return row, field

def create_plan_card(title, price, badge_text, features, status="default"):
    card = QFrame()
    card.setObjectName("plan_card")
    card.setProperty("status", status)
    card.setMinimumHeight(360)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(22, 22, 22, 22)
    layout.setSpacing(12)

    head = QHBoxLayout()
    title_label = QLabel(title)
    title_label.setObjectName("plan_title")
    if status == "active":
        title_label.setProperty("status", "premium")
    badge = create_status_badge(badge_text)
    head.addWidget(title_label)
    head.addStretch()
    head.addWidget(badge)

    price_label = QLabel(price)
    price_label.setObjectName("plan_price")

    layout.addLayout(head)
    layout.addWidget(price_label)

    for feature in features:
        feature_label = QLabel(feature)
        feature_label.setObjectName("plan_feature")
        feature_label.setWordWrap(True)
        layout.addWidget(feature_label)

    layout.addStretch()
    return card, layout

def create_payment_card_widget(card, on_preferred, on_update, on_delete):
    card_box = QFrame()
    card_box.setObjectName("payment_card")
    card_box.setProperty("preferred", "true" if card["is_preferred"] else "false")
    cb_layout = QHBoxLayout(card_box)
    cb_layout.setContentsMargins(16, 14, 16, 14)
    cb_layout.setSpacing(14)

    card_icon = QLabel("CARD")
    card_icon.setObjectName("card_icon")

    last_4 = card["number"][-4:] if len(card["number"]) >= 4 else "0000"
    brand = "VISA" if card["number"].startswith("4") else "MASTERCARD" if card["number"].startswith("5") else "KART"

    info_layout = QVBoxLayout()
    info_layout.setSpacing(4)
    brand_line = QLabel(f"{brand} / {'VARSAYILAN' if card['is_preferred'] else 'KAYITLI'}")
    brand_line.setObjectName("payment_brand")
    number_line = QLabel(f"**** **** **** {last_4}")
    number_line.setObjectName("payment_number")
    meta_line = QLabel(f"Son kullanma: {card['exp']}")
    meta_line.setObjectName("payment_meta")
    holder_line = QLabel(f"Kart sahibi: {card['name']}")
    holder_line.setObjectName("payment_holder")

    info_layout.addWidget(brand_line)
    info_layout.addWidget(number_line)
    info_layout.addWidget(meta_line)
    info_layout.addWidget(holder_line)

    cb_layout.addWidget(card_icon)
    cb_layout.addLayout(info_layout)
    cb_layout.addStretch()

    if not card["is_preferred"]:
        pref_btn = create_action_button("Varsayılan Yap", "success", 132, 34)
        pref_btn.clicked.connect(on_preferred)
        cb_layout.addWidget(pref_btn)

    update_btn = create_action_button("Güncelle", "subtle", 96, 34)
    update_btn.clicked.connect(on_update)
    cb_layout.addWidget(update_btn)

    delete_btn = create_action_button("Sil", "danger", 70, 34)
    delete_btn.clicked.connect(on_delete)
    cb_layout.addWidget(delete_btn)

    return card_box

def create_page_header(title, context=""):
    header = QFrame()
    header.setObjectName("page_header")
    layout = QVBoxLayout(header)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    title_label = QLabel(title)
    title_label.setObjectName("page_title")
    context_label = QLabel(context.upper())
    context_label.setObjectName("page_context")

    layout.addWidget(title_label)
    if context:
        layout.addWidget(context_label)
    return header, title_label, context_label

class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("face_thumbnail")
        self.setProperty("selected", "false")

    def mousePressEvent(self, event):
        self.clicked.emit(self.path)

class FaceSelectionDialog(QDialog):
    def __init__(self, dataset_folder, is_premium, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Referans Yüz Seç")
        self.setFixedSize(760, 560)
        self.selected_path = None
        self.face_items = {}
        self.setStyleSheet(GLOBAL_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = QLabel("Kullanmak İstediğiniz Karakteri Seçin")
        title.setObjectName("dialog_title")
        title.setText("Referans Yuz Secimi")
        layout.addWidget(title)
        context = QLabel("DATASET / KAYNAK YUZ HAVUZU")
        context.setObjectName("page_context")
        context.setContentsMargins(0, 0, 0, 0)
        helper = QLabel("Canli degisimde kullanilacak referans yuzu secin. Standart hesaplarda liste ilk 10 kayitla sinirlidir.")
        helper.setObjectName("screen_caption")
        helper.setWordWrap(True)
        layout.addWidget(context)
        layout.addWidget(helper)
        layout.addWidget(create_status_badge("PREMIUM" if is_premium else "STANDARD LIMIT"))

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(12)
        
        row, col = 0, 0
        found_faces = False
        if os.path.exists(dataset_folder):
            all_files = [f for f in os.listdir(dataset_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            
            if not is_premium:
                all_files = all_files[:10]
                
            for file in all_files:
                found_faces = True
                filepath = os.path.join(dataset_folder, file)
                name = os.path.splitext(file)[0].replace('_', ' ').title()
                
                item_frame = QFrame()
                item_frame.setObjectName("face_picker_item")
                item_frame.setProperty("selected", "false")
                item_layout = QVBoxLayout(item_frame)
                item_layout.setContentsMargins(10, 10, 10, 10)
                item_layout.setSpacing(8)
                item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label = ClickableLabel(filepath)
                pixmap = QPixmap(filepath)
                pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pixmap)
                img_label.setFixedSize(112, 112)
                img_label.setScaledContents(True)
                img_label.clicked.connect(self.face_selected)
                
                text_label = QLabel(name)
                text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                text_label.setObjectName("face_name_label")
                text_label.setWordWrap(True)
                text_label.setFixedWidth(128)
                
                item_layout.addWidget(img_label)
                item_layout.addWidget(text_label)
                self.grid_layout.addWidget(item_frame, row, col)
                self.face_items[filepath] = (item_frame, img_label)
                
                col += 1
                if col == 4:
                    col = 0
                    row += 1
        if not found_faces:
            empty_text = "Dataset klasoru bulunamadi veya desteklenen gorsel yok." if not os.path.exists(dataset_folder) else "Dataset icinde secilebilir referans yuz bulunamadi."
            empty = QLabel(empty_text)
            empty.setObjectName("face_empty_state")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setWordWrap(True)
            self.grid_layout.addWidget(empty, 0, 0)
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

        self.selection_status = QLabel("Henuz bir referans yuz secilmedi.")
        self.selection_status.setObjectName("status_label")
        self.selection_status.setProperty("status", "info")
        layout.addWidget(self.selection_status)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel_btn = create_action_button("Iptal", "subtle", 104, 38)
        cancel_btn.clicked.connect(self.reject)
        self.confirm_btn = create_action_button("Secimi Kullan", "primary", 136, 38)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.accept)
        actions.addWidget(cancel_btn)
        actions.addWidget(self.confirm_btn)
        layout.addLayout(actions)

    def face_selected(self, path):
        self.selected_path = path
        for item_frame, img_label in self.face_items.values():
            set_style_state(item_frame, selected="false")
            set_style_state(img_label, selected="false")
        if path in self.face_items:
            item_frame, img_label = self.face_items[path]
            set_style_state(item_frame, selected="true")
            set_style_state(img_label, selected="true")
        name = os.path.splitext(os.path.basename(path))[0].replace('_', ' ').title()
        self.selection_status.setText(f"Secili referans: {name}")
        set_style_state(self.selection_status, status="success")
        self.confirm_btn.setEnabled(True)
        self.accept()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PersonaShift - Sistem Girişi")
        self.setFixedSize(460, 520)
        self.setStyleSheet(GLOBAL_STYLE)
        self.is_authenticated = False
        self.is_premium = False
        self.full_name = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(0)
        layout.addStretch()

        panel = create_card_frame()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 28, 28, 28)
        panel_layout.setSpacing(14)

        kicker = QLabel("SECURE ACCESS NODE")
        kicker.setObjectName("login_kicker")
        panel_layout.addWidget(kicker)

        title = QLabel("PersonaShift Hub")
        title.setObjectName("login_title")
        panel_layout.addWidget(title)

        helper = QLabel("Kurumsal yapay zeka oturumunuza devam etmek icin hesap bilgilerinizi girin.")
        helper.setObjectName("login_helper")
        helper.setWordWrap(True)
        panel_layout.addWidget(helper)

        panel_layout.addSpacing(10)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("E-posta adresi")
        self.user_input.setMinimumHeight(42)
        self.user_input.setProperty("role", "loginInput")
        panel_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Şifre")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMinimumHeight(42)
        self.pass_input.setProperty("role", "loginInput")
        panel_layout.addWidget(self.pass_input)

        panel_layout.addSpacing(6)

        self.login_btn = QPushButton("Giriş Yap")
        self.login_btn.setObjectName("action_btn")
        self.login_btn.clicked.connect(self.authenticate)
        self.login_btn.setMinimumHeight(42)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(lambda: set_style_state(self.error_label, visibleState="error"))
        panel_layout.addWidget(self.login_btn)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setProperty("visibleState", "empty")
        self.error_label.setMinimumHeight(34)
        panel_layout.addWidget(self.error_label)

        footer = create_status_badge("AUTH READY")
        panel_layout.addWidget(footer)

        layout.addWidget(panel)
        layout.addStretch()

    def authenticate(self):
        email = self.user_input.text()
        password = self.pass_input.text()

        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS")
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT full_name, is_premium FROM users WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()

            if user:
                self.full_name = user[0]
                self.is_premium = user[1]
                self.is_authenticated = True
                self.accept()
            else:
                self.error_label.setText("Hatalı e-posta veya şifre.")

            cursor.close()
            conn.close()
        except Exception as e:
            self.error_label.setText("Veritabanı bağlantı hatası!")
            print(e)

class MainWindow(QMainWindow):
    def __init__(self, full_name="Misafir", is_premium=False):
        super().__init__()
        self.setWindowTitle("PersonaShift - Yönetim Paneli")
        self.setFixedSize(1280, 680)
        self.setStyleSheet(GLOBAL_STYLE)

        self.full_name = full_name
        self.user_is_premium = is_premium 

        self.payment_cards = [
            {"id": 1, "number": "4321000000004321", "exp": "12/28", "cvv": "123", "name": "Ömer Utku Aktemur", "is_preferred": True},
            {"id": 2, "number": "5555000000009876", "exp": "05/27", "cvv": "456", "name": "Ömer Utku Aktemur", "is_preferred": False}
        ]
        self.editing_card_id = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(0) 
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(12, 12, 12, 12)
        self.sidebar_layout.setSpacing(12)

        sidebar_header = QFrame()
        sidebar_header.setObjectName("sidebar_header")
        sidebar_header_layout = QVBoxLayout(sidebar_header)
        sidebar_header_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_header_layout.setSpacing(3)

        brand_mark = QLabel("PS")
        brand_mark.setObjectName("brand_mark")
        brand_name = QLabel("PERSONASHIFT HUB")
        brand_name.setObjectName("brand_name")
        brand_caption = QLabel("AI VIDEO CONTROL")
        brand_caption.setObjectName("brand_caption")
        sidebar_header_layout.addWidget(brand_mark)
        sidebar_header_layout.addWidget(brand_name)
        sidebar_header_layout.addWidget(brand_caption)
        self.sidebar_layout.addWidget(sidebar_header)

        self.sidebar_layout.addWidget(create_section_title("Navigation"))

        self.menu_buttons = []
        menus = [
            ("Ana Sayfa", 0),
            ("Canlı Değişim", 1),
            ("Hesap Ayarları", 2),
            ("Ödeme Yöntemleri", 3),
            ("Abonelik Detayları", 4),
            ("Teknik Destek", 5)
        ]

        for text, index in menus:
            btn = create_nav_button(text)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            self.sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        self.menu_buttons[0].setChecked(True)
        self.sidebar_layout.addStretch()

        sidebar_footer = QFrame()
        sidebar_footer.setObjectName("sidebar_footer")
        sidebar_footer_layout = QVBoxLayout(sidebar_footer)
        sidebar_footer_layout.setContentsMargins(14, 12, 14, 12)
        sidebar_footer_layout.setSpacing(6)

        self.user_name_label = QLabel(self.full_name)
        self.user_name_label.setObjectName("user_name_label")
        self.user_status_label = create_status_badge("Premium Uye" if self.user_is_premium else "Standart Uye")

        self.user_info_label = QLabel(f"{self.full_name}\nPremium Üye" if self.user_is_premium else f"{self.full_name}\nStandart Üye")
        self.user_info_label.setObjectName("muted_label")

        sidebar_footer_layout.addWidget(self.user_name_label)
        sidebar_footer_layout.addWidget(self.user_status_label)
        sidebar_footer_layout.addWidget(self.user_info_label)
        self.sidebar_layout.addWidget(sidebar_footer)

        self.main_layout.addWidget(self.sidebar)

        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(350)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.top_bar = QFrame()
        self.top_bar.setObjectName("top_bar")
        self.top_bar.setFixedHeight(68)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(20, 0, 20, 0)
        self.top_bar_layout.setSpacing(12)

        self.menu_toggle_btn = QPushButton("☰")
        self.menu_toggle_btn.setObjectName("menu_toggle_btn")
        self.menu_toggle_btn.setFixedSize(36, 36)
        self.menu_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.top_bar_layout.addWidget(self.menu_toggle_btn)

        page_header, self.page_title_label, self.page_context_label = create_page_header("Ana Sayfa / Dashboard", "CONTROL PANEL")
        self.top_bar_layout.addWidget(page_header)
        self.top_bar_layout.addStretch()
        self.account_badge = create_status_badge("Premium" if self.user_is_premium else "Standard")
        self.top_bar_layout.addWidget(self.account_badge)

        self.content_layout.addWidget(self.top_bar)

        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        self.create_pages()
        self.content_layout.addWidget(self.pages)

        self.main_layout.addWidget(self.content_container)

        self.master_opacity = QGraphicsOpacityEffect(self.pages)
        self.pages.setGraphicsEffect(self.master_opacity)
        
        self.master_fade = QPropertyAnimation(self.master_opacity, b"opacity")
        self.master_fade.setDuration(250)
        self.master_fade.setStartValue(0.0)
        self.master_fade.setEndValue(1.0)
        self.master_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.is_camera_running = False

        self.apply_account_restrictions()

    def toggle_sidebar(self):
        width = self.sidebar.width()
        if width == 0:
            self.sidebar_animation.setStartValue(0)
            self.sidebar_animation.setEndValue(256)
        else:
            self.sidebar_animation.setStartValue(width)
            self.sidebar_animation.setEndValue(0)
        self.sidebar_animation.start()

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        titles = ["Ana Sayfa / Dashboard", "Canlı Yüz Değiştirme Paneli", "Hesap Yönetimi", "Ödeme Altyapısı", "Abonelik Durumu", "Destek Merkezi"]
        self.page_title_label.setText(titles[index])
        
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

        self.master_fade.start()

    def add_scrollable_page(self, page_widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(page_widget)
        self.pages.addWidget(scroll)

    def create_pages(self):
        # --- SAYFA 0: ANA SAYFA ---
        p0 = QWidget()
        l0 = QVBoxLayout(p0)
        l0.setContentsMargins(40, 34, 40, 40)
        l0.setSpacing(18)

        dashboard_header = QHBoxLayout()
        header_copy = QVBoxLayout()
        welcome = QLabel(f"Tekrar Hoş Geldiniz, {self.full_name}")
        welcome.setObjectName("screen_heading")
        desc = QLabel("Hesap, abonelik ve canlı yüz değişim durumunu tek panelden izleyin.")
        desc.setObjectName("screen_caption")
        header_copy.addWidget(welcome)
        header_copy.addWidget(desc)
        dashboard_header.addLayout(header_copy)
        dashboard_header.addStretch()
        dashboard_header.addWidget(create_status_badge("CONTROL READY"))
        l0.addLayout(dashboard_header)

        status_grid = QGridLayout()
        status_grid.setSpacing(14)
        plan_value = "Premium aktif" if self.user_is_premium else "Standart hesap"
        plan_context = "HD netleştirici ve kayıt özellikleri açık." if self.user_is_premium else "Premium özellikler kamera panelinde kilitli."
        status_grid.addWidget(create_info_card("Kullanıcı Durumu", self.full_name, "Oturum doğrulandı ve profil yönetimi hazır.", "success"), 0, 0)
        status_grid.addWidget(create_info_card("Abonelik Durumu", plan_value, plan_context, "success" if self.user_is_premium else "info"), 0, 1)
        status_grid.addWidget(create_info_card("Kamera / İşlem", "Beklemede", "Canlı değişim motoru başlatılmadı. Kamera panelinden akışı açabilirsiniz.", "premium"), 0, 2)
        status_grid.addWidget(create_info_card("Kayıtlı Kartlar", f"{len(self.payment_cards)} yöntem", "Varsayılan kart ve faturalama bilgileri ödeme sayfasında yönetilir.", "info"), 1, 0)
        status_grid.addWidget(create_info_card("Referans Yüz Havuzu", "Dataset hazır", "Standart hesaplarda seçim listesi ilk 10 kayıtla sınırlanır.", "info"), 1, 1)
        status_grid.addWidget(create_info_card("Sistem Durumu", "Motor hazır", "Video iş parçacığı bağlantısı kurulu; canlı ekran beklemede.", "success"), 1, 2)
        l0.addLayout(status_grid)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(14)

        quick_actions = create_card_frame()
        qa_layout = QVBoxLayout(quick_actions)
        qa_layout.setContentsMargins(18, 18, 18, 18)
        qa_layout.setSpacing(12)
        qa_title = QLabel("HIZLI AKSİYONLAR")
        qa_title.setObjectName("card_title")
        qa_context = QLabel("Sık kullanılan işlemlere doğrudan geçin.")
        qa_context.setObjectName("card_context")

        btn_jump_cam = create_action_button("Canlı Değişimi Aç", "primary", height=40)
        btn_jump_cam.clicked.connect(lambda: self.switch_page(1))
        btn_jump_sub = create_action_button("Aboneliği İncele", "ghost", height=38)
        btn_jump_sub.clicked.connect(lambda: self.switch_page(4))
        btn_jump_payments = create_action_button("Ödeme Yöntemleri", "subtle", height=38)
        btn_jump_payments.clicked.connect(lambda: self.switch_page(3))

        qa_layout.addWidget(qa_title)
        qa_layout.addWidget(qa_context)
        qa_layout.addWidget(btn_jump_cam)
        qa_layout.addWidget(btn_jump_sub)
        qa_layout.addWidget(btn_jump_payments)
        qa_layout.addStretch()
        bottom_layout.addWidget(quick_actions, stretch=1)

        operations = create_card_frame()
        op_layout = QVBoxLayout(operations)
        op_layout.setContentsMargins(18, 18, 18, 18)
        op_layout.setSpacing(10)
        op_title = QLabel("OPERASYON ÖZETİ")
        op_title.setObjectName("card_title")
        op_layout.addWidget(op_title)
        for line in [
            "• v1.2 güncellemesi yüklü ve arayüz teması aktif.",
            "• OBS Virtual Camera köprüsü stabil durumda.",
            "• Profil ve ödeme değişiklikleri yerel oturumda hazır tutuluyor.",
            "• Teknik destek merkezi hesap bağlamıyla kullanılabilir."
        ]:
            item = QLabel(line)
            item.setObjectName("card_context")
            item.setWordWrap(True)
            op_layout.addWidget(item)
        op_layout.addStretch()
        bottom_layout.addWidget(operations, stretch=1)

        l0.addLayout(bottom_layout)
        l0.addStretch()
        self.add_scrollable_page(p0)

        # --- SAYFA 1: KAMERA VE YAPAY ZEKA PANELİ ---
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(40, 34, 40, 40)
        l1.setSpacing(16)

        cam_header = QHBoxLayout()
        cam_title_block = QVBoxLayout()
        cam_title = QLabel("Canli Degisim Operasyon Ekrani")
        cam_title.setObjectName("screen_title")
        cam_desc = QLabel("Kamera akisini, referans yuz secimini ve isleme parametrelerini tek konsoldan yonetin.")
        cam_desc.setObjectName("screen_caption")
        cam_title_block.addWidget(cam_title)
        cam_title_block.addWidget(cam_desc)
        cam_header.addLayout(cam_title_block)
        cam_header.addStretch()
        l1.addLayout(cam_header)

        camera_body = QHBoxLayout()
        camera_body.setSpacing(16)
        l1.addLayout(camera_body)
        
        self.camera_preview_panel = QFrame()
        self.camera_preview_panel.setObjectName("camera_preview_panel")
        self.camera_preview_panel.setProperty("state", "idle")
        preview_layout = QVBoxLayout(self.camera_preview_panel)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(12)

        self.image_label = QLabel()
        self.image_label.setFixedSize(768, 432)
        self.image_label.setObjectName("camera_viewport")
        self.image_label.setProperty("state", "idle")
        self.image_label.setText("CAMERA OFFLINE\nStart camera to initialize live preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        camera_body.addWidget(self.camera_preview_panel, stretch=3)

        cam_ctrl = QFrame()
        cam_ctrl.setObjectName("camera_controls_panel")
        cam_ctrl_lay = QVBoxLayout(cam_ctrl)
        cam_ctrl_lay.setContentsMargins(16, 16, 16, 16)
        cam_ctrl_lay.setSpacing(12)
        
        self.camera_btn = QPushButton("Kamerayı Başlat")
        self.camera_btn.setObjectName("action_btn")
        self.camera_btn.setProperty("variant", "primary")
        self.camera_btn.setMinimumHeight(38)
        self.camera_btn.clicked.connect(self.toggle_camera)
        cam_ctrl_lay.addWidget(self.camera_btn)

        self.select_face_btn = QPushButton("Referans Yüz Seç")
        self.select_face_btn.setProperty("variant", "ghost")
        self.select_face_btn.setMinimumHeight(38)
        self.select_face_btn.clicked.connect(self.open_face_selection)
        cam_ctrl_lay.addWidget(self.select_face_btn)

        selected_face_title = QLabel("SECILI REFERANS")
        selected_face_title.setObjectName("control_label")
        self.selected_face_label = QLabel("Referans yuz secilmedi")
        self.selected_face_label.setObjectName("selected_face_value")
        self.selected_face_label.setWordWrap(True)
        cam_ctrl_lay.addWidget(selected_face_title)
        cam_ctrl_lay.addWidget(self.selected_face_label)

        self.capture_btn = QPushButton("Anlık Fotoğraf Çek")
        self.capture_btn.setObjectName("action_btn")
        self.capture_btn.setProperty("variant", "success")
        self.capture_btn.setMinimumHeight(38)
        self.capture_btn.clicked.connect(self.capture_photo)
        cam_ctrl_lay.addWidget(self.capture_btn)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        self.status_label.setProperty("status", "info")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        cam_ctrl_lay.addWidget(self.status_label)

        self.restriction_panel = QFrame()
        self.restriction_panel.setObjectName("restriction_panel")
        self.restriction_panel.setProperty("status", "unlocked" if self.user_is_premium else "locked")
        restriction_layout = QVBoxLayout(self.restriction_panel)
        restriction_layout.setContentsMargins(12, 10, 12, 10)
        restriction_layout.setSpacing(4)
        restriction_title = QLabel("PLAN KISITLARI")
        restriction_title.setObjectName("control_label")
        self.restriction_text = QLabel("Premium mod aktif: HD, tek yuz modu ve kayit aksiyonlari acik." if self.user_is_premium else "Standart mod: HD, tek yuz modu, fotograf kaydi ve cozunurluk ayari kilitli.")
        self.restriction_text.setObjectName("restriction_text")
        self.restriction_text.setWordWrap(True)
        restriction_layout.addWidget(restriction_title)
        restriction_layout.addWidget(self.restriction_text)
        cam_ctrl_lay.addWidget(self.restriction_panel)

        grp = QGroupBox("Performans ve Donanım")
        grplay = QVBoxLayout(grp)
        
        self.res_combo = QComboBox()
        self.res_combo.addItems(["1920x1080 (FHD)", "1280x720 (HD)", "640x480 (SD)"])
        self.res_combo.setCurrentIndex(1)
        self.res_combo.currentIndexChanged.connect(self.change_resolution)
        
        self.fps_checkbox = QCheckBox("Canlı FPS Göster")
        self.fps_checkbox.setChecked(True)
        self.hd_checkbox = QCheckBox("HD Yüz Netleştirici")
        self.hd_checkbox.stateChanged.connect(self.toggle_hd_mode)
        self.single_face_checkbox = QCheckBox("Sadece Ana Yüzü Değiştir")
        self.single_face_checkbox.stateChanged.connect(self.toggle_single_face)
        
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(-100, 100)
        self.bright_slider.setValue(0)
        self.bright_slider.valueChanged.connect(self.update_params)
        
        self.cont_slider = QSlider(Qt.Orientation.Horizontal)
        self.cont_slider.setRange(50, 300)
        self.cont_slider.setValue(100)
        self.cont_slider.valueChanged.connect(self.update_params)
        
        grplay.addWidget(QLabel("Kamera Çözünürlüğü:"))
        grplay.addWidget(self.res_combo)
        grplay.addWidget(self.fps_checkbox)
        grplay.addWidget(self.hd_checkbox)
        grplay.addWidget(self.single_face_checkbox)
        grplay.addWidget(QLabel("Parlaklık"))
        grplay.addWidget(self.bright_slider)
        grplay.addWidget(QLabel("Kontrast"))
        grplay.addWidget(self.cont_slider)
        
        cam_ctrl_lay.addWidget(grp)
        cam_ctrl_lay.addStretch()
        
        camera_body.addWidget(cam_ctrl, stretch=1)
        l1.addStretch()
        self.add_scrollable_page(p1)

        # --- SAYFA 2: HESAP AYARLARI ---
        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(40, 34, 40, 40)
        l2.setSpacing(16)

        p2_header = QHBoxLayout()
        title_block = QVBoxLayout()
        p2_title = QLabel("Profil Detayları")
        p2_title.setObjectName("screen_title")
        p2_desc = QLabel("Görüntüleme modunda alanlar kilitlidir. Düzenle ile profil bilgileri geçici olarak açılır.")
        p2_desc.setObjectName("screen_caption")
        title_block.addWidget(p2_title)
        title_block.addWidget(p2_desc)

        self.edit_profile_btn = create_action_button("Düzenle", "primary", 108, 36)
        self.edit_profile_btn.clicked.connect(self.toggle_profile_edit)

        p2_header.addLayout(title_block)
        p2_header.addStretch()
        p2_header.addWidget(self.edit_profile_btn)
        l2.addLayout(p2_header)

        account_summary = QHBoxLayout()
        account_summary.setSpacing(14)
        account_summary.addWidget(create_info_card("Oturum", "Doğrulandı", "LoginDialog.authenticate() ile gelen kullanıcı bağlamı aktif.", "success"))
        account_summary.addWidget(create_info_card("Plan", "Premium" if self.user_is_premium else "Standart", "Kamera ve abonelik kısıtları mevcut plana göre uygulanır.", "premium" if self.user_is_premium else "info"))
        account_summary.addWidget(create_info_card("Profil Modu", "Salt okunur", "Kaydet sonrası alanlar tekrar kilitlenir.", "info"))
        l2.addLayout(account_summary)

        form_panel = QFrame()
        form_panel.setObjectName("form_panel")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(10)

        form_title = QLabel("KİMLİK VE İLETİŞİM")
        form_title.setObjectName("card_title")
        form_layout.addWidget(form_title)

        self.profile_fields = []

        for label_text, default_value in [
            ("İsim", "Ömer Utku"),
            ("Soyisim", "Aktemur"),
            ("E-Posta Adresi", "utku@personashift.com"),
            ("Doğum Tarihi", "28.07.2003"),
            ("Cinsiyet", "Erkek"),
            ("Konum (Şehir/Ülke)", "İstanbul, Türkiye"),
            ("Telefon Numarası", "+90 555 000 0000"),
        ]:
            row, field = create_form_row(label_text, default_value)
            self.profile_fields.append(field)
            form_layout.addWidget(row)

        hint = QLabel("Kaydet düğmesi mevcut davranışı korur: düzenleme modunu kapatır ve alanları yeniden salt okunur yapar.")
        hint.setObjectName("field_hint")
        hint.setWordWrap(True)
        form_layout.addWidget(hint)

        l2.addWidget(form_panel)
        l2.addStretch()
        self.add_scrollable_page(p2)

        # --- SAYFA 3: ÖDEME YÖNTEMLERİ ---
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(0, 0, 0, 0)

        self.p3_stack = QStackedWidget()

        self.p3_list_widget = QWidget()
        p3_list_layout = QVBoxLayout(self.p3_list_widget)
        p3_list_layout.setContentsMargins(40, 34, 40, 40)
        p3_list_layout.setSpacing(16)

        p3_header_list = QHBoxLayout()
        title_block = QVBoxLayout()
        p3_title_list = QLabel("Ödeme Yöntemleri")
        p3_title_list.setObjectName("screen_title")
        p3_desc = QLabel("Varsayılan kartınızı, kayıtlı ödeme yöntemlerini ve kart güncellemelerini buradan yönetin.")
        p3_desc.setObjectName("screen_caption")
        title_block.addWidget(p3_title_list)
        title_block.addWidget(p3_desc)

        self.add_card_btn = create_action_button("Yeni Kart Ekle", "primary", 140, 36)
        self.add_card_btn.clicked.connect(lambda: self.open_inline_card_form(None))

        p3_header_list.addLayout(title_block)
        p3_header_list.addStretch()
        p3_header_list.addWidget(self.add_card_btn)
        p3_list_layout.addLayout(p3_header_list)

        payment_summary = QHBoxLayout()
        payment_summary.setSpacing(14)
        self.payment_count_card = create_info_card("Kart Sayısı", str(len(self.payment_cards)), "Kayıtlı yöntemler varsayılan kart önce listelenir.", "info")
        self.payment_count_value = self.payment_count_card.findChild(QLabel, "card_value")
        self.payment_default_card = create_info_card("Varsayılan", "Aktif" if any(c["is_preferred"] for c in self.payment_cards) else "Yok", "Ödemeler tercih edilen kart üzerinden işlenir.", "success" if any(c["is_preferred"] for c in self.payment_cards) else "warning")
        self.payment_default_value = self.payment_default_card.findChild(QLabel, "card_value")
        payment_summary.addWidget(self.payment_count_card)
        payment_summary.addWidget(self.payment_default_card)
        payment_summary.addWidget(create_info_card("Güvenlik", "Yerel maskeleme", "Liste görünümünde yalnızca son dört hane gösterilir.", "premium"))
        p3_list_layout.addLayout(payment_summary)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)

        p3_list_layout.addWidget(self.cards_container)
        p3_list_layout.addStretch()
        self.p3_stack.addWidget(self.p3_list_widget)

        self.p3_form_widget = QWidget()
        p3_form_layout = QVBoxLayout(self.p3_form_widget)
        p3_form_layout.setContentsMargins(40, 34, 40, 40)
        p3_form_layout.setSpacing(16)

        self.form_title = QLabel("Kart Ekle/Güncelle")
        self.form_title.setObjectName("screen_title")
        form_desc = QLabel("Kart bilgilerini girin. Kayıt sonrası liste görünümüne dönülür ve kartlar yeniden çizilir.")
        form_desc.setObjectName("screen_caption")
        p3_form_layout.addWidget(self.form_title)
        p3_form_layout.addWidget(form_desc)

        form_box = QFrame()
        form_box.setObjectName("form_panel")
        fb_layout = QVBoxLayout(form_box)
        fb_layout.setContentsMargins(18, 18, 18, 18)
        fb_layout.setSpacing(12)

        form_kicker = QLabel("KART BİLGİLERİ")
        form_kicker.setObjectName("card_title")
        fb_layout.addWidget(form_kicker)

        num_row, self.card_num_input = create_form_row("Tam Kart Numarası", "", False)
        self.card_num_input.setStyleSheet(COMPONENT_STYLES["form_input"])
        self.card_num_input.setPlaceholderText("0000 0000 0000 0000")
        self.card_num_input.setMaxLength(19)
        fb_layout.addWidget(num_row)

        exp_cvv_row = QHBoxLayout()
        exp_row, self.card_exp_input = create_form_row("Son Kullanma", "", False)
        self.card_exp_input.setStyleSheet(COMPONENT_STYLES["form_input"])
        self.card_exp_input.setPlaceholderText("12/28")
        self.card_exp_input.setMaxLength(5)

        cvv_row, self.card_cvv_input = create_form_row("CVV", "", False)
        self.card_cvv_input.setStyleSheet(COMPONENT_STYLES["form_input"])
        self.card_cvv_input.setPlaceholderText("123")
        self.card_cvv_input.setMaxLength(3)
        exp_cvv_row.addWidget(exp_row)
        exp_cvv_row.addWidget(cvv_row)
        fb_layout.addLayout(exp_cvv_row)

        name_row, self.card_name_input = create_form_row("Kart Üzerindeki İsim", "", False)
        self.card_name_input.setStyleSheet(COMPONENT_STYLES["form_input"])
        self.card_name_input.setPlaceholderText("Örn: Ömer Utku Aktemur")
        fb_layout.addWidget(name_row)

        p3_form_layout.addWidget(form_box)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = create_action_button("İptal Et", "danger", 120, 40)
        cancel_btn.clicked.connect(self.close_inline_card_form)

        save_btn = create_action_button("Kaydet", "primary", 120, 40)
        save_btn.clicked.connect(self.save_inline_card_form)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        p3_form_layout.addLayout(btn_layout)
        p3_form_layout.addStretch()

        self.p3_stack.addWidget(self.p3_form_widget)
        l3.addWidget(self.p3_stack)

        self.add_scrollable_page(p3)

        self.render_payment_cards()

        # --- SAYFA 4: ABONELİK DETAYLARI ---
        self.p4 = QWidget()
        self.l4 = QVBoxLayout(self.p4)
        self.l4.setContentsMargins(40, 34, 40, 40)
        self.l4.setSpacing(16)

        self.p4_header = QLabel("Abonelik Detayları")
        self.p4_header.setObjectName("screen_title")
        self.p4_desc = QLabel("Mevcut planınızı, premium farklarını ve yükseltme/iptal aksiyonlarını buradan yönetin.")
        self.p4_desc.setObjectName("screen_caption")
        self.l4.addWidget(self.p4_header)
        self.l4.addWidget(self.p4_desc)

        self.subscription_status_layout = QHBoxLayout()
        self.subscription_status_layout.setSpacing(14)
        self.l4.addLayout(self.subscription_status_layout)

        self.sub_alert_box = QFrame()
        self.sub_alert_box.setObjectName("alert_box")
        self.sub_alert_box.hide()
        self.sub_alert_layout = QHBoxLayout(self.sub_alert_box)
        self.sub_alert_layout.setContentsMargins(16, 12, 16, 12)
        
        self.sub_alert_msg = QLabel()
        self.sub_alert_msg.setObjectName("screen_caption")
        self.sub_alert_layout.addWidget(self.sub_alert_msg)
        self.sub_alert_layout.addStretch()
        
        self.sub_alert_btn_no = QPushButton("Vazgeç")
        self.sub_alert_btn_yes = QPushButton("Onayla")
        self.sub_alert_layout.addWidget(self.sub_alert_btn_no)
        self.sub_alert_layout.addWidget(self.sub_alert_btn_yes)
        
        self.l4.addWidget(self.sub_alert_box)

        self.plans_layout = QHBoxLayout()
        self.plans_layout.setSpacing(25)

        self.render_subscription_page()
        
        self.l4.addLayout(self.plans_layout)
        self.l4.addStretch()
        self.add_scrollable_page(self.p4)

        # --- SAYFA 5: TEKNİK DESTEK ---
        p5 = QWidget()
        l5 = QVBoxLayout(p5)
        l5.setContentsMargins(40, 34, 40, 40)
        l5.setSpacing(16)

        p5_header = QHBoxLayout()
        support_title_block = QVBoxLayout()
        p5_title = QLabel("Teknik Destek")
        p5_title.setObjectName("screen_title")
        p5_desc = QLabel("Kamera, abonelik ve ödeme akışları için destek talebi oluşturun veya hızlı durum bilgilerini inceleyin.")
        p5_desc.setObjectName("screen_caption")
        support_title_block.addWidget(p5_title)
        support_title_block.addWidget(p5_desc)
        p5_header.addLayout(support_title_block)
        p5_header.addStretch()
        p5_header.addWidget(create_status_badge("SUPPORT ONLINE"))
        l5.addLayout(p5_header)

        support_grid = QGridLayout()
        support_grid.setSpacing(14)

        for index, (code, title, body, status) in enumerate([
            ("CAM-01", "Kamera ve canlı değişim", "Cihaz seçimi, çözünürlük ve yüz seçimi akışlarında yaşanan sorunlar.", "success"),
            ("ACC-02", "Hesap ve profil", "Profil düzenleme, oturum ve hesap kısıtlarıyla ilgili talepler.", "info"),
            ("PAY-03", "Ödeme yöntemleri", "Kart ekleme, güncelleme, silme ve varsayılan kart seçim desteği.", "premium"),
            ("SUB-04", "Abonelik işlemleri", "Premium yükseltme, iptal onayı ve plan kapsamı hakkında destek.", "warning"),
        ]):
            tile = QFrame()
            tile.setObjectName("support_tile")
            tile.setProperty("status", status)
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(16, 14, 16, 14)
            tile_layout.setSpacing(8)
            code_label = QLabel(code)
            code_label.setObjectName("support_code")
            title_label = QLabel(title)
            title_label.setObjectName("card_value")
            body_label = QLabel(body)
            body_label.setObjectName("support_body")
            body_label.setWordWrap(True)
            tile_layout.addWidget(code_label)
            tile_layout.addWidget(title_label)
            tile_layout.addWidget(body_label)
            support_grid.addWidget(tile, index // 2, index % 2)

        l5.addLayout(support_grid)

        ticket_panel = QFrame()
        ticket_panel.setObjectName("form_panel")
        ticket_layout = QVBoxLayout(ticket_panel)
        ticket_layout.setContentsMargins(18, 18, 18, 18)
        ticket_layout.setSpacing(12)

        ticket_title = QLabel("DESTEK TALEBİ")
        ticket_title.setObjectName("card_title")
        ticket_layout.addWidget(ticket_title)

        subject_input = QLineEdit()
        subject_input.setPlaceholderText("Konu başlığı (Örn: Kamera açılmıyor)")
        subject_input.setMinimumHeight(40)

        msg_input = QLineEdit()
        msg_input.setPlaceholderText("Karşılaştığınız sorunu detaylıca açıklayın...")
        msg_input.setMinimumHeight(92)
        msg_input.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        meta_line = QLabel("Yanıt kanalı: hesap e-posta adresi / Öncelik: plana göre belirlenir")
        meta_line.setObjectName("field_hint")

        send_btn = create_action_button("Talebi Gönder", "primary", 150, 40)

        ticket_layout.addWidget(subject_input)
        ticket_layout.addWidget(msg_input)
        ticket_layout.addWidget(meta_line)
        ticket_layout.addWidget(send_btn, alignment=Qt.AlignmentFlag.AlignRight)
        l5.addWidget(ticket_panel)
        l5.addStretch()
        self.add_scrollable_page(p5)

    def render_subscription_page(self):
        while self.plans_layout.count():
            item = self.plans_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.subscription_status_layout.count():
            item = self.subscription_status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_plan = "Premium" if self.user_is_premium else "Standart"
        self.subscription_status_layout.addWidget(create_info_card("Mevcut Plan", current_plan, "Plan değişikliği kamera kısıtlarını ve destek önceliğini etkiler.", "success" if self.user_is_premium else "info"))
        self.subscription_status_layout.addWidget(create_info_card("Premium Kısıtları", "Açık" if not self.user_is_premium else "Kalktı", "Standart hesapta HD netleştirici, tek yüz modu ve fotoğraf kaydı sınırlıdır.", "warning" if not self.user_is_premium else "success"))
        self.subscription_status_layout.addWidget(create_info_card("Faturalama", "$19.99 / ay" if self.user_is_premium else "Ücretsiz", "Yükseltme ve iptal aksiyonları onay adımıyla yürütülür.", "premium"))

        std_features = [
            "Temel yüz değiştirme ve standart işleme hızı",
            "Dataset listesinde standart seçim sınırı",
            "Topluluk desteği ve temel yardım akışı",
            "HD netleştirici ve kayıt aksiyonları kapalı"
        ]
        std_box, std_lay = create_plan_card(
            "Standart Sürüm",
            "Ücretsiz",
            "Mevcut" if not self.user_is_premium else "Opsiyon",
            std_features,
            "active" if not self.user_is_premium else "default"
        )

        self.std_btn = create_action_button("Mevcut Plan" if not self.user_is_premium else "Standarta Geç", "ghost", height=40)
        self.std_btn.setEnabled(self.user_is_premium)
        
        if self.user_is_premium:
            self.std_btn.clicked.connect(self.prompt_cancel_subscription)
        
        std_lay.addWidget(self.std_btn)

        pre_features = [
            "Sınırsız yüz değiştirme ve geniş referans listesi",
            "HD netleştirici motoru ve tek yüz modu",
            "Anlık fotoğraf kaydetme aksiyonu",
            "Öncelikli teknik destek ve erken erişim özellikleri"
        ]
        pre_box, pre_lay = create_plan_card(
            "Pro / Premium",
            "$19.99 / ay",
            "Mevcut" if self.user_is_premium else "Yükselt",
            pre_features,
            "active" if self.user_is_premium else "default"
        )

        if self.user_is_premium:
            self.pre_btn = create_action_button("Aboneliği İptal Et", "danger", height=40)
            self.pre_btn.clicked.connect(self.prompt_cancel_subscription)
        else:
            self.pre_btn = create_action_button("Premium'a Geç", "primary", height=40)
            self.pre_btn.clicked.connect(self.prompt_upgrade_subscription)
        
        pre_lay.addWidget(self.pre_btn)

        self.plans_layout.addWidget(std_box)
        self.plans_layout.addWidget(pre_box)

    def prompt_cancel_subscription(self):
        set_style_state(self.sub_alert_box, status="error")
        self.sub_alert_msg.setText("Premium ayrıcalıklarınızı kaybetmek istediğinize emin misiniz?")
        
        self.sub_alert_btn_yes.setText("Evet, İptal Et")
        set_style_state(self.sub_alert_btn_yes, variant="danger")
        self.sub_alert_btn_yes.show()
        
        self.sub_alert_btn_no.setText("Vazgeç")
        set_style_state(self.sub_alert_btn_no, variant="subtle")
        self.sub_alert_btn_no.show()

        try: self.sub_alert_btn_yes.clicked.disconnect()
        except: pass
        try: self.sub_alert_btn_no.clicked.disconnect()
        except: pass

        self.sub_alert_btn_yes.clicked.connect(self.execute_cancel)
        self.sub_alert_btn_no.clicked.connect(self.sub_alert_box.hide)
        
        self.sub_alert_box.show()

    def execute_cancel(self):
        self.user_is_premium = False
        self.user_info_label.setText("Ömer Utku\nStandart Üye")
        self.render_subscription_page()
        
        set_style_state(self.sub_alert_box, status="success")
        self.sub_alert_msg.setText("Aboneliğiniz iptal edildi. Standart hesaba geçtiniz.")
        self.sub_alert_btn_yes.hide()
        
        self.sub_alert_btn_no.setText("Tamam")
        self.sub_alert_btn_no.clicked.disconnect()
        self.sub_alert_btn_no.clicked.connect(self.sub_alert_box.hide)

    def prompt_upgrade_subscription(self):
        set_style_state(self.sub_alert_box, status="confirm")
        self.sub_alert_msg.setText("Aylık $19.99 karşılığında Premium ayrıcalıklara geçişi onaylıyor musunuz?")
        
        self.sub_alert_btn_yes.setText("Evet, Onaylıyorum")
        set_style_state(self.sub_alert_btn_yes, variant="primary")
        self.sub_alert_btn_yes.show()
        
        self.sub_alert_btn_no.setText("Vazgeç")
        set_style_state(self.sub_alert_btn_no, variant="subtle")
        self.sub_alert_btn_no.show()

        try: self.sub_alert_btn_yes.clicked.disconnect()
        except: pass
        try: self.sub_alert_btn_no.clicked.disconnect()
        except: pass

        self.sub_alert_btn_yes.clicked.connect(self.execute_upgrade)
        self.sub_alert_btn_no.clicked.connect(self.sub_alert_box.hide)
        
        self.sub_alert_box.show()

    def execute_upgrade(self):
        self.user_is_premium = True
        self.user_info_label.setText("Ömer Utku\nPremium Üye")
        self.render_subscription_page()
        
        set_style_state(self.sub_alert_box, status="success")
        self.sub_alert_msg.setText("Tebrikler! Premium ayrıcalıklarından anında faydalanmaya başlayabilirsiniz.")
        self.sub_alert_btn_yes.hide()
        
        self.sub_alert_btn_no.setText("Harika")
        self.sub_alert_btn_no.clicked.disconnect()
        self.sub_alert_btn_no.clicked.connect(self.sub_alert_box.hide)

    def render_payment_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if hasattr(self, "payment_count_value"):
            self.payment_count_value.setText(str(len(self.payment_cards)))
        if hasattr(self, "payment_default_value"):
            has_default = any(c["is_preferred"] for c in self.payment_cards)
            self.payment_default_value.setText("Aktif" if has_default else "Yok")
            set_style_state(self.payment_default_card, status="success" if has_default else "warning")

        sorted_cards = sorted(self.payment_cards, key=lambda x: not x["is_preferred"])

        if not sorted_cards:
            self.cards_layout.addWidget(create_info_card("Kayıtlı Kart Yok", "Yeni kart ekleyin", "Ödeme ve abonelik işlemleri için en az bir kart ekleyebilirsiniz.", "warning"))
            return

        for card in sorted_cards:
            card_box = create_payment_card_widget(
                card,
                lambda checked=False, c_id=card["id"]: self.set_preferred_card(c_id),
                lambda checked=False, c=card: self.open_inline_card_form(c),
                lambda checked=False, c_id=card["id"]: self.delete_card(c_id)
            )
            self.cards_layout.addWidget(card_box)

    def delete_card(self, card_id):
        card_to_delete = next((c for c in self.payment_cards if c["id"] == card_id), None)
        if card_to_delete:
            self.payment_cards.remove(card_to_delete)
            if card_to_delete["is_preferred"] and len(self.payment_cards) > 0:
                self.payment_cards[0]["is_preferred"] = True
            self.render_payment_cards()

    def set_preferred_card(self, card_id):
        for card in self.payment_cards:
            card["is_preferred"] = (card["id"] == card_id)
        self.render_payment_cards() 

    def switch_p3_stack(self, index):
        self.p3_stack.setCurrentIndex(index)
        self.master_fade.start()

    def open_inline_card_form(self, card=None):
        if card is None:
            self.form_title.setText("Yeni Kart Ekle")
            self.editing_card_id = None
            self.card_num_input.clear()
            self.card_exp_input.clear()
            self.card_cvv_input.clear()
            self.card_name_input.clear()
        else:
            self.form_title.setText("Kart Bilgilerini Güncelle")
            self.editing_card_id = card["id"]
            self.card_num_input.setText(card["number"])
            self.card_exp_input.setText(card["exp"])
            self.card_cvv_input.setText(card["cvv"])
            self.card_name_input.setText(card["name"])
        
        self.switch_p3_stack(1) 

    def save_inline_card_form(self):
        num = self.card_num_input.text().strip() or "0000000000000000"
        if self.editing_card_id is None:
            new_id = max([c["id"] for c in self.payment_cards] + [0]) + 1
            self.payment_cards.append({
                "id": new_id,
                "number": num,
                "exp": self.card_exp_input.text().strip() or "00/00",
                "cvv": self.card_cvv_input.text().strip() or "000",
                "name": self.card_name_input.text().strip() or "Bilinmiyor",
                "is_preferred": len(self.payment_cards) == 0 
            })
        else:
            for c in self.payment_cards:
                if c["id"] == self.editing_card_id:
                    c["number"] = num
                    c["exp"] = self.card_exp_input.text().strip()
                    c["cvv"] = self.card_cvv_input.text().strip()
                    c["name"] = self.card_name_input.text().strip()
                    break
        
        self.render_payment_cards()
        self.switch_p3_stack(0) 

    def close_inline_card_form(self):
        self.switch_p3_stack(0) 

    def toggle_hd_mode(self, state):
        self.thread.hd_mode = (state == 2)

    def toggle_camera(self):
        if not self.is_camera_running:
            self.thread.start()
            self.camera_btn.setText("Kamerayı Durdur")
            set_style_state(self.camera_btn, variant="danger")
            set_style_state(self.camera_preview_panel, state="running")
            set_style_state(self.image_label, state="running")
            self.is_camera_running = True
        else:
            self.thread.stop()
            self.camera_btn.setText("Kamerayı Başlat")
            set_style_state(self.camera_btn, variant="primary")
            self.image_label.clear()
            self.image_label.setText("CAMERA OFFLINE\nStart camera to initialize live preview")
            set_style_state(self.camera_preview_panel, state="idle")
            set_style_state(self.image_label, state="idle")
            self.is_camera_running = False

    def open_face_selection(self):
        dataset_path = "dataset"
        dialog = FaceSelectionDialog(dataset_path, self.user_is_premium, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_file = dialog.selected_path
            if not selected_file:
                return
            name = os.path.splitext(os.path.basename(selected_file))[0].replace('_', ' ').title()
            self.select_face_btn.setText(f"Seçili: {name}")
            self.selected_face_label.setText(name)
            self.thread.set_source_face(selected_file)

    def update_image(self, cv_img, fps):
        if self.fps_checkbox.isChecked():
            cv2.putText(cv_img, f"FPS: {fps}", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (59, 130, 246), 2, cv2.LINE_AA)

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        scaled_img = qt_img.scaled(768, 432, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(QPixmap.fromImage(scaled_img))
        self.thread.ui_ready = True

    def toggle_profile_edit(self):
        is_editing = self.edit_profile_btn.text() == "Kaydet"
        
        if is_editing:
            self.edit_profile_btn.setText("Düzenle")
            set_style_state(self.edit_profile_btn, variant="primary")
            for field in self.profile_fields:
                field.setReadOnly(True)
                field.setStyleSheet(COMPONENT_STYLES["profile_readonly"])
        else:
            self.edit_profile_btn.setText("Kaydet")
            set_style_state(self.edit_profile_btn, variant="success")
            for field in self.profile_fields:
                field.setReadOnly(False)
                field.setStyleSheet(COMPONENT_STYLES["profile_editable"])

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def update_params(self):
        self.thread.brightness = self.bright_slider.value()
        self.thread.contrast = self.cont_slider.value() / 100.00

    def capture_photo(self):
        if self.thread.last_frame is not None:
            if not os.path.exists("captures"):
                os.makedirs("captures")
            
            filename = f"captures/persona_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png"
            cv2.imwrite(filename, self.thread.last_frame)
            
            self.status_label.setText(f"✓ Fotoğraf kaydedildi!")
            set_style_state(self.status_label, status="success")
            self.status_label.show()
            
            QTimer.singleShot(5000, self.status_label.hide)
        else:
            self.status_label.setText("! Kamera aktif değil")
            set_style_state(self.status_label, status="error")
            self.status_label.show()
            QTimer.singleShot(3000, self.status_label.hide)

    def change_resolution(self):
        text = self.res_combo.currentText()
        if "1920" in text:
            self.thread.set_resolution(1920, 1080)
        elif "1280" in text:
            self.thread.set_resolution(1280, 720)
        elif "640" in text:
            self.thread.set_resolution(640, 480)

    def toggle_single_face(self, state):
        self.thread.single_face_mode = (state == 2)

    def apply_account_restrictions(self):
        if hasattr(self, 'user_name_label'):
            self.user_name_label.setText(self.full_name)
        if hasattr(self, 'restriction_panel'):
            set_style_state(self.restriction_panel, status="unlocked" if self.user_is_premium else "locked")
        if hasattr(self, 'restriction_text'):
            self.restriction_text.setText("Premium mod aktif: HD, tek yuz modu ve kayit aksiyonlari acik." if self.user_is_premium else "Standart mod: HD, tek yuz modu, fotograf kaydi ve cozunurluk ayari kilitli.")
        if hasattr(self, 'user_status_label'):
            self.user_status_label.setText("Premium Üye" if self.user_is_premium else "Standart Üye")

        if not self.user_is_premium:
            if hasattr(self, 'capture_btn'):
                self.capture_btn.setEnabled(False)
                self.capture_btn.setText("Anlık Fotoğraf Çek (Premium)")
                set_style_state(self.capture_btn, variant="subtle")

            if hasattr(self, 'hd_checkbox'):
                self.hd_checkbox.setEnabled(False)
                self.hd_checkbox.setText("HD Yüz Netleştirici (Premium)")
            
            if hasattr(self, 'single_face_checkbox'):
                self.single_face_checkbox.setEnabled(False)
                self.single_face_checkbox.setText("Sadece Ana Yüzü Değiştir (Premium)")

            if hasattr(self, 'bright_slider'):
                self.bright_slider.setEnabled(False)
            if hasattr(self, 'cont_slider'):
                self.cont_slider.setEnabled(False)

            if hasattr(self, 'res_combo'):
                self.res_combo.setEnabled(False)