# Check correctness of example C++ code.
# input: related files to test (from get-files-to-test.py, read from $FILES_TO_TEST)
# output: None. Print to GitHub Action step summary.

import os
import subprocess

def code2examples(source_filename):
    dirname = os.path.dirname(source_filename)
    basename = os.path.splitext(os.path.basename(source_filename))[0]
    extname = os.path.splitext(source_filename)[1]
    if not extname.endswith(('.cpp', '.py')):
        return None
    examples_dir = dirname.replace('code', 'examples')
    in_filename = os.path.normpath(os.path.join(examples_dir, basename + '.in'))
    ans_filename = os.path.normpath(os.path.join(examples_dir, basename + '.ans'))
    if os.path.exists(in_filename) and os.path.exists(ans_filename):
        return (in_filename, ans_filename)
    else:
        return None

ACCEPTED, ERROR = 1, 0

def check_correctness(test_file):
    print(f'::group::Test for {test_file}...')

    if not os.path.exists(test_file):
        print(f"File {test_file} does not exist.\n::endgroup::")
        return ERROR, f'文件 {test_file} 不存在'
    test_examples = code2examples(test_file)
    if test_examples == None:
        print(f"Example file(s) for {test_file} does not exist.\n::endgroup::")
        return ERROR, f'文件 {test_file} 的样例输入或样例输出不存在（如果不希望测试 {test_file}，请创建 {test_file.replace(".cpp", ".skip_test")}）'

    # 这个指令及以后还没有修改
    compile_command = f"g++ -std=c++17 {" ".join(auxfiles)} -o {mainfile.split(".")[0]}"
    print(compile_command, end=' ')
    result = subprocess.run(compile_command, shell=True)
    if result.returncode != 0:
        print(f'\n::endgroup::')
        print(f'::error file={mainfile},title=CE!::Compile Error! with error code {result.returncode}')
        summary += f'## CE: {mainfile}\n- 主要文件：`{mainfile}`\n- 辅助文件：`{", ".join(auxfiles)}`\n- 测试点：`{", ".join(examples)}`\n- **编译指令**：{compile_command}\n- **错误代码**：{result.returncode}\n\n'
        return ERROR, summary
    else:
        print('OK')
  
    # 对不提供数据点的特殊处理
    if len(examples) == 0:
        print(f'\n::endgroup::')
        print(f"::warning file={mainfile},title=No data!::Can't find data to test. If you don't want this notice, create {mainfile.replace('.cpp', '.skip_test')}")
        summary += f'## No Data: {mainfile}\n- 主要文件：`{mainfile}`\n- 辅助文件：`{", ".join(auxfiles)}`\n- 测试点：`{", ".join(examples)}`\n- 编译指令：{compile_command}\n成功编译，但因数据不存在未能进一步测试。**如果不希望进行测试，请创建{mainfile.replace(".cpp", ".skip_test")}**\n\n'
        return ACCEPTED, summary  

    # 逐个测试
    executable = mainfile.split(".")[0]
    check_command = (f'diff -b -B {e.replace(".in", ".out")} {e.replace(".in", ".ans")}' for e in examples)
    for check, e in zip(check_command, examples):
        print(f'{executable} < {e} > {e.replace(".in", ".out")}', end=' ')
        with open(e, 'r') as fstdin:
            with open(e.replace(".in", ".out"), 'w') as fstdout:
                result = subprocess.run(executable, shell=True, stdin=fstdin, stdout=fstdout)
        if result.returncode != 0:
            print(f'\n::endgroup::')
            print(f'::error file={mainfile},title=RE!::Runtime Error! with error code: {result.returncode}')
            summary += f'## RE: {mainfile}\n- 主要文件：`{mainfile}`\n- 辅助文件：`{", ".join(auxfiles)}`\n- 测试点：`{", ".join(examples)}`\n- **出错测试点**：{e}\n- **错误代码**：{result.returncode}\n\n'
            return ERROR, summary
        else:
            print('OK')

        print(check, end=' ')
        result = subprocess.run(check, shell=True, stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            print(f'\n::endgroup::')
            print(f'::error file={e},title=WA!::Wrong Answer on: {e}')
            summary += f'## WA: {mainfile}\n- 主要文件：`{mainfile}`\n- 辅助文件：`{", ".join(auxfiles)}`\n- 测试点：`{", ".join(examples)}`\n- **出错测试点**：{e}\n\n期望得到：\n```\n{open(e.replace(".in", ".ans")).read()}\n```\n但得到输出：\n```\n{open(e.replace(".in", ".out")).read()}\n```\n\n'
            return ERROR, summary
        else:
            print(f'Accepted!')

    summary += f'## AC: {mainfile} ({len(examples)} tests)\n- 主要文件：`{mainfile}`\n- 辅助文件：`{", ".join(auxfiles)}`\n- 测试点：`{", ".join(examples)}`\n\n'
    print(f'::endgroup::')
    return ACCEPTED, summary

if __name__ == "__main__":
    test_files = os.environ.get("TEST_CPP_FILES").split("|")
    cnt_ac, cnt_error = 0, 0
    summary = ""
    for test_file in test_files:
        # correctness, summary = correctness_check(mainfile, auxfile, example, skiptest, summary)
        # cnt_ac = cnt_ac + 1 if correctness == ACCEPTED else cnt_ac
        # cnt_error = cnt_error + 1 if correctness == ERROR else cnt_error
        """
        with open(os.environ.get('GITHUB_STEP_SUMMARY'), 'w') as f:
            f.write(f'# TOTAL {len(mainfiles)} TESTS, {cnt_ac} ACCEPTED, {cnt_skip} SKIPPED, {cnt_error} ERROR\n\n')
            f.write(summary)
            print(f'::group::TOTAL {len(mainfiles)} TESTS, {cnt_ac} ACCEPTED, {cnt_skip} SKIPPED, {cnt_error} ERROR\n::endgroup::')
        """
    if cnt_error > 0:
        exit(1)

