# Find related files to conduct correctness check and undefined behavior checks.
# input: changed files (from tj-actions/changed-files, read from res.txt)
# output: related files to test (write to $GITHUB_OUTPUT, access by setting env to the output and with os.environ.get())

import os

def get_files_to_test(filenames):
    mainfiles_to_test_cpp = set()
    mainfiles_to_test_py = set()
    
    mainfiles_cpp, auxfiles_cpp, examples_cpp, skiptest_cpp = [], [], [], []
    mainfiles_py, auxfiles_py, examples_py, skiptest_py = [], [], [], []

    for filename in filenames:
        dirname, basename, extname = os.path.dirname(filename), os.path.splitext(os.path.basename(filename))[0], os.path.splitext(filename)[1]
        
        if extname.endswith('.cpp'):
            # 处理 C++ 文件变更
            mainfile = os.path.normpath(os.path.join(dirname, basename.split('.')[0] + '.cpp'))
            if mainfile in mainfiles_to_test_cpp:
                continue
            else:
                mainfiles_to_test_cpp.add(mainfile)
            
            temp_auxfiles = []
            for root, _, files in os.walk(dirname):
                for file in files:
                    if file.split('.')[0] == basename.split('.')[0] and file.endswith('.cpp'):
                        temp_auxfiles.append(os.path.normpath(os.path.join(root, file)))
            
            temp_examples = []
            for root, _, files in os.walk(dirname.replace('code', 'examples')):
                for file in files:
                    if file.split('.')[0] == basename.split('.')[0] and file.endswith('.in') and os.path.exists(os.path.join(root, file.replace('.in', '.ans'))):
                        temp_examples.append(os.path.normpath(os.path.join(root, file)))
            
            temp_skiptest = False
            if os.path.exists(os.path.join(dirname, basename + '.skip_test')):
                temp_skiptest = True
            
            mainfiles_cpp.append(mainfile)
            auxfiles_cpp.append(temp_auxfiles)
            examples_cpp.append(temp_examples)
            skiptest_cpp.append(temp_skiptest)
            
        elif extname.endswith('.py'):
            # 处理 Python 文件变更
            mainfile = os.path.normpath(os.path.join(dirname, basename.split('.')[0] + '.py'))
            if mainfile in mainfiles_to_test_py:
                continue
            else:
                mainfiles_to_test_py.add(mainfile)
            
            temp_auxfiles = []
            for root, _, files in os.walk(dirname):
                for file in files:
                    if file.split('.')[0] == basename.split('.')[0] and file.endswith('.py'):
                        temp_auxfiles.append(os.path.normpath(os.path.join(root, file)))
            
            temp_examples = []
            for root, _, files in os.walk(dirname.replace('code', 'examples')):
                for file in files:
                    if file.split('.')[0] == basename.split('.')[0] and file.endswith('.in') and os.path.exists(os.path.join(root, file.replace('.in', '.ans'))):
                        temp_examples.append(os.path.normpath(os.path.join(root, file)))
            
            temp_skiptest = False
            if os.path.exists(os.path.join(dirname, basename + '.skip_test')):
                temp_skiptest = True
            
            mainfiles_py.append(mainfile)
            auxfiles_py.append(temp_auxfiles)
            examples_py.append(temp_examples)
            skiptest_py.append(temp_skiptest)
            
        elif extname.endswith(('.in', '.ans')):
            # 处理测试文件变更 - 同时扫描 C++ 和 Python
            # 扫描 C++ 文件
            mainfile_cpp = os.path.normpath(os.path.join(dirname.replace('examples', 'code'), basename.split('.')[0] + '.cpp'))
            if mainfile_cpp not in mainfiles_to_test_cpp and os.path.exists(mainfile_cpp):
                mainfiles_to_test_cpp.add(mainfile_cpp)
                
                temp_auxfiles_cpp = []
                cpp_dir = dirname.replace('examples', 'code')
                for root, _, files in os.walk(cpp_dir):
                    for file in files:
                        if file.split('.')[0] == basename.split('.')[0] and file.endswith('.cpp'):
                            temp_auxfiles_cpp.append(os.path.normpath(os.path.join(root, file)))
                
                temp_examples_cpp = [os.path.normpath(os.path.join(dirname, basename + '.in'))]
                
                temp_skiptest_cpp = False
                if os.path.exists(os.path.join(cpp_dir, basename + '.skip_test')):
                    temp_skiptest_cpp = True
                
                mainfiles_cpp.append(mainfile_cpp)
                auxfiles_cpp.append(temp_auxfiles_cpp)
                examples_cpp.append(temp_examples_cpp)
                skiptest_cpp.append(temp_skiptest_cpp)
            
            # 扫描 Python 文件
            mainfile_py = os.path.normpath(os.path.join(dirname.replace('examples', 'code'), basename.split('.')[0] + '.py'))
            if mainfile_py not in mainfiles_to_test_py and os.path.exists(mainfile_py):
                mainfiles_to_test_py.add(mainfile_py)
                
                temp_auxfiles_py = []
                py_dir = dirname.replace('examples', 'code')
                for root, _, files in os.walk(py_dir):
                    for file in files:
                        if file.split('.')[0] == basename.split('.')[0] and file.endswith('.py'):
                            temp_auxfiles_py.append(os.path.normpath(os.path.join(root, file)))
                
                temp_examples_py = [os.path.normpath(os.path.join(dirname, basename + '.in'))]
                
                temp_skiptest_py = False
                if os.path.exists(os.path.join(py_dir, basename + '.skip_test')):
                    temp_skiptest_py = True
                
                mainfiles_py.append(mainfile_py)
                auxfiles_py.append(temp_auxfiles_py)
                examples_py.append(temp_examples_py)
                skiptest_py.append(temp_skiptest_py)

    # 输出到 GitHub Actions
    with open(os.environ.get("GITHUB_OUTPUT"), 'w') as f:
        output_lines = []
        
        if mainfiles_cpp:
            output_lines.append(f'files_to_test_cpp={(mainfiles_cpp, auxfiles_cpp, examples_cpp, skiptest_cpp)}')
        
        if mainfiles_py:
            output_lines.append(f'files_to_test_py={(mainfiles_py, auxfiles_py, examples_py, skiptest_py)}')
        
        f.write('\n'.join(output_lines))
        print('\n'.join(output_lines))

with open("res.txt") as file_object:
    lines = file_object.readlines()
changed_files = [name for line in lines for name in line.split()]
get_files_to_test(changed_files)