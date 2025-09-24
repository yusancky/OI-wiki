from dataclasses import dataclass
import os
import subprocess
from utils import *

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
WHITE = "\033[0;37m"
RESET = "\033[0m"

incolor = lambda color, text: f"{color}{text}{RESET}"


@dataclass(frozen=True)
class Status:
    errcode: int
    color: str

    def __str__(self):
        return f"{self.__class__.__name__}({self.errcode})"

    def colored(self):
        return f"{self.color}{self}{RESET}"


@dataclass(frozen=True)
class CompileOK(Status):
    errcode: int = 0
    color: str = GREEN


@dataclass(frozen=True)
class CE(Status):
    errcode: int
    color: str = RED


@dataclass(frozen=True)
class AC(Status):
    errcode: int = 0
    color: str = GREEN


@dataclass(frozen=True)
class RE(Status):
    errcode: int
    color: str = RED


@dataclass(frozen=True)
class WA(Status):
    errcode: int
    color: str = RED


def ub_check(mainfile):
    print(incolor(BLUE, f"Test for {mainfile}..."))
    
    auxfiles = get_auxfiles(mainfile)

    CALL_VCVARS_BAT = r'call "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat"'

    def gen(
        compilers,
        standards,
        optimizations,
        auxfiles,
        sanitizers,
        mainfile,
        omit_ms_style=False,
    ):
        assert compilers is not None and compilers != []
        assert standards is not None and standards != []
        assert optimizations is not None and optimizations != []
        assert sanitizers is not None and sanitizers != []

        def arrgen():
            if not omit_ms_style:
                return [
                    f'{compiler} {standard} {optimization} {sanitizer} {" ".join(auxfiles)} -o {mainfile.split(".")[0]}{c_name}{s_name}{o_name}{san_name}'
                    for compiler, c_name in compilers
                    for standard, s_name in standards
                    for optimization, o_name in optimizations
                    for sanitizer, san_name in sanitizers
                ]
            else:
                return [
                    f'{compiler} {standard} {optimization} {sanitizer} {" ".join(auxfiles)} /Fe:{os.path.normpath(mainfile.split(".")[0])}{c_name}{s_name}{o_name}{san_name}'
                    for compiler, c_name in compilers
                    for standard, s_name in standards
                    for optimization, o_name in optimizations
                    for sanitizer, san_name in sanitizers
                ]

        def productgen():
            return [
                f'{os.path.normpath(mainfile.split(".")[0])}{c_name}{s_name}{o_name}{san_name}'
                for _, c_name in compilers
                for _, s_name in standards
                for _, o_name in optimizations
                for _, san_name in sanitizers
            ]

        return (arrgen(), productgen())

    concat = lambda a, b: (a[0] + b[0], a[1] + b[1])
    config_map = {
        "x86_64 Ubuntu": concat(
            gen(
                compilers=[
                    ("clang++ -Wno-unused-result", ".Clang"),
                    ("g++-9 -Wno-unused-result", ".GCC9"),
                    ("g++-13 -Wno-unused-result", ".GCC13"),
                ],
                standards=[
                    ("-std=c++14", ".CPP14"),
                    ("-std=c++17", ".CPP17"),
                    ("-std=c++2a", ".CPP20"),
                ],
                optimizations=[("-O0", ".O0"), ("-O2", ".O2"), ("-O3", ".O3")],
                sanitizers=[("", ".NA")],
                auxfiles=auxfiles,
                mainfile=mainfile,
            ),
            gen(
                compilers=[
                    ("clang++ -Wno-unused-result", ".Clang"),
                    ("g++-13 -Wno-unused-result", ".GCC13"),
                ],
                standards=[
                    ("-std=c++14", ".CPP14"),
                    ("-std=c++17", ".CPP17"),
                    ("-std=c++2a", ".CPP20"),
                ],
                optimizations=[("", ".NA")],
                sanitizers=[("-fsanitize=undefined,address", ".UBSAN-ASAN")],
                auxfiles=auxfiles,
                mainfile=mainfile,
            ),
        ),
        "x86_64 Alpine": gen(
            compilers=[
                ("clang++ -Wno-unused-result", ".Clang"),
                ("g++ -Wno-unused-result", ".GCC"),
            ],
            standards=[
                ("-std=c++14", ".CPP14"),
                ("-std=c++17", ".CPP17"),
                ("-std=c++2a", ".CPP20"),
            ],
            optimizations=[("-O0", ".O0"), ("-O2", ".O2"), ("-O3", ".O3")],
            sanitizers=[("", ".NA")],
            auxfiles=auxfiles,
            mainfile=mainfile,
        ),
        "x86_64 Windows": concat(
            gen(
                compilers=[
                    ("clang++ -Wno-unused-result -D_CRT_SECURE_NO_WARNINGS", ".Clang"),
                    ("g++ -Wno-unused-result -D_CRT_SECURE_NO_WARNINGS", ".GCC"),
                ],
                standards=[
                    ("-std=c++14", ".CPP14"),
                    ("-std=c++17", ".CPP17"),
                    ("-std=c++2a", ".CPP20"),
                ],
                optimizations=[("-O0", ".O0"), ("-O2", ".O2"), ("-O3", ".O3")],
                sanitizers=[("", ".NA")],
                auxfiles=auxfiles,
                mainfile=mainfile,
            ),
            gen(
                compilers=[
                    (
                        f"{CALL_VCVARS_BAT} && cl.exe /EHsc /D_CRT_SECURE_NO_WARNINGS",
                        ".MSVC",
                    )
                ],
                standards=[
                    ("/std:c++14", ".CPP14"),
                    ("/std:c++17", ".CPP17"),
                    ("/std:c++20", ".CPP20"),
                ],
                optimizations=[("/Od", ".O0"), ("/O2", ".O2")],
                sanitizers=[("", ".NA")],
                auxfiles=auxfiles,
                mainfile=mainfile,
                omit_ms_style=True,
            ),
        ),
        "riscv64 Ubuntu": gen(
            compilers=[
                ("clang++ -Wno-unused-result", ".Clang"),
                ("g++ -Wno-unused-result", ".GCC"),
            ],
            standards=[
                ("-std=c++14", ".CPP14"),
                ("-std=c++17", ".CPP17"),
                ("-std=c++2a", ".CPP20"),
            ],
            optimizations=[("-O0", ".O0"), ("-O2", ".O2"), ("-O3", ".O3")],
            sanitizers=[("", ".NA")],
            auxfiles=auxfiles,
            mainfile=mainfile,
        ),
        "arm64 MacOS": gen(
            compilers=[
                ("clang++ -Wno-unused-result", ".Clang"),
                ("g++-13 -Wno-unused-result", ".GCC13"),
            ],
            standards=[
                ("-std=c++14", ".CPP14"),
                ("-std=c++17", ".CPP17"),
                ("-std=c++2a", ".CPP20"),
            ],
            optimizations=[("-O0", ".O0"), ("-O2", ".O2"), ("-O3", ".O3")],
            sanitizers=[("", ".NA")],
            auxfiles=auxfiles,
            mainfile=mainfile,
        ),
    }

    compile_commands_dict = {
        "x86_64 Ubuntu": config_map["x86_64 Ubuntu"][0],
        "x86_64 Alpine": config_map["x86_64 Alpine"][0],
        "x86_64 Windows": config_map["x86_64 Windows"][0],
        "riscv64 Ubuntu": config_map["riscv64 Ubuntu"][0],
        "arm64 MacOS": config_map["arm64 MacOS"][0],
    }

    compile_products_dict = {
        "x86_64 Ubuntu": config_map["x86_64 Ubuntu"][1],
        "x86_64 Alpine": config_map["x86_64 Alpine"][1],
        "x86_64 Windows": config_map["x86_64 Windows"][1],
        "riscv64 Ubuntu": config_map["riscv64 Ubuntu"][1],
        "arm64 MacOS": config_map["arm64 MacOS"][1],
    }

    compile_commands = compile_commands_dict[runs_on]
    compile_products = compile_products_dict[runs_on]

    return_status = {}
    this_file_looks_odd = False
    for compile_command, compile_product in zip(compile_commands, compile_products):
        printbuffer = ""  # Buffer the contents to print in the buffer
        fold_this_run = True
        # print("::group::" + incolor(BLUE, f"With config: {compile_product.split('/')[-1]}..."))
        # print(compile_command, end=' ')
        printbuffer += compile_command + " "
        result = subprocess.run(compile_command, shell=True, capture_output=True)
        if result.returncode != 0:
            this_file_looks_odd = True
            fold_this_run = False
            status_vector = [CE(result.returncode)]
            # print(status_vector[0].colored())
            printbuffer += status_vector[0].colored() + "\n"
            # print('  ---- Compile Stdout: ----')
            printbuffer += "  ---- Compile Stdout: ----\n"
            # print('\n'.join(list(map(lambda x: '  ' + x, result.stdout.decode().split('\n')))))
            printbuffer += (
                "\n".join(
                    list(map(lambda x: "  " + x, result.stdout.decode().split("\n")))
                )
                + "\n"
            )
            # print('  ---- Compile Stderr: ----')
            printbuffer += "  ---- Compile Stderr: ----\n"
            # print('\n'.join(list(map(lambda x: '  ' + x, result.stderr.decode().split('\n')))))
            printbuffer += (
                "\n".join(
                    list(map(lambda x: "  " + x, result.stderr.decode().split("\n")))
                )
                + "\n"
            )

        else:
            status_vector = [CompileOK()]
            # print(status_vector[0].colored())
            printbuffer += status_vector[0].colored() + "\n"
            if result.stdout or result.stderr:
                # print('  ---- Compile Stdout: ----')
                printbuffer += "  ---- Compile Stdout: ----\n"
                # print('\n'.join(list(map(lambda x: '  ' + x, result.stdout.decode().split('\n')))))
                printbuffer += (
                    "\n".join(
                        list(
                            map(lambda x: "  " + x, result.stdout.decode().split("\n"))
                        )
                    )
                    + "\n"
                )
                # print('  ---- Compile Stderr: ----')
                printbuffer += "  ---- Compile Stderr: ----\n"
                # print('\n'.join(list(map(lambda x: '  ' + x, result.stderr.decode().split('\n')))))
                printbuffer += (
                    "\n".join(
                        list(
                            map(lambda x: "  " + x, result.stderr.decode().split("\n"))
                        )
                    )
                    + "\n"
                )

            in_file, out_file, ans_file = get_examples(mainfile)
            # print(f'{compile_product} < {in_file} > {out_file}', end=' ')
            printbuffer += (
                f'{compile_product} < {in_file} > {out_file}' + " "
            )
            result = subprocess.run(
                f"{os.path.join(os.path.curdir, compile_product)}",
                capture_output=True,
                input=open(in_file, "rb").read(),
                shell=True,
            )
            with open(out_file, "wb") as f:
                f.write(result.stdout)
            if result.returncode != 0:
                this_file_looks_odd = True
                fold_this_run = False
                status_vector.append(RE(result.returncode))
                # print(status_vector[-1].colored())
                printbuffer += status_vector[-1].colored() + "\n"
                # print('  ---- Execution Stdout: ----')
                printbuffer += "  ---- Execution Stdout: ----\n"
                # print('\n'.join(list(map(lambda x: '  ' + x, result.stdout.decode().split('\n')))))
                printbuffer += (
                    "\n".join(
                        list(
                            map(
                                lambda x: "  " + x,
                                result.stdout.decode().split("\n"),
                            )
                        )
                    )
                    + "\n"
                )
                # print('  ---- Execution Stderr: ----')
                printbuffer += "  ---- Execution Stderr: ----\n"
                # print('\n'.join(list(map(lambda x: '  ' + x, result.stderr.decode().split('\n')))))
                printbuffer += (
                    "\n".join(
                        list(
                            map(
                                lambda x: "  " + x,
                                result.stderr.decode().split("\n"),
                            )
                        )
                    )
                    + "\n"
                )

            else:
                # print(incolor(GREEN, 'OK'))
                printbuffer += incolor(GREEN, "OK") + "\n"
                # print(f'diff -b -B {out_file} {ans_file}', end=' ')
                printbuffer += f'diff -b -B {out_file} {ans_file} '
                result = subprocess.run(
                    f'diff -b -B {out_file} {ans_file}',
                    capture_output=True,
                    shell=True,
                )
                if result.returncode != 0:
                    this_file_looks_odd = True
                    fold_this_run = False
                    status_vector.append(WA(result.returncode))
                else:
                    status_vector.append(AC())
                # print(status_vector[-1].colored())
                printbuffer += status_vector[-1].colored() + "\n"
                if result.returncode != 0:
                    # print('  ---- We expect: ----')
                    printbuffer += "  ---- We expect: ----\n"
                    # print('\n'.join(list(map(lambda x: '  ' + x, open(ans_file).read().split('\n')))))
                    printbuffer += (
                        "\n".join(
                            list(
                                map(
                                    lambda x: "  " + x,
                                    open(ans_file)
                                    .read()
                                    .split("\n"),
                                )
                            )
                        )
                        + "\n"
                    )
                    # print('  ---- We get: ----')
                    printbuffer += "  ---- We get: ----\n"
                    # print('\n'.join(list(map(lambda x: '  ' + x, open(out_file).read().split('\n')))))
                    printbuffer += (
                        "\n".join(
                            list(
                                map(
                                    lambda x: "  " + x,
                                    open(out_file)
                                    .read()
                                    .split("\n"),
                                )
                            )
                        )
                        + "\n"
                    )
        # print(f'{compile_product.split(os.path.pathsep)[-1]}: ', end='')
        printbuffer += f"{compile_product.split(os.path.pathsep)[-1]}: "
        for status in status_vector:
            # print(status.colored(), end='; ')
            printbuffer += status.colored() + "; "

        if fold_this_run:
            print(
                "::group::"
                + incolor(BLUE, f"With config: {compile_product.split('/')[-1]}...")
            )
            print(printbuffer)
            print("\n::endgroup::")
        else:
            print(
                incolor(RED, "✘ ")
                + incolor(BLUE, f"With config: {compile_product.split('/')[-1]}...")
            )
            print(printbuffer)
            print("\n")
        return_status[compile_product] = status_vector

    print(incolor(BLUE, f"Result for {mainfile}: "))
    for key in return_status:
        print(f"-  {key}: ", end="")
        for status in return_status[key]:
            print(status.colored(), end="; ")
        print()
    if this_file_looks_odd:
        print(
            f"::error file={mainfile},title=Potential UB::Potential UB. Please take a look."
        )
    print()
    return this_file_looks_odd, return_status


if __name__ == "__main__":
    test_files = os.environ.get("TEST_CPP_FILES")
    runs_on = os.environ.get("RUNS_ON")
    cnts = [0, 0]
    output = {}
    """
    for test_file in test_files:
        this_file_looks_odd, return_status = ub_check(test_file)
        output_status = {}
        for key in return_status:
            output_status[key] = [str(i) for i in return_status[key]]
        output[test_file] = output_status
        cnt[1 if this_file_looks_odd else 0] += 1
    with open("output.txt", "w") as f:
        f.write(str(output))
    """
    if cnt[1]:
        print(f"Found {cnt[1]} files with potential UB.")
        exit(cnt[1])
