"""
配置验证工具
用于验证应用配置的数据类型、必填项和枚举值
"""

from typing import Dict, Any, List, Optional, Tuple
from typing_extensions import get_args, get_origin
import json


# ==================== 配置结构定义 ====================

# 默认配置模板
DEFAULT_CONFIG = {
    "app": {
        "name": "AI活动秀",
        "version": "1.0.0",
        "debug": False
    },
    "features": {
        "ai_show": {
            "enabled": True,
            "invite_code_mode": True,
            "payment_mode": True,
            "employee_mode": True,
            "auto_close_time": 20
        },
        "quiz": {
            "enabled": True,
            "voice_input": False,
            "push_prize": True
        },
        "lottery": {
            "enabled": True,
            "voice_trigger": False,
            "push_winner": True
        },
        "inner_show": {
            "enabled": True,
            "digital_human_announce": True
        }
    }
}

# 配置项定义 schema
CONFIG_SCHEMA = {
    "app": {
        "type": "object",
        "required": True,
        "properties": {
            "name": {
                "type": "string",
                "required": True,
                "description": "应用名称"
            },
            "version": {
                "type": "string",
                "required": False,
                "pattern": r"^\d+\.\d+\.\d+$",
                "description": "版本号 (格式: x.y.z)"
            },
            "debug": {
                "type": "boolean",
                "required": False,
                "description": "调试模式"
            }
        }
    },
    "features": {
        "type": "object",
        "required": True,
        "properties": {
            "ai_show": {
                "type": "object",
                "required": True,
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "required": False,
                        "description": "启用AI百变秀"
                    },
                    "invite_code_mode": {
                        "type": "boolean",
                        "required": False,
                        "description": "邀请码模式"
                    },
                    "payment_mode": {
                        "type": "boolean",
                        "required": False,
                        "description": "支付模式"
                    },
                    "employee_mode": {
                        "type": "boolean",
                        "required": False,
                        "description": "员工模式"
                    },
                    "auto_close_time": {
                        "type": "integer",
                        "required": False,
                        "min": 5,
                        "max": 300,
                        "description": "自动关闭时间(秒)"
                    }
                }
            },
            "quiz": {
                "type": "object",
                "required": True,
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "required": False,
                        "description": "启用知识问答"
                    },
                    "voice_input": {
                        "type": "boolean",
                        "required": False,
                        "description": "语音输入"
                    },
                    "push_prize": {
                        "type": "boolean",
                        "required": False,
                        "description": "推送奖品信息"
                    }
                }
            },
            "lottery": {
                "type": "object",
                "required": True,
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "required": False,
                        "description": "启用幸运抽奖"
                    },
                    "voice_trigger": {
                        "type": "boolean",
                        "required": False,
                        "description": "语音触发抽奖"
                    },
                    "push_winner": {
                        "type": "boolean",
                        "required": False,
                        "description": "推送中奖信息"
                    }
                }
            },
            "inner_show": {
                "type": "object",
                "required": True,
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "required": False,
                        "description": "启用内场秀"
                    },
                    "digital_human_announce": {
                        "type": "boolean",
                        "required": False,
                        "description": "数字人播报"
                    }
                }
            }
        }
    }
}


# ==================== 验证错误类 ====================

class ValidationError(Exception):
    """配置验证错误"""
    def __init__(self, message: str, field_path: str = ""):
        self.message = message
        self.field_path = field_path
        super().__init__(self.message)

    def __str__(self):
        if self.field_path:
            return f"字段 '{self.field_path}': {self.message}"
        return self.message


# ==================== 验证函数 ====================

def validate_config(config: Dict[str, Any], schema: Dict = None) -> Tuple[bool, List[str]]:
    """
    验证配置数据

    Args:
        config: 要验证的配置字典
        schema: 配置schema，默认使用CONFIG_SCHEMA

    Returns:
        (is_valid, errors): 验证结果和错误列表
    """
    if schema is None:
        schema = CONFIG_SCHEMA

    errors = []

    try:
        _validate_object(config, schema, "")
    except ValidationError as e:
        errors.append(str(e))

    return len(errors) == 0, errors


def _validate_object(value: Any, schema: Dict, path: str):
    """验证对象类型"""
    if not isinstance(value, dict):
        raise ValidationError(f"期望对象类型，实际为 {type(value).__name__}", path)

    properties = schema.get("properties", {})

    # 检查必填字段
    for prop_name, prop_schema in properties.items():
        if prop_schema.get("required", False) and prop_name not in value:
            raise ValidationError(f"缺少必填字段 '{prop_name}'", path)

    # 验证每个字段
    for prop_name, prop_value in value.items():
        if prop_name not in properties:
            # 允许额外的字段，但给出警告
            continue

        new_path = f"{path}.{prop_name}" if path else prop_name
        _validate_value(prop_value, properties[prop_name], new_path)


