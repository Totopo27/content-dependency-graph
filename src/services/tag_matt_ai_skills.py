import json
from pathlib import Path

# Semantic tagging for Matt Pocock's AI Workflow & Skills series
AI_SKILLS_TAGS = {
    "M6mYodf0dJM": {
        "title": "mattpocock/skills: A Complete AI Coding Workflow, End-to-End",
        "segments": {
            "seg_M6mYodf0dJM_01": {
                "taught": ["npx-skills-cli", "skills-architecture", "token-budget-skills"],
                "required": ["nodejs-runtime", "cli-basics"]
            },
            "seg_M6mYodf0dJM_02": {
                "taught": ["issue-tracker-setup", "domain-documentation", "context-md-adr"],
                "required": ["skills-architecture"]
            },
            "seg_M6mYodf0dJM_03": {
                "taught": ["grill-with-docs", "llm-smart-zone", "to-spec-compression"],
                "required": ["context-md-adr", "domain-documentation"]
            },
            "seg_M6mYodf0dJM_04": {
                "taught": ["implement-skill", "subagent-code-review", "two-axis-review"],
                "required": ["to-spec-compression", "grill-with-docs"]
            }
        }
    },
    "EJyuu6zlQCg": {
        "title": "5 Claude Code Skills I Use Every Single Day",
        "segments": {
            "seg_EJyuu6zlQCg_01": {
                "taught": ["agent-process-discipline", "grill-me-skill", "design-tree-concept"],
                "required": ["claude-code-basics"]
            },
            "seg_EJyuu6zlQCg_02": {
                "taught": ["write-prd-skill", "prd-to-issues-skill", "vertical-slices-breakdown"],
                "required": ["grill-me-skill", "design-tree-concept"]
            },
            "seg_EJyuu6zlQCg_03": {
                "taught": ["subagent-code-review-patterns", "fowler-smell-baseline"],
                "required": ["vertical-slices-breakdown"]
            },
            "seg_EJyuu6zlQCg_04": {
                "taught": ["triage-labels-workflow"],
                "required": ["prd-to-issues-skill"]
            }
        }
    },
    "-QFHIoCo-Ko": {
        "title": "Full Walkthrough: Workflow for AI Coding — Matt Pocock",
        "segments": {
            "seg_-QFHIoCo-Ko_01": {
                "taught": ["llm-smart-zone-vs-dumb-zone", "attention-quadratic-degradation", "context-window-hygiene"],
                "required": ["llm-prompting-basics"]
            },
            "seg_-QFHIoCo-Ko_02": {
                "taught": ["multiphase-loops", "ralph-wiggum-loop-comparison", "small-task-sizing"],
                "required": ["llm-smart-zone-vs-dumb-zone"]
            },
            "seg_-QFHIoCo-Ko_03": {
                "taught": ["session-phases-system-explore-impl-test", "compacting-pitfalls"],
                "required": ["context-window-hygiene"]
            },
            "seg_-QFHIoCo-Ko_04": {
                "taught": ["end-to-end-agent-lifecycle"],
                "required": ["multiphase-loops", "session-phases-system-explore-impl-test"]
            }
        }
    }
}

def tag_ai_skills():
    fixture_path = Path("tests/fixtures/matt_pocock_ai_skills.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog["channel_id"] = "UC_mattpocockuk_ai"
    catalog["channel_title"] = "Matt Pocock: AI Coding & Agent Skills"

    for v in catalog["videos"]:
        v_id = v["id"]
        if v_id in AI_SKILLS_TAGS:
            v["title"] = AI_SKILLS_TAGS[v_id]["title"]
            seg_rules = AI_SKILLS_TAGS[v_id]["segments"]
            for seg in v["segments"]:
                s_id = seg["segment_id"]
                if s_id in seg_rules:
                    seg["concepts_taught"] = seg_rules[s_id]["taught"]
                    seg["concepts_required"] = seg_rules[s_id]["required"]

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print("Successfully tagged Matt Pocock AI Skills catalog.")

if __name__ == "__main__":
    tag_ai_skills()
