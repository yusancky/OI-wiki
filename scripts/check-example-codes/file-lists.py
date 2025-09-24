import os

extnames = [".cpp", ".py"]


def check_available(file):
    if ".aux" in file:
        return False
    dirname = os.path.dirname(filename)
    basename = os.path.splitext(os.path.basename(code_filename))[0]
    skip_file = os.path.normpath(os.path.join(dirname, basename + ".skip_test"))
    return not os.path.exists(skip_file)


def examples2code(example_file):
    dirname = os.path.dirname(example_file)
    basename = os.path.splitext(os.path.basename(example_file))[0]
    code_dir = dirname.replace("examples", "code")
    code_files = []
    for extname in extnames:
        code_file = os.path.normpath(os.path.join(code_dir, basename + extname))
        if os.path.exists(code_file) and check_available(code_file):
            code_files.append(code_file)
    return code_files


def output(name, value):
    with open(os.environ.get("GITHUB_OUTPUT"), "a") as f:
        f.write(f"{name}={value if value else 'None'}\n")


if __name__ == "__main__":
    changed_files = os.environ.get("all_changed_files")
    other_changed_files = os.environ.get("other_changed_files")
    if changed_files and "check-example-codes" not in other_changed_files:
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
            for root, _, files in os.walk("docs"):
                for file in files:
                    if file.endswith(extname) and check_available(file):
                        all_extnamed_codes.append(os.path.join(root, file))
            output(f"TEST_{extname[1:].upper()}_FILES", " ".join(all_extnamed_codes))
