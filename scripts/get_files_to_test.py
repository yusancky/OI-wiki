# Find related files to conduct correctness check and undefined behavior checks.
# input: changed files (from tj-actions/changed-files, read from res.txt)
# output: related files to test (write to $GITHUB_OUTPUT, access by setting env to the output and with os.environ.get())

import os

extnames = [".cpp", ".py"]

def examples2code(example_file):
    dirname = os.path.dirname(example_file)
    basename = os.path.splitext(os.path.basename(example_file))[0]
    code_dir = dirname.replace("examples", "code")
    code_files = []
    for extname in extnames:
        if os.path.exists(os.path.join(code_dir, basename + extname)):
            code_files.append(os.path.normpath(os.path.join(code_dir, basename + extname)))
    return code_files

if __name__ == "__main__":
    changed_files = open("res.txt").read().split()
    changed_codes = []
    for changed_file in changed_files:
        if os.path.splitext(changed_file)[1] in ["in", "ans"]:
            code_files = examples2code(changed_file)
            for code_file in code_files:
                changed_codes.append(code_file)
        else:
            changed_codes.append(changed_file)
    for extname in extnames:
        # output
