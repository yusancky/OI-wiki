# Find related files to conduct correctness check and undefined behavior checks.
# input: changed files (from tj-actions/changed-files, read from res.txt)
# output: related files to test (write to $GITHUB_OUTPUT, access by setting env to the output and with os.environ.get())

import os


def collect_files(main_ext, filenames):
    mainfiles_to_test, mainfiles, auxfiles, examples, skiptest = set(), [], [], [], []

    for filename in filenames:
        dirname = os.path.dirname(filename)
        basename = os.path.splitext(os.path.basename(filename))[0]
        extname = os.path.splitext(filename)[1]

        if extname.endswith(main_ext):
            mainfile = os.path.normpath(
                os.path.join(dirname, basename.split(".")[0] + main_ext)
            )
            if mainfile in mainfiles_to_test:
                continue
            mainfiles_to_test.add(mainfile)

            temp_auxfiles = []
            for root, _, files in os.walk(dirname):
                for file in files:
                    if file.split(".")[0] == basename.split(".")[0] and file.endswith(
                        main_ext
                    ):
                        temp_auxfiles.append(os.path.normpath(os.path.join(root, file)))

            temp_examples = []
            for root, _, files in os.walk(dirname.replace("code", "examples")):
                for file in files:
                    if (
                        file.split(".")[0] == basename.split(".")[0]
                        and file.endswith(".in")
                        and os.path.exists(
                            os.path.join(root, file.replace(".in", ".ans"))
                        )
                    ):
                        temp_examples.append(os.path.normpath(os.path.join(root, file)))

            temp_skiptest = os.path.exists(
                os.path.join(dirname, basename + ".skip_test")
            )

            mainfiles.append(mainfile)
            auxfiles.append(temp_auxfiles)
            examples.append(temp_examples)
            skiptest.append(temp_skiptest)

        elif extname.endswith((".in", ".ans")):
            mainfile = os.path.normpath(
                os.path.join(
                    dirname.replace("examples", "code"),
                    basename.split(".")[0] + main_ext,
                )
            )
            if mainfile in mainfiles_to_test or not os.path.exists(mainfile):
                continue
            mainfiles_to_test.add(mainfile)

            temp_auxfiles = []
            for root, _, files in os.walk(dirname.replace("examples", "code")):
                for file in files:
                    if file.split(".")[0] == basename.split(".")[0] and file.endswith(
                        main_ext
                    ):
                        temp_auxfiles.append(os.path.normpath(os.path.join(root, file)))

            temp_examples = [os.path.normpath(os.path.join(dirname, basename + ".in"))]

            temp_skiptest = os.path.exists(
                os.path.join(
                    dirname.replace("examples", "code"), basename + ".skip_test"
                )
            )

            mainfiles.append(mainfile)
            auxfiles.append(temp_auxfiles)
            examples.append(temp_examples)
            skiptest.append(temp_skiptest)

    return mainfiles, auxfiles, examples, skiptest


def get_files_to_test(filenames):
    languages = ["cpp", "py"]

    outputs = {}
    for lang in languages:
        outputs[lang] = collect_files(f".{lang}", filenames)

    with open(os.environ.get("GITHUB_OUTPUT"), "w") as f:
        output_lines = []
        for lang, (mainfiles, auxfiles, examples, skiptest) in outputs.items():
            if mainfiles:
                output_lines.append(
                    f"files_to_test_{lang}={(mainfiles, auxfiles, examples, skiptest)}"
                )
            any_lang = any(not s for s in skiptest) if mainfiles else False
            output_lines.append(f"any_{lang}={str(any_lang).lower()}")
        f.write("\n".join(output_lines))
        print("\n".join(output_lines))


if __name__ == "__main__":
    changed_files = open("res.txt").read().split()
    get_files_to_test(changed_files)
