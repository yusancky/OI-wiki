# Find related files to conduct correctness check and undefined behavior checks.
# input: changed files (from tj-actions/changed-files)
# output: related files to test (write to $GITHUB_OUTPUT)

import os

extnames = [".cpp", ".py"]


def examples2code(example_file):
    dirname = os.path.dirname(example_file)
    basename = os.path.splitext(os.path.basename(example_file))[0]
    code_dir = dirname.replace("examples", "code")
    code_files = []
    for extname in extnames:
        if os.path.exists(os.path.join(code_dir, basename + extname)):
            code_files.append(
                os.path.normpath(os.path.join(code_dir, basename + extname))
            )
    return code_files


if __name__ == "__main__":
    changed_files = os.environ.get["all_changed_files"]
    if changed_files == None:
        for extname in extnames:
            all_extnamed_codes = []
            for root, dirs, files in os.walk("docs"):
                for file in files:
                    if file.endswith(extname):
                        all_extnamed_codes.append(os.path.join(root, file))
        all_extnamed_codes = " ".join(all_extnamed_codes)
        if all_extnamed_codes == "":
            all_extnamed_codes = "None"
        with open(os.environ.get("GITHUB_OUTPUT"), "w") as f:
            f.write(f"TEST_{extname.upper()}_FILES={all_extnamed_codes}")
    changed_codes = []
    for changed_file in changed_files:
        if os.path.splitext(changed_file)[1] in ["in", "ans"]:
            code_files = examples2code(changed_file)
            for code_file in code_files:
                changed_codes.append(code_file)
        else:
            changed_codes.append(changed_file)
    for extname in extnames:
        changed_extnamed_codes = " ".join(
            filter(lambda x: x.endswith(".cpp"), changed_codes)
        )
        if changed_extnamed_codes == "":
            changed_extnamed_codes = "None"
        with open(os.environ.get("GITHUB_OUTPUT"), "w") as f:
            f.write(f"TEST_{extname.upper()}_FILES={changed_extnamed_codes}")
