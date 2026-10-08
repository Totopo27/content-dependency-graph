import json
from pathlib import Path

# Concept Mapping Heuristics tailored for Matt Pocock's TypeScript Curriculum:
# 1. Video 1: "TypeScript Speedrun: Crash Course for Beginners" (YmxwicpROps)
# 2. Video 2: "6 TypeScript tips to turn you into a WIZARD" (lraHlXpuhKs)
# 3. Video 3: "TypeScript 4.9 deep dive" (Danki1DyiuI)
# 4. Video 4: "The SECRET POWER of indexed access types" (plsnFfbqVEo)

TITLES_AND_CONCEPTS = {
    "YmxwicpROps": {
        "title": "TypeScript Speedrun: Crash Course for Beginners",
        "segments": {
            "seg_YmxwicpROps_01": {
                "taught": ["type-inference", "type-annotations", "interfaces-basics"],
                "required": ["javascript-fundamentals"]
            },
            "seg_YmxwicpROps_02": {
                "taught": ["tsc-compiler", "ide-autocomplete", "ambient-types"],
                "required": ["type-inference", "interfaces-basics"]
            },
            "seg_YmxwicpROps_03": {
                "taught": ["primitive-types", "strict-mode", "array-types"],
                "required": ["type-annotations"]
            },
            "seg_YmxwicpROps_04": {
                "taught": ["object-types", "optional-properties", "union-types"],
                "required": ["primitive-types", "interfaces-basics"]
            },
            "seg_YmxwicpROps_05": {
                "taught": ["type-assertions", "literal-types", "any-type"],
                "required": ["union-types", "object-types"]
            }
        }
    },
    "lraHlXpuhKs": {
        "title": "6 TypeScript tips to turn you into a WIZARD",
        "segments": {
            "seg_lraHlXpuhKs_01": {
                "taught": ["utility-types-exclude-extract", "utility-types-pick-omit"],
                "required": ["union-types", "object-types"]
            },
            "seg_lraHlXpuhKs_02": {
                "taught": ["prettify-type-helper", "loose-autocomplete-trick"],
                "required": ["union-types", "intersection-types"]
            },
            "seg_lraHlXpuhKs_03": {
                "taught": ["mapped-types-basics", "key-remapping", "template-literal-types"],
                "required": ["union-types", "object-types"]
            },
            "seg_lraHlXpuhKs_04": {
                "taught": ["discriminated-unions"],
                "required": ["mapped-types-basics", "literal-types", "union-types"]
            }
        }
    },
    "Danki1DyiuI": {
        "title": "TypeScript 4.9 Deep Dive: satisfies Operator",
        "segments": {
            "seg_Danki1DyiuI_01": {
                "taught": ["file-watching-events", "type-narrowing-in-operator"],
                "required": ["object-types", "tsc-compiler"]
            },
            "seg_Danki1DyiuI_02": {
                "taught": ["auto-accessors-classes", "satisfies-operator"],
                "required": ["type-inference", "object-types", "union-types"]
            }
        }
    },
    "plsnFfbqVEo": {
        "title": "The SECRET POWER of indexed access types",
        "segments": {
            "seg_plsnFfbqVEo_01": {
                "taught": ["indexed-access-types", "tuple-indexing"],
                "required": ["object-types", "union-types"]
            }
        }
    }
}


def enrich_catalog():
    fixture_path = Path("tests/fixtures/matt_pocock_catalog.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog["channel_id"] = "UC_mattpocockuk"
    catalog["channel_title"] = "Matt Pocock (Total TypeScript)"

    for v in catalog["videos"]:
        vid_id = v["id"]
        if vid_id in TITLES_AND_CONCEPTS:
            v["title"] = TITLES_AND_CONCEPTS[vid_id]["title"]
            seg_rules = TITLES_AND_CONCEPTS[vid_id]["segments"]
            for seg in v["segments"]:
                s_id = seg["segment_id"]
                if s_id in seg_rules:
                    seg["concepts_taught"] = seg_rules[s_id]["taught"]
                    seg["concepts_required"] = seg_rules[s_id]["required"]

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Enriched Matt Pocock catalog with semantic concept tags.")


if __name__ == "__main__":
    enrich_catalog()
