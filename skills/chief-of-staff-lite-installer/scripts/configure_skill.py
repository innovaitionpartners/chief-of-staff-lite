#!/usr/bin/env python3
"""Preview or apply a bounded Chief of Staff Lite personalization."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any
import zipfile


SKILL_NAME = "chief-of-staff-lite"
PLATFORMS = {"codex", "claude-code", "claude", "cowork", "chatgpt"}
HOSTED_PLATFORMS = {"claude", "cowork", "chatgpt"}
PORTABLE_ARCHIVE_NAME = "chief-of-staff-lite-personalized.zip"
COWORK_PLUGIN_NAME = "chief-of-staff-lite-personalized.plugin"
BEGIN_MARKER = "<!-- CSL-CONFIG:BEGIN -->"
END_MARKER = "<!-- CSL-CONFIG:END -->"
INSTALLER_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = INSTALLER_ROOT.parent.parent
TEMPLATE_PATH = INSTALLER_ROOT / "assets" / "chief-of-staff-lite.template.md"
DAILY_SKILL_ROOT = INSTALLER_ROOT.parent / SKILL_NAME
DAILY_SKILL_PATH = DAILY_SKILL_ROOT / "SKILL.md"
DAILY_SKILL_RELATIVE_PATH = Path("skills") / SKILL_NAME / "SKILL.md"
TEMPLATE_RELATIVE_PATH = (
    Path("skills")
    / "chief-of-staff-lite-installer"
    / "assets"
    / "chief-of-staff-lite.template.md"
)

# The temporary interview payload is small JSON. This cap rejects accidental document
# uploads while leaving ample room for the bounded CEO configuration schema.
MAX_CONFIG_BYTES = 65_536
# Individual business-context fields should stay concise enough to guide a daily brief.
DEFAULT_TEXT_MAX_CHARS = 600
MAX_CEO_NAME_CHARS = 120
MAX_COMPANY_NAME_CHARS = 160
# Product limits keep the daily brief focused and prevent setup from becoming a data dump.
MAX_STRATEGIC_PRIORITIES = 5
MAX_CEO_ONLY_DECISIONS = 6
MAX_PRIORITY_STAKEHOLDERS = 12
MAX_ESCALATION_TRIGGERS = 10
MAX_SOURCES = 10

CONFIG_FIELD_ORDER = (
    "ceo_name",
    "company",
    "ceo_mandate",
    "strategic_priorities",
    "ceo_only_decisions",
    "priority_stakeholders",
    "escalation_triggers",
    "brief_preference",
    "include_follow_up_drafts",
    "sources",
)
CONFIG_KEYS = set(CONFIG_FIELD_ORDER)
SOURCE_KEYS = {"name", "scope", "access_mode", "usage"}
ACCESS_MODES = {"connected", "manual", "unavailable"}
ACCESS_MODE_LABELS = {
    "connected": "appears available here",
    "manual": "pasted updates",
    "unavailable": "skipped for now",
}

# These formats are sufficiently specific to reject deterministically. Generic labels
# such as "API key" and instruction-like phrases are only review candidates because
# their meaning depends on context.
BLOCKED_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", re.IGNORECASE),
)
SECRET_REVIEW_PATTERNS = (
    re.compile(
        r"\b(password|passcode|api[_ -]?key|access[_ -]?token|private[_ -]?key)\s*[:=]\s*\S+",
        re.IGNORECASE,
    ),
)
INSTRUCTION_REVIEW_PATTERNS = (
    re.compile(r"\bignore\s+(all|any|previous|prior|your)\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\b(system prompt|developer message)\b", re.IGNORECASE),
    re.compile(r"\b(bypass|override)\s+(the\s+)?(rules?|safety|instructions?)\b", re.IGNORECASE),
)


class ConfigError(ValueError):
    """A user-correctable configuration or safety error."""


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_config_path(path: Path) -> Path:
    if path.is_symlink():
        raise ConfigError("The temporary configuration cannot be a symbolic link.")
    resolved = path.resolve(strict=True)
    allowed_roots = {Path("/tmp").resolve(), Path(tempfile.gettempdir()).resolve()}
    if not any(_is_within(resolved, root) for root in allowed_roots):
        roots = ", ".join(sorted(str(root) for root in allowed_roots))
        raise ConfigError(
            "The configuration must be a temporary file under one of these locations: "
            f"{roots}."
        )
    if resolved.stat().st_size > MAX_CONFIG_BYTES:
        raise ConfigError("The configuration is larger than the 64 KB safety limit.")
    return resolved


def read_config_payload(args: argparse.Namespace) -> tuple[Any, Path | None]:
    """Read config from the current invocation or a validated temporary file."""
    if args.config_stdin:
        payload = sys.stdin.buffer.read(MAX_CONFIG_BYTES + 1)
        if len(payload) > MAX_CONFIG_BYTES:
            raise ConfigError("The configuration is larger than the 64 KB safety limit.")
        return json.loads(payload.decode("utf-8")), None
    config_path = validate_config_path(args.config)
    return json.loads(config_path.read_text(encoding="utf-8")), config_path


def clean_text(
    value: Any, field: str, *, max_length: int = DEFAULT_TEXT_MAX_CHARS
) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"'{field}' must be text.")
    text = " ".join(value.split()).strip()
    if not text:
        raise ConfigError(f"'{field}' cannot be blank.")
    if len(text) > max_length:
        raise ConfigError(f"'{field}' exceeds the {max_length}-character limit.")
    if BEGIN_MARKER in text or END_MARKER in text:
        raise ConfigError(f"'{field}' contains a reserved configuration marker.")
    if any(pattern.search(text) for pattern in BLOCKED_SECRET_PATTERNS):
        raise ConfigError(
            f"'{field}' contains a recognized credential format. Remove it before continuing."
        )
    if any(ord(character) < 32 for character in text):
        raise ConfigError(f"'{field}' contains unsupported control characters.")
    return text


def clean_list(
    value: Any,
    field: str,
    *,
    minimum: int = 1,
    maximum: int = MAX_SOURCES,
) -> list[str]:
    if not isinstance(value, list):
        raise ConfigError(f"'{field}' must be a list.")
    if not minimum <= len(value) <= maximum:
        raise ConfigError(
            f"'{field}' must contain between {minimum} and {maximum} items."
        )
    return [clean_text(item, f"{field}[{index}]") for index, item in enumerate(value)]


def validate_config(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ConfigError("The configuration must be a JSON object.")
    unknown = set(raw) - CONFIG_KEYS
    missing = CONFIG_KEYS - set(raw)
    if unknown:
        raise ConfigError(f"Unknown configuration keys: {', '.join(sorted(unknown))}.")
    if missing:
        raise ConfigError(f"Missing configuration keys: {', '.join(sorted(missing))}.")

    include_drafts = raw["include_follow_up_drafts"]
    if not isinstance(include_drafts, bool):
        raise ConfigError("'include_follow_up_drafts' must be true or false.")

    sources = raw["sources"]
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_SOURCES:
        raise ConfigError(
            f"'sources' must contain between 1 and {MAX_SOURCES} sources."
        )

    clean_sources: list[dict[str, str]] = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ConfigError(f"'sources[{index}]' must be an object.")
        unknown_source = set(source) - SOURCE_KEYS
        missing_source = SOURCE_KEYS - set(source)
        if unknown_source:
            raise ConfigError(
                f"Unknown keys in sources[{index}]: {', '.join(sorted(unknown_source))}."
            )
        if missing_source:
            raise ConfigError(
                f"Missing keys in sources[{index}]: {', '.join(sorted(missing_source))}."
            )
        access_mode = clean_text(source["access_mode"], f"sources[{index}].access_mode")
        if access_mode not in ACCESS_MODES:
            raise ConfigError(
                f"sources[{index}].access_mode must be connected, manual, or unavailable."
            )
        clean_sources.append(
            {
                "name": clean_text(source["name"], f"sources[{index}].name"),
                "scope": clean_text(source["scope"], f"sources[{index}].scope"),
                "access_mode": access_mode,
                "usage": clean_text(source["usage"], f"sources[{index}].usage"),
            }
        )

    return {
        "ceo_name": clean_text(
            raw["ceo_name"], "ceo_name", max_length=MAX_CEO_NAME_CHARS
        ),
        "company": clean_text(
            raw["company"], "company", max_length=MAX_COMPANY_NAME_CHARS
        ),
        "ceo_mandate": clean_text(raw["ceo_mandate"], "ceo_mandate"),
        "strategic_priorities": clean_list(
            raw["strategic_priorities"],
            "strategic_priorities",
            maximum=MAX_STRATEGIC_PRIORITIES,
        ),
        "ceo_only_decisions": clean_list(
            raw["ceo_only_decisions"],
            "ceo_only_decisions",
            maximum=MAX_CEO_ONLY_DECISIONS,
        ),
        "priority_stakeholders": clean_list(
            raw["priority_stakeholders"],
            "priority_stakeholders",
            maximum=MAX_PRIORITY_STAKEHOLDERS,
        ),
        "escalation_triggers": clean_list(
            raw["escalation_triggers"],
            "escalation_triggers",
            maximum=MAX_ESCALATION_TRIGGERS,
        ),
        "brief_preference": clean_text(raw["brief_preference"], "brief_preference"),
        "include_follow_up_drafts": include_drafts,
        "sources": clean_sources,
    }


def iter_config_text(config: dict[str, Any]) -> list[tuple[str, str]]:
    """Return stable field paths and text for review-candidate scanning."""
    values: list[tuple[str, str]] = []
    for field in CONFIG_FIELD_ORDER:
        value = config[field]
        if isinstance(value, str):
            values.append((field, value))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    values.append((f"{field}[{index}]", item))
                elif isinstance(item, dict):
                    for source_field in ("name", "scope", "access_mode", "usage"):
                        values.append(
                            (f"{field}[{index}].{source_field}", item[source_field])
                        )
    return values


def review_candidates(config: dict[str, Any]) -> list[tuple[str, str]]:
    """Surface possible issues without claiming a context-dependent verdict."""
    candidates: list[tuple[str, str]] = []
    for field, text in iter_config_text(config):
        if any(pattern.search(text) for pattern in SECRET_REVIEW_PATTERNS):
            candidates.append((field, "possible-credential"))
        if any(pattern.search(text) for pattern in INSTRUCTION_REVIEW_PATTERNS):
            candidates.append((field, "instruction-like-language"))
    return candidates


def print_review_candidates(candidates: list[tuple[str, str]]) -> None:
    for field, candidate_type in candidates:
        print(f"REVIEW_CANDIDATE field={field} type={candidate_type}")
    if candidates:
        print(
            "REVIEW_REQUIRED: inspect these fields in context; the scanner does not "
            "decide whether the text is safe or unsafe."
        )


def markdown_text(text: str) -> str:
    return text.replace("|", r"\|")


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"  - {markdown_text(item)}" for item in items)


def render_config_block(config: dict[str, Any]) -> str:
    source_rows = "\n".join(
        "| {name} | {scope} | {access_mode} | {usage} |".format(
            **{key: markdown_text(value) for key, value in source.items()}
        )
        for source in config["sources"]
    )
    drafts = "yes" if config["include_follow_up_drafts"] else "no"
    return f"""{BEGIN_MARKER}
