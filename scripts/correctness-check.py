import os

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

