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


def output(name, value):
    with open(os.environ.get("GITHUB_OUTPUT"), "a") as f:
        f.write(f"{name}={value if value else 'None'}\n")


if __name__ == "__main__":
    changed_files = os.environ.get("all_changed_files")
    if changed_files:
        changed_codes = set()
        for changed_file in changed_files.split():
            if os.path.splitext(changed_file)[1] in ["in", "ans"]:
                changed_codes.update(examples2code(changed_file))
            else:
                changed_codes.add(changed_file)
        for extname in extnames:
            changed_extnamed_codes = " ".join(
                filter(lambda x: x.endswith(extname), changed_codes)
            )
            output(f"TEST_{extname[1:].upper()}_FILES", changed_extnamed_codes)
    else:
        for extname in extnames:
            all_extnamed_codes = []
            for root, dirs, files in os.walk("docs"):
                for file in files:
                    if file.endswith(extname):
                        all_extnamed_codes.append(os.path.join(root, file))
            output(f"TEST_{extname[1:].upper()}_FILES", " ".join(all_extnamed_codes))