## CEO operating context

**Configuration status:** active

- **CEO:** {markdown_text(config['ceo_name'])}
- **Company:** {markdown_text(config['company'])}
- **CEO mandate:** {markdown_text(config['ceo_mandate'])}
- **Strategic priorities:**
{bullet_lines(config['strategic_priorities'])}
- **CEO-only decisions or unblockers:**
{bullet_lines(config['ceo_only_decisions'])}
- **Priority stakeholders:**
{bullet_lines(config['priority_stakeholders'])}
- **Escalate when:**
{bullet_lines(config['escalation_triggers'])}
- **Brief preference:** {markdown_text(config['brief_preference'])}
- **Include follow-up drafts:** {drafts}

### Configured information sources

| Source | Relevant scope | Access mode | How to use it |
|---|---|---|---|
{source_rows}
{END_MARKER}"""


def platform_approval_action(platform: str, is_update: bool) -> tuple[str, str]:
    if platform in {"codex", "claude-code"}:
        return (
            "Create or update the user-owned Chief of Staff Lite skill shown by preview.",
            "Reply **Yes, install it** to approve this exact setup.",
        )
    if platform == "cowork":
        if is_update:
            return (
                "Update your existing Chief of Staff Lite skill with this configuration. "
                "Cowork will show a replacement `.plugin` package for you to review and install.",
                "Reply **Yes, prepare the update** to approve this exact change. "
                "Cowork will review and install the replacement package separately.",
            )
        return (
            "Create a personalized `.plugin` package for Cowork to review and install separately.",
            "Reply **Yes, create the package** to approve this exact setup. You will review and install the resulting package separately.",
        )
    return (
        "Create a temporary personalized ZIP for you to install separately.",
        "Reply **Yes, create the file** to approve this exact setup. You will install the resulting file separately.",
    )


def render_approval_preview(
    config: dict[str, Any],
    platform: str,
    *,
    is_update: bool,
    has_temporary_config: bool,
) -> str:
    """Render the complete user-visible approval contract from validated config."""
    priorities = "; ".join(markdown_text(item) for item in config["strategic_priorities"])
    decisions = "; ".join(markdown_text(item) for item in config["ceo_only_decisions"])
    stakeholders = "; ".join(
        markdown_text(item) for item in config["priority_stakeholders"]
    )
    escalations = "; ".join(
        markdown_text(item) for item in config["escalation_triggers"]
    )
    sources = "\n".join(
        "- {name} — {mode} — {scope} — use: {usage}".format(
            name=markdown_text(source["name"]),
            mode=ACCESS_MODE_LABELS[source["access_mode"]],
            scope=markdown_text(source["scope"]),
            usage=markdown_text(source["usage"]),
        )
        for source in config["sources"]
    )
    drafts = "yes, never sent automatically" if config["include_follow_up_drafts"] else "no"
    action, approval = platform_approval_action(platform, is_update)
    unchanged = (
        "Your existing skill has not been changed yet."
        if is_update
        else "Nothing has been written or installed yet."
    )
    cleanup = (
        "\n- Delete the temporary setup file after a successful install or package creation."
        if has_temporary_config
        else ""
    )
    return f"""## Your Chief of Staff Lite setup

