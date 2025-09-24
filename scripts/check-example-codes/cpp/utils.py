import os


def get_auxfiles(cpp_filename):
    dirname = os.path.dirname(cpp_filename)
    basename = os.path.splitext(os.path.basename(cpp_filename))[0]
    auxfiles = []
    for root, _, files in os.walk(dirname):
        for file in files:
            if file.split(".")[0] == basename.split(".")[0] and file.endswith(".cpp"):
                auxfiles.append(os.path.normpath(os.path.join(root, file)))
    return auxfiles

def get_examples(code_filename):
    dirname = os.path.dirname(code_filename)
    basename = os.path.splitext(os.path.basename(code_filename))[0]
    examples_dir = dirname.replace("code", "examples")
    in_file = os.path.normpath(os.path.join(examples_dir, basename + ".in"))
    out_file = os.path.normpath(os.path.join(examples_dir, basename + ".out"))
    ans_file = os.path.normpath(os.path.join(examples_dir, basename + ".ans"))
    return in_file, out_file, ans_file