def _validate_value(value: Any, schema: Dict, path: str):
    """根据schema验证值"""
    value_type = schema.get("type")

    if value_type == "string":
        _validate_string(value, schema, path)
    elif value_type == "integer":
        _validate_integer(value, schema, path)
    elif value_type == "boolean":
        _validate_boolean(value, path)
    elif value_type == "object":
        _validate_object(value, schema, path)
    elif value_type == "array":
        _validate_array(value, schema, path)
    else:
        raise ValidationError(f"未知的类型: {value_type}", path)


def _validate_string(value: Any, schema: Dict, path: str):
    """验证字符串类型"""
    if not isinstance(value, str):
        raise ValidationError(f"期望字符串类型，实际为 {type(value).__name__}", path)

    # 验证正则表达式
    pattern = schema.get("pattern")
    if pattern:
        import re
        if not re.match(pattern, value):
            raise ValidationError(f"字符串格式不匹配，期望格式: {pattern}", path)


def _validate_integer(value: Any, schema: Dict, path: str):
    """验证整数类型"""
    if not isinstance(value, int):
        raise ValidationError(f"期望整数类型，实际为 {type(value).__name__}", path)

    # 验证范围
    min_val = schema.get("min")
    max_val = schema.get("max")

    if min_val is not None and value < min_val:
        raise ValidationError(f"值不能小于 {min_val}", path)
    if max_val is not None and value > max_val:
        raise ValidationError(f"值不能大于 {max_val}", path)


def _validate_boolean(value: Any, path: str):
    """验证布尔类型"""
    if not isinstance(value, bool):
        raise ValidationError(f"期望布尔类型，实际为 {type(value).__name__}", path)


def _validate_array(value: Any, schema: Dict, path: str):
    """验证数组类型"""
    if not isinstance(value, list):
        raise ValidationError(f"期望数组类型，实际为 {type(value).__name__}", path)

    # 验证数组元素
    items_schema = schema.get("items")
    if items_schema:
        for i, item in enumerate(value):
            item_path = f"{path}[{i}]"
            _validate_value(item, items_schema, item_path)


# ==================== 配置处理工具 ====================

def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return DEFAULT_CONFIG.copy()


def reset_to_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    重置为默认配置（保留app_id）

    Args:
        config: 当前配置

    Returns:
        重置后的配置
    """
    # 保存app_id
    app_id = config.get("app_id")

    # 获取默认配置
    default = get_default_config()

    # 恢复app_id
    if app_id:
        default["app_id"] = app_id

    return default


def merge_config(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置（update覆盖base）

    Args:
        base: 基础配置
        update: 更新的配置

    Returns:
        合并后的配置
    """
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result


def get_config_schema() -> Dict:
    """获取配置schema（用于前端生成表单）"""
    return {
        "schema": CONFIG_SCHEMA,
        "default": DEFAULT_CONFIG,
        "ui_schema": {
            "app": {
                "ui:order": ["name", "version", "debug"],
                "name": {
                    "ui:title": "应用名称",
                    "ui:placeholder": "请输入应用名称"
                },
                "version": {
                    "ui:title": "版本号",
                    "ui:placeholder": "例如: 1.0.0"
                },
                "debug": {
                    "ui:title": "调试模式",
                    "ui:widget": "checkbox"
                }
            },
            "features": {
                "ui:order": ["ai_show", "quiz", "lottery", "inner_show"],
                "ai_show": {
                    "ui:title": "AI百变秀",
                    "enabled": {"ui:title": "启用"},
                    "invite_code_mode": {"ui:title": "邀请码模式"},
                    "payment_mode": {"ui:title": "支付模式"},
                    "employee_mode": {"ui:title": "员工模式"},
                    "auto_close_time": {
                        "ui:title": "自动关闭时间(秒)",
                        "ui:widget": "range",
                        "ui:min": 5,
                        "ui:max": 300
                    }
                },
                "quiz": {
                    "ui:title": "知识问答",
                    "enabled": {"ui:title": "启用"},
                    "voice_input": {"ui:title": "语音输入"},
                    "push_prize": {"ui:title": "推送奖品信息"}
                },
                "lottery": {
                    "ui:title": "幸运抽奖",
                    "enabled": {"ui:title": "启用"},
                    "voice_trigger": {"ui:title": "语音触发"},
                    "push_winner": {"ui:title": "推送中奖信息"}
                },
                "inner_show": {
                    "ui:title": "内场秀",
                    "enabled": {"ui:title": "启用"},
                    "digital_human_announce": {"ui:title": "数字人播报"}
                }
            }
        }
    }


def validate_field_type(value: Any, expected_type: str, field_name: str = "") -> bool:
    """
    验证字段类型

    Args:
        value: 要验证的值
        expected_type: 期望的类型 (string/integer/boolean/object/array)
        field_name: 字段名称（用于错误提示）

    Returns:
        是否验证通过
    """
    type_map = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list
    }

    if expected_type not in type_map:
        raise ValueError(f"未知的类型: {expected_type}")

    expected_python_type = type_map[expected_type]
    return isinstance(value, expected_python_type)
