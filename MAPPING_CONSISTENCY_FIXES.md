# Mapping Consistency Fixes Report

## Summary
修复了 streamlit_app.py、rules.clp 和 case_library.txt 中映射的所有不一致问题。

---

## 1. STREAMLIT_APP.PY 修改

### STEP 1: Display Visuals
| 问题 | 旧值 | 新值 | 原因 |
|------|------|------|------|
| Distorted image 值 | `distorted-image` | `distorted` | 匹配 rules.clp 中 display-ram-distortion 规则 |

### STEP 2: Audio System

#### Volume Bar Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `bar-moving`, `bar-irregular`, `bar-frozen` | `moving`, `irregular`, `frozen` |

#### Sound Output Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `sound-none`, `sound-distorted`, `sound-normal` | `none`, `distorted`, `normal` |

#### Sound Card Status Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `card-not-detected`, `card-detected` | `not-detected`, `detected` |

### STEP 3: Thermal & CPU

#### Temperature Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `temp-above-85`, `temp-rising-rapidly`, `temp-normal` | `above-85`, `rising-rapidly`, `normal` |

#### Boot Warning Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `warn-cpu-overheat`, `warn-none` | `cpu-overheat`, `none` |

### STEP 4: Power & Startup

#### Power Lights Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `light-on`, `light-off` | `on`, `off` |

#### Fan Status Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `fan-silent`, `fan-spinning` | `silent`, `spinning` |

### STEP 5: Storage, Beeps & Errors

#### Error Message Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `err-disk-boot-failure`, `err-smart-warning`, `err-ide-not-ready`, `err-none` | `disk-boot-failure`, `smart-warning`, `ide-not-ready`, `none` |

#### Beep Code Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `beep-very-short`, `beep-short`, `beep-long`, `beep-repeated-long`, `beep-continuous`, `beep-none` | `very-short`, `short`, `long`, `repeated-long`, `continuous`, `none` |

#### Device Age Mapping
| 问题 | 旧值 | 新值 |
|------|------|------|
| 值前缀 | `age-old`, `age-new` | `old`, `new` |

---

## 2. CASE_LIBRARY.TXT 修改

### 所有 CASE 的特征值标准化

所有 case_library.txt 中的特征值已更新为去掉多余前缀的简洁形式：

| 特征 | 旧值示例 | 新值示例 |
|------|---------|---------|
| fan-status | `fan-status:fan-spinning` | `fan-status:spinning` |
| power-lights | `power-lights:light-on` | `power-lights:on` |
| cpu-temp | `cpu-temp:temp-above-85` | `cpu-temp:above-85` |
| sound-output | `sound-output:sound-none` | `sound-output:none` |
| beep-code | `beep-code:beep-long` | `beep-code:long` |
| error-message | `error-message:err-smart-warning` | `error-message:smart-warning` |
| device-age | `device-age:age-old` | `device-age:old` |
| system-age | `system-age:age-old` | `system-age:old` |

### 更新的 CASE 列表
- CASE-10001 至 CASE-10020: 所有特征值已标准化

---

## 3. RULES.CLP

### 状态
✅ **无需修改** - rules.clp 中的症状名称和值已经是正确的格式，与修改后的 streamlit_app.py 匹配。

### 验证
所有 CLIPS 规则中的症状定义都遵循简洁命名规范：
- `(symptom (name volume-bar) (value moving)...)` ✓
- `(symptom (name sound-output) (value none)...)` ✓
- `(symptom (name beep-duration) (value very-short)...)` ✓

---

## 4. Boot-Behavior 特殊处理

在 STEP 5 中添加了逻辑来正确映射 `boot-behavior`：
```python
# boot-behavior maps to system-state:random-shutdowns from STEP 4
if 'system-state' in st.session_state.answers and \
   st.session_state.answers['system-state'][0] == "Computer shuts down randomly":
    st.session_state.answers['boot-behavior'] = (
        st.session_state.answers['system-state'][0], 
        ("random-reboots", 1.0)
    )
```

这确保了 `storage-wear` 规则能够正确触发（需要 `boot-behavior:random-reboots` 和 `device-age:old`）。

---

## 总体变更统计

- **streamlit_app.py**: 12 处映射修改
- **case_library.txt**: 20 个 CASE（CASE-10001 至 CASE-10020）中的特征值标准化
- **rules.clp**: 无需修改（已正确）

## 一致性现状

✅ **完全一致** - 现在三个文件（streamlit_app.py、rules.clp、case_library.txt）中的特征名称和值完全对应。
