import os
import subprocess
from utils import *


def check_correctness(test_file):
    print(f"::group::Test for {test_file}...")

    if not os.path.exists(test_file):
        print(f"File {test_file} does not exist\n::endgroup::")
        return 1, f"❌ 文件 {test_file} 不存在"

    auxfiles = " ".join(get_auxfiles(test_file))
    executable = test_file.split(".")[0]
    compile_command = f"g++ -std=c++17 {auxfiles} -o {executable}"
    print(compile_command, end=" ")
    result = subprocess.run(compile_command, shell=True)
    if result.returncode != 0:
        print(
            f"CE\n::endgroup::\n::error file={test_file},title=Compile Error::Compile Error with error code {result.returncode}"
        )
        return 1, f"❌ 文件 {test_file} 编译错误"
    print("OK")

    in_file, out_file, ans_file = get_examples(test_file)
    if not (os.path.exists(in_file) and os.path.exists(ans_file)):
        print(
            f"::warning file={test_file},title=Example file(s) does not exist::Example file(s) for {test_file} does not exist, so its output will not be checked\n::endgroup::"
        )
        return (
            1,
            f"⚠️ 文件 {test_file} 的样例输入 {in_file} 或样例输出 {ans_file} 不存在，无法校验输出结果。请上传对应样例，或将没有样例的代码直接嵌入 Markdown 文件的代码块中。",
        )

    print(f"Runing {executable} with input {in_file}", end=" ")
    result = subprocess.run(
        executable, shell=True, stdin=open(in_file, "r"), stdout=open(out_file, "w")
    )
    if result.returncode != 0:
        print(
            f"::error file={test_file},title=Runtime Error::Runtime Error with error code: {result.returncode}\n::endgroup::"
        )
        return 1, f"❌ 文件 {test_file} 运行时错误"
    print("OK")

    check_command = f"diff -b -B {out_file} {ans_file}"
    print(check_command, end=" ")
    result = subprocess.run(check_command, shell=True, stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        print(
            f"::error file={test_file},title=Wrong Answer::The output is different to the answer {ans_file}"
        )
        return (
            1,
            f"❌ 文件 {test_file} 输出与答案不同\n    答案：\n    ```\n    {open(ans_file).read().replace(os.linesep, f'{os.linesep}    ')}\n    ```\n    输出：\n    ```\n    {open(ans_file).read().replace(os.linesep, f'{os.linesep}    ')}\n    ```",
        )
    print("Accepted!\n::endgroup::")
    return 0, f"✅ 文件 {test_file} 通过测试"


if __name__ == "__main__":
    test_files = os.environ.get("TEST_CPP_FILES").split(" ")
    cnts = [0, 0]
    summary = ""
    for test_file in test_files:
        correctness, test_summary = check_correctness(test_file)
        cnts[correctness] += 1
        summary += "- " + test_summary
    general_summary = f"TOTAL {len(test_files)} TESTS, {cnts[0]} ACCEPTED, {cnts[1]} ERROR/WARNING"
    print(general_summary)
    open(os.environ.get("GITHUB_STEP_SUMMARY"), "w").write(
        f"**{general_summary}**\n\n{summary}"
    )
    exit(cnts[2])
