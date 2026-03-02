"""
Skill catalog loader.

Skills live in:
  skills/<skill_name>/SKILL.md

This module keeps parsing lightweight (no extra dependency).
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillInfo:
    key: str
    name: str
    description: str
    path: Path


class SkillCatalog:
    def __init__(self, skills_dir: str = "./skills"):
        self.skills_dir = Path(skills_dir)
        self._skills: dict[str, SkillInfo] = {}

    def refresh(self):
        self._skills = {}
        if not self.skills_dir.exists():
            return

        for skill_md in sorted(self.skills_dir.glob("*/SKILL.md")):
            info = self._parse_skill_file(skill_md)
            # Two keys: folder key + human name key
            self._skills[info.key.lower()] = info
            self._skills[info.name.lower()] = info

    def list_skills(self) -> list[SkillInfo]:
        # Deduplicate aliases by path
        by_path: dict[Path, SkillInfo] = {}
        for info in self._skills.values():
            by_path[info.path] = info
        return sorted(by_path.values(), key=lambda item: item.key)

    def get_skill(self, name: str) -> SkillInfo | None:
        if not name:
            return None
        return self._skills.get(name.lower())

    def build_prompt_block(self) -> str:
        skills = self.list_skills()
        if not skills:
            return "No local skills are installed."

        lines = [
            "Available local skills (use when task matches):",
        ]
        for skill in skills:
            lines.append(f"- {skill.key}: {skill.description} (file: {skill.path})")

        lines.append(
            "If a skill is relevant, read the SKILL.md file first using read_file before executing steps."
        )
        return "\n".join(lines)

    def build_run_prompt(self, skill: SkillInfo, user_instruction: str = "") -> str:
        instruction = user_instruction.strip() or "(No extra instruction provided.)"
        return (
            "Run the following local skill carefully.\n\n"
            f"Skill: {skill.name}\n"
            f"Skill key: {skill.key}\n"
            f"Skill file path: {skill.path}\n"
            "Step 1) Read the SKILL.md file.\n"
            "Step 2) Follow the instructions exactly.\n"
            "Step 3) Execute required tool actions.\n"
            "Step 4) Return concise result + changed files.\n\n"
            f"User instruction: {instruction}"
        )

    def _parse_skill_file(self, path: Path) -> SkillInfo:
        text = path.read_text(encoding="utf-8")
        folder_key = path.parent.name

        frontmatter, body = self._split_frontmatter(text)
        name = frontmatter.get("name") or folder_key
        description = frontmatter.get("description") or self._extract_description(body)

        return SkillInfo(
            key=folder_key,
            name=name,
            description=description,
            path=path.resolve(),
        )

    @staticmethod
    def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
        if not text.startswith("---"):
            return {}, text

        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text

        raw_frontmatter = parts[1]
        body = parts[2]
        frontmatter: dict[str, str] = {}

        for line in raw_frontmatter.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                frontmatter[key] = value

        return frontmatter, body

    @staticmethod
    def _extract_description(body: str) -> str:
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("-"):
                continue
            return stripped[:200]
        return "No description"
