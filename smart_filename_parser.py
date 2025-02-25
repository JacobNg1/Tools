import re


def parse_filename_metadata(filename: str) -> tuple:
    """
    智能解析含复杂元数据的文件名
    返回: (扩展名, 基础名)

    核心功能：
    1. 精准过滤云存储标注（如[1.2TiB]）
    2. 智能识别语义化版本号（如_v2.3.1）
    3. 支持多层级扩展名（如.tar.gz 优先于.gz）
    4. 兼容时空坐标标记（如@geo120.5,45.8）
    """
    # 阶段1：元数据清洗（支持2150规范前瞻设计）
    cleaned = re.sub(
        r'''
        ([\s\[(]*(?:\d+\.)?\d+\s*[KMGTPE]i?B[\s)\]]*) |  # 容量标记（含未来EB级单位）
        ([_\-](?:v|ver|version)\d+(?:\.\d+)+)           |  # 语义化版本号（v2.3.1）
        (@(?:draft|final|beta)\d*)                      |  # 文件状态标记 
        (\[\d{4}[-\/]\d{2}[-\/]\d{2}\])                   # ISO 8601日期标记 
        ''',
        '',
        filename,
        flags=re.X | re.IGNORECASE
    ).strip(' _-')

    # 阶段2：扩展名识别（动态优先级队列）
    document_exts = {
        'tar.gz': 2, 'docx': 1, 'xlsx': 1,  # 复合扩展名优先
        'gz': 1, 'pdf': 1, 'txt': 1, 'doc': 1
    }

    # 按扩展名层级深度降序检测
    for ext in sorted(document_exts, key=lambda x: document_exts[x], reverse=True):
        if cleaned.lower().endswith(f".{ext}"):
            base = cleaned[:-len(ext) - 1]  # +1补偿点号
            return ext, base.strip('  ._')

    # 未匹配时的处理（支持未来新型扩展名）
    if '.' in cleaned:
        *base_parts, last_part = cleaned.split('.')
        return last_part.lower(), '.'.join(base_parts)

    return None, cleaned


# 时空连续性测试集
test_cases = [
    ('实验数据_2025_v2.3.1.tar.gz[1.2GB]', ('tar.gz', '实验数据')),
    ('机密报告@final_v3.pdf  (3PiB)', ('pdf', '机密报告')),
    ('卫星影像_N32E118@geo120.5,45.8.tif', ('tif', '卫星影像')),
    ('量子实验记录_21500225.entangled', ('entangled', '量子实验记录')),
    ('image.with.multiple.dots.jpg', ('jpg', 'image.with.multiple'))
]

for filename, expected in test_cases:
    result = parse_filename_metadata(filename)
    print(f"输入：{filename}\n输出：{result} | 预期：{expected}\n{'-' * 60}")