**CEO:** {markdown_text(config['ceo_name'])}, {markdown_text(config['company'])}
**Mandate:** {markdown_text(config['ceo_mandate'])}
**Priorities:** {priorities}
**CEO-only decisions:** {decisions}
**Sources:**
{sources}
**Priority stakeholders:** {stakeholders}
**Escalate when:** {escalations}
**Brief style:** {markdown_text(config['brief_preference'])}
**Follow-up drafts:** {drafts}

{unchanged}

### What will happen
- {action}
- Preserve the daily workflow and safety rules.
- Store no passwords, tokens, or credentials.
- Make no tool connections or external changes.{cleanup}

{approval}"""


def replace_config_block(skill_text: str, config_block: str) -> str:
    if skill_text.count(BEGIN_MARKER) != 1 or skill_text.count(END_MARKER) != 1:
        raise ConfigError(
            "The target skill does not have exactly one recognized configuration block. "
            "It was not changed."
        )
    before, remainder = skill_text.split(BEGIN_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    return before + config_block + after


def has_active_config(skill_text: str) -> bool:
    """Detect whether the recognized config block represents an existing setup."""
    if BEGIN_MARKER not in skill_text or END_MARKER not in skill_text:
        return False
    block = skill_text.split(BEGIN_MARKER, 1)[1].split(END_MARKER, 1)[0]
    return bool(
        re.search(r"\*\*Configuration status:\*\*\s*active\b", block)
    )


def platform_target(platform: str) -> Path:
    home = Path.home().resolve()
    if platform == "codex":
        codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
        return codex_home / "skills" / SKILL_NAME
    if platform == "claude-code":
        claude_home = Path(
            os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")
        ).expanduser()
        return claude_home / "skills" / SKILL_NAME
    raise ConfigError(f"'{platform}' does not use a local skill target.")


def validate_target(platform: str) -> Path:
    target_arg = platform_target(platform)
    if target_arg.name != SKILL_NAME:
        raise ConfigError(f"The target folder must be named '{SKILL_NAME}'.")
    if target_arg.exists() and target_arg.is_symlink():
        raise ConfigError("The target skill folder cannot be a symbolic link.")
    if target_arg.parent.exists() and target_arg.parent.is_symlink():
        raise ConfigError("The user skill directory cannot be a symbolic link.")
    target = target_arg.resolve(strict=False)
    plugin_skills_root = INSTALLER_ROOT.parent.resolve()
    if _is_within(target, plugin_skills_root):
        raise ConfigError(
            "The installer will not personalize a plugin-owned skill. Choose the correct "
            "platform so it can use a user-owned skill directory."
        )
    skill_path = target / "SKILL.md"
    if skill_path.is_symlink():
        raise ConfigError("The installer will not overwrite a symbolic-linked SKILL.md.")
    if target.exists() and not skill_path.exists() and any(target.iterdir()):
        raise ConfigError(
            "The target folder contains files but no recognized Chief of Staff Lite SKILL.md. "
            "It was not changed."
        )
    return target


def is_cowork_session_outputs_root(path: Path) -> bool:
    """Accept only the exact user-visible outputs mount inside a Cowork session."""
    parts = path.parts
    if (
        len(parts) < 5
        or parts[0] != "/"
        or parts[1] != "sessions"
        or not re.fullmatch(r"[A-Za-z0-9._-]+", parts[2])
    ):
        return False
    return tuple(parts[3:]) in {
        ("mnt", "outputs"),
        ("mnt", "data", "outputs"),
        ("mnt", "user-data", "outputs"),
    }


def validate_export_path(platform: str) -> Path:
    # Cowork normally supplies a user-visible outputs mount. If it does not, using
    # the system temp directory is intentional; the host must surface that file
    # through its native preview rather than copying it to an unvalidated path.
    root_arg = Path(
        os.environ.get("CSL_EXPORT_DIR", tempfile.gettempdir())
    ).expanduser()
    if root_arg.exists() and root_arg.is_symlink():
        raise ConfigError("The portable export directory cannot be a symbolic link.")
    root = root_arg.resolve(strict=False)
    allowed_roots = {
        Path("/tmp").resolve(),
        Path(tempfile.gettempdir()).resolve(),
        Path("/mnt/data/outputs").resolve(),
        Path("/mnt/outputs").resolve(),
        Path("/mnt/user-data/outputs").resolve(),
    }
    allowed = any(_is_within(root, candidate) for candidate in allowed_roots)
    if platform == "cowork":
        allowed = allowed or is_cowork_session_outputs_root(root)
    if not allowed:
        raise ConfigError(
            "The portable package must be created in a temporary directory or the "
            "Cowork outputs directory."
        )
    package_name = COWORK_PLUGIN_NAME if platform == "cowork" else PORTABLE_ARCHIVE_NAME
    archive = root / package_name
    if archive.exists() and archive.is_symlink():
        raise ConfigError("The portable package cannot overwrite a symbolic link.")
    return archive


def load_base_skill(target: Path) -> tuple[str, str]:
    skill_path = target / "SKILL.md"
    if skill_path.exists():
        current = skill_path.read_text(encoding="utf-8")
        if not re.search(r"^name:\s*chief-of-staff-lite\s*$", current, re.MULTILINE):
            raise ConfigError(
                "The existing SKILL.md is not Chief of Staff Lite. It was not changed."
            )
        return current, current
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return "", template


def validate_plugin_bundle() -> None:
    """Verify the installer and daily skill ship together as one plugin."""
    required_files = {
        "installer template": TEMPLATE_PATH,
        "daily skill": DAILY_SKILL_PATH,
    }
    missing = [label for label, path in required_files.items() if not path.is_file()]
    if missing:
        raise ConfigError(
            "The Chief of Staff Lite plugin is incomplete. Missing: "
            f"{', '.join(missing)}. Reinstall the complete plugin before setup."
        )
    daily_skill = DAILY_SKILL_PATH.read_text(encoding="utf-8")
    if not re.search(r"^name:\s*chief-of-staff-lite\s*$", daily_skill, re.MULTILINE):
        raise ConfigError(
            "The bundled daily skill is not recognized as Chief of Staff Lite. "
            "Reinstall the complete plugin before setup."
        )
    if TEMPLATE_PATH.read_text(encoding="utf-8") != daily_skill:
        raise ConfigError(
            "The installer template does not match the bundled daily skill. "
            "Reinstall the complete plugin before setup."
        )


def approval_hash(skill_text: str, destination: str) -> str:
    payload = skill_text + "\n\0DESTINATION\0\n" + destination
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def print_preview(
    current_skill: str,
    proposed_skill: str,
    skill_path: Path,
    digest: str,
    config: dict[str, Any],
    platform: str,
    is_update: bool,
    has_temporary_config: bool,
) -> None:
    current_lines = current_skill.splitlines(keepends=True)
    proposed_lines = proposed_skill.splitlines(keepends=True)
    diff = difflib.unified_diff(
        current_lines,
        proposed_lines,
        fromfile=str(skill_path) if current_skill else "/dev/null",
        tofile=str(skill_path),
    )
    sys.stdout.writelines(diff)
    print("APPROVAL_PREVIEW_BEGIN")
    print(
        render_approval_preview(
            config,
            platform,
            is_update=is_update,
            has_temporary_config=has_temporary_config,
        )
    )
    print("APPROVAL_PREVIEW_END")
    print(f"APPROVAL_HASH={digest}")
    print("PREVIEW_ONLY: no files were written.")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def atomic_write_zip(path: Path, skill_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            archive.writestr(f"{SKILL_NAME}/SKILL.md", skill_text)
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def atomic_write_cowork_plugin(path: Path, skill_text: str) -> None:
    """Package a personalized copy of the complete plugin for Cowork."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    included_roots = (Path(".claude-plugin"), Path(".codex-plugin"), Path("skills"))
    included_files = (Path("README.md"), Path("LICENSE"))
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for relative_root in included_roots:
                source_root = PLUGIN_ROOT / relative_root
                if not source_root.is_dir():
                    continue
                for source_path in sorted(source_root.rglob("*")):
                    if source_path.is_symlink():
                        raise ConfigError(
                            f"The plugin contains a symbolic link that cannot be packaged: "
                            f"{source_path.relative_to(PLUGIN_ROOT)}"
                        )
                    if not source_path.is_file():
                        continue
                    relative_path = source_path.relative_to(PLUGIN_ROOT)
                    if relative_path in {
                        DAILY_SKILL_RELATIVE_PATH,
                        TEMPLATE_RELATIVE_PATH,
                    }:
                        archive.writestr(str(relative_path), skill_text)
                    else:
                        archive.write(source_path, str(relative_path))
            for relative_path in included_files:
                source_path = PLUGIN_ROOT / relative_path
                if source_path.is_file():
                    archive.write(source_path, str(relative_path))
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or apply a bounded Chief of Staff Lite configuration."
    )
    parser.add_argument("--platform", choices=sorted(PLATFORMS))
    config_source = parser.add_mutually_exclusive_group()
    config_source.add_argument("--config", type=Path)
    config_source.add_argument(
        "--config-stdin",
        action="store_true",
        help="Read the complete JSON configuration from this invocation's standard input.",
    )
    parser.add_argument(
        "--check-bundle",
        action="store_true",
        help="Verify that the complete two-skill plugin is installed.",
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approved-hash")
    parser.add_argument(
        "--cleanup-config",
        action="store_true",
        help="Delete the validated temporary configuration after a successful apply.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validate_plugin_bundle()
        if args.check_bundle:
            print("BUNDLE_OK: installer and daily skill are present.")
            return 0
        if args.platform is None or (args.config is None and not args.config_stdin):
            raise ConfigError(
                "--platform and either --config or --config-stdin are required unless "
                "--check-bundle is used."
            )
        if args.cleanup_config and args.config_stdin:
            raise ConfigError("--cleanup-config cannot be used with --config-stdin.")
        raw_config, config_path = read_config_payload(args)
        config = validate_config(raw_config)
        candidates = review_candidates(config)
        print_review_candidates(candidates)

        if args.platform in HOSTED_PLATFORMS:
            archive_path = validate_export_path(args.platform)
            if args.platform == "cowork":
                current_skill = DAILY_SKILL_PATH.read_text(encoding="utf-8")
                base_skill = current_skill
                skill_path = DAILY_SKILL_RELATIVE_PATH
            else:
                current_skill = ""
                base_skill = TEMPLATE_PATH.read_text(encoding="utf-8")
                skill_path = Path(SKILL_NAME) / "SKILL.md"
            proposed_skill = replace_config_block(base_skill, render_config_block(config))
        else:
            target = validate_target(args.platform)
            current_skill, base_skill = load_base_skill(target)
            proposed_skill = replace_config_block(base_skill, render_config_block(config))
            skill_path = target / "SKILL.md"
            archive_path = None
        is_update = has_active_config(current_skill)
        destination = f"{args.platform}:{skill_path}:{archive_path or ''}"
        digest = approval_hash(proposed_skill, destination)

        if not args.apply:
            print_preview(
                current_skill,
                proposed_skill,
                skill_path,
                digest,
                config,
                args.platform,
                is_update,
                config_path is not None,
            )
            if archive_path is not None:
                print(f"PACKAGE_PATH={archive_path}")
            return 0

        if not args.approved_hash:
            raise ConfigError("--apply requires --approved-hash from the latest preview.")
        if not re.fullmatch(r"[0-9a-f]{64}", args.approved_hash):
            raise ConfigError("The approved hash must be a 64-character SHA-256 value.")
        if args.approved_hash != digest:
            raise ConfigError(
                "The approved hash does not match the current proposed skill. "
                "Run preview again and ask the CEO to approve the new version."
            )

        if args.platform == "cowork":
            atomic_write_cowork_plugin(archive_path, proposed_skill)
        elif archive_path is not None:
            atomic_write_zip(archive_path, proposed_skill)
        else:
            atomic_write(skill_path, proposed_skill)
        if args.cleanup_config and config_path is not None:
            config_path.unlink()
        if archive_path is not None:
            print(f"EXPORTED: {archive_path}")
        else:
            print(f"INSTALLED: {skill_path}")
        print(f"APPROVAL_HASH={digest}")
        if args.cleanup_config and config_path is not None:
            print(f"REMOVED_TEMP_CONFIG: {config_path}")
        return 0
    except FileNotFoundError as error:
        print(f"ERROR: Required file not found: {error.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(
            f"ERROR: The configuration is not valid JSON: line {error.lineno}, "
            f"column {error.colno}.",
            file=sys.stderr,
        )
        return 2
    except (ConfigError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
