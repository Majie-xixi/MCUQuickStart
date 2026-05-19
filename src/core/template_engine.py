"""Template engine: replace {{PLACEHOLDER}} tokens in template files."""
from pathlib import Path


def _read_template(path: Path) -> str:
    """Read a template file, trying common encodings."""
    raw = path.read_bytes()
    for encoding in ("utf-8", "gbk", "gb2312", "latin-1"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def render(template_path: Path, output_path: Path, variables: dict):
    """Read template file, replace {{VAR}} tokens with values, write output."""
    content = _read_template(template_path)
    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", str(value))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def render_directory(template_dir: Path, output_dir: Path, variables: dict):
    """Render all files in a directory recursively."""
    for file_path in template_dir.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(template_dir)
            out_path = output_dir / rel_path
            render(file_path, out_path, variables)


def copy_file(src: Path, dst: Path):
    """Copy a file, creating parent dirs as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
