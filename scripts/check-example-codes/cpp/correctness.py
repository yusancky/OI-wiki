import argparse
import os
import subprocess
from utils import *


def run_test_cpp(test_file):
    auxfiles = " ".join(get_auxfiles(test_file))
    executable = test_file.split(".")[0]
    compile_command = f"g++ -std=c++17 {auxfiles} -o {executable}"
    print(compile_command, end=" ")
    result = subprocess.run(compile_command, shell=True)
    if result.returncode != 0:
        print(f"CE\n::error file={test_file},title=编译错误::编译错误（错误码：{result.returncode}）\n::endgroup::")
        return 1, f"❌ 编译错误（错误码；{result.returncode}）"
    print("OK")

    in_file, out_file, ans_file = get_examples(test_file)
    if not (os.path.exists(in_file) and os.path.exists(ans_file)):
        print(
            f"::warning file={test_file},title=样例不存在::样例输入 {in_file} 或样例输出 {ans_file} 不存在，无法校验输出结果，请上传对应样例。如果无法提供样例，请在代码文件所在文件夹创建扩展名为 .skip_test 的文件\n::endgroup::"
        )
        return (
            1,
            f"⚠️ 样例输入 {in_file} 或样例输出 {ans_file} 不存在，无法校验输出结果，请上传对应样例。如果无法提供样例，请在代码文件所在文件夹创建扩展名为 .skip_test 的文件",
        )

    print(f"运行 {executable}（样例输入：{in_file}）", end=" ")
    try:
        result = subprocess.run(
            executable, shell=True, stdin=open(in_file, "r"), stdout=open(out_file, "w"), timeout = 30
        )
        if result.returncode != 0:
            print(
                f"RE\n::error file={test_file},title=运行时错误::运行时错误（错误码：{result.returncode}）\n::endgroup::"
            )
            return 1, f"❌ 运行时错误（错误码：{result.returncode}）"
        print("OK")
        return 0, f"✅ 编译、运行成功"
    except subprocess.TimeoutExpired:
        print(f"\n::error file={test_file},title=运行超时::运行时间超出 30 秒限制\n::endgroup::")
        return 1, f"❌ 运行时间超出 30 秒限制"


def check_answer(test_file):
    in_file, out_file, ans_file = get_examples(test_file)
    command = f"diff -b -B {out_file} {ans_file}"
    print(command, end=" ")
    result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        print(
            f"::error file={test_file},title=输出错误::编译、运行成功，但输出与答案（{ans_file}）不同\n::endgroup::"
        )
        return (
            1,
            f"❌ 编译、运行成功，但输出与答案不同\n    答案：\n    ```\n    {open(ans_file).read().replace(os.linesep, f'{os.linesep}    ')}\n    ```\n    输出：\n    ```\n    {open(ans_file).read().replace(os.linesep, f'{os.linesep}    ')}\n    ```",
        )
    print("Accepted!\n::endgroup::")
    return 0, f"✅ 编译、运行成功，且输出正确"


def check_correctness(test_file, language):
    if not os.path.exists(test_file):
        print(f"文件不存在\n::endgroup::")
        return 1, f"❌ 文件不存在"
    correctness, test_summary = globals()[f"run_test_{language}"](test_file)
    if correctness != 0:
        return correctness, test_summary
    return check_answer(test_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-language", type=str, required=True, choices=["cpp", "py"])
    language = parser.parse_args().language
    test_files = os.environ.get(f"TEST_{language.upper()}_FILES", "").split()
    cnts = [0, 0]
    summary = ""
    for test_file in test_files:
        print(f"::group::测试 {test_file}")
        correctness, test_summary = check_correctness(test_file, language)
        cnts[correctness] += 1
        summary += "- " + test_summary + "\n"
    general_summary = (f"已完成 {len(test_files)} 个测试，其中通过 {cnts[0]} 个，错误/警告/运行超时 {cnts[1]} 个")
    print(general_summary)
    open(os.environ.get("GITHUB_STEP_SUMMARY"), "w").write(f"**{general_summary}**\n\n{summary}")
    exit(cnts[1])
