import os

extnames = [".cpp", ".py"]


def check_availability(file):
    dirname = os.path.dirname(file)
    if dirname.split('/')[-1] in ["images"]:
        return false
    basename = os.path.splitext(os.path.basename(file))[0]
    extname = os.path.splitext(os.path.basename(file))[1]
    if "." in basename:
        basename = basename.split(".")[0]
        if os.path.exists(os.path.join(dirname, basename + extname)):
            return os.path.normpath(os.path.join(dirname, basename + extname))
    skip_file = os.path.join(dirname, basename + ".skip_test")
    if os.path.exists(skip_file):
        return False
    else:
        return os.path.normpath(os.path.join(dirname, basename + extname))


def examples2code(example_file):
    dirname = os.path.dirname(example_file)
    basename = os.path.splitext(os.path.basename(example_file))[0]
    code_dir = dirname.replace("examples", "code")
    code_files = []
    for extname in extnames:
        code_file = os.path.normpath(os.path.join(code_dir, basename + extname))
        if os.path.exists(code_file) and check_availability(code_file):
            code_files.append(check_availability(code_file))
    return code_files


def output(name, value):
    with open(os.environ.get("GITHUB_OUTPUT"), "a") as f:
        f.write(f"{name}={value if value else 'None'}\n")


if __name__ == "__main__":
    changed_files = os.environ.get("all_changed_files")
    changed_codes = set()
    for changed_file in changed_files.split():
        if os.path.splitext(changed_file)[1] in extnames:
            changed_codes.add(changed_file)
        else:
            changed_codes.update(examples2code(changed_file))
    for extname in extnames:
        if extname == ".py":
            all_extnamed_codes = []
            for root, _, files in os.walk("docs"):
                for file in files:
                    if file.endswith(extname) and check_availability(os.path.join(root, file)):
                        all_extnamed_codes.append(check_availability(os.path.join(root, file)))
            output(f"TEST_{extname[1:].upper()}_FILES", " ".join(all_extnamed_codes))
        else:
            changed_extnamed_codes = " ".join(
                filter(lambda x: x.endswith(extname), changed_codes)
            )
            output(f"TEST_{extname[1:].upper()}_FILES", changed_extnamed_codes)
