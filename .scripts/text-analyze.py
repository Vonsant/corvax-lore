import os
import re
import json
from subprocess import check_output


def analyze_text(text):
    if not isinstance(text, str):
        text = str(text)
    words = len(re.findall(r"\b\w+\b", text))
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    return {
        "words": words,
        "chars": chars,
        "chars_no_spaces": chars_no_spaces,
    }


def main():
    try:
        base_branch = os.getenv("GITHUB_BASE_REF", "main")
        diff_output = check_output(["git", "diff", "--unified=0", f"origin/{base_branch}"], encoding="utf-8")
        file_changes = {}

        current_file = None
        for line in diff_output.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
                if current_file != "/dev/null":
                    file_changes[current_file] = {"added_lines": "", "removed_lines": "", "stats": {}}
            elif current_file and current_file != "/dev/null":
                if line.startswith("+") and not line.startswith("+++") and len(line) > 1:
                    file_changes[current_file]["added_lines"] += line[1:] + "\n"
                elif line.startswith("-") and not line.startswith("---") and len(line) > 1:
                    file_changes[current_file]["removed_lines"] += line[1:] + "\n"

        total_stats = {
            "added": {"words": 0, "chars": 0, "chars_no_spaces": 0},
            "removed": {"words": 0, "chars": 0, "chars_no_spaces": 0},
            "final": {"words": 0, "chars": 0, "chars_no_spaces": 0},
        }

        for file_path, changes in list(file_changes.items()):
            try:
                added_stats = analyze_text(changes["added_lines"])
                removed_stats = analyze_text(changes["removed_lines"])

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        full_text = f.read()
                    final_stats = analyze_text(full_text)
                except FileNotFoundError:
                    print(f"Warning: File not found: {file_path}")
                    final_stats = {"words": 0, "chars": 0, "chars_no_spaces": 0}
                except Exception as e:
                    print(f"Warning: Error reading file {file_path}: {str(e)}")
                    final_stats = {"words": 0, "chars": 0, "chars_no_spaces": 0}

                file_changes[file_path]["stats"] = {
                    "added": added_stats,
                    "removed": removed_stats,
                    "final": final_stats,
                }

                for key in total_stats["added"]:
                    total_stats["added"][key] += added_stats[key]
                    total_stats["removed"][key] += removed_stats[key]
                    total_stats["final"][key] += final_stats[key]

            except Exception as e:
                print(f"Warning: Error processing file {file_path}: {str(e)}")
                del file_changes[file_path]

        results = {
            "total_files": len(file_changes),
            "file_changes": file_changes,
            "total_stats": total_stats,
        }

        with open("statistics.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
